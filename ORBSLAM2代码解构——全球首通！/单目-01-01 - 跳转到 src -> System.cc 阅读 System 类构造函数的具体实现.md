# src/System.cc

主要阅读该文件中 **`System` 类的构造函数**


## 重点代码逐行解析


- ### ORBSLAM2 中变量遵循的命名规则

  - 遵循的命名规则也被称作 **匈牙利命名法**

  - 变量名的第一个字母为 `m` 表示该变量为某类的成员变量

  - 变量名的第一, 第二个字母表示数据类型:
  
    - `p` 表示指针类型
    - `n` 表示 `int` 类型
    - `b` 表示 `bool` 类型
    - `s` 表示 `std::set` 类型
    - `v` 表示 `std::vector` 类型
    - `l` 表示 `std::list` 类型
    - `KF` 表示 `KeyFrame` 类型


- ###  1. 成员变量初始化列表

  - `System` 类的构造函数
 
  - 第一个 `System` 是类名, 表示这是 `ORB_SLAM2::System` 类的构造函数; 第二个 `System` 是构造函数的名称, 必须与类名相同

  - 在System类构造函数体外, 是部分成员变量的初始化列表, 用于初始化类的部分成员变量
  
  ```c++
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
   ```

  - 其中, 变量 `mSensor`, `mpViewer`, `mbReset`, `mbActivateLocalizationMode` 和 `mbDeactivateLocalizationMode` 是 System 类的成员变量, 它们是在 `include/System.h` 中定义的

  ```c++
          // 成员变量的命名方式, 类的变量名有前缀m, 如果这个变量是指针类型还要多加个前缀p, 如果是进程则加个前缀t, 等等
  
          // 传感器类型
          // Input sensor
          eSensor mSensor;
  
          // 查看器, 可视化界面
          // The viewer draws the map and the current camera pose. It uses Pangolin.
          Viewer* mpViewer;
  
          // 复位标志
          // Reset flag
          std::mutex mMutexReset;
          bool mbReset;
  
          // 模式改变标志
          // Change mode flags
          std::mutex mMutexMode;
          bool mbActivateLocalizationMode;
          bool mbDeactivateLocalizationMode;
  ```


- ### 2. 输出当前传感器类型

  ```c++
      cout << "Input sensor was set to: ";
  
      if(mSensor==MONOCULAR)
          cout << "Monocular" << endl;
      else if(mSensor==STEREO)
          cout << "Stereo" << endl;
      else if(mSensor==RGBD)
          cout << "RGB-D" << endl;
  ```


- ### 3. 读取配置文件

  - 先将配置文件的路径转换成字符串, 然后以只读的方式打开

  ```c++
          //  Check settings file
          // 先将配置文件的路径转换成字符串, 然后以只读的方式打开
          cv::FileStorage fsSettings(strSettingsFile.c_str(), cv::FileStorage::READ);
          // 如果打开失败, 就输出调试信息
          if(!fsSettings.isOpened())
          {
              cerr << "Failed to open settings file at: " << strSettingsFile << endl;
              // 然后退出
              exit(-1);
          }
  ```


- ### 4. 加载 ORB 字典

  - 这里跟 `ORBSLAM2` 的源码不同, 源码用的词典是 `DBoW2`, 而 `SuperPoint + ORBSLAM2` 项目中使用的是 `DBoW3`
 
  - 因此, 成员变量 `mpVocabulary` 没有 `loadFromTextFile` 这个方法 

  ```c++
        // 建立一个新的 ORB 字典
          mpVocabulary = new ORBVocabulary();
          // Origin:
          /**
          bool bVocLoad = mpVocabulary->loadFromTextFile(strVocFile);
          if(!bVocLoad)
          {
              cerr << "Wrong path to vocabulary. " << endl;
              cerr << "Falied to open at: " << strVocFile << endl;
              exit(-1);
          }
          cout << "Vocabulary loaded!" << endl << endl;
          **/
          mpVocabulary->load(strVocFile);
  ```

  - 其中, 成员变量 `mpVocabulary` 是在 `include/System.h` 中定义的
 
  ```c++
          // 一个指向 ORB 字典的指针
          // ORB vocabulary used for place recognition and feature matching.
          ORBVocabulary* mpVocabulary;
  ```


