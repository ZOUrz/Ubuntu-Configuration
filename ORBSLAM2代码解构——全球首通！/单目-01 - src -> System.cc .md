# 跳转到 src/System.cc 阅读 System 类构造函数的具体实现

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

  - 在 `System` 类构造函数体外, 是部分成员变量的初始化列表, 用于初始化类的部分成员变量
  
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

  - 其中, 变量 `mSensor`, `mpViewer`, `mbReset`, `mbActivateLocalizationMode` 和 `mbDeactivateLocalizationMode` 是 `System` 类的成员变量, 它们是在 `include/System.h` 中定义的

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

  - 这行代码使用 `new` 关键字创建一个 `KeyFrameDatabase` 对象，并将其指针存储在成员指针变量 `mpKeyFrameDatabase`, 并调用 `KeyFrameDatabase` 类的构造函数来初始化该对象
 
  - 具体实现是在 `src/KeyFrameDatabase.cc` 里, 所以需要去到该文件里看看 `KeyFrameDatabase` 类构造函数的具体实现
  

- ### 4. 地图(数据库)

  ```c++
          // Create the Map
          mpMap = new Map();
  ```

  - 这行代码使用 `new` 关键字创建一个 `Map` 对象，并将其指针存储在成员指针变量 `mpMap`, 并调用 `Map` 类的构造函数来初始化该对象
 
  - 具体实现是在 `src/Map.cc` 里, 所以需要去到该文件里看看 `Map` 类构造函数的具体实现


- ### 5. 帧绘制器

  ```c++
          // 这里的帧绘制器和地图绘制器将会被可视化的 Viewer 所使用
          // Create Drawers. These are used by the Viewer
          mpFrameDrawer = new FrameDrawer(mpMap);
  ```

  - 这行代码使用 `new` 关键字创建一个 `FrameDrawer` 对象，并将其指针存储在成员指针变量 `mpFrameDrawer`, 并调用 `FrameDrawer` 类的构造函数来初始化该对象
 
  - 具体实现是在 `src/FrameDrawer.cc` 里, 所以需要去到该文件里看看 `FrameDrawer` 类构造函数的具体实现


- ### 6. 地图绘制器

  ```c++
          // 这里的帧绘制器和地图绘制器将会被可视化的 Viewer 所使用
          // Create Drawers. These are used by the Viewer
          mpMapDrawer = new MapDrawer(mpMap, strSettingsFile);
  ```

  - 这行代码使用 `new` 关键字创建一个 `MapDrawer` 对象，并将其指针存储在成员指针变量 `mpMapDrawer`, 并调用 `MapDrawer` 类的构造函数来初始化该对象
 
  - 具体实现是在 `src/MapDrawer.cc` 里, 所以需要去到该文件里看看 `MapDrawer` 类构造函数的具体实现


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

  - 这行代码使用 `new` 关键字创建一个 `Tracking` 对象，并将其指针存储在成员指针变量 `mpTracker`, 并调用 `Tracking` 类的构造函数来初始化该对象
 
  - 具体实现是在 `src/Tracking.cc` 里, 所以需要去到该文件里看看 `Tracking` 类构造函数的具体实现


- ### 8. 局部建图器

  ```c++
          // 初始化局部建图器并运行局部建图线程
          // Initialize the Local Mapping thread and launch
          mpLocalMapper = new LocalMapping(mpMap, mSensor==MONOCULAR);
          mptLocalMapping = new thread(&ORB_SLAM2::LocalMapping::Run,mpLocalMapper);
  ```

  - 第一行代码:

    - 使用 `new` 关键字创建一个 `LocalMapping` 对象，并将其指针存储在成员指针变量 `mpLocalMapper`, 并调用 `LocalMapping` 类的构造函数来初始化该对象
    - 具体实现是在 `src/LocalMapping.cc` 里, 所以需要去到该文件里看看 `LocalMapping` 类构造函数的具体实现

  - 第二行代码:

    - 首先使用 `new thread` 创建一个新的 `std::thread` 对象, 表示创建了一个新线程
    - 其中, `&ORB_SLAM2::LocalMapping::Run` 表示的是指向 `ORB_SLAM2::LocalMapping` 类的成员函数 `Run` 的指针, 使用 `&` 符号来获取 `Run` 函数的地址
    - `Run` 函数是 `LocalMapping` 类的一个成员函数, 用于处理与局部地图( `Local Mapping` )相关的操作
    - `mpLocalMapper`: 是传递给 `Run` 函数的对象指针, 是一个 `ORB_SLAM2::LocalMapping` 类的实例, 其被传递给 `Run` 函数作为 `this` 指针, 意味着 `Run` 将在 `mpLocalMapper` 对象上执行
    - `mptLocalMapping`: 是一个指向 `std::thread` 的指针, 用于保存创建的线程对象, 在 `new thread` 之后, 这个指针 `mptLocalMapping` 将指向新创建的线程
    - `Run` 函数的具体实现是在 `src/LocalMapping.cc` 里, 所以同样需要去到该文件里看看 `Run` 函数的具体实现


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

