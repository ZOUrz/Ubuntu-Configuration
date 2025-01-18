import os
import cv2
import time
import yaml
import logging

import torch
from utils import plot_matches, create_logger, LoadImagesFromKITTI
from SuperGlue import SuperGlue
from SuperPointExtractor import SuperPointExtractor


class SuperGlueMatcher(object):
    def __init__(self, matchThreshold, sgPath, sgWeights, cuda, logger):

        self.cuda =cuda
        self.device = 'cuda' if torch.cuda.is_available() and self.cuda else 'cpu'
        logger.info("==>Using device: {}!!!".format(self.device))

        assert sgWeights in ['indoor', 'outdoor']
        self.path = os.path.join(sgPath, 'superglue_{}.pth'.format(sgWeights))
        logger.info("==>creating SuperGlue matcher...")
        self.superglue = SuperGlue(matchThreshold, self.path, logger).to(self.device)

        self.superglue.eval()

    def __call__(self, kptdescs):
        # setup data for superglue
        logging.debug("prepare input data for superglue...")
        data = {
            'image_size0': torch.from_numpy(kptdescs["ref"]["image_size"]).float().to(self.device),
            'image_size1': torch.from_numpy(kptdescs["cur"]["image_size"]).float().to(self.device)
        }

        if "torch" in kptdescs["cur"]:
            data['scores0'] = kptdescs["ref"]["torch"]["scores"][0].unsqueeze(0)
            data['keypoints0'] = kptdescs["ref"]["torch"]["keypoints"][0].unsqueeze(0)
            data['descriptors0'] = kptdescs["ref"]["torch"]["descriptors"][0].unsqueeze(0)

            data['scores1'] = kptdescs["cur"]["torch"]["scores"][0].unsqueeze(0)
            data['keypoints1'] = kptdescs["cur"]["torch"]["keypoints"][0].unsqueeze(0)
            data['descriptors1'] = kptdescs["cur"]["torch"]["descriptors"][0].unsqueeze(0)
        else:
            data['scores0'] = torch.from_numpy(kptdescs["ref"]["scores"]).float().to(self.device).unsqueeze(0)
            data['keypoints0'] = torch.from_numpy(kptdescs["ref"]["keypoints"]).float().to(self.device).unsqueeze(0)
            data['descriptors0'] = torch.from_numpy(kptdescs["ref"]["descriptors"]).float().to(self.device).unsqueeze(
                0).transpose(1, 2)

            data['scores1'] = torch.from_numpy(kptdescs["cur"]["scores"]).float().to(self.device).unsqueeze(0)
            data['keypoints1'] = torch.from_numpy(kptdescs["cur"]["keypoints"]).float().to(self.device).unsqueeze(0)
            data['descriptors1'] = torch.from_numpy(kptdescs["cur"]["descriptors"]).float().to(self.device).unsqueeze(
                0).transpose(1, 2)

        # Forward !!
        logging.debug("matching keypoints with superglue...")
        pred = self.superglue(data)

        # get matching keypoints
        kpts0 = kptdescs["ref"]["keypoints"]
        kpts1 = kptdescs["cur"]["keypoints"]

        matches = pred['matches0'][0].cpu().numpy()
        confidence = pred['matching_scores0'][0].cpu().detach().numpy()

        # Sort them in the order of their confidence.
        match_conf = []
        for i, (m, c) in enumerate(zip(matches, confidence)):
            match_conf.append([i, m, c])
        match_conf = sorted(match_conf, key=lambda x: x[2], reverse=True)

        valid = [[l[0], l[1]] for l in match_conf if l[1] > -1]
        v0 = [l[0] for l in valid]
        v1 = [l[1] for l in valid]
        mkpts0 = kpts0[v0]
        mkpts1 = kpts1[v1]

        ret_dict = {
            "ref_keypoints": mkpts0,
            "cur_keypoints": mkpts1,
            "match_score": confidence[v0]
        }

        return ret_dict


if __name__ == "__main__":
    # 创建日志器, 记录运行信息
    logger = create_logger(name='SuperPointDetector')

    # 禁用pytorch梯度计算
    torch.set_grad_enabled(False)

    with open("params/KITTI00-02.yaml", 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    Timestamps, ImageFilenames = LoadImagesFromKITTI(
        "/home/zourz/work/Dataset/SLAM/KITTI/data_odometry_gray/dataset/sequences/01"
    )

    width = config["Camera.width"]
    height = config["Camera.height"]
    cuda = config["Model.cuda"]  # 是否使用GPU
    nFeatures = config["Model.SPextractor.nFeatures"]  # 每一帧提取的特征点数 1024
    kptThreshold = config["Model.SPextractor.kptThreshold"]  # 提取SuperPoint特征点的阈值
    spPath = config["Model.SPextractor.spPath"]  # SuperPoint预训练权重的路径
    matchThreshold = config["Model.SGmatcher.matchThreshold"]  # SuperGlue匹配的阈值
    sgPath = config["Model.SGmatcher.sgPath"]  # SuperGlue预训练权重的路径
    sgWeights = config["Model.SGmatcher.sgWeights"]  # SuperGlue预训练权重的类型

    extractor = SuperPointExtractor(width, height, nFeatures, kptThreshold, spPath, cuda, logger)
    matcher = SuperGlueMatcher(matchThreshold, sgPath, sgWeights, cuda, logger)

    kptdescs = {}
    imgs = {}
    for i, imgfile in enumerate(ImageFilenames):
        img = cv2.imread(imgfile)

        start_time = time.time()  # 记录开始时间

        imgs["cur"] = img
        kptdescs["cur"] = extractor(img)

        if i >= 1:
            matches = matcher(kptdescs)

            end_time = time.time()  # 记录结束时间
            elapsed_time = end_time - start_time  # 计算运行时间
            print(f"运行时间: {elapsed_time:.4f}秒")

            img = plot_matches(
                imgs['ref'], imgs['cur'],
                matches['ref_keypoints'][0:300], matches['cur_keypoints'][0:300],
                matches['match_score'][0:300], layout='lr'
            )

            cv2.imshow("track", img)
            cv2.waitKey(100)

        kptdescs["ref"], imgs["ref"] = kptdescs["cur"], imgs["cur"]
