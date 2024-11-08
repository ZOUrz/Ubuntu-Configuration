# include/Viewer.h

- 目前先不用阅读 `Viewer` 类的构造函数, 因为暂时还没有调用, 所以就不用解析代码了

## 重头开始构建ORBSLAM2

- 如果是从零开始构建 `ORBSLAM2` 系统, 就按照下面给出的文件内容进行代码的编写

- ### 1. include/Viewer.h

  - Build from scratch - Changed 0

  - 定义了一个空的 `Viewer` 类

  ```c++
  #ifndef VIEWER_H
  #define VIEWER_H
  
  namespace ORB_SLAM2
  {
  
    class Viewer
    {
  
    };
  }
  
  #endif //VIEWER_H
  ```


- ### 2. include/System.h

  - Build from scratch - Changed 1

  - 文件开头加上:

  ```c++
  #include "Viewer.h"
  ```

  - 然后加上成员变量 `mpViewer` 的声明, 实际上是一个 Viewer 类的指针, 但并未分配内存或调用构造函数
 
  ```c++
            // The viewer draws the map and the current camera pose. It uses Pangolin.
            // 查看器, 可视化界面
            Viewer* mpViewer;
  ```

  - 完整代码

  ```c++
  #ifndef SYSTEM_H
  #define SYSTEM_H
  
  
  #include <mutex>
  
  #include "Viewer.h"

  
  namespace ORB_SLAM2
  {
  
      // 本类的定义
      class System
      {
  
      public:
          // Input sensor
          // 这个枚举类型用于表示本系统所使用的传感器类型
          enum eSensor
          {
              MONOCULAR = 0,
              STEREO = 1,
              RGBD = 2
          };
  
          // Initialize the SLAM system. It launches the Local Mapping, Loop Closing and Viewer threads.
          // 构造函数, 用来初始化整个系统
          // 构造函数的参数如下: 词典文件路径, 配置文件路径, 传感器类型, 是否使用可视化界面
          System(const std::string &strVocFile, const std::string &strSettingsFile,
                 eSensor sensor, bool bUseViewer = true);
  
      private:
  
          // 变量名的命名方式: 类的变量名有前缀m, 如果这个变量是指针类型还要多加个前缀p, 如果是进程那么加个前缀t
  
          // Input sensor
          // 传感器类型
          eSensor mSensor;
    
          // The viewer draws the map and the current camera pose. It uses Pangolin.
          // 查看器, 可视化界面
          Viewer* mpViewer;
  
          // Reset flag
          // 复位标志
          std::mutex mMutexReset;  // 用于实现互斥锁
          bool mbReset;
  
          // Change mode flags
          // 模式改变标志
          std::mutex mMutexMode;  // 用于实现互斥锁
          bool mbActivateLocalizationMode;
          bool mbDeactivateLocalizationMode;
  
      };
  
  }
  
  #endif //SYSTEM_H
  
  ```

- ### 3. include/System.cc

  - Build from scratch - Changed 1

  - 在 `成员变量初始化列表` 中加上:

  ```c++
          mpViewer(static_cast<Viewer*>(nullptr))
  ```

  - 完整代码

  ```c++
  // 主进程的实现文件
  
  #include <iostream>
  #include <opencv2/core/core.hpp>
  
  #include "System.h"
  
  
  using namespace std;
  
  
  namespace ORB_SLAM2
  {
      // 系统的构造函数, 将会启动其他线程
      // 第一个 System 是类名, 表示这是 ORB_SLAM2::System 类的构造函数
      // 第二个 System 是构造函数的名称, 必须与类名相同
      // 构造函数的参数如下: 词典文件路径, 配置文件路径, 传感器类型, 是否使用可视化界面
      System::System(const string &strVocFile, const string &strSettingsFile,
                     const eSensor sensor, const bool bUseViewer):
          // System 类构造函数的成员初始化列表, 用于初始化类的部分成员变量
          mSensor(sensor), // Origin: mpViewer(static_cast<Viewer*>(NULL)),
          mpViewer(static_cast<Viewer*>(nullptr)), mbReset(false),
          mbActivateLocalizationMode(false), mbDeactivateLocalizationMode(false)
      {
          // Output welcome message
          cout << endl <<
          "ORB-SLAM2 Copyright (C) 2014-2016 Raul Mur-Artal, University of Zaragoza." << endl <<
          "This program comes with ABSOLUTELY NO WARRANTY;" << endl  <<
          "This is free software, and you are welcome to redistribute it" << endl <<
          "under certain conditions. See LICENSE.txt." << endl << endl;
  
          // 输出当前传感器类型
          cout << "Input sensor was set to: ";
  
          if (mSensor==MONOCULAR)
              cout << "Monocular" << endl;
          else if (mSensor==STEREO)
              cout << "Stereo" << endl;
          else if (mSensor==RGBD)
              cout << "RGB-D" << endl;
  
          // Check settings file
          // 先将配置文件的路径转换成为字符串, 以只读的方式打开
          cv::FileStorage fsSettings(strSettingsFile.c_str(), cv::FileStorage::READ);
          // 如果打开失败, 就输出调试信息
          if (!fsSettings.isOpened())
          {
              cerr << "Failed to open settings file at: " << strSettingsFile << endl;
              // 然后退出
              exit(-1);
          }
  
          // Load ORB Vocabulary
          cout << endl << "Loading ORB Vocabulary. This could take a while..." << endl;
  
      }
  
  }
  
  ```
  