- ### 5. 创建关键帧数据库

  ```c++
          // Create KeyFrame Database
          mpKeyFrameDatabase = new KeyFrameDatabase(*mpVocabulary);
  ```
  
  - 其中, 成员变量 `mpKeyFrameDatabase` 是在 `include/System.h` 中定义的
 
  ```c++
          // 关键帧数据库的指针, 这个数据库用于重定位和回环检测
          // KeyFrame database for place recognition (relocalization and loop detection).
          KeyFrameDatabase* mpKeyFrameDatabase;
  ```


- ### 6. 创建地图

  ```c++
          // Create the Map
          mpMap = new Map();
  ```

  - 其中, 成员变量 `mpMap` 是在 `include/System.h` 中定义的
 
  ```c++
          // 指向地图(数据库)的指针
          // Map structure that stores the pointers to all KeyFrames and MapPoints.
          Map* mpMap;
  ```


- ### 7. 创建绘制器

  - 这里的帧绘制器和地图绘制器将会被可视化的 `Viewer` 所使用
 
  ```c++
          // 这里的帧绘制器和地图绘制器将会被可视化的 Viewer 所使用
          // Create Drawers. These are used by the Viewer
          mpFrameDrawer = new FrameDrawer(mpMap);
          mpMapDrawer = new MapDrawer(mpMap, strSettingsFile);
  ```

  - 其中, 成员变量 `mpFrameDrawer` 和 `mpMapDrawer` 是在 `include/System.h` 中定义的
 
  ```c++
          // 帧绘制器
          FrameDrawer* mpFrameDrawer;
          // 地图绘制器
          MapDrawer* mpMapDrawer;
  ```


- ### 8. 创建追踪器

  - 在本主进程中初始化追踪器
 
  - `Tracking` 类的构造函数输入的参数如下: `this`, `字典`, `帧绘制器`, `地图绘制器`, `地图`, `关键帧地图`, `配置文件路径`, `传感器类型`
 
  - `this` 代表 `System` 类的当前对象指针, 其作用为, `Tracking` 类的构造函数中的 `pSys` 参数会接收到 `this`，也就是当前 `System` 对象的指针, 通过将 `this` 作为参数传递给 `Tracking`，能获得 `System` 类实例的指针，从而可以在 `Tracking` 类的内部使用它
 
  ```c++
          // 在本主进程中初始化追踪器
          // Initialize the Tracking thread
          // (it will live in the main thread of execution, the one that called this constructor)
          // Tracking 类的构造函数输入的参数如下: this, 字典, 帧绘制器, 地图绘制器, 地图, 关键帧地图, 配置文件路径, 传感器类型
          // this 代表 System 类的当前对象指针
          // 其作用为, Tracking 类的构造函数中的 pSys 参数会接收到 this，也就是当前 System 对象的指针
          // 通过将 this 作为参数传递给 Tracking，能获得 System 类实例的指针，从而可以在 Tracking 类的内部使用它
          mpTracker = new Tracking(this, mpVocabulary, mpFrameDrawer, mpMapDrawer,
                                   mpMap, mpKeyFrameDatabase, strSettingsFile, mSensor);
  ```

  - 其中, 成员变量 `mpTracker` 是在 `include/System.h` 中定义的
 
  ```c++
          // 追踪器, 除了进行运动追踪外还要负责创建关键帧, 创建新地图点和进行重定位的工作
          // Tracker. It receives a frame and computes the associated camera pose.
          // It also decides when to insert a new keyframe, create some new MapPoints and
          // performs relocalization if tracking fails.
          Tracking* mpTracker;
  ```


