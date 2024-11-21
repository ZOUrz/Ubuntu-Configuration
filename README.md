# Ubuntu Configuration

This repository serves as a reference for reinstalling and configuring deep learning environments on Ubuntu from scratch, providing both personal documentation and a guide for beginners.

这个仓库作为一份参考, 旨在从头开始重新安装和配置 Ubuntu 上的深度学习环境, 既是个人记录文档, 也是初学者的指南



## 1. 重装 Ubuntu18.04 系统

- 参考链接: https://zhuanlan.zhihu.com/p/667673008

- Ubuntu18.04 系统镜像文件下载链接: https://releases.ubuntu.com/18.04/

- 点击如图所示的文件即可进行下载

  ![Ubuntu18.04](/Screenshot/Ubuntu18.04iso.png)

- 由于我的电脑只有一个 256GB 的固态硬盘, 另外一块硬盘是 4TB 的机械硬盘, 因此将 Ubuntu 系统装在固态硬盘中

- 在分配 `根目录` 时, 参考链接里作者用的是 512GB 的硬盘, 所以作者分配了 160GB, 且分配了大概 300GB 给了 `/home` 目录; 而对于我自己的电脑来说, 只需要分配 64GB 给 `根目录`, 将多余的 160GB 分配给 `/home` 目录

- **Note:** 参考上面的链接进行重装时, 注意不要按照链接的方式分配 `tmp` 空间, 否则在安装一些软件的时候会提示 `tmp` 空间不足(我在安装 Nvidia 显卡驱动时遇到了), 可以跳过这一步, 让 `tmp` 直接分配到根目录即可(也许分配大一点可以解决? 但具体多少就不会出问题我没有进行测试)

- **Note:** 此外, 我还遇到了 Nvidia 显卡与 Ubuntu 内核不兼容的问题, 我的显卡是 RTX 2070Super, 根据链接的教程可以进行安装, 但是重启后会花屏, 且无法进入系统, 解决办法如下:

  - 参考链接: https://www.cnblogs.com/booturbo/p/13967033.html



## 2. 挂载硬盘

- 参考链接 1: https://blog.csdn.net/u011895157/article/details/130559749

- 参考链接 2: https://blog.csdn.net/qq_36357820/article/details/78421242

- 获取硬盘的 uuid

  ```
  ls -l /dev/disk/by-uuid
  ```

  ![uuid]

- 复制硬盘的 uuid，然后修改 fstab 文件

  ```
  sudo gedit /etc/fstab 
  ```

- 在文件最后添加如下图所示内容

  ![fstab]

  - 参数说明:

    - 第一列: 实际分区名, 卷标( Lable )或 UUID
  
      - SATA磁盘示例: /dev/hda1, /dev/hda2
      - SCSI磁盘示例：/dev/sda, /dev/sdb。
      - 使用标签时示例: LABEL=/
  
    - 第二列: 挂载点
  
      - 必须是已存在的目录, 建议挂载目录权限设置为 777，以便兼容
  
    - 第三列: 文件系统类型
  
      - 常见类型: ext2, ext3 等
      - 使用 auto 时, 系统自动检测文件系统类型, 通常用于可移动设备
  
    - 第四列: 挂载选项
  
      - auto: 系统自动挂载
      - defaults: 默认挂载选项( rw, suid, dev, exec, auto, nouser, async)
      - noauto: 不自动挂载
      - ro: 只读挂载
      - rw: 可读可写挂载
      - nouser: 只有超级用户可以挂载
      - user: 任何用户可以挂载
      - **Note:** 光驱和软驱需装有介质才能挂载，通常为 noauto。
  
    - 第五列: dump 备份设置
  
      - 1: 允许 dump 备份
      - 0: 不进行备份
      
    - 第六列: fsck 磁盘检查顺序
  
      - 0: 不检查
      - 1: 根分区
      - 2: 其他分区, 数字越小, 越先检查, 如果两个分区相同, 系统会同时检查

- 重启系统

  ```
  sudo reboot
  ```

- 设置硬盘权限

  - 查询磁盘挂载点当前权限

  ```
  ls -ld /home//zourz/work
  ```

  - 更改磁盘所属用户
 
  ```
  sudo chown zourz:zourz ~/work/
  ```

  ![chown]
  
  





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
