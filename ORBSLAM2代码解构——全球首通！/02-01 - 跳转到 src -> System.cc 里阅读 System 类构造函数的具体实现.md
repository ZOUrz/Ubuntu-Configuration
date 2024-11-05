# src/System.cc

主要阅读该文件中 **System 类的构造函数**


## 重点代码逐行解析


### ORBSLAM2中变量遵循的命名规则

遵循的命名规则也被称作**匈牙利命名法**

* 变量名的第一个字母为 m 表示该变量为某类的成员变量

* 变量名的第一, 第二个字母表示数据类型:
  
    * p 表示指针类型
    * n 表示 int 类型
    * b 表示 bool 类型
    * s 表示 std::set 类型
    * v 表示 std::vector 类型
    * l 表示 std::list 类型
    * KF 表示 KeyFrame 类型


###  1. 构造函数体外的部分成员变量初始化

```c++
    // 系统的构造函数, 将会启动其他线程
    // 第一个 System 是类名, 表示这是 ORB_SLAM2::System 类的构造函数
    // 第二个 System 是构造函数的名称, 必须与类名相同
    // 构造函数的参数如下: 词典文件路径, 配置文件路径, 传感器类型, 是否使用可视化界面
    System::System(const string &strVocFile, const string &strSettingsFile,
                   const eSensor sensor, const bool bUseViewer):
        // System 类构造函数的成员初始化列表, 用于初始化类的部分成员变量
        mSensor(sensor), mpViewer(static_cast<Viewer*>(nullptr)), mbReset(false),
        mbActivateLocalizationMode(false), mbDeactivateLocalizationMode(false)
```

其中, 变量

* mSensor
* mpViewer
* mbReset
* mbActivateLocalizationMode
* mbDeactivateLocalizationMode

是 System 类的成员变量

上述提到的部分成员变量是在 include/System.h中定义的

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

### 2. 构造函数体内的部分成员变量初始化

```c++
      // 建立一个新的ORB字典
        mpVocabulary = new ORBVocabulary();
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

        // Create KeyFrame Database
        mpKeyFrameDatabase = new KeyFrameDatabase(*mpVocabulary);

        // Create the Map
        mpMap = new Map();

        // 这里的帧绘制器和地图绘制器将会被可视化的 Viewer 所使用
        // Create Drawers. These are used by the Viewer
        mpFrameDrawer = new FrameDrawer(mpMap);
        mpMapDrawer = new MapDrawer(mpMap, strSettingsFile);

        // 在本主进程中初始化追踪器
        // Initialize the Tracking thread
        // (it will live in the main thread of execution, the one that called this constructor)
        // Tracking类的构造函数输入的参数如下: this, 字典, 帧绘制器, 地图绘制器, 地图, 关键帧地图, 配置文件路径, 传感器类型
        // this 代表 System 类的当前对象指针
        // 其作用为, Tracking 类的构造函数中的 pSys 参数会接收到 this，也就是当前 System 对象的指针
        // 通过将 this 作为参数传递给 Tracking，能获得 System 类实例的指针，从而可以在 Tracking 类的内部使用它
        mpTracker = new Tracking(this, mpVocabulary, mpFrameDrawer, mpMapDrawer,
                                 mpMap, mpKeyFrameDatabase, strSettingsFile, mSensor);

        // 初始化局部建图器并运行局部建图线程
        // Initialize the Local Mapping thread and launch
        mpLocalMapper = new LocalMapping(mpMap, mSensor==MONOCULAR);
        mptLocalMapping = new thread(&ORB_SLAM2::LocalMapping::Run,mpLocalMapper);

        // 初始化回环检测器并运行回环检测线程
        // Initialize the Loop Closing thread and launch
        // LoopClosing类的构造函数输入的参数如下: 地图, 关键帧数据库, ORB字典, 当前的传感器是否是单目
        mpLoopCloser = new LoopClosing(mpMap, mpKeyFrameDatabase, mpVocabulary, mSensor!=MONOCULAR);
        mptLoopClosing = new thread(&ORB_SLAM2::LoopClosing::Run, mpLoopCloser);

        // Initialize the Viewer thread and launch
        // 如果指定需要进行可视化, 则运行可视化部分
        if(bUseViewer)
        {
            // 初始化 Viewer 并运行 Viewer线程
            // Viewer类的构造函数输入的参数如下: this, 帧绘制器, 地图绘制器, 追踪器, 配置文件路径
            mpViewer = new Viewer(this, mpFrameDrawer, mpMapDrawer, mpTracker, strSettingsFile);
            mptViewer = new thread(&Viewer::Run, mpViewer);
            // 设置追踪器的 Viewer
            mpTracker->SetViewer(mpViewer);
        }
```