- ### 9. 创建局部见图器和局部建图线程

  - 初始化局部建图器并运行局部建图线程
 
  ```c++
          // 初始化局部建图器并运行局部建图线程
          // Initialize the Local Mapping thread and launch
          mpLocalMapper = new LocalMapping(mpMap, mSensor==MONOCULAR);
          mptLocalMapping = new thread(&ORB_SLAM2::LocalMapping::Run,mpLocalMapper);
  ```

  - 其中, 成员变量 `mpLocalMapper` 和 `mptLocalMapping` 是在 `include/System.h` 中定义的
 
  ```c++
          // 局部建图器, 局部BA由它进行
          // Local Mapper. It manages the local map and performs local bundle adjustment.
          LocalMapping* mpLocalMapper;
  
          // 系统除了在主进程中进行运动追踪外, 会创建局部建图线程, 回环检测线程和可视化线程
          // System threads: Local Mapping, Loop Closing, Viewer.
          // The Tracking thread "lives" in the main execution thread that creates the System object.
          std::thread* mptLocalMapping;
  ```


- ### 10. 创建回环检测器和回环检测线程

  - 初始化回环检测器并运行回环检测线程
 
  - `LoopClosin`g 类的构造函数输入的参数如下: `地图`, `关键帧数据库`, `ORB 字典`, `当前的传感器是否是单目`
 
  ```c++
          // 初始化回环检测器并运行回环检测线程
          // Initialize the Loop Closing thread and launch
          // LoopClosing 类的构造函数输入的参数如下: 地图, 关键帧数据库, ORB 字典, 当前的传感器是否是单目
          mpLoopCloser = new LoopClosing(mpMap, mpKeyFrameDatabase, mpVocabulary, mSensor!=MONOCULAR);
          mptLoopClosing = new thread(&ORB_SLAM2::LoopClosing::Run, mpLoopCloser);
  ```

  - 其中, 成员变量 `mpLoopCloser` 和 `mptLoopClosing` 是在 `include/System.h` 中定义的
 
  ```c++
          // 回环检测器, 会执行位姿图优化并且开一个新的线程进行全局BA
          // Loop Closer. It searches loops with every new keyframe. If there is a loop it performs
          // a pose graph optimization and full bundle adjustment (in a new thread) afterwards.
          LoopClosing* mpLoopCloser;
  
          // 系统除了在主进程中进行运动追踪外, 会创建局部建图线程, 回环检测线程和可视化线程
          // System threads: Local Mapping, Loop Closing, Viewer.
          // The Tracking thread "lives" in the main execution thread that creates the System object.
          std::thread* mptLoopClosing;
  ```  


- ### 11. 创建可视化器

  - 如果指定需要进行可视化, 则运行可视化部分

  - 初始化 `Viewer` 并运行 `Viewer` 线程

  - `Viewer` 类的构造函数输入的参数如下: `this`, `帧绘制器`, `地图绘制器`, `追踪器`, `配置文件路径`
 
  - 然后设置 `mpTracker` 的内部指针, 指向 `mpViewer`, 这样使得 `mpTracker` 可以调用 `mpViewer` 中的函数或使用其数据

  ```c++
          // Initialize the Viewer thread and launch
          // 如果指定需要进行可视化, 则运行可视化部分
          if(bUseViewer)
          {
              // 初始化 Viewer 并运行 Viewer线程
              // Viewer 类的构造函数输入的参数如下: this, 帧绘制器, 地图绘制器, 追踪器, 配置文件路径
              mpViewer = new Viewer(this, mpFrameDrawer, mpMapDrawer, mpTracker, strSettingsFile);
              mptViewer = new thread(&Viewer::Run, mpViewer);
              // 设置追踪器的 Viewer
              mpTracker->SetViewer(mpViewer);
          }
  ```

  - 其中, 成员变量 `mpViewer` 在构造函数体外的成员变量初始化列表中已经提到过了, 成员变量 `mptViewer` 是在 `include/System.h` 中定义的

