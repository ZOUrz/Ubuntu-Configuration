# Ubuntu Configuration

This repository serves as a reference for reinstalling and configuring deep learning environments on Ubuntu from scratch, providing both personal documentation and a guide for beginners.

这个仓库作为一份参考, 旨在从头开始重新安装和配置 Ubuntu 上的深度学习环境, 既是个人记录文档, 也是初学者的指南



## 1. 重装 Ubuntu18.04 系统

- 参考链接: https://zhuanlan.zhihu.com/p/667673008

- Ubuntu18.04 系统镜像文件下载链接: https://releases.ubuntu.com/18.04/

- 点击如图所示的文件即可进行下载

  ![Ubuntu18.04](/Screenshot/1_1_iso.png)

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

  ![uuid](/Screenshot/2_1_uuid.png)

- 复制硬盘的 uuid，然后修改 fstab 文件

  ```
  sudo gedit /etc/fstab 
  ```

- 在文件最后添加如下图所示内容

  ![fstab](/Screenshot/2_2_fstab.png)

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
  ls -ld /home/zourz/work
  ```

  - 更改磁盘所属用户
 
  ```
  sudo chown zourz:zourz ~/work/
  ```

  ![chown](Screenshot/2_3_chown.png)
  

## 3. 安装百度网盘

- 参考链接: https://blog.csdn.net/suiqianjushi/article/details/123824801

- 下载 Linux 版本的 `deb 格式`

![BaiduNetdisk](Screenshot/3_1_BaiduNetdisk.png)

- **夸克网盘不支持 Linux 系统!!**


## 4. 使用 Clash 科学上网

- 安装 Clash for Windows 客户端

  - 下载链接: https://github.com/lantongxue/clash_for_windows_pkg/releases

    - **如果点击没反应, 应该是网络问题, 最好连接手机热点进行下载!!!**

  - 下载 Clash.for.Windows-0.20.39-x64-linux.tar.gz  

  ![Download Clash](/Screenshot/4_1_DownloadClash.png)

  - 解压缩

    ```
    tar -zxvf Clash.for.Windows-0.20.39-x64-linux.tar.gz -C ~/work/ProgramFiles/
    ```

  - 启动客户端, 在 Clash 文件夹目录打开终端, 输入

    ```
    ./cfw
    ```

    ![ClashClient](/Screenshot/4_2_ClashClient.png)


- 导入节点并设置代理

  - **Note:** 可以选择其他的方式获取 Clash 订阅的链接, 这里分享的是我使用的 CuteCloud

  - CuteCloud 官网链接: https://dh.cutecloud.link/

  - 进入后注册登录(最好使用手机热点), 然后购买套餐后便可在主页一键复制 Clash 订阅

    ![CuteCloud](/Screenshot/4_3_CuteCloud.png)

  - 回到 Clash 客户端, 点击 `Profiles`, 复制订阅链接到输入框中, 点击 `Download` 下载节点

    ![ImportNodes](/Screenshot/4_4_ImportNodes.png)

  - 注意这里的端口号是 `7890`

    ![Port](/Screenshot/4_5_Port.png)

  - 然后在 Firefox 浏览器上设置代理

    ![SetProxy](/Screenshot/4_6_SetProxy.png)

  - 确定后便大功告成! Enjoy!

    ![Google](/Screenshot/4_7_Google.png)


## 5. 安装 Git, gcc 和 CMake

```
sudo apt update
sudo apt-get install git
sudo apt-get install build-essential 
sudo apt-get install cmake
```


## 6. 安装 Anaconda

- 参考链接: https://blog.csdn.net/qq_64671439/article/details/135293643

- 现在下载需要提供邮箱

  ![DowanloadAnaconda_1](/Screenshot/6_1_DownloadAnaconda_1.png)

- 下载 x86 版本

  ![DowanloadAnaconda_2](/Screenshot/6_2_DownloadAnaconda_2.png)

  - 可以通过在终端输入 `uname -m` 来查询自己电脑的架构
 
    ![x86_64](Screenshot/6_3_x86_64.png)

- 然后根据参考链接进行安装即可

- 安装完成后需要给 Anaconda 进行换源

  ```
  conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/free/
  conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/main/
  conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/conda-forge/
  conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/pytorch/
  conda config --set show_channel_urls yes
  ```


## 7. 安装 CLion

- CLion 是用于 C++ 代码的编写

- 参考链接: https://blog.csdn.net/xiaowenshen/article/details/118761466

- 如果没有按照参考链接的方法生成桌面快捷方式, 可以按如下方式生成:

  - Tools --> Create Command-line Launcher (Desktop Shortcut)
 
- 学生认证:

  - 参考链接: https://blog.csdn.net/weixin_74009895/article/details/140642484
 
  - 如果不是学生的话, 也可以选择去淘宝购买激活码
 
  - 点击 Help -> Register 进行登录激活
 
- **Note:** 如果下载最新版的 CLion(如 2024.3 ), 会由于 `GLIBC` 版本太低而报错, 比如 CLion 2024.3 版本需要 `GLIBC 2.28`, 而 Ubuntu 18.04 默认使用的是 `GLIBC 2.27`, 因此需要下载旧版本的 CLion, 亲测 **CLion 2024.1** 版本的可以用(也可以升级 `GLIBC`)

   ![CLionVersion](Screenshot/7_1_CLionVersion.png)

- 设置字体

  - CLion 默认的字体很小, 可以在设置中自定义字体, 打开 File -> Settings -> Editor -> Font -> Size 即可调整字体大小
 
    ![CLionFont](Screenshot/7_2_CLionFont.png)


## 8. 安装 Pycharm 专业版

- Pycharm 是用于 Pycharm 代码的编写

- 参考链接: https://blog.csdn.net/weixin_39450145/article/details/130022227

- **Note:** 为了避免安装报错, 选择安装 **Pycharm 专业版 2024.1**

- 如果没有按照参考链接的方法生成桌面快捷方式, 可以按如下方式生成:

  - Tools --> Desktop Entry (Taskbar Shortcut)

- 学生认证的方式跟 CLion 是一样的, 认证后登录账号即可激活


## 9. 安装英伟达显卡驱动

- 参考链接: https://blog.csdn.net/coolsmartboy/article/details/120532547

  ![NvidiaDriver](/Screenshot/9_1_NvidiaDriver.png)



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



https://blog.csdn.net/qq_25749749/article/details/143408256