其中, 变量

* mpVocabulary
* mpKeyFrameDatabase
* mpMap
* mpFrameDrawer
* mpMapDrawer
* mpTracker
* mpLocalMapper
* mptLocalMapping
* mpLoopCloser
* mptLoopClosing
* mptViewer

是在 include/System.h 中定义的

```c++
        // 一个指向ORB字典的指针
        // ORB vocabulary used for place recognition and feature matching.
        ORBVocabulary* mpVocabulary;

        // 关键帧数据库的指针, 这个数据库用于重定位和回环检测
        // KeyFrame database for place recognition (relocalization and loop detection).
        KeyFrameDatabase* mpKeyFrameDatabase;

        // 指向地图(数据库)的指针
        // Map structure that stores the pointers to all KeyFrames and MapPoints.
        Map* mpMap;

        // 追踪器, 除了进行运动追踪外还要负责创建关键帧, 创建新地图点和进行重定位的工作
        // Tracker. It receives a frame and computes the associated camera pose.
        // It also decides when to insert a new keyframe, create some new MapPoints and
        // performs relocalization if tracking fails.
        Tracking* mpTracker;

        // 局部建图器, 局部BA由它进行
        // Local Mapper. It manages the local map and performs local bundle adjustment.
        LocalMapping* mpLocalMapper;

        // 回环检测器, 会执行位姿图优化并且开一个新的线程进行全局BA
        // Loop Closer. It searches loops with every new keyframe. If there is a loop it performs
        // a pose graph optimization and full bundle adjustment (in a new thread) afterwards.
        LoopClosing* mpLoopCloser;
        // 帧绘制器
        FrameDrawer* mpFrameDrawer;
        // 地图绘制器
        MapDrawer* mpMapDrawer;

        // 系统除了在主进程中进行运动追踪外, 会创建局部建图线程, 回环检测线程和可视化线程
        // System threads: Local Mapping, Loop Closing, Viewer.
        // The Tracking thread "lives" in the main execution thread that creates the System object.
        std::thread* mptLocalMapping;
        std::thread* mptLoopClosing;
        std::thread* mptViewer;
```

### 3. 余下没有初始化的成员变量

在 include/System.h 中还有

* mTrackingState
* mTrackedMapPoints
* mTrackedKeyPointsUn
* mMutexState
   
这四个成员变量没有在构造函数中进行初始化, 后续用到它们的时候会再提一下

```c++
        // 追踪状态标志
        // Tracking state
        int mTrackingState;
        
        std::vector<MapPoint*> mTrackedMapPoints;
        std::vector<cv::KeyPoint> mTrackedKeyPointsUn;
        std::mutex mMutexState;
```

不过在CLion中会出现警告 System 类的构造函数中没有初始化 mTrackingState 的提示, 这个成员变量代表追踪器的状态, 输出的值为 2 (目前不知道数值的具体意义)

如果不想出现这个警告, 可以在构造函数最后加上以下代码, 不会影响代码正常运行

```c++
        // 初始化 mTrackingState 的值, 直接设置为0, 只是为了避免CLion的警告提示
        mTrackingState = 0;
```