```c++
        // 系统除了在主进程中进行运动追踪外, 会创建局部建图线程, 回环检测线程和可视化线程
        // System threads: Local Mapping, Loop Closing, Viewer.
        // The Tracking thread "lives" in the main execution thread that creates the System object.
        std::thread* mptViewer;
```


- ### 12. 设置进程间的指针

  - 设置 `mpTracker`, `mpLocalMapper` 和 `mpLoopCloser` 三个进程之间的指针

  - 设置指针的目的是, 为了使各个进程之间能够互相访问和交互
 
  - 举例来说, `mpTracker` 需要访问 `mpLocalMapper`, 因此需要设置 `mpTracker` 对象的内部指针, 指向 `mpLocalMapper`, 从而使得 `mpTracker` 可以调用 `mpLocalMapper` 中的函数或使用其数据
 
  ```c++
          // 设置进程间的指针, 使它们能够相互访问和交互
          // 举例来说, mpTracker 需要访问 mpLocalMapper, 因此需要设置 mpTracker 对象的内部指针, 指向 mpLocalMapper
          // 从而使得 mpTracker 可以调用 mpLocalMapper 中的函数或使用其数据
          // Set pointers between threads
          mpTracker->SetLocalMapper(mpLocalMapper);
          mpTracker->SetLoopClosing(mpLoopCloser);
  
          mpLocalMapper->SetTracker(mpTracker);
          mpLocalMapper->SetLoopCloser(mpLoopCloser);
  
          mpLoopCloser->SetTracker(mpTracker);
          mpLoopCloser->SetLocalMapper(mpLocalMapper);
  ```

  - 其实在上面的代码 `创建可视化器` 中, 已经有类似的操作了, 目的是为了让 mpTracker 能够调用 mpViewer 中的函数或使用其数据

  ```c++
              // 设置追踪器的 Viewer
              mpTracker->SetViewer(mpViewer);
  ```

  - 上述的函数可以在各自的头文件中中找到它们的声明

    - include/Tracking.h

    ```c++
        void SetLocalMapper(LocalMapping* pLocalMapper);
        void SetLoopClosing(LoopClosing* pLoopClosing);
        void SetViewer(Viewer* pViewer);
    ```
    
    - include/LocalMapping.h

    ```c++
        void SetLoopCloser(LoopClosing* pLoopCloser);
        void SetTracker(Tracking* pTracker);
    ```

    - include/LoopClosing.h
   
    ```c++
        void SetTracker(Tracking* pTracker);
        void SetLocalMapper(LocalMapping* pLocalMapper);
    ```

  - 可以在各自的源文件中找到它们的具体实现

    - src/Tracking.cc
  
    ```c++
    void Tracking::SetViewer(Viewer *pViewer)
    {
        mpViewer=pViewer;
    }
    void Tracking::SetLocalMapper(LocalMapping *pLocalMapper)
    {
        mpLocalMapper=pLocalMapper;
    }
    void Tracking::SetLoopClosing(LoopClosing *pLoopClosing)
    {
        mpLoopClosing=pLoopClosing;
    }
    ```

    - src/LocalMapping.cc
    
    ```c++
    void LocalMapping::SetLoopCloser(LoopClosing* pLoopCloser)
    {
        mpLoopCloser = pLoopCloser;
    }
    void LocalMapping::SetTracker(Tracking *pTracker)
    {
        mpTracker=pTracker;
    }
    ```

    - src/LoopClosing.cc
   
    ```c++
    void LoopClosing::SetTracker(Tracking *pTracker)
    {
        mpTracker=pTracker;
    }
    void LoopClosing::SetLocalMapper(LocalMapping *pLocalMapper)
    {
        mpLocalMapper=pLocalMapper;
    }
    ```


