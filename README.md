# Ubuntu-buildSLAM

**This project serves as a personal reference for building a SLAM system from scratch on Ubuntu, documenting the process to ensure that key steps are not forgotten.**

本项目旨在为在Ubuntu系统上从头构建SLAM系统提供个人参考，并记录整个过程，以确保关键步骤不会被遗忘

## 1. Reinstall Ubuntu 18.04 (重装Ubuntu18.04系统)

Reference link: https://zhuanlan.zhihu.com/p/667673008

Ubuntu18.04iso download link：https://releases.ubuntu.com/18.04/

![Ubuntu18.04](/Screenshot/Ubuntu18.04iso.png)

## 2. Mount the hard drive (挂载硬盘)

Reference link 1: https://blog.csdn.net/u011895157/article/details/130559749

Reference link 2: https://blog.csdn.net/qq_36357820/article/details/78421242

## 3. Download datasets (下载数据集)

**TUM:** https://cvg.cit.tum.de/data/datasets/rgbd-dataset/download

**No need to download everything, just download as shown.**

不需要全部下载，只需要下载如同所示的即可

![TUM1](/Screenshot/TUM1.png)

![TUM2](/Screenshot/TUM2.png)

**EuRoC:** https://projects.asl.ethz.ch/datasets/doku.php?id=kmavvisualinertialdatasets

![EuRoC](/Screenshot/EuRoC.png)

**KITTI:** 

Official link: https://www.cvlibs.net/datasets/kitti/eval_odometry.php
      
Baidu link: https://pan.baidu.com/s/1oXqNR_yd4MkgfABDa9FGSw?pwd=lsdb Extraction code：lsdb

## 4. Use Clash client for internet access with proxy (使用Clash科学上网)

### (1) Install Clash client (下载Clash客户端)

Download link: https://github.com/lantongxue/clash_for_windows_pkg/releases

**!!!最好先连接手机热点进行下载!!!**

下载Clash.for.Windows-0.20.39-x64-linux.tar.gz 

## 5. Build and install CMake from source code (从源代码编译安装CMake)

Reference link: https://blog.csdn.net/suiyingy/article/details/136552895

