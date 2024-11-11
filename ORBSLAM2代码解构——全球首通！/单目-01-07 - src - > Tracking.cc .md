# 跳转到 src/Tracking.cc 阅读 Tracking 类构造函数的具体实现

- 阅读该文件中 `Tracking` 类的构造函数


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


- ### 1. 成员变量初始化列表

  - `Tracking` 类的构造函数
 
  - 在 `Tracking` 类构造函数体外, 是部分成员变量的初始化列表, 用于初始化类的部分成员变量

  ```c++
      // 构造函数
      // 构造函数的参数如下: 系统实例, BOW字典, 帧绘制器, 地图点绘制器, 地图句柄, 关键帧产生的词袋数据库, 配置文件路径, 传感器类型
      Tracking::Tracking(System *pSys, ORBVocabulary* pVoc, FrameDrawer *pFrameDrawer, MapDrawer *pMapDrawer,
                         Map *pMap, KeyFrameDatabase* pKFDB, const string &strSettingPath, const int sensor):
          mState(NO_IMAGES_YET), mSensor(sensor), mbOnlyTracking(false), mbVO(false), mpORBVocabulary(pVoc),
          mpKeyFrameDB(pKFDB), mpInitializer(static_cast<Initializer*>(nullptr)), mpSystem(pSys), mpViewer(nullptr),
          mpFrameDrawer(pFrameDrawer), mpMapDrawer(pMapDrawer), mpMap(pMap), mnLastRelocFrameId(0)
  ```

  - 其中, 变量 `mState`, `mSensor`, `mbOnlyTracking`, `mbVO`, `mpORBVocabulary`, `mpKeyFrameDB`, `mpInitializer`, `mpSystem`, `mpViewer`, `mpFrameDrawer`, `mpMapDrawer`, `mpMap` 和 `mnLastRelocFrameId` 是 `Tracking` 类的成员变量, 它们是在 `include/Tracking.h` 中定义的

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

- ### 2. 从配置文件中加载相机参数

  ```c++
          // Step 1 从配置文件中加载相机参数
          // Load camera parameters from settings file
          cv::FileStorage fSettings(strSettingPath, cv::FileStorage::READ);
          float fx = fSettings["Camera.fx"];
          float fy = fSettings["Camera.fy"];
          float cx = fSettings["Camera.cx"];
          float cy = fSettings["Camera.cy"];
  ```

- ### 3. 构造相机内参矩阵

  ```c++
          // Step 1-1 构造相机内参矩阵
          //     |fx  0   cx|
          // K = |0   fy  cy|
          //     |0   0   1 |
          cv::Mat K = cv::Mat::eye(3,3,CV_32F);
          K.at<float>(0,0) = fx;
          K.at<float>(1,1) = fy;
          K.at<float>(0,2) = cx;
          K.at<float>(1,2) = cy;
          K.copyTo(mK);
  ```

  - 其中, 成员变量 `mK` 是在 `include/Tracking.h` 中定义的
 
  ```c++
          // 相机的内参数矩阵
          cv::Mat mK;
  ```

- ### 4.获取图像矫正系数

  ```c++
          // Step 1-2 图像矫正系数
          // [k1, k2, p1, p2, k3]
          cv::Mat DistCoef(4,1,CV_32F);
          DistCoef.at<float>(0) = fSettings["Camera.k1"];
          DistCoef.at<float>(1) = fSettings["Camera.k2"];
          DistCoef.at<float>(2) = fSettings["Camera.p1"];
          DistCoef.at<float>(3) = fSettings["Camera.p2"];
          // 有些相机的畸变系数中会没有 k3 项
          const float k3 = fSettings["Camera.k3"];
          if(k3!=0)
          {
              DistCoef.resize(5);
              DistCoef.at<float>(4) = k3;
          }
          DistCoef.copyTo(mDistCoef);
  ```

  - 其中, 成员变量 `mDistCoef` 是在 `include/Tracking.h` 中定义的
  
  ```c++
          // 相机的去畸变参数
          cv::Mat mDistCoef;
  ```

- ### 5. 获取双目摄像头基线

  - 相机的基线长度 * 相机的焦距

  ```c++
          // 双目摄像头baseline * fx 50
          mbf = fSettings["Camera.bf"];
  ```

  - 其中, 成员变量 `mbf` 是在 `include/Tracking.h` 中定义的

  ```c++
          // 相机的基线长度 * 相机的焦距
          float mbf;
  ```

- ### 6. 获取FPS

  ```c++
          float fps = fSettings["Camera.fps"];
          if(fps==0)
              fps=30;
  ```

- ### 7. 获取最小最大时间间隔

  ```c++
          // Max/Min Frames to insert keyframes and to check relocalisation
          // 新建关键帧和重定位中用来判断最小最大时间间隔, 和帧率有关
          mMinFrames = 0;
          mMaxFrames = static_cast<int>(fps);
  ```

  - 其中, 成员变量 `mMinFrames` 和 `mMaxFrames` 是在 `include/Tracking.h` 中定义的

  ```c++
          // New KeyFrame rules (according to fps)
          // 新建关键帧和重定位中用来判断最小最大时间间隔, 和帧率有关
          int mMinFrames;
          int mMaxFrames;
  ```

- ### 8. 参数输出

  ```c++
          // Step 1-3 输出
          cout << endl << "Camera Parameters: " << endl;
          cout << "- fx: " << fx << endl;
          cout << "- fy: " << fy << endl;
          cout << "- cx: " << cx << endl;
          cout << "- cy: " << cy << endl;
          cout << "- k1: " << DistCoef.at<float>(0) << endl;
          cout << "- k2: " << DistCoef.at<float>(1) << endl;
          if(DistCoef.rows==5)
              cout << "- k3: " << DistCoef.at<float>(4) << endl;
          cout << "- p1: " << DistCoef.at<float>(2) << endl;
          cout << "- p2: " << DistCoef.at<float>(3) << endl;
          cout << "- fps: " << fps << endl;
  ```

