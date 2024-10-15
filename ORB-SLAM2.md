**This project aims to provide the author with a reference record to ensure that critical steps are not overlooked.**

本项目旨在为作者提供一份参考记录, 以确保关键步骤不被遗漏

# ORB-SLAM2

**This document provides an overview of the testing, evaluation, and modifications related to ORB-SLAM2.**

本文档概述了与ORB-SLAM2相关的测试, 评估和修改事宜.

## 1. Build Stereo Examples on KITTI Dataset

Execute the following command. Change `KITTIX.yaml` to KITTI00-02.yaml, KITTI03.yaml or KITTI04-12.yaml for sequence 0 to 2, 3, and 4 to 12 respectively.

Change `PATH_TO_DATASET_FOLDER` to the uncompressed dataset folder.

Change `SEQUENCE_NUMBER` to 00, 01, 02,.., 10.

```
./Examples/Stereo/stereo_kitti Vocabulary/ORBvoc.txt Examples/Stereo/KITTIX.yaml PATH_TO_DATASET_FOLDER/dataset/sequences/SEQUENCE_NUMBER
```

## 2. Install KITTI Odometry Evaluation Toolbox

Reference link: https://github.com/Huangying-Zhan/kitti-odom-eval/tree/master




