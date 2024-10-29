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


对于最顶上的金字塔图层

图像尺寸346 × 105, padding后的图像尺寸384 × 143, 其中padding=19

提取特征点时, 又要预留3个像素的宽度出来给FAST角点, 所以用于特征点提取的尺寸为352 × 111

然后进行网格的划分, 预设的网格大小为30 × 30

则一行可以划分的网格数为: 352.0 / 30 = 11.73 --> 11

一列可以划分的网格数为： 111.0 /30 = 3.7 --> 3

这样一个网格内所占的像素为：

对于行, 352.0 / 11.0 = 32

对于列, 111.0 / 3.0 = 37

然后就进行网格的划分:

要明确的一点是, FAST特征点在提取时是需要该像素点为圆心, 半径为3的圆, 而我们希望不要忽略图像的边界像素点, 因此需要预留宽度为3的padding, 因此网格尺寸32 × 37, 是有效图像尺寸, 是希望在这个size内的所有像素点能够用于特征点的提取

因此, 对于一个网格来说, 一行占了32个像素, 再加上预留的padding, 那该网格一行要取32 + 3 + 3 = 38个像素点, 而列同理, 一列要取37 + 3 + 3 = 43个像素点

首先对列进行划分, 第一个有效像素点的坐标为(19, 19), 在考虑padding后, 第一个网格的左上角坐标为(19-3, 19-3) = (16, 16), 进而得出该网格右下角坐标为(16+38-1, 16+43-1) = (53, 58)

*能看懂为什么要减1的都是神人！*










