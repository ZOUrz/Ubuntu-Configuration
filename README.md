**This project aims to provide the author with a reference record to ensure that critical steps are not overlooked.**

本项目旨在为作者提供一份参考记录, 以确保关键步骤不被遗漏

# Ubuntu System Configuration

**The content of this document outlines the process of configuring the Ubuntu system from scratch to facilitate learning and testing of SLAM.**

本文档的内容概述了从头配置Ubuntu系统的过程, 以便于学习和测试SLAM

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

不需要全部下载，只需要下载如图所示的即可


![TUM1](/Screenshot/TUM1.png)

![TUM2](/Screenshot/TUM2.png)


**EuRoC:** https://projects.asl.ethz.ch/datasets/doku.php?id=kmavvisualinertialdatasets


![EuRoC](/Screenshot/EuRoC.png)


**KITTI:** 

Official link: https://www.cvlibs.net/datasets/kitti/eval_odometry.php
      
Baidu link: https://pan.baidu.com/s/1oXqNR_yd4MkgfABDa9FGSw?pwd=lsdb Extraction code：lsdb

## 4. Use Clash client for internet access with proxy (使用Clash科学上网)

### (1) Install Clash client (安装Clash for Windows客户端)

Download link: https://github.com/lantongxue/clash_for_windows_pkg/releases

**!!!最好先连接手机热点进行下载!!!**

a. 下载Clash.for.Windows-0.20.39-x64-linux.tar.gz


![Download Clash](/Screenshot/DownloadClash.png)


b. Unzip (解压缩):

```
tar -zxvf Clash.for.Windows-0.20.39-x64-linux.tar.gz
```

c. Launch the client (启动客户端)

```
mv Clash\ for\ Windows-0.20.39-x64-linux clash
cd clash/
./cfw
```

![ClashClient](/Screenshot/ClashClient.png)


### (2) Import nodes and set proxy (导入节点并设置代理)

**注: 可以选择其他的方式获取Clash订阅的链接,  这里分享的是作者本人使用的CuteCloud(不一定最好)**

CuteCloud link: https://dh.cutecloud.link/

a. 进入后注册登录(最好使用手机热点), 然后购买套餐后便可在主页一键复制Clash订阅


![CuteCloud](/Screenshot/CuteCloud.png)


b. 回到Clash客户端, 点击Profiles, 复制订阅链接到输入框中, 点击Download下载节点


![ImportNodes](/Screenshot/ImportNodes.png)


c. 注意这里的端口号是7890


![Port](/Screenshot/Port.png)


d. 然后在Firefox浏览器上设置代理


![SetProxy](/Screenshot/SetProxy.png)


e. 确定后便大功告成! Enjoy!


![Google](/Screenshot/Google.png)


## 5. Build and install CMake from source code (从源代码编译安装CMake)

Reference link: https://blog.csdn.net/suiyingy/article/details/136552895

a. Directly download version 3.28.1 of CMake from the official website (从官网直接下载cmake的3.28.1版本)

```
wget https://cmake.org/files/v3.28/cmake-3.28.1.tar.gz
```

b. Decompress the downloaded file (解压缩下载的文件)

```
tar -zxvf cmake-3.28.1.tar.gz
cd cmake-3.28.1
```

c. Compile and install CMake (编译并安装Cmake)

```
./bootstrap
make
sudo make install
```
d. Verify the installation (验证安装)

```
cmake --version
```
## 6. Install Git (安装Git)

```
sudo apt-get install git
```
## 7. Install ORB-SLAM2 (安装ORB-SLAM2)

**Refer to the blog link to download and install various prerequisite libraries, including Pangolin, OpenCV, Eigen3, DBoW2, g2o, and ROS**

参考链接的博客, 下载安装各种前置库, Pangolin, OpenCV, Eigen3, DBoW2, g2o, ROS

Reference link: https://blog.csdn.net/weixin_43013761/article/details/123093639

**Then install and compile ORB-SLAM2**

然后安装编译ORB-SLAM2

### (1) Note: During the installation of ROS, some options may differ from the reference link. Please refer to the selections shown in the image below.

**注: 安装ROS时, 有几个选项跟参考的链接不一样, 参考下图所选的即可**


![ROS1](/Screenshot/ROS1.png)

![ROS2](/Screenshot/ROS2.png)

![ROS3](/Screenshot/ROS3.png)


### (2) When installing rosdep, do not follow the method in the reference link! You should use the following method for installation:

**在安装rosdpe时, 不要使用参考链接的方式进行安装!!!, 应当使用如下方式进行安装:**

```
wget http://fishros.com/install -O fishros && . fishros
```


![ROSdepc](/Screenshot/ROSdepc.png)


```
rosdepc update
```
## 8. Install Anaconda (安装Anaconda)

Reference link: https://blog.csdn.net/qq_64671439/article/details/135293643

### (1) 给Anaconda换源:

```
conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/conda-forge/
conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/pytorch/
conda config --set show_channel_urls yes
```

## 9. Install VSCode (安装VSCode)

**Note: It is recommended to download an earlier version of VSCode, as newer versions may produce errors due to outdated libraries on Ubuntu 18.04!**

注: 要下载较低版本的VSCode, 否则会因为ubuntu18.04的库太旧导致报错!

**In this case, I downloaded version 1.73 of VSCode.**

此处, 本人下载的是1.73版本的VSCode

download link: https://code.visualstudio.com/updates/v1_73

```
sudo dpkg -i code_1.73.1-1667967334_amd64.deb
```
### (1) 安装扩展

Chinese (Simplified) Language Pack for Visual Studio Code, C/C++, C/C++ Extension Pack, C/C++ Themes, CMake, CMake Tools, ROS, ROS Snippets

### (2) 设置字体

Reference link: https://miracle.blog.csdn.net/article/details/130294351

## 10. Install Nivida Driver (安装英伟达显卡驱动)

Reference link: https://blog.csdn.net/coolsmartboy/article/details/120532547


![NvidiaDriver](/Screenshot/NvidiaDriver.png)


## 11. Install CUDA 10.2 and CUDNN 8.2.2 (安装CUDA10.2和CUDNN8.2.2)

Reference link 1: https://blog.csdn.net/mao_hui_fei/article/details/121140152

Reference link 2: https://blog.csdn.net/coolsmartboy/article/details/120532547