- 如果是从零开始构建 `ORBSLAM2` 系统, 就按照下面给出的文件内容进行代码的编写  



- ### 1. include/System.h

  - Build from scratch - Changed 0

  ```c++
  #ifndef SYSTEM_H
  #define SYSTEM_H
  
  
  #include <mutex>
  
  
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


- ### 2. src/System.cc

  - Build from scratch - Changed 0

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
  
      }
      
  }
  
  ```


- ### 3. mono_kitti.cc

  - Build from scratch - Changed 1

  - 在文件开头加上:

  ```c++
  #include "System.h"
  ```

  - 然后加上以下这段代码

  ```c++
      // Step 3 加载 SLAM 系统
      // Create SLAM system. It initializes all system threads and gets ready to process frames.
      // 输入的参数如下: 词典文件路径, 配置文件路径, 传感器类型, 是否使用可视化界面
      ORB_SLAM2::System SLAM(argv[1],argv[2],ORB_SLAM2::System::MONOCULAR,true);
  ```

  - 完整代码

  ```c++
  
  #include <fstream>
  #include <iomanip>
  #include <iostream>
  #include <opencv2/core/core.hpp>
  
  #include "System.h"
  
  using namespace std;
  
  
  // 获取图像序列中每一张图像的路径和时间戳
  void LoadImages (const string &strPathToSequence, vector<string> &vstrImageFilenames, vector<double> &vTimestamps);
  
  
  int main(int argc, char **argv)
  {
      // Step 1 检查输入参数个数是否足够
      if(argc != 4)
      {
          cerr << endl << "Usage: ./mono_kitti path_to_vocabulary path_to_settings path_to_sequence" << endl;
          return 1;
      }
  
      // Step 2 加载图像
      // Retrieve paths to images
      // 图像序列的文件名, 字符串序列
      vector<string> vstrImageFilenames;
      // 时间戳
      vector<double> vTimestamps;
      LoadImages(string(argv[3]), vstrImageFilenames, vTimestamps);
  
      // 当前图像序列的图片数目
      // int nImages = vstrImageFilenames.size();
      int nImages = static_cast<int>(vstrImageFilenames.size());
  
      // Step 3 加载 SLAM 系统
      // Create SLAM system. It initializes all system threads and gets ready to process frames.
      // 输入的参数如下: 词典文件路径, 配置文件路径, 传感器类型, 是否使用可视化界面
      ORB_SLAM2::System SLAM(argv[1],argv[2],ORB_SLAM2::System::MONOCULAR,true);
  }
  
  
  // 获取图像序列中每一张图像的路径和时间戳
  void LoadImages(const string &strPathToSequence, vector<string> &vstrImageFilenames, vector<double> &vTimestamps)
  {
      // Step 1 读取时间戳文件
      ifstream fTimes;
      string strPathTimeFile = strPathToSequence + "/times.txt";
      fTimes.open(strPathTimeFile.c_str());
      while(!fTimes.eof())
      {
          string s;
          getline(fTimes,s);
          // 当该行不为空时执行
          if(!s.empty())
          {
              stringstream ss;
              ss << s;
              double t;
              ss >> t;
              // 保存时间戳
              vTimestamps.push_back(t);
          }
      }
  
      // Step 2 使用左目图像, 生成左目图像序列中每一张图像的文件名
      string strPrefixLeft = strPathToSequence + "/image_0/";
  
      //const int nTimes = vTimestamps.size();
      const int nTimes = static_cast<int>(vTimestamps.size());
      vstrImageFilenames.resize(nTimes);
  
      for(int i=0; i<nTimes; i++)
      {
          stringstream ss;
          ss << setfill('0') << setw(6) << i;
          vstrImageFilenames[i] = strPrefixLeft + ss.str() + ".png";
      }
  }
  
  ```