- ### 13. 余下没有初始化的成员变量

  - 在 include/System.h 中还有

    - mTrackingState
    - mTrackedMapPoints
    - mTrackedKeyPointsUn
    - mMutexState

  - 这四个成员变量没有在构造函数中进行初始化, 后续用到它们的时候会再提一下

  ```c++
          // 追踪状态标志
          // Tracking state
          int mTrackingState;
          
          std::vector<MapPoint*> mTrackedMapPoints;
          std::vector<cv::KeyPoint> mTrackedKeyPointsUn;
          std::mutex mMutexState;
  ```

  - 不过在 `CLion` 中会出现警告 `System` 类的构造函数中没有初始化 `mTrackingState` 的提示, 这个成员变量代表追踪器的状态, 在 `SLAM` 系统运行时输出的值为 2 (目前不知道数值的具体意义)

  - 如果不想出现这个警告, 可以在构造函数最后加上以下代码, 不会影响代码正常运行

  ```c++
          // 初始化 mTrackingState 的值, 直接设置为0, 只是为了避免CLion的警告提示
          mTrackingState = 0;
  ```


## 需要进行跳转阅读的位置

- 在 `System.cc` 文件的 `System` 类构造函数中, 所调用的来自其他文件定义的类


- ### 1. 可视化器(1)

  - 在 `System.cc` 文件开头:
 
  ```c++
            mpViewer(static_cast<Viewer*>(nullptr)),
  ```

  - 注意, 这行代码中, `mpViewer` 是一个指向 `Viewer` 对象的指针, 将 `nullptr` (空指针)转换为 `Viewer*` 类型, 这样可以显式地将 `mpViewer` 初始化为 `nullptr`
 
  - 所以这行代码并没有创建 `Viewer` 实例, 因此不会调用其构造函数, 因此只需要跳转到 `include/Viewer.h`查看


- ### 2. ORB 字典

  ```c++
          // 建立一个新的 ORB 字典
          mpVocabulary = new ORBVocabulary();
  ```

  - `ORBVocabulary` 类的是在 `include/ORBVocabulary.h` 里声明的, 没有源文件, 所以需要去到头文件里面看看


- ### 3. 关键帧数据库

  ```c++
          // Create KeyFrame Database
          mpKeyFrameDatabase = new KeyFrameDatabase(*mpVocabulary);
  ```


- ### 4. 地图(数据库)

  ```c++
          // Create the Map
          mpMap = new Map();
  ```


- ### 5. 帧绘制器

  ```c++
          // 这里的帧绘制器和地图绘制器将会被可视化的 Viewer 所使用
          // Create Drawers. These are used by the Viewer
          mpFrameDrawer = new FrameDrawer(mpMap);
          mpMapDrawer = new MapDrawer(mpMap, strSettingsFile);
  ```


- ### 6. 地图绘制器

  ```c++
          // 这里的帧绘制器和地图绘制器将会被可视化的 Viewer 所使用
          // Create Drawers. These are used by the Viewer
          mpFrameDrawer = new FrameDrawer(mpMap);
          mpMapDrawer = new MapDrawer(mpMap, strSettingsFile);
  ```


- ### 7. 追踪器

  ```c++
          // 在本主进程中初始化追踪器
          // Initialize the Tracking thread
          // (it will live in the main thread of execution, the one that called this constructor)
          // Tracking 类的构造函数输入的参数如下: this, 字典, 帧绘制器, 地图绘制器, 地图, 关键帧地图, 配置文件路径, 传感器类型
          // this 代表 System 类的当前对象指针
          // 其作用为, Tracking 类的构造函数中的 pSys 参数会接收到 this，也就是当前 System 对象的指针
          // 通过将 this 作为参数传递给 Tracking，能获得 System 类实例的指针，从而可以在 Tracking 类的内部使用它
          mpTracker = new Tracking(this, mpVocabulary, mpFrameDrawer, mpMapDrawer,
                                   mpMap, mpKeyFrameDatabase, strSettingsFile, mSensor);
  ```


