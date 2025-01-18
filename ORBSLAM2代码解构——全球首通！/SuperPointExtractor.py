import os
import cv2
import math
import time
import logging
import numpy as np

import torch

from utils import image2tensor, plot_keypoints, create_logger
from SuperPoint import SuperPoint


class ExtractorNode:
    def __init__(self):
        self.bNoMore = False  # 是否需要进一步细分当前节点
        self.vKeys = []  # 存储当前节点内的特征点列表
        self.vScores = []
        self.vDesc = []  # 存储特征点列表中对应的特征点描述子
        self.UL = None  # 左上角坐标
        self.UR = None  # 右上角坐标
        self.BL = None  # 左下角坐标
        self.BR = None  # 右下角坐标

    def DivideNode(self, n1, n2, n3, n4):
        # 将当前节点划分为四个子节点

        # ceil: 向上取整
        half_x = math.ceil((self.UR[0] - self.UL[0]) / 2)  # 计算水平分割线
        half_y = math.ceil((self.BR[1] - self.UL[1]) / 2)  # 计算垂直分割线

        # 定义每个子节点的边界
        n1.UL = self.UL
        n1.UR = (self.UL[0] + half_x, self.UL[1])
        n1.BL = (self.UL[0], self.UL[1] + half_y)
        n1.BR = (self.UL[0] + half_x, self.UL[1] + half_y)

        n2.UL = n1.UR
        n2.UR = self.UR
        n2.BL = n1.BR
        n2.BR = (self.UR[0], self.UL[1] + half_y)

        n3.UL = n1.BL
        n3.UR = n1.BR
        n3.BL = self.BL
        n3.BR = (n1.BR[0], self.BL[1])

        n4.UL = n3.UR
        n4.UR = n2.BR
        n4.BL = n3.BR
        n4.BR = self.BR

        # 将特征点和对应的描述子分配给对应的子节点
        for kp, scores, desc in zip(self.vKeys, self.vScores, self.vDesc):
            if kp[0] < n1.UR[0]:
                if kp[1] < n1.BR[1]:
                    n1.vKeys.append(kp)
                    n1.vScores.append(scores)
                    n1.vDesc.append(desc)
                else:
                    n3.vKeys.append(kp)
                    n3.vScores.append(scores)
                    n3.vDesc.append(desc)
            elif kp[1] < n1.BR[1]:
                n2.vKeys.append(kp)
                n2.vScores.append(scores)
                n2.vDesc.append(desc)
            else:
                n4.vKeys.append(kp)
                n4.vScores.append(scores)
                n4.vDesc.append(desc)

        # 如果子节点只包含一个特征点, 则标记 bNoMore 为 True, 表示不再细分
        if len(n1.vKeys) == 1:
            n1.bNoMore = True
        if len(n2.vKeys) == 1:
            n2.bNoMore = True
        if len(n3.vKeys) == 1:
            n3.bNoMore = True
        if len(n4.vKeys) == 1:
            n4.bNoMore = True

        return n1, n2, n3, n4


