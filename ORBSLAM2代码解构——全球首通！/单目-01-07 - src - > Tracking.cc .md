# 跳转到 src/Tracking.cc 阅读 Tracking 类构造函数的具体实现

- 阅读该文件中 `Tracking` 类的构造函数


## 重点代码逐行解析


```c++
    // 构造函数
    // 构造函数的参数如下: 系统实例, BOW字典, 帧绘制器, 地图点绘制器, 地图句柄, 关键帧产生的词袋数据库, 配置文件路径, 传感器类型
    Tracking::Tracking(System *pSys, ORBVocabulary* pVoc, FrameDrawer *pFrameDrawer, MapDrawer *pMapDrawer,
                       Map *pMap, KeyFrameDatabase* pKFDB, const string &strSettingPath, const int sensor):
        mState(NO_IMAGES_YET), mSensor(sensor), mbOnlyTracking(false), mbVO(false), mpORBVocabulary(pVoc),
        mpKeyFrameDB(pKFDB), mpInitializer(static_cast<Initializer*>(nullptr)), mpSystem(pSys), mpViewer(nullptr),
        mpFrameDrawer(pFrameDrawer), mpMapDrawer(pMapDrawer), mpMap(pMap), mnLastRelocFrameId(0)
```

```c++
        // 跟踪状态
        eTrackingState mState;

        // 传感器类型: MONOCULAR, STEREO, RGBD
        // Input sensor
        int mSensor;

        // 标记当前系统是处于 SLAM 状态还是纯定位状态
        // True if local mapping is deactivated and we are performing only localization
        bool mbOnlyTracking;

        // 当进行纯定位时才会有的一个变量, 为 false 表示该帧匹配了很多的地图点, 跟踪是正常的
        // 如果少于10个则为 true, 表示快要完蛋了
        // In case of performing only localization, this flag is true when there are no matches to points in the map.
        // Still tracking will continue if there are enough matches with temporal points.
        // In that case we are doing visual odometry.
        // The system will try to do relocalization to recover "zero-drift" localization to the map.
        bool mbVO;

        // BoW 词袋模型相关
        // BoW
        // ORB 特征字典
        ORBVocabulary* mpORBVocabulary;
        // 当前系统运行的时候, 关键帧所产生的数据库
        KeyFrameDatabase* mpKeyFrameDB;

        // 单目初始器
        // Initalization (only for monocular)
        // Initializer* mpInitializer;

        // 指向系统实例的指针
        // System
        System* mpSystem;

        // 可视化器相关
        // Drawers
        // 可视化器对象句柄
        Viewer* mpViewer;
        // 帧绘制器句柄
        FrameDrawer* mpFrameDrawer;
        // 地图绘制器句柄
        MapDrawer* mpMapDrawer;

        // (全局)地图句柄
        // Map
        Map* mpMap;

        // 上一次重定位的那一帧的ID
        unsigned int mnLastRelocFrameId;
```




