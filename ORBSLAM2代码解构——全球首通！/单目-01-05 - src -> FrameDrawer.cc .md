# 跳转到 src/FrameDrawer.cc 阅读 FrameDrawer 类构造函数的具体实现

- `FrameDrawer` 类的构造函数就几行代码, 比较简单

- 重点是其中的成员变量 `mState` 被设置为 `Tracking:SYSTEM_NOT_READY`, 这里需要进行跳转


## 重点代码逐行解析

- ### 1. 构造函数

 ```c++
     // 构造函数
     FrameDrawer::FrameDrawer(Map* pMap):
         mpMap(pMap)
     {
         mState = Tracking::SYSTEM_NOT_READY;
         // 初始化图像显示画布
         // 包括: 图像, 特征点连线形成的轨迹(初始化时), 框(跟踪时的MapPoint), 圈(跟踪时的特征点)
         // !!! 固定画布大小为 640 * 480
         mIm = cv::Mat(480,640,CV_8UC3, cv::Scalar(0,0,0));
     }
 ```

 - 其中, 构造函数以及其成员变量是在 `include/FrameDrawer` 中声明的

 ```c++
         // 构造函数
         FrameDrawer(Map* pMap);
 ```

 ```c++
         // Info of the frame to be drawn
         // 当前绘制的图像
         cv::Mat mIm;
 
         // 当前 SLAM 系统的工作状态
         int mState;
 
         // 地图指针
         Map* mpMap;
 ```


## 需要进行跳转阅读的位置

- ### 1. Tracking:SYSTEM_NOT_READY
 
 ```c++
         mState = Tracking::SYSTEM_NOT_READY;
 ```

  - 这一行代码将系统状态 `mState` 设置为 `Tracking::SYSTEM_NOT_READY`

  - 其中, `Tracking` 类中定义了枚举类型 `eTrackingState`, 而 `SYSTEM_NOT_READY` 是枚举类型的一个成员

  - 由于定义的代码位于 `include/Tracking.h`中, 因此只需要跳转到该文件中即可


## 重头开始构建 ORBSLAM2

- 如果是从零开始构建 `ORBSLAM2` 系统, 就按照下面给出的文件内容进行代码的编写


- ### 1. include/FrameDrawer.h

 - Build from scratch - Changed 0

 ```c++
 #ifndef FRAMEDRAWER_H
 #define FRAMEDRAWER_H
 
 #include "Map.h"
 
 #include<opencv2/core/core.hpp>
 #include<opencv2/features2d/features2d.hpp>
 
 
 namespace ORB_SLAM2
 {
     // 要用到的其他类的前向声明
     // 在该项目代码中，类之间可能存在复杂的相互依赖关系
     // 例如, System 类可能需要引用 Viewer 类, 而 Viewer 类可能又引用 System 类, 前向声明能够打破这种直接的依赖关系
     // 如果不使用前向声明, 而直接包含头文件, 可能会导致头文件之间的循环依赖, 进而导致编译错误或头文件包含的死循环
     // 通过前向声明, 编译器不会立即要求完整定义, 只需要一个简单的类声明, 防止了这些问题
     class Tracking;
     class Viewer;
 
     class FrameDrawer
     {
     public:
 
         // 构造函数
         FrameDrawer(Map* pMap);
 
 
     protected:
 
         // Info of the frame to be drawn
         // 当前绘制的图像
         cv::Mat mIm;
 
         // 当前 SLAM 系统的工作状态
         int mState;
 
         // 地图指针
         Map* mpMap;
     };
 
 }
 
 #endif //FRAMEDRAWER_H
 
 ```


