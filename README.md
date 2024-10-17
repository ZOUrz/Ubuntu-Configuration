**This project aims to provide the author with a reference record to ensure that critical steps are not overlooked.**

本项目旨在为作者提供一份参考记录, 以确保关键步骤不被遗漏

# Ubuntu System Configuration (Ubuntu系统配置)

- The content of this document outlines the process of configuring the Ubuntu system from scratch to facilitate learning and testing of SLAM.

- 本文档的内容概述了从头配置Ubuntu系统的过程, 以便于学习和测试SLAM



## 1. Reinstall Ubuntu 18.04 (重装Ubuntu18.04系统)

Reference link: https://zhuanlan.zhihu.com/p/667673008

Ubuntu18.04iso download link：https://releases.ubuntu.com/18.04/


![Ubuntu18.04](/Screenshot/Ubuntu18.04iso.png)



## 2. Mount the hard drive (挂载硬盘)

Reference link 1: https://blog.csdn.net/u011895157/article/details/130559749

Reference link 2: https://blog.csdn.net/qq_36357820/article/details/78421242



## 3. Download datasets (下载数据集)

### TUM

Download link: https://cvg.cit.tum.de/data/datasets/rgbd-dataset/download

- No need to download everything, just download as shown.

- 不需要全部下载，只需要下载如图所示的即可


![TUM1](/Screenshot/TUM1.png)

![TUM2](/Screenshot/TUM2.png)


### EuRoC

Download link: https://projects.asl.ethz.ch/datasets/doku.php?id=kmavvisualinertialdatasets


![EuRoC](/Screenshot/EuRoC.png)


### KITTI

Official download link: https://www.cvlibs.net/datasets/kitti/eval_odometry.php
      
BaiduYun download link: https://pan.baidu.com/s/1oXqNR_yd4MkgfABDa9FGSw?pwd=lsdb Extraction code：lsdb



## 4. Use Clash client for internet access with proxy (使用Clash科学上网)

### (1) Install Clash client (安装Clash for Windows客户端)

Download link: https://github.com/lantongxue/clash_for_windows_pkg/releases

**!!!最好先连接手机热点进行下载**

- a. 下载Clash.for.Windows-0.20.39-x64-linux.tar.gz


![Download Clash](/Screenshot/DownloadClash.png)


- b. Unzip (解压缩):

```
tar -zxvf Clash.for.Windows-0.20.39-x64-linux.tar.gz
```

- c. Launch the client (启动客户端)

```
mv Clash\ for\ Windows-0.20.39-x64-linux clash
cd clash/
./cfw
```

![ClashClient](/Screenshot/ClashClient.png)


### (2) Import nodes and set proxy (导入节点并设置代理)

**注: 可以选择其他的方式获取Clash订阅的链接,  这里分享的是我使用的CuteCloud(不一定最好)**

CuteCloud link: https://dh.cutecloud.link/

- a. 进入后注册登录(最好使用手机热点), 然后购买套餐后便可在主页一键复制Clash订阅


![CuteCloud](/Screenshot/CuteCloud.png)


- b. 回到Clash客户端, 点击Profiles, 复制订阅链接到输入框中, 点击Download下载节点


![ImportNodes](/Screenshot/ImportNodes.png)


- c. 注意这里的端口号是7890


![Port](/Screenshot/Port.png)


- d. 然后在Firefox浏览器上设置代理


![SetProxy](/Screenshot/SetProxy.png)


- e. 确定后便大功告成! Enjoy!


![Google](/Screenshot/Google.png)



## 5. Install Git (安装Git)

```
sudo apt-get install git
```



## 6. Install ORB-SLAM2 (安装ORB-SLAM2)

- Refer to the blog link to download and install various prerequisite libraries, including Pangolin, OpenCV, Eigen3, DBoW2, g2o, and ROS

- 参考链接的博客, 下载安装各种前置库, Pangolin, OpenCV, Eigen3, DBoW2, g2o, ROS

- Reference link: https://blog.csdn.net/weixin_43013761/article/details/123093639

- Then install and compile ORB-SLAM2**

- 然后安装编译ORB-SLAM2

### (1) Note: During the installation of ROS, some options may differ from the reference link. Please refer to the selections shown in the image below.

- **注: 安装ROS时, 有几个选项跟参考的链接不一样, 参考下图所选的即可**


![ROS1](/Screenshot/ROS1.png)

![ROS2](/Screenshot/ROS2.png)

