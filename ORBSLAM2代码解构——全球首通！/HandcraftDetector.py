import cv2
import math
import logging
import numpy as np

from packaging import version

from utils.tools import plot_keypoints


class ExtractorNode:
    def __init__(self):
        self.bNoMore = False  # 是否需要进一步细分当前节点
        self.vKeys = []  # 存储当前节点内的特征点列表
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
        for kp, desc in zip(self.vKeys, self.vDesc):
            if kp.pt[0] < n1.UR[0]:
                if kp.pt[1] < n1.BR[1]:
                    n1.vKeys.append(kp)
                    n1.vDesc.append(desc)
                else:
                    n3.vKeys.append(kp)
                    n3.vDesc.append(desc)
            elif kp.pt[1] < n1.BR[1]:
                n2.vKeys.append(kp)
                n2.vDesc.append(desc)
            else:
                n4.vKeys.append(kp)
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


class HandcraftDetector(object):
    default_config = {
        "type": "ORB",
        "nfeatures": 1000,
        "scaleFactor": 1.2,
        "nLevels": 4,
        "edgeThreshold": 19,
        "iniThreshold": 20,
        "minThreshold": 7,
    }

    def __init__(self, config=None):
        self.config = self.default_config
        self.config = {**self.config, **config}  # 将传入的 config 与默认配置进行合并, 会覆盖默认配置中的相关项
        logging.info("Handcraft detector config: ")
        logging.info(self.config)

        self.nfeatures = self.config["nfeatures"]
        self.scaleFactor = self.config["scaleFactor"]
        self.nLevels = self.config["nLevels"]
        self.edgeThreshold = self.config["edgeThreshold"]
        self.iniThreshold = self.config["iniThreshold"]
        self.minThreshold = self.config["minThreshold"]

        self.mvScaleFactor = [1.0] * self.nLevels  # 存储每层图像缩放系数的 List, 并调整为符合图层数目的大小
        self.mvLevelSigma2 = [1.0] * self.nLevels  # 每层图像相对初始图像缩放因子的平方
        # 逐层计算图像金字塔中图像相当于初始图像的缩放系数
        for i in range(1, self.nLevels):
            self.mvScaleFactor[i] = self.mvScaleFactor[i-1] * self.scaleFactor
            self.mvLevelSigma2[i] = self.mvScaleFactor[i] * self.mvScaleFactor[i]
        # 生成两个对应的列表, 保存了 mvScaleFactor 和 mvLevelSigma2 中每个元素的倒数
        self.mvInvScaleFactor = [1.0 / x for x in self.mvScaleFactor]
        self.mvInvLevelSigma2 = [1.0 / x for x in self.mvLevelSigma2]

        self.mnFeaturesPerLevel = []  # 初始化一个空的每层金字塔要提取的特征点个数列表
        factor = 1.0 / self.scaleFactor  # 图片降采样缩放系数的倒数
        # 第 0 层图像应该分配的特征点数量
        nDesiredFeaturesPerScale = self.nfeatures * (1-factor) / (1-pow(factor, self.nLevels))

        sumFeatures = 0
        # 开始逐层计算要分配的特征点个数, 顶层图像除外
        for level in range(self.nLevels-1):
            # 分配 (round: 用于将参数四舍五入到最接近的整数)
            self.mnFeaturesPerLevel.append(round(nDesiredFeaturesPerScale))
            sumFeatures += self.mnFeaturesPerLevel[level]  # 累计
            nDesiredFeaturesPerScale *= factor  # 乘系数
        # 由于上面的取整操作, 可能会导致剩余一些特征点没有被分配, 所以将剩余的特征点分配到最高的图层中
        # [434, 362, 302, 251, 209, 175, 145, 122]
        self.mnFeaturesPerLevel.append(max(self.nfeatures - sumFeatures, 0))

    def __call__(self, image):
        # 存储所有的特征点和对应的描述子
        keypoints, descriptors = [], []

        # Step 1 检查图像是否是单通道灰度图
        if image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Step 2 构建图像金字塔
        self.mvImagePyramid = []  # 初始化一个空的图像金字塔列表
        self.ComputePyramid(image)

        if self.config["type"] == "ORB":
            logging.info("creating ORB detector...")
        elif self.config["type"] == "SIFT":
            logging.info("creating SIFT detector...")

        # Step 3 使用四叉树的方式计算每层图像的特征点和描述子并进行分配
        # allkeypoints 的 size 可以看作是 [level, KeypointsPerLevel], alldescriptors 同理
        allkeypoints, alldescriptors = self.ComputeFeaturesOctTree()

        # Step 4 对非第 0 层图像中的特征点的坐标恢复到第 0 层图像(原图像)的坐标系下
        for level in range(self.nLevels):
            # 获取在 allkeypoints 中当前图层中的所有特征点和对应的描述子
            KeypointsPerLevel = allkeypoints[level]
            DescriptorsPerLevel = alldescriptors[level]
            if level != 0:
                # 获取当前图层的缩放系数
                scale = self.mvScaleFactor[level]
                # 遍历本层所有的特征点
                for kp in KeypointsPerLevel:
                    x, y = kp.pt
                    kp.pt = (x * scale, y * scale)

            # Step 5 将 KeypointsPerLevel 和 DescriptorsPerLevel 插入到 keypoints 和 descriptors 的末尾
            keypoints += KeypointsPerLevel
            descriptors += DescriptorsPerLevel

        """
        # ---------- 中间结果可视化 ----------
        image_color = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        for kp in keypoints:
            center = tuple(map(int, kp.pt))
            image_color = cv2.circle(image_color, center, 1, (0, 255, 0), -1)
        print(f"---------- ----------")
        cv2.imshow(f"Keypoint: {len(keypoints)}", image_color)
        # ---------- 中间结果可视化 ----------
        """

        kpts = np.zeros((len(keypoints), 2))
        scores = np.zeros((len(keypoints)))
        for i, p in enumerate(keypoints):
            kpts[i, 0] = p.pt[0]
            kpts[i, 1] = p.pt[1]
            scores[i] = p.response

        desc = np.vstack([descriptors])

        return {"image_size": np.array([image.shape[0], image.shape[1]]),
                "keypoints": kpts,
                "scores": scores,
                "descriptors": desc}

    def ComputePyramid(self, image):

        # 开始遍历所有的图层
        for level in range(self.nLevels):
            scale = self.mvInvScaleFactor[level]  # 获取本层图像的缩放系数的倒数
            sz = (round(image.shape[1] * scale), round(image.shape[0] * scale))
            if level != 0:
                # 对第 0 层以上图像, 将原始图像按 sz 缩放到当前层
                self.mvImagePyramid.append(
                    cv2.resize(self.mvImagePyramid[level-1], (sz[0], sz[1]), interpolation=cv2.INTER_LINEAR))
            else:
                # 对第 0 层图像, 不进行缩放
                self.mvImagePyramid.append(image)

    def ComputeFeaturesOctTree(self):
        # 存储所有图层中包含的特征点和描述子列表
        allkeypoints = []
        alldescriptors = []

        # 图像 cell 的尺寸, 是个正方形, 可以理解为边长
        w = 30

        # 处理每一层图像
        for level in range(self.nLevels):

            # 存储当前层图像中需要进行平均分配的特征点和描述子
            vToDistributeKeys = []
            vToDistributeDesc = []

            # 计算进行特征点提取的图像区域尺寸
            width = self.mvImagePyramid[level].shape[1]  # [1241, 1034, 862, 718, 598, 499, 416, 346]
            height = self.mvImagePyramid[level].shape[0]  # [376, 313, 261, 218, 181, 151, 126, 105]

            # 计算当前层图像中, 网格的行数和列数
            nCols = width // w  # [41, 34, 28, 23, 19, 16, 13, 11]
            nRows = height // w  # [12, 10, 8, 7, 6, 5, 4, 3]

            # 计算每个网格实际的行数和列数(ceil: 向上取整)
            wCell = math.ceil(width / nCols)  # [31, 31, 31, 32, 32, 32, 32, 32]
            hCell = math.ceil(height / nRows)  # [32, 32, 33, 32, 31, 31, 32, 35]

            # 开始遍历网格, 以行开始遍历
            for i in range(nRows):
                # 计算当前网格初始行坐标
                iniY = i * hCell
                # 计算当前网格最大的行坐标, 这里的 38 = 19 + 19, 即考虑到了多出来 19 是为了进行 ORB 特征点提取用(计算描述子)
                maxY = iniY + hCell + 38 - 1
                # 如果初始的行坐标就已经超过了有效的图像边界了, 则跳过, 这里的"有效图像"是指原始的, 可以提取 ORB 特征点的图像区域
                if iniY >= height - 38:
                    continue
                # 如果图像太小导致不能够正好划分出来整齐的图像网格, 那么就要减小最后一行网格图像的尺寸
                if maxY > height:
                    maxY = height - 1
                # 开始列的遍历
                for j in range(nCols):
                    # 计算初始的列坐标
                    iniX = j * wCell
                    # 计算当前网格的最大列坐标
                    maxX = iniX + wCell + 38 - 1
                    # 如果初始的列坐标就已经超过了有效的图像边界了, 则跳过
                    if iniX >= width - 38:
                        continue
                    # 如果最大列坐标越过图像边界, 则进行调整
                    if maxX > width:
                        maxX = width - 1

                    # print(f"({iniX}, {iniY}), ({maxX}, {maxY})")sssssss

                    """
                    # ---------- 中间结果可视化 ----------
                    image_color = cv2.cvtColor(self.mvImagePyramid[level], cv2.COLOR_GRAY2BGR)
                    image_color = cv2.rectangle(image_color, (iniX, iniY), (maxX, maxY), (255, 0, 0), thickness=5)
                    cv2.imshow(f"Level {level}", image_color)
                    cv2.waitKey(0)
                    # cv2.destroyAllWindows()
                    # ---------- 中间结果可视化 ----------
                    """

                    # 提取特征点, 自适应阈值
                    sub_image = self.mvImagePyramid[level][iniY:maxY, iniX:maxX]
                    # 调用 OpenCV 库来检测特征点
                    if self.config["type"] == "ORB":
                        det = cv2.ORB_create(nlevels=1, edgeThreshold=self.edgeThreshold,
                                             fastThreshold=self.iniThreshold)
                    elif self.config["type"] == "SIFT":
                        det = cv2.SIFT_create(nfeatures=500, nOctaveLayers=1, edgeThreshold=self.edgeThreshold,
                                              contrastThreshold=self.iniThreshold)
                    kpts, desc = det.detectAndCompute(sub_image, None)

                    # 如果在这个网格中, 使用默认的检测阈值没有能够检测到特征点
                    if len(kpts) == 0:
                        # 那么就使用更低的阈值来重新检测
                        if self.config["type"] == "ORB":
                            det = cv2.ORB_create(nlevels=1, edgeThreshold=self.edgeThreshold,
                                                 fastThreshold=self.minThreshold)
                        elif self.config["type"] == "SIFT":
                            det = cv2.SIFT_create(nfeatures=500, nOctaveLayers=1, edgeThreshold=self.edgeThreshold,
                                                  contrastThreshold=self.minThreshold)
                        kpts, desc = det.detectAndCompute(sub_image, None)

                    # 当网格中检测到特征点的时候
                    if kpts:
                        # 遍历其中所有的特征点
                        for kpt, des in zip(kpts, desc):
                            # 原始坐标(基于网格的坐标)
                            x, y = kpt.pt
                            # 修改后的坐标(恢复到当前图层内的坐标)
                            new_x = x + j * wCell
                            new_y = y + i * hCell
                            # 创建一个新的 KeyPoint, 其他参数保持不变
                            updated_kpt = cv2.KeyPoint(new_x, new_y, kpt.size, kpt.angle, kpt.response,
                                                       kpt.octave, kpt.class_id)
                            vToDistributeKeys.append(updated_kpt)
                            vToDistributeDesc.append(des)

            # 对提取出来的特征点进行四叉树分配, 并根据 self.mnFeaturesPerLevel[level] 剔除
            keypoints, descriptors = self.DistributeOctTree(vToDistributeKeys, vToDistributeDesc, 0, width-1,
                                                            0, height-1, self.mnFeaturesPerLevel[level], level)

            for kp in keypoints:
                kp.octave = level

            """
            # ---------- 中间结果可视化 ----------
            image_color = cv2.cvtColor(self.mvImagePyramid[level], cv2.COLOR_GRAY2BGR)
            for kp in keypoints:
                center = tuple(map(int, kp.pt))
                image_color = cv2.circle(image_color, center, 2, (0, 255, 0), -1)
            print(f"---------- ----------")
            cv2.imshow(f"Level: {level}--Keypoint: {len(keypoints)}", image_color)
            # cv2.imshow(f"Level: {level}", image_color)
            print(f"Level {level}: ", width, height, nCols, nRows, wCell, hCell)
            # ---------- 中间结果可视化 ----------
            """

            allkeypoints.append(keypoints)
            alldescriptors.append(descriptors)

        return allkeypoints, alldescriptors

    def DistributeOctTree(self, vToDistributeKeys, vToDistributeDese, minX, maxX, minY, maxY, num, level):
        # Step 1 根据宽高比确定初始节点数目
        # 计算应该生成的初始节点个数, 根节点的数量 nIni 是根据边界的宽高比值确定的, 一般是 1 或者 2
        nIni = round((maxX - minX) / (maxY - minY))  # 如果宽高比小于 0.5, 则会报错
        # 初始节点的 x 方向有多少个像素
        hx = (maxX - minX) / nIni
        # 存储有提取器节点的列表
        lNodes = []
        # 存储初始提取器节点的列表, 大小为 nIni
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
            # 将 LNodes 中最后一个元素的引用赋给 vpIniNodes[i]
            vpIniNodes[i] = lNodes[-1]

        # Step 3 将特征点和对应的描述子分配到子提取器节点中
        for kp, desc in zip(vToDistributeKeys, vToDistributeDese):
            # 按照特征点的 x 坐标, 分配给对应图像区域的提取器节点(初始提取器节点)
            idx = int(kp.pt[0] // hx)
            vpIniNodes[idx].vKeys.append(kp)
            vpIniNodes[idx].vDesc.append(desc)

        # Step 4 遍历此提取器节点列表, 标记那些不可再分裂的节点, 删除那些没有分配到特征点的节点
        i = 0
        while i < len(lNodes):
            node = lNodes[i]
            # 如果初始的提取器节点所分配到的特征点个数为 1
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
            # 声明一个列表用于存储节点的 vSize 句柄对
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
                        # 如果子节点中有特征点, 则添加到 lNodes 中
                        if len(n.vKeys) > 0:
                            # 插入到 lNodes 的前面
                            lNodes.insert(0, n)
                            # 确保 lit 一直指向的是分裂前的母节点
                            lit += 1
                            # 再判断其包含的特征点数目是否大于 1
                            if len(n.vKeys) > 1:
                                # 如果有超过一个的特征点, 那么待展开的节点计数加 1
                                nToExpand += 1
                                # 保存这个节点里包含的特征点数目和该节点
                                vSizeAndPointerToNode.append((len(n.vKeys), lNodes[0]))
                    # 删除分裂前的母节点
                    lNodes.pop(lit)

                    """
                    # ---------- 中间结果可视化 ----------
                    if level == 0:
                        image_color = cv2.cvtColor(self.mvImagePyramid[level], cv2.COLOR_GRAY2BGR)
                        for kp in vToDistributeKeys:
                            center = tuple(map(int, kp.pt))
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
            image_color = cv2.cvtColor(self.mvImagePyramid[level], cv2.COLOR_GRAY2BGR)
            for kp in vToDistributeKeys:
                center = tuple(map(int, kp.pt))
                image_color = cv2.circle(image_color, center, 1, (0, 255, 0), -1)

            # print(f"---------- {lit} ----------")
            for node in lNodes:
                image_color = cv2.rectangle(image_color, (node.UL[0], node.UL[1]), (node.BR[0], node.BR[1]),
                                            (0, 255, 255), thickness=1)
                # print(node.UR)
            cv2.imshow(f"Level {level}--lNodes {len(lNodes)}--nToExpand {nToExpand}", image_color)
            cv2.waitKey(0)
            # cv2.destroyAllWindows()
            # ---------- 中间结果可视化 ----------
            """

            # 判断是否满足停止条件, 满足一个即可
            if len(lNodes) >= num or len(lNodes) == prevSize:
                bFinish = True

            # Step 6 当再划分之后所有的 Node 数大于要求数目时, 就慢慢划分直到使其刚刚达到或者超过要求的特征点个数
            elif len(lNodes) + nToExpand * 3 > num:
                # 如果再分裂一次那么数目就要超了, 这里想办法尽可能使其刚刚达到或者超过要求的特征点个数就退出
                while not bFinish:
                    # 获取当前的 lNodes 中的节点个数
                    prevSize = len(lNodes)
                    # 保留那些还可以分裂的节点的信息
                    vPrevSizeAndPointerToNode = vSizeAndPointerToNode
                    # 清空
                    vSizeAndPointerToNode = []
                    # 对需要划分的节点进行排序, 对 pair 对的第一个元素进行排序(特征点个数), 默认是从小到大排序
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
                            # 如果子节点中有特征点, 则添加到 lNodes 中
                            if len(n.vKeys) > 0:
                                # 插入到 lNodes 的前面
                                lNodes.insert(0, n)
                                # 再判断其包含的特征点数目是否大于 1
                                if len(n.vKeys) > 1:
                                    # 为后续可能的又一次 for 循环做准备
                                    vSizeAndPointerToNode.append((len(n.vKeys), lNodes[0]))
                        # 删除母节点
                        lNodes.remove(node)

                        """
                        # ---------- 中间结果可视化 ----------
                        if level == 0:
                            image_color = cv2.cvtColor(self.mvImagePyramid[level], cv2.COLOR_GRAY2BGR)
                            for kp in vToDistributeKeys:
                                center = tuple(map(int, kp.pt))
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
                    image_color = cv2.cvtColor(self.mvImagePyramid[level], cv2.COLOR_GRAY2BGR)
                    for kp in vToDistributeKeys:
                        center = tuple(map(int, kp.pt))
                        image_color = cv2.circle(image_color, center, 1, (0, 255, 0), -1)
                    for node in lNodes:
                        image_color = cv2.rectangle(image_color, (node.UL[0], node.UL[1]),
                                                    (node.BR[0], node.BR[1]), (0, 255, 255), thickness=1)
                    cv2.imshow(f"Level {level}--lNodes {len(lNodes)}--FeatureNUm {num}", image_color)
                    cv2.waitKey(0)
                    # cv2.destroyAllWindows()
                    # ---------- 中间结果可视化 ----------
                    """


                    # 这里理想中应该是一个 for 循环就能够达成结束条件了, 但有些子节点所在的区域会没有特征点
                    # 因此很有可能一次 for 循环之后, 特征点的数目还是不能够满足要求, 所以还是需要判断结束条件
                    # 判断是否达到了停止条件
                    if len(lNodes) >= num or len(lNodes) == prevSize:
                        bFinish = True

        # Step 7 保留每个区域响应值最大的一个兴趣点
        # 用来存储过滤后的特征点和描述子
        vResultKeys = []
        vResultDesc = []
        # 遍历节点列表
        for node in lNodes:
            # 得到这个节点区域中的特征点和描述子列表
            vNodeKeys = node.vKeys
            vNodeDesc = node.vDesc
            # 获取第一个特征点和对应的描述子, 作为最大响应值对应的关键点
            pKP = vNodeKeys[0]
            pDC = vNodeDesc[0]
            # 用第一个特征点的响应值初始化最大响应值
            maxResponse = pKP.response
            # 开始遍历这个节点区域中的所有特征点, 从第二个特征点开始
            for k in range(1, len(vNodeKeys)):
                # 更新最大响应值
                if vNodeKeys[k].response > maxResponse:
                    # 更新 pKp 和 pDC 指向具有最大响应值的 keypoints
                    pKP = vNodeKeys[k]
                    pDC = vNodeDesc[k]
                    maxResponse = vNodeKeys[k].response
            # 将这个节点区域中响应值最大的特征点加入最终的要保留的特征点列表中
            vResultKeys.append(pKP)
            vResultDesc.append(pDC)

        # 返回最终过滤好的特征点列表
        return vResultKeys, vResultDesc


if __name__ == "__main__":
    # 设置日志配置，显示 INFO 级别及以上的日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    img0 = cv2.imread("/home/zourz/work/Dataset/SLAM/KITTI/data_odometry_gray/dataset/sequences/00/image_0/000001.png")

    handcraft_detector = HandcraftDetector({"type": "ORB"})
    kptdesc = handcraft_detector(img0)

    img = plot_keypoints(img0, kptdesc["keypoints"])
    cv2.imshow(f"FeatureExtractor", img)
    cv2.waitKey()