class SuperPointExtractor(object):
    def __init__(self, width, height, nFeatures, kptThreshold, spPath, cuda, logger):

        self.cuda = cuda
        self.device = 'cuda' if torch.cuda.is_available() and self.cuda else 'cpu'
        logger.info("==>Using device: {}!!!".format(self.device))

        self.path = os.path.join(spPath, "superpoint_v1.pth")
        logger.info("==>creating SuperPoint detector...")
        self.superpoint = SuperPoint(kptThreshold, self.path, logger).to(self.device)
        self.superpoint.eval()

        self.nFeatures = nFeatures
        self.width = width
        self.height = height

        self.height_crop = self.height - self.height % 8
        self.width_crop = self.width - self.width % 8
        self.BoardY = self.height % 8 // 2
        self.BoardX = self.width % 8 // 2

    def __call__(self, image):
        # 存储所有的特征点和对应的描述子
        keypoints, descriptors = [], []

        height, width, channel = image.shape
        # Step 1 检查图像的长宽是否符合要求
        assert (height == self.height and width == self.width), ('The height and width in config must be the same as '
                                                                 'the height and width of the image')

        # Step 2 检查图像是否是单通道灰度图
        if channel == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Step 3 中心裁剪图像, 为了后续进行图像金字塔的构建和SuperPoint提取(图像长宽须被8整除)
        self.image_cropped = image[self.BoardY:self.BoardX+self.height_crop, self.BoardX:self.BoardY+self.width_crop]

        # Step 4 对裁剪后的图像提取特征点
        image_tensor = image2tensor(self.image_cropped, self.device)
        pred_ = self.superpoint({'image': image_tensor})

        # Step 5 对提取出来的特征点进行四叉树分配, 并根据self.nfeatures剔除
        ToDistributeKeys = pred_["keypoints"][0].cpu().detach().tolist()
        ToDistributeScores = pred_["scores"][0].cpu().detach().tolist()
        ToDistributeDesc = pred_["descriptors"][0].cpu().detach().numpy().transpose()
        ToDistributeDesc = [ToDistributeDesc[i, :] for i in range(ToDistributeDesc.shape[0])]

        keypoints, scores, descriptors = self.DistributeOctTree(
            ToDistributeKeys, ToDistributeScores, ToDistributeDesc,
            0, self.width_crop-1, 0, self.height_crop-1, self.nFeatures
        )

        # Step 5 将分配好的特征点坐标恢复到原图像的坐标系下
        for kp in keypoints:
            kp[0] = kp[0] + self.BoardX
            kp[1] = kp[1] + self.BoardY

        """
        # ---------- 中间结果可视化 ----------
        image_color = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        for kp in keypoints:
            center = tuple(map(int, kp))
            image_color = cv2.circle(image_color, center, 1, (0, 255, 0), -1)

        cv2.imshow(f"Keypoints: {len(keypoints)}", image_color)
        cv2.waitKey(0)
        # ---------- 中间结果可视化 ----------
        """

        ret_dict = {
            "image_size": np.array([height, width]),
            "keypoints": np.array(keypoints),
            "scores": np.array(scores),
            "descriptors": np.array(descriptors)
        }

        return ret_dict

    def DistributeOctTree(self, ToDistributeKeys, ToDistributeScores, ToDistributeDesc, minX, maxX, minY, maxY, num):
        # Step 1 根据宽高比确定初始节点数目
        # 计算应该生成的初始节点个数, 根节点的数量nIni是根据边界的宽高比值确定的, 一般是1或者2
        nIni = round((maxX - minX) / (maxY - minY))  # 如果宽高比小 0.5, 则会报错
        # 初始节点的 x 方向有多少个像素
        hx = (maxX - minX) / nIni
        # 存储有提取器节点的列表
        lNodes = []
        # 存储初始提取器节点的列表, 大小为nIni
        vpIniNodes = [None] * nIni

        # Step 2 生成初始提取器节点
        for i in range(nIni):
            # 生成一个提取器节点
            ni = ExtractorNode()
            # 设置提取器节点的图像边界
            ni.UL = (int(hx * i), 0)
            ni.UR = (int(hx * (i+1)), 0)
            ni.BL = (int(ni.UL[0]), maxY-minY)
            ni.BR = (int(ni.UR[0]), maxY-minY)
            ni.vKeys = []
            ni.vDesc = []

            # 将提取器节点添加到列表中
            lNodes.append(ni)
            # 将lNodes中最后一个元素的引用赋给vpIniNodes[i]
            vpIniNodes[i] = lNodes[-1]

        # Step 3 将特征点和对应的描述子分配到子提取器节点中
        for kp, score, desc in zip(ToDistributeKeys, ToDistributeScores, ToDistributeDesc):
            # 按照特征点的x坐标, 分配给对应图像区域的提取器节点(初始提取器节点)
            idx = int(kp[0] // hx)
            vpIniNodes[idx].vKeys.append(kp)
            vpIniNodes[idx].vScores.append(score)
            vpIniNodes[idx].vDesc.append(desc)

        # Step 4 遍历此提取器节点列表, 标记那些不可再分裂的节点, 删除那些没有分配到特征点的节点
        i = 0
        while i < len(lNodes):
            node = lNodes[i]
            # 如果初始的提取器节点所分配到的特征点个数为1
            if len(node.vKeys) == 1:
                node.bNoMore = True
                i += 1
            elif len(node.vKeys) == 0:
                lNodes.pop(i)
            else:
                i += 1

        # 结束标志位清空
        bFinish = False
        # 记录迭代次数
        iteration = 0

        # Step 5 利用四叉树方法对图像进行划分区域, 均匀分配特征点
        while not bFinish:
            # 更新迭代次数
            iteration += 1
            # 当前节点个数
            prevSize = len(lNodes)
            # 重新定位迭代器指向列表头部
            lit = 0
            # 需要展开的节点计数, 这个一直保持累计, 不清零
            nToExpand = 0
            # 声明一个列表用于存储节点的vSize句柄对
            # 这个变量记录了在一次分裂循环中, 那些可以再继续进行分裂的节点中包含的特征点数目和句柄
            vSizeAndPointerToNode = []
            # 将目前的子区域进行划分
            # 开始遍历列表中所有的提取器节点, 并进行分解或保留
            while lit < len(lNodes):
                node = lNodes[lit]
                # 如果提取器节点只有一个特征点, 那么就没有必要再进行细分了
                if node.bNoMore:
                    # 跳过当前节点, 继续下一个
                    lit += 1
                    continue
                else:
                    # 如果当前的提取器节点具有超过一个的特征点, 则进行分裂
                    n1, n2, n3, n4 = ExtractorNode(), ExtractorNode(), ExtractorNode(), ExtractorNode()
                    node.DivideNode(n1, n2, n3, n4)
                    for n in [n1, n2, n3, n4]:
                        # 如果子节点中有特征点, 则添加到lNodes中
                        if len(n.vKeys) > 0:
                            # 插入到lNodes的前面
                            lNodes.insert(0, n)
                            # 确保lit一直指向的是分裂前的母节点
                            lit += 1
                            # 再判断其包含的特征点数目是否大于1
                            if len(n.vKeys) > 1:
                                # 如果有超过一个的特征点, 那么待展开的节点计数加1
                                nToExpand += 1
                                # 保存这个节点里包含的特征点数目和该节点
                                vSizeAndPointerToNode.append((len(n.vKeys), lNodes[0]))
                    # 删除分裂前的母节点
                    lNodes.pop(lit)

                    """
                    # ---------- 中间结果可视化 ----------
                    image_color = cv2.cvtColor(self.image_cropped, cv2.COLOR_GRAY2BGR)
                    for kp in ToDistributeKeys:
                        center = tuple(map(int, kp))
                        image_color = cv2.circle(image_color, center, 1, (0, 255, 0), -1)

                    print(f"---------- {lit} ----------")
                    for node in lNodes:
                        image_color = cv2.rectangle(image_color, (node.UL[0], node.UL[1]), (node.BR[0], node.BR[1]),
                                                    (0, 255, 255), thickness=1)
                        print(node.UR)
                    cv2.imshow(f"lNodes: {len(lNodes)}--nToExpand: {nToExpand}", image_color)
                    cv2.waitKey(0)
                    cv2.destroyAllWindows()
                    # ---------- 中间结果可视化 ----------
                    """

            """
            # ---------- 中间结果可视化 ----------
            image_color = cv2.cvtColor(self.image_cropped, cv2.COLOR_GRAY2BGR)
            for kp in ToDistributeKeys:
                center = tuple(map(int, kp))
                image_color = cv2.circle(image_color, center, 1, (0, 255, 0), -1)

            for node in lNodes:
                image_color = cv2.rectangle(image_color, (node.UL[0], node.UL[1]), (node.BR[0], node.BR[1]),
                                            (0, 255, 255), thickness=1)
                # print(node.UR)
            cv2.imshow(f"lNodes {len(lNodes)}--nToExpand {nToExpand}", image_color)
            cv2.waitKey(0)
            # cv2.destroyAllWindows()
            # ---------- 中间结果可视化 ----------
            """

            # 判断是否满足停止条件, 满足一个即可
            if len(lNodes) >= num or len(lNodes) == prevSize:
                bFinish = True

            # Step 6 当再划分之后所有的Node数大于要求数目时, 就慢慢划分直到使其刚刚达到或者超过要求的特征点个数
            elif len(lNodes) + nToExpand * 3 > num:
                # 如果再分裂一次那么数目就要超了, 这里想办法尽可能使其刚刚达到或者超过要求的特征点个数就退出
                while not bFinish:
                    # 获取当前的lNodes中的节点个数
                    prevSize = len(lNodes)
                    # 保留那些还可以分裂的节点的信息
                    vPrevSizeAndPointerToNode = vSizeAndPointerToNode
                    # 清空
                    vSizeAndPointerToNode = []
                    # 对需要划分的节点进行排序, 对pair对的第一个元素进行排序(特征点个数), 默认是从小到大排序
                    # 优先分裂特征点多的节点, 使得特征点密集的区域保留更少的特征点
                    vPrevSizeAndPointerToNode.sort(key=lambda x: x[0])
                    # 从后往前遍历
                    for j in range(len(vPrevSizeAndPointerToNode)-1, -1, -1):
                        # 对每个需要进行分裂的节点进行分裂
                        node = vPrevSizeAndPointerToNode[j][1]
                        n1, n2, n3, n4 = ExtractorNode(), ExtractorNode(), ExtractorNode(), ExtractorNode()
                        node.DivideNode(n1, n2, n3, n4)
                        # 处理子节点
                        for n in [n1, n2, n3, n4]:
                            # 如果子节点中有特征点, 则添加到lNodes中
                            if len(n.vKeys) > 0:
                                # 插入到lNodes的前面
                                lNodes.insert(0, n)
                                # 再判断其包含的特征点数目是否大于1
                                if len(n.vKeys) > 1:
                                    # 为后续可能的又一次for循环做准备
                                    vSizeAndPointerToNode.append((len(n.vKeys), lNodes[0]))
                        # 删除母节点
                        lNodes.remove(node)

                        """
                        # ---------- 中间结果可视化 ----------
                        image_color = cv2.cvtColor(self.image_cropped, cv2.COLOR_GRAY2BGR)
                        for kp in ToDistributeKeys:
                            center = tuple(map(int, kp))
                            image_color = cv2.circle(image_color, center, 1, (0, 255, 0), -1)
                        print(f"---------- ----------")
                        for node in lNodes:
                            image_color = cv2.rectangle(image_color, (node.UL[0], node.UL[1]),
                                                        (node.BR[0], node.BR[1]), (0, 255, 255), thickness=1)
                        cv2.imshow(f"lNodes: {len(lNodes)}--FeatureNUm: {num}", image_color)
                        cv2.waitKey(0)
                        cv2.destroyAllWindows()
                        # ---------- 中间结果可视化 ----------
                        """

                        # 判断是否超过了需要的特征点数, 是的话退出, 不是的话继续这个分裂过程, 直到刚刚达到或者超过要求的特征点个数
                        if len(lNodes) >= num:
                            break

                    """
                    # ---------- 中间结果可视化 ----------
                    image_color = cv2.cvtColor(self.image_cropped, cv2.COLOR_GRAY2BGR)
                    for kp in ToDistributeKeys:
                        center = tuple(map(int, kp))
                        image_color = cv2.circle(image_color, center, 1, (0, 255, 0), -1)
                    for node in lNodes:
                        image_color = cv2.rectangle(image_color, (node.UL[0], node.UL[1]),
                                                    (node.BR[0], node.BR[1]), (0, 255, 255), thickness=1)
                    cv2.imshow(f"lNodes {len(lNodes)}--FeatureNUm {num}", image_color)
                    cv2.waitKey(0)
                    # cv2.destroyAllWindows()
                    # ---------- 中间结果可视化 ----------
                    """

                    # 这里理想中应该是一个for循环就能够达成结束条件了, 但有些子节点所在的区域会没有特征点
                    # 因此很有可能一次for循环之后, 特征点的数目还是不能够满足要求, 所以还是需要判断结束条件
                    # 判断是否达到了停止条件
                    if len(lNodes) >= num or len(lNodes) == prevSize:
                        bFinish = True

        # Step 7 保留每个区域响应值最大的一个兴趣点
        # 用来存储过滤后的特征点, 响应值和描述子
        vResultKeys = []
        vResultScores = []
        vResultDesc = []
        # 遍历节点列表
        for node in lNodes:
            # 得到这个节点区域中的特征点和描述子列表
            vNodeKeys = node.vKeys
            vNodeScores = node.vScores
            vNodeDesc = node.vDesc
            # 获取第一个特征点和对应的描述子, 作为最大响应值对应的关键点
            pKP = vNodeKeys[0]
            pSC = vNodeScores[0]
            pDC = vNodeDesc[0]
            # 用第一个特征点的响应值初始化最大响应值
            maxResponse = pSC
            # 开始遍历这个节点区域中的所有特征点, 从第二个特征点开始
            for k in range(1, len(vNodeKeys)):
                # 更新最大响应值
                if vNodeScores[k] > maxResponse:
                    # 更新pKp, pSC和pDC指向具有最大响应值的keypoints
                    pKP = vNodeKeys[k]
                    pSC = vNodeScores[k]
                    pDC = vNodeDesc[k]
                    maxResponse = vNodeScores[k]
            # 将这个节点区域中响应值最大的特征点加入最终的要保留的特征点列表中
            vResultKeys.append(pKP)
            vResultScores.append(pSC)
            vResultDesc.append(pDC)

        # 返回最终过滤好的特征点, 响应值和描述子列表
        return vResultKeys, vResultScores, vResultDesc


if __name__ == "__main__":
    # 创建日志器, 记录运行信息
    logger = create_logger(name='SuperPointDetector')

    # 禁用pytorch梯度计算
    torch.set_grad_enabled(False)

    img = cv2.imread("/home/zourz/work/Dataset/SLAM/KITTI/data_odometry_gray/dataset/sequences/00/image_0/000125.png")

    extractor = SuperPointExtractor(width=1241, height=376, nFeatures=1204, kptThreshold=0.005,
                                    cuda=True, spPath="./weights/superpoint", logger=logger)

    start_time = time.time()  # 记录开始时间

    kptdescs = extractor(img)

    end_time = time.time()  # 记录结束时间

    elapsed_time = end_time - start_time  # 计算运行时间
    print(f"运行时间: {elapsed_time:.4f}秒")

    img = plot_keypoints(img, kptdescs["keypoints"])
    cv2.imshow("SuperPoint", img)
    cv2.waitKey()