- ### 9. 获取图像的颜色通道顺序

  ```c++
          // 1:RGB 0:BGR
          int nRGB = fSettings["Camera.RGB"];
          // RGB 图像的颜色通道顺序
          mbRGB = nRGB;
  
          if(mbRGB)
              cout << "- color order: RGB (ignored if grayscale)" << endl;
          else
              cout << "- color order: BGR (ignored if grayscale)" << endl;
  ```

  - 其中, 成员变量 `mbRGB` 是在 `include/Tracking.h` 中定义的

  ```c++
          // RGB 图像的颜色通道顺序
          // Color order (true RGB, false BGR, ignored if grayscale)
          bool mbRGB;
  ```

- ### 10. 加载 ORB 特征点有关的参数

  ```c++
          // Step 2 加载 ORB 特征点有关的参数, 并新建特征点提取器
          // Load ORB parameters
  
          // 每一帧提取的特征点数 1000
          int nFeatures = fSettings["ORBextractor.nFeatures"];
          // 图像建立金字塔时的变化尺度 1.2
          float fScaleFactor = fSettings["ORBextractor.scaleFactor"];
          // 尺度金字塔的层数 8
          int nLevels = fSettings["ORBextractor.nLevels"];
          // 提取FAST特征点的默认阈值 20
          int fIniThFAST = fSettings["ORBextractor.iniThFAST"];
          // 如果默认阈值提取不出足够的 FAST 特征点, 则使用最小阈值 8
          int fMinThFAST = fSettings["ORBextractor.minThFAST"];
  ```

- ### 11. 特征点提取器实例化

  - `Tracking` 过程都会用到 `mpORBextractorLeft` 作为特征点提取器
 
  - 如果是双目, `Tracking` 过程中还会用到 `mpORBextractorRight` 作为右目特征点提取器
 
  - 在单目初始化的时候, 会用 `mpIniORBextractor` 来作为特征点提取器

  ```c++
          // Tracking 过程都会用到 mpORBextractorLeft 作为特征点提取器
          mpORBextractorLeft = new ORBextractor(nFeatures,fScaleFactor,nLevels,fIniThFAST,fMinThFAST);
  
          // 如果是双目, Tracking 过程中还会用到 mpORBextractorRight 作为右目特征点提取器
          if(sensor==System::STEREO)
              mpORBextractorRight = new ORBextractor(nFeatures,fScaleFactor,nLevels,fIniThFAST,fMinThFAST);
  
          // 在单目初始化的时候, 会用 mpIniORBextractor 来作为特征点提取器
          if(sensor==System::MONOCULAR)
              mpIniORBextractor = new ORBextractor(2*nFeatures,fScaleFactor,nLevels,fIniThFAST,fMinThFAST);
  ```

  - 其中, 成员变量 `mpORBextractorLeft`, `mpORBextractorRight` 和 `mpIniORBextractor` 是在 `include/Tracking.h` 中定义的

  ```c++
          // 作者自己编写和改良的 ORB 特征点提取器
          // ORB
          ORBextractor* mpORBextractorLeft, *mpORBextractorRight;
          // 在初始化的时候使用的特征点提取器, 其提取道德特征点个数会更多
          ORBextractor* mpIniORBextractor;
  ```

- ### 12. 输出 ORB 特征点提取的相关参数

  ```c++
          cout << endl  << "ORB Extractor Parameters: " << endl;
          cout << "- Number of Features: " << nFeatures << endl;
          cout << "- Scale Levels: " << nLevels << endl;
          cout << "- Scale Factor: " << fScaleFactor << endl;
          cout << "- Initial Fast Threshold: " << fIniThFAST << endl;
          cout << "- Minimum Fast Threshold: " << fMinThFAST << endl;
  ```

- ### 13.

  ```c++
          if(sensor==System::STEREO || sensor==System::RGBD)
          {
              // 判断一个 3D 点远/近的阈值 mbf * 35 / fx
              // ThDepth 其实就是表示基线长度的多少倍
              mThDepth = mbf*(float)fSettings["ThDepth"]/fx;
              cout << endl << "Depth Threshold (Close/Far Points): " << mThDepth << endl;
          }
  
          if(sensor==System::RGBD)
          {
              // 深度相机 disparity 转化为 depth 时的因子
              mDepthMapFactor = fSettings["DepthMapFactor"];
              if(fabs(mDepthMapFactor)<1e-5)
                  mDepthMapFactor=1;
              else
                  mDepthMapFactor = 1.0f/mDepthMapFactor;
          }
  ```

  - 其中, 成员变量 `mThDepth` 和 `mDepthMapFactor` 是在 `include/Tracking.h` 中定义的

  ```c++
          // 用于区分远点和金点的阈值, 近点认为可信度比较高, 远点则要求在两个关键帧中得到匹配
          // Threshold close/far points.
          // Points seen as close by the stereo/RGBD sensor are considered reliable and inserted from just one frame.
          // Far points requiere a match in two keyframes.
          float mThDepth;
  
          // 深度缩放因子, 链接深度值和具体深度值的参数, 只对 RGBD 输入有效
          // For RGB-D inputs only. For some datasets (e.g. TUM) the depthmap values are scaled.
          float mDepthMapFactor;
  ```
