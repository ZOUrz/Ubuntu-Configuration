# ORB-SLAM2 Configuration

This document provides a detailed tutorial on ORB-SLAM2, including the processes of installation, compilation, dataset execution, and evaluation. It serves both as a personal memo and as a reference for beginners.

本文档提供了 ORB-SLAM2 的详细教程, 包括安装, 编译, 跑数据集以及评估的流程, 既是个人备忘录, 也可以为初学者提供一定参考


## 1. 安装编译 ORB-SLAM2

- 参考以下链接, 下载并安装各种前置库, Pangolin, OpenCV, Eigen3, DBoW2, g2o, ROS

  - 参考链接: https://blog.csdn.net/weixin_43013761/article/details/123093639

- 然后安装编译 ORB-SLAM2

- **Note 1:** 我将 Pangolin 和 OpenCV 这两个库都安装在 `~/Thirdparty` 目录下(我的 Libtorch 也装在这里)

- **Note 2:** 安装 ROS 时, 有几个选项跟参考的链接不一样, 参考下图所选的即可

  ![ROS1](/Screenshot/ROS1.png)
  
  ![ROS2](/Screenshot/ROS2.png)
  
  ![ROS3](/Screenshot/ROS3.png)

- **Note 3:** 在安装 rosdpe 时, 不要使用参考链接的方式进行安装, 应当使用如下方式进行安装:

  - 在终端输入:

    ```
    wget http://fishros.com/install -O fishros && . fishros
    ```

    ![ROSdepc](/Screenshot/ROSdepc.png)

  - 然后输入:

    ```
    rosdepc update
    ```


## 2. 下载数据集

- ## 2.1 TUM

  - 下载链接: https://cvg.cit.tum.de/data/datasets/rgbd-dataset/download

  - 不需要全部下载, 只需下载如图所示的即可

    ![TUM1](/Screenshot/TUM1.png)
  
    ![TUM2](/Screenshot/TUM2.png)

- ## 2.2 EuRoC

  - 下载链接: https://projects.asl.ethz.ch/datasets/doku.php?id=kmavvisualinertialdatasets

    ![EuRoC](/Screenshot/EuRoC.png)

- ## 2.3 KITTI

  - 官网下载链接: https://www.cvlibs.net/datasets/kitti/eval_odometry.php
 
  - 但是国内去官网下载的话, 速度非常慢, 这里我提供了百度网盘的下载地址
      
    - 百度网盘下载链接: https://pan.baidu.com/s/1oXqNR_yd4MkgfABDa9FGSw?pwd=lsdb 提取码：lsdb


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

为啥第一个有效像素点到网格左上角坐标不需要-1? 这是因为padding的三个像素不包含第一个有效像素, 所以是直接往外扩充3个像素点即可

而网格左上角的这个像素点坐标是(16, 16), 是包含在这个网格内的, 因此网格右上角的像素点坐标为(16+38-1, 16) = (53, 16), 中间隔了53 - 16 + 1 = 38个像素, 对于列的计算也是同理

为什么要这么烧脑？ 因为这里说的像素点坐标是指这个像素点的位置, 是要考虑这个点是否被包含在所选定的范围之内的, 可以认为是有物理体积的, 而不是数学上可被认为体积不计的点, 数学上是只考虑边界的, 一条边长是没有宽度的

```ruby
require 'redcarpet'
markdown = Redcarpet.new("Hello World!")
puts markdown.to_html
```

```cmake
MESSAGE("Build type: " ${CMAKE_BUILD_TYPE})
```

```c++
#ifndef ORBEXTRACTOR_H
#define ORBEXTRACTOR_H

#include <vector>
#include <list>
#include <opencv/cv.h>
```

./Examples_old/Stereo/stereo_kitti_old ./Vocabulary/ORBvoc.txt ./Examples_old/Stereo/KITTI00-02.yaml ~/work/Dataset/SLAM/KITTI/data_odometry_gray/dataset/sequences/00