- ### 2. src/FrameDrawer.cc

 - Build from scratch - Changed 0

 ```c++
 // 帧绘制器
 
 #include "FrameDrawer.h"
 
 #include <opencv2/core/core.hpp>
 #include <opencv2/highgui/highgui.hpp>
 
 
 namespace ORB_SLAM2
 {
 
     // 构造函数
     FrameDrawer::FrameDrawer(Map* pMap):
         mpMap(pMap)
     {
         mState = Tracking::SYSTEM_NOT_READY;
         // 初始化图像显示画布
         // 包括: 图像, 特征点连线形成的轨迹(初始化时), 框(跟踪时的MapPoint), 圈(跟踪时的特征点)
         // !!! 固定画布大小为 640 * 480
         mIm = cv::Mat(480,640,CV_8UC3, cv::Scalar(0,0,0));
     }
 
 }
 
 ```


- ### 3. include/System.h

 - Build from scratch - Changed 5

 - 文件开头加上

 ```c++
 #include "FrameDrawer.h"
 ```

 - 然后添加成员变量

 ```c++
         // 帧绘制器
         FrameDrawer* mpFrameDrawer;
 ```

 - 完整代码

 ```c++
 #ifndef SYSTEM_H
 #define SYSTEM_H
 
 
 #include <mutex>
 
 #include "Viewer.h"
 #include "ORBVocabulary.h"
 #include "KeyFrameDatabase.h"
 #include "Map.h"
 #include "FrameDrawer.h"
 
 
 namespace ORB_SLAM2
 {
     // 要用到的其他类的前向声明
     // 在该项目代码中，类之间可能存在复杂的相互依赖关系
     // 例如, System 类可能需要引用 Viewer 类, 而 Viewer 类可能又引用 System 类, 前向声明能够打破这种直接的依赖关系
     // 如果不使用前向声明, 而直接包含头文件, 可能会导致头文件之间的循环依赖, 进而导致编译错误或头文件包含的死循环
     // 通过前向声明, 编译器不会立即要求完整定义, 只需要一个简单的类声明, 防止了这些问题
     class Viewer;
     class FrameDrawer;
     class Map;
     class Tracking;  // 源码是注释调的, 不注释也能正常运行, 目前不清楚作者注释的动机
     class LocalMapping;
     class LoopClosing;
 
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
 
         // ORB vocabulary used for place recognition and feature matching.
         // 一个指向ORB字典的指针
         ORBVocabulary* mpVocabulary;
 
         // 关键帧数据库的指针, 这个数据库用于重定位和回环检测
         // KeyFrame database for place recognition (relocalization and loop detection).
         KeyFrameDatabase* mpKeyFrameDatabase;
 
         // 指向地图(数据库)的指针
         // Map structure that stores the pointers to all KeyFrames and MapPoints.
         Map* mpMap;
 
         // The viewer draws the map and the current camera pose. It uses Pangolin.
         // 查看器, 可视化界面
         Viewer* mpViewer;
 
         // 帧绘制器
         FrameDrawer* mpFrameDrawer;
 
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


- ### 4. src/System.cc

 - Build from scratch - Changed 5

 - 在代码最后加上

 ```c++
         // 这里的帧绘制器和地图绘制器将会被可视化的 Viewer 所使用
         // Create Drawers. These are used by the Viewer
         mpFrameDrawer = new FrameDrawer(mpMap);
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
 
         // 建立一个新的ORB字典
         mpVocabulary = new ORBVocabulary();
         // 尝试加载字典
         try
         {
             mpVocabulary->load(strVocFile);
             cout << "Vocabulary loaded!" << endl << endl;
         }
         // 如果加载失败, 就输出调试信息
         catch (const exception &e) {
             cerr << "Wrong path to vocabulary. " << endl;
             cerr << "Falied to open at: " << strVocFile << endl;
             // 然后退出
             exit(-1);
         }
 
         // Create KeyFrame Database
         mpKeyFrameDatabase = new KeyFrameDatabase(*mpVocabulary);
 
         // Create the Map
         mpMap = new Map();
 
         // 这里的帧绘制器和地图绘制器将会被可视化的 Viewer 所使用
         // Create Drawers. These are used by the Viewer
         mpFrameDrawer = new FrameDrawer(mpMap);
 
     }
 
 }
 
 ```

- ### 5. CMakeLists

```cmake

```

```cmake

```