![ROS3](/Screenshot/ROS3.png)


### (2) When installing rosdep, do not follow the method in the reference link! You should use the following method for installation:

- **在安装rosdpe时, 不要使用参考链接的方式进行安装!!!, 应当使用如下方式进行安装:**

```
wget http://fishros.com/install -O fishros && . fishros
```


![ROSdepc](/Screenshot/ROSdepc.png)


```
rosdepc update
```



## 7. Install Anaconda (安装Anaconda)

Reference link: https://blog.csdn.net/qq_64671439/article/details/135293643

### (1) 给Anaconda换源:

```
conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/conda-forge/
conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/pytorch/
conda config --set show_channel_urls yes
```



## 8. Install CLion and Pycharm (安装CLion和Pycharm)

### (1) CLion for C++ (CLion用于C++)

Reference link: https://blog.csdn.net/xiaowenshen/article/details/118761466

### (2) Pycharm for Python (Pycharm用于Python)

Reference link: https://blog.csdn.net/weixin_39450145/article/details/130022227

### (3) Set shortcut (设置快捷方式)

- Tools --> Create Command-line Launcher (Desktop Shortcut)

- 工具 --> 创建桌面条目 (桌面快捷方式)

- Tools --> Desktop Entry (Taskbar Shortcut)

- 工具 --> 创建命令行启动器 (任务栏快捷方式)



## 9. Install Nivida Driver (安装英伟达显卡驱动)

Reference link: https://blog.csdn.net/coolsmartboy/article/details/120532547


![NvidiaDriver](/Screenshot/NvidiaDriver.png)



## 10. Install CUDA 10.2 and CUDNN 8.2.2 (安装CUDA10.2和CUDNN8.2.2)

### (1) Install CUDA 10.2

Download link: https://developer.nvidia.com/cuda-10.2-download-archive

- Select as shown in the figure

- 按如图所示进行选择


![CUDA1](/Screenshot/CUDA1.png)


- Run the download command to download

- 运行下载命令进行下载

```
wget https://developer.download.nvidia.com/compute/cuda/10.2/Prod/local_installers/cuda_10.2.89_440.33.01_linux.run
```

- Run the installation command

- 运行安装命令

```
sudo sh cuda_10.2.89_440.33.01_linux.run
```

- Select as shown in the figure

- 按如图所示进行选择


![CUDA4](/Screenshot/CUDA4.png)

![CUDA2](/Screenshot/CUDA2.png)

![CUDA3](/Screenshot/CUDA3.png)


- Configure CUDA into the environment variables

- 将CUDA配置到环境变量

```
gedit ~/.bashrc
```

- Add the following statements at the end of the file

- 在文件末尾添加以下语句

```
export CUDA_HOME=$CUDA_HOME:/usr/local/cuda-10.2
export PATH=$PATH:/usr/local/cuda-10.2/bin
export LD_LIBRARY_PATH=/usr/local/cuda-10.2/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
```

- Apply the changes to the environment configuration

-  使更改的环境配置生效

```
source ~/.bashrc
```

### (2) Install CUDNN 8.2.2 

Download link: https://developer.nvidia.com/rdp/cudnn-archive

- Download "cuDNN Library for Linux (x86)"

```
sudo cp cuda/include/* -R /usr/local/cuda/include/ 
sudo cp cuda/lib64/libcudnn* /usr/local/cuda/lib64/ 
sudo chmod a+r /usr/local/cuda/include/cudnn.h 
sudo chmod a+r /usr/local/cuda/lib64/libcudnn*
```

```
cat /usr/local/cuda/include/cudnn_version.h | grep CUDNN_MAJOR -A 2
```

Reference link 1: https://blog.csdn.net/mao_hui_fei/article/details/121140152

Reference link 2: https://blog.csdn.net/coolsmartboy/article/details/120532547

Reference link 3: https://blog.csdn.net/BIT_HXZ/article/details/127604530

## 11. Install libtorch (安装libtorch)

**The official PyTorch website only provides the latest version of libtorch. You can download previous versions of libtorch from the following link.**

Pytorch官网只提供最新版本的libtorch, 参考以下链接可以下载到libtorch以往版本

Reference link: https://blog.csdn.net/weixin_43742643/article/details/114156298

**Here, I downloaded version 1.8.1 of libtorch.**

这里我下载的是1.8.1版本的libtorch

![TestLibtorch](/Screenshot/TestLibtorch.png)