- ### 8. 局部建图器

  ```c++
          // 初始化局部建图器并运行局部建图线程
          // Initialize the Local Mapping thread and launch
          mpLocalMapper = new LocalMapping(mpMap, mSensor==MONOCULAR);
          mptLocalMapping = new thread(&ORB_SLAM2::LocalMapping::Run,mpLocalMapper);
  ```


- ### 9. 回环检测器

  ```c++
          // 初始化回环检测器并运行回环检测线程
          // Initialize the Loop Closing thread and launch
          // LoopClosing 类的构造函数输入的参数如下: 地图, 关键帧数据库, ORB 字典, 当前的传感器是否是单目
          mpLoopCloser = new LoopClosing(mpMap, mpKeyFrameDatabase, mpVocabulary, mSensor!=MONOCULAR);
          mptLoopClosing = new thread(&ORB_SLAM2::LoopClosing::Run, mpLoopCloser);
  ```


- ### 10. 可视化器(2)

  ```c++
          // Initialize the Viewer thread and launch
          // 如果指定需要进行可视化, 则运行可视化部分
          if(bUseViewer)
          {
              // 初始化 Viewer 并运行 Viewer线程
              // Viewer 类的构造函数输入的参数如下: this, 帧绘制器, 地图绘制器, 追踪器, 配置文件路径
              mpViewer = new Viewer(this, mpFrameDrawer, mpMapDrawer, mpTracker, strSettingsFile);
              mptViewer = new thread(&Viewer::Run, mpViewer);
              // 设置追踪器的 Viewer
              mpTracker->SetViewer(mpViewer);
          }
  ```





## 重头开始构建 ORBSLAM2

- 如果是从零开始构建 `ORBSLAM2` 系统,  

- ### 1. mono_kitti.cc 的修改

  - 在文件开头加上

mono_kitti.cc

```c++
#include "System.h"
```


```c++
    // Step 3 加载 SLAM 系统
    // Create SLAM system. It initializes all system threads and gets ready to process frames.
    // 输入的参数如下: 词典文件路径, 配置文件路径, 传感器类型, 是否使用可视化界面
    ORB_SLAM2::System SLAM(argv[1],argv[2],ORB_SLAM2::System::MONOCULAR,true);
```

- ### 1. include/System.h (Build from scratch - Changed 0)

  - 如果是从零开始构建 ORBSLAM2 系统 


```c++
#ifndef SYSTEM_H
#define SYSTEM_H


#include <mutex>

//#include "Viewer.h"
//#include "ORBVocabulary.h"


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

        // ORB vocabulary used for place recognition and feature matching.
        // 一个指向ORB字典的指针
        // ORBVocabulary* mpVocabulary;

        // The viewer draws the map and the current camera pose. It uses Pangolin.
        // 查看器, 可视化界面
        // Viewer* mpViewer;

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
        // mpViewer(static_cast<Viewer*>(nullptr)),
        mbReset(false), mbActivateLocalizationMode(false), mbDeactivateLocalizationMode(false)
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
        // mpVocabulary = new ORBVocabulary();
        // 尝试加载字典
        /**
        try
        {
            mpVocabulary->load(strVocFile);
            cout << "Vocabulary loaded!" << endl << endl;
        }
        // 如果加载失败, 就输出调试信息
        catch (const exception &e)
        {
            cerr << "Wrong path to vocabulary. " << endl;
            cerr << "Falied to open at: " << strVocFile << endl;
            // 然后退出
            exit(-1);
        }
        **/


        // Create KeyFrame Database
        // mpKeyFrameDatabase = new KeyFrameDatabase(*mpVocabulary);

    }
    
}

```