- ### 4. CMakeLists

  - Build from scratch - Changed 1
 
  - 在文件以下位置进行修改, 将 `System.cc` 源文件添加到库中
 
  ```cmake
  # 创建一个名为${PROJECT_SOURCE_DIR}的共享库(SHARED表示生成动态链接库), 并将指定的源文件添加到库中
  add_library(${PROJECT_NAME} SHARED
          src/System.cpp
  )
  ```

  - 完整代码

  ```cmake
  # 指定CMake的最低版本要求为2.8
  cmake_minimum_required(VERSION 2.8)
  # 定义一个名为ORB_SLAM2的项目
  project(My_ORBSLAM2)
  
  # 检查CMAKE_BUILD_TYPE是否被定义, 如果没有, 则将其设置为Release
  # 因此该项目默认构建为发布模式
  # * -------------------- *
  # 以下是一些常见的构建类型及其区别:
  # - Release
  #   - 特点: 开启优化, 去除调试信息
  #   - 用途: 用于发布版本, 确保代码在性能上的最优化, 适合最终用户使用
  # - Debug
  #   - 特点: 包含调试信息, 禁用优化
  #   - 用途: 用于开发和调试阶段, 方便使用调试器进行代码调试, 可以查看变量值, 调用栈等信息
  # - RelWithDebInfo (Release with Debug Info)
  #   - 特点: 开启优化并包含调试信息
  #   - 用途: 适用于希望在发布版本中保留调试信息的情况, 便于在发布版本中进行后续的故障排查
  # - MinSieRel (Minimum Size Release)
  #   - 特点: 优化代码以减小可执行文件的大小, 而不是最大化性能
  #   - 用途: 适用于对可执行文件大小敏感的场合, 如嵌入式系统或存储受限的设备
  IF(NOT CMAKE_BUILD_TYPE)
      SET(CMAKE_BUILD_TYPE Release)
  ENDIF()
  
  # 输出当前的构建类型, 用于调试和确认当前的构建配置
  MESSAGE("Build type: " ${CMAKE_BUILD_TYPE})
  
  # 设置C和C++编译器的Flags
  # -Wall: 开启所有警告, -03: 进行最高级别的优化, -march=native: 优化代码以适应当前的处理器架构
  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS}  -Wall  -O3 -march=native ")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall   -O3 -march=native")
  
  # Check C++11 or C++0x support
  # 引入CheckCXXCompilerFlag模块, 用于检查编译器是否支持特定的C++ Flag
  include(CheckCXXCompilerFlag)
  # 检查编译器是否支持C++11(-std=c++11)和C++0x(-std=c++0x)
  # 这两个检查的结果将分别存储在COMPILER_SUPPORTS_CXX11和COMPILER_SUPPORTS_CXX0X
  CHECK_CXX_COMPILER_FLAG("-std=c++11" COMPILER_SUPPORTS_CXX11)
  CHECK_CXX_COMPILER_FLAG("-std=c++0x" COMPILER_SUPPORTS_CXX0X)
  # 如果支持C++11, 则将C++编译Flag设置为-std=c++11, 并定义一个宏COMPILEDWITHC11
  # 如果不支持C++11但支持C++0x, 则将C++编译Flag设置为-std=c++0x, 定义COMPILEDWITHC0X
  # 如果两者都不支持, 则输出一个致命错误信息, 提示用户更换编译器
  if(COMPILER_SUPPORTS_CXX11)
      set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
      add_definitions(-DCOMPILEDWITHC11)
      message(STATUS "Using flag -std=c++11.")
  elseif(COMPILER_SUPPORTS_CXX0X)
      set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x")
      add_definitions(-DCOMPILEDWITHC0X)
      message(STATUS "Using flag -std=c++0x.")
  else()
      message(FATAL_ERROR "The compiler ${CMAKE_CXX_COMPILER} has no C++11 support. Please use a different C++ compiler.")
  endif()
  
  # 将${PROJECT_SOURCE_DIR}/cmake_modules添加到CMake模块搜索路径中, 使得CMake可以在该目录下查找自定义的CMake模块
  # ORBSLAM2项目中自定义了FindEigen3.cmake, 该文件存放于项目路径内的cmake_modules文件夹中
  # 将该目录添加到CMake搜索路径中, 则CMake可以在构建过程中找到并使用这些自定义模块
  LIST(APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake_modules)
  
  # find_package会在系统的标准路径和用户指定的路径中查找指定的库或包, 它会搜索库的头文件和二进制文件(如共享库或静态库), 并根据指定版本要求进行匹配
  # 尝试查找OpenCV库, 要求版本至少为3.0, QUIET表示在没有找到库时不会输出警告信息
  find_package(OpenCV 3.0 QUIET)
  # 如果第一个未找到OpenCV, 则尝试查找版本为2.4.3的OpenCV, 如果仍未找到, 则输出致命错误信息, 终止构建过程
  if(NOT OpenCV_FOUND)
      find_package(OpenCV 2.4.3 QUIET)
      if(NOT OpenCV_FOUND)
          message(FATAL_ERROR "OpenCV > 2.4.3 not found.")
      endif()
  endif()
  
  # 查找Eigen3和Pangolin库, REQUIRED表示如果找不到这些库, CMake会报错并终止构建
  find_package(Eigen3 3.1.0 REQUIRED)
  find_package(Pangolin REQUIRED)
  
  # include_directories用于指定编译器在编译源文件时查找头文件的目录
  # 这些目录的路径会被添加到编译器的搜索路径中, 当编译器遇到#include指令时, 会在这些目录中查找所需的头文件
  # 指定要包含的头文件目录:
  include_directories(
          ${PROJECT_SOURCE_DIR}  # 项目的根目录
          ${PROJECT_SOURCE_DIR}/include  # 项目的include目录, 通常用于存放公共头文件
          ${EIGEN3_INCLUDE_DIR}  # Eigen3库的头文件目录
          ${Pangolin_INCLUDE_DIRS}  # Pangolin库的头文件目录
  )
  
  # 设置库文件的输出目录为${PROJECT_SOURCE_DIR}/lib, 即编译生成的共享库将存放在该目录中
  set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/lib)
  
  # 创建一个名为${PROJECT_SOURCE_DIR}的共享库(SHARED表示生成动态链接库), 并将指定的源文件添加到库中
  add_library(${PROJECT_NAME} SHARED
          src/System.cpp
  )
  
  # 指定${PROJECT_SOURCE_DIR}库链接的其他库
  target_link_libraries(${PROJECT_NAME}
          ${OpenCV_LIBS}  # OpenCV库
          ${EIGEN3_LIBS}  # Eigen3库
          ${Pangolin_LIBRARIES}  # Pangolin库
          # 还链接了位于Thirdparty/DBoW2和Thirdparty/g2o的第三方库
          #${PROJECT_SOURCE_DIR}/Thirdparty/DBoW3/lib/libDBoW3.so
          #${PROJECT_SOURCE_DIR}/Thirdparty/g2o/lib/libg2o.so
  )
  
  # Build examples
  
  # 设置可执行文件的输出目录为${PROJECT_SOURCE_DIR}/Examples/RGB-D
  #set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/Examples/RGB-D)
  # 创建一个名为rgbd_tum的可执行文件, 并指定其源文件为Examples/RGB-D/rgbd_tum.cc
  #add_executable(rgbd_tum Examples/RGB-D/rgbd_tum.cc)
  # 将rgbd_tum可执行文件链接到${PROJECT_SOURCE_DIR}库, 使得可执行文件可以使用库中的功能
  #target_link_libraries(rgbd_tum ${PROJECT_NAME})
  
  # 以下代码也是相同的逻辑
  #set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/Examples/Stereo)
  #add_executable(stereo_kitti Examples/Stereo/stereo_kitti.cpp)
  #target_link_libraries(stereo_kitti ${PROJECT_NAME})
  #add_executable(stereo_euroc Examples/Stereo/stereo_euroc.cc)
  #target_link_libraries(stereo_euroc ${PROJECT_NAME})
  
  set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/Examples/Monocular)
  #add_executable(mono_tum Examples/Monocular/mono_tum.cc)
  #target_link_libraries(mono_tum ${PROJECT_NAME})
  add_executable(mono_kitti Examples/Monocular/mono_kitti.cpp)
  target_link_libraries(mono_kitti ${PROJECT_NAME})
  #add_executable(mono_euroc Examples/Monocular/mono_euroc.cc)
  #target_link_libraries(mono_euroc ${PROJECT_NAME})

  ```
  
