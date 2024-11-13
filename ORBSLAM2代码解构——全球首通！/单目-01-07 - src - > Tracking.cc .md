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


- ### 13. 计算 mThDepth 和 mDepthMapFactor

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


## 需要进行跳转阅读的位置

  - 在 `Tracking.cc` 文件的 `Tracking` 类构造函数中, 所调用的来自其他文件定义的类


- ### 1. 初始化器

  ```
          mpInitializer(static_cast<Initializer*>(nullptr))
  ```

  - 在这行代码中, `mpInitializer` 是一个指向 `Initializer` 对象的指针, 将 `nullptr` (空指针)转换为 `Initializer` 类型, 这样可以显式地将 `mpInitializer` 初始化为 `nullptr`

  - 所以这行代码并没有创建 `Initializer` 实例, 因此不会调用其构造函数, 因此只需要跳转到 `include/Initializer.h` 查看


- ### 2. 特征点提取器

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

  - 这三行代码同样都使用了 `new` 关键字来创建 `ORBextractor` 对象, 并将其指针存储在成员指针变量 `mpORBextractorLeft`, `mpORBextractorRight` 和 `mpIniORBextractor`, 并调用 `ORBextractor` 类的构造函数来初始化对象
 
  - 具体实现是在 `src/ORBextractor.cc` 里, 所以需要去到该文件里看看 `ORBextractor` 类构造函数的具体实现


## 重头开始构建 ORBSLAM2

- 如果是从零开始构建 `ORBSLAM2` 系统, 就按照下面给出的文件内容进行代码的编写


- ### 1. include/Tracking.h

  - Build from scratch - Changed 1
 
  - 添加了 `Tracking` 类的构造函数以及相应的成员变量
 
  - 这里就先不管成员变量 `mpORBextractorLeft`, `mpORBextractorRight`, `mpIniORBextractor` 和 `mpInitializer` 的声明, 先注释掉或者可以先不写
 
  ```c++
  #ifndef TRACKING_H
  #define TRACKING_H
  
  
  #include<opencv2/core/core.hpp>
  #include<opencv2/features2d/features2d.hpp>
  
  #include "System.h"
  #include "Viewer.h"
  #include "KeyFrameDatabase.h"
  #include "Map.h"
  #include "FrameDrawer.h"
  #include "MapDrawer.h"
  
  
  #include "ORBVocabulary.h"
  
  
  using namespace std;
  
  
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
      class LocalMapping;
      class LoopClosing;
      class System;
  
      class Tracking
      {
      public:
          // 构造函数
          // 构造函数的参数如下: 系统实例, BOW字典, 帧绘制器, 地图点绘制器, 地图句柄, 关键帧产生的词袋数据库, 配置文件路径, 传感器类型
          Tracking(System* pSys, ORBVocabulary* pVoc, FrameDrawer* pFrameDrawer, MapDrawer* pMapDrawer,
                   Map* pMap, KeyFrameDatabase* pKFDB, const string &strSettingPath, int sensor);
  
          // 跟踪状态类型
          // Tracking states
          enum eTrackingState
          {
              SYSTEM_NOT_READY=-1,  // 系统没有准备好的状态, 一般就是在启动后加载配置文件和词典文件时候的状态
              NO_IMAGES_YET=0,  // 当前无图像
              NOT_INITIALIZED=1,  // 有图像但是没有完成初始化
              OK=2,  // 正常时候的工作状态
              LOST=3  // 系统已经跟丢了的状态
          };
  
          // 跟踪状态
          eTrackingState mState;
  
          // 传感器类型: MONOCULAR, STEREO, RGBD
          // Input sensor
          int mSensor;
  
          // 标记当前系统是处于 SLAM 状态还是纯定位状态
          // True if local mapping is deactivated and we are performing only localization
          bool mbOnlyTracking;
  
      protected:
  
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
          ORBVocabulary *mpORBVocabulary;
          // 当前系统运行的时候, 关键帧所产生的数据库
          KeyFrameDatabase *mpKeyFrameDB;
  
          // 指向系统实例的指针
          // System
          System *mpSystem;
  
          // 可视化器相关
          // Drawers
          // 可视化器对象句柄
          Viewer *mpViewer;
          // 帧绘制器句柄
          FrameDrawer *mpFrameDrawer;
          // 地图绘制器句柄
          MapDrawer *mpMapDrawer;
  
          // (全局)地图句柄
          // Map
          Map *mpMap;
  
          // 相机的参数矩阵相关
          // Calibration matrix
          // 相机的内参数矩阵
          cv::Mat mK;
          // 相机的去畸变参数
          cv::Mat mDistCoef;
          // 相机的基线长度 * 相机的焦距
          float mbf;
  
          // New KeyFrame rules (according to fps)
          // 新建关键帧和重定位中用来判断最小最大时间间隔, 和帧率有关
          int mMinFrames;
          int mMaxFrames;
  
          // 用于区分远点和金点的阈值, 近点认为可信度比较高, 远点则要求在两个关键帧中得到匹配
          // Threshold close/far points.
          // Points seen as close by the stereo/RGBD sensor are considered reliable and inserted from just one frame.
          // Far points requiere a match in two keyframes.
          float mThDepth;
  
          // 深度缩放因子, 链接深度值和具体深度值的参数, 只对 RGBD 输入有效
          // For RGB-D inputs only. For some datasets (e.g. TUM) the depthmap values are scaled.
          float mDepthMapFactor;
  
          // 上一次重定位的那一帧的ID
          unsigned int mnLastRelocFrameId;
  
          // RGB 图像的颜色通道顺序
          // Color order (true RGB, false BGR, ignored if grayscale)
          bool mbRGB;
  
        };
  
  }
  
  #endif //TRACKING_H
  
  ```


- ### 2. src/Tracking.cc

  - Build from scratch - Changed 0

  ```c++
  // 追踪线程
  
  
  #include "Tracking.h"
  
  #include"Map.h"
  #include"FrameDrawer.h"
  
  //#include<mutex>
  //#include<iostream>
  #include <opencv2/core/core.hpp>
  #include <opencv2/features2d/features2d.hpp>
  
  
  using namespace std;
  
  namespace ORB_SLAM2
  {
  
      // 构造函数
      // 构造函数的参数如下: 系统实例, BOW字典, 帧绘制器, 地图点绘制器, 地图句柄, 关键帧产生的词袋数据库, 配置文件路径, 传感器类型
      Tracking::Tracking(System *pSys, ORBVocabulary* pVoc, FrameDrawer *pFrameDrawer, MapDrawer *pMapDrawer,
                         Map *pMap, KeyFrameDatabase* pKFDB, const string &strSettingPath, const int sensor):
          mState(NO_IMAGES_YET), mSensor(sensor), mbOnlyTracking(false), mbVO(false), mpORBVocabulary(pVoc),
          mpKeyFrameDB(pKFDB),
          mpSystem(pSys), mpViewer(nullptr),
          mpFrameDrawer(pFrameDrawer), mpMapDrawer(pMapDrawer), mpMap(pMap), mnLastRelocFrameId(0)
      {
          // Step 1 从配置文件中加载相机参数
          // Load camera parameters from settings file
          cv::FileStorage fSettings(strSettingPath, cv::FileStorage::READ);
          float fx = fSettings["Camera.fx"];
          float fy = fSettings["Camera.fy"];
          float cx = fSettings["Camera.cx"];
          float cy = fSettings["Camera.cy"];
  
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
  
          // 双目摄像头baseline * fx 50
          mbf = fSettings["Camera.bf"];
  
          float fps = fSettings["Camera.fps"];
          if(fps==0)
              fps=30;
  
          // Max/Min Frames to insert keyframes and to check relocalisation
          // 新建关键帧和重定位中用来判断最小最大时间间隔, 和帧率有关
          mMinFrames = 0;
          mMaxFrames = static_cast<int>(fps);
  
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
  
          // 1:RGB 0:BGR
          int nRGB = fSettings["Camera.RGB"];
          // RGB 图像的颜色通道顺序
          mbRGB = nRGB;
  
          if(mbRGB)
              cout << "- color order: RGB (ignored if grayscale)" << endl;
          else
              cout << "- color order: BGR (ignored if grayscale)" << endl;
  
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
  
          cout << endl  << "ORB Extractor Parameters: " << endl;
          cout << "- Number of Features: " << nFeatures << endl;
          cout << "- Scale Levels: " << nLevels << endl;
          cout << "- Scale Factor: " << fScaleFactor << endl;
          cout << "- Initial Fast Threshold: " << fIniThFAST << endl;
          cout << "- Minimum Fast Threshold: " << fMinThFAST << endl;
  
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
  
      }
  
  }
  
  ```


- ### 3. include/System.h

  - Build from scratch - Changed 7
   
  - 文件开头加上:
 
  ```c++
  #include "Tracking.h"
  ```

  - 然后添加成员变量

  ```c++
          // 追踪器, 除了进行运动追踪外还要负责创建关键帧, 创建新地图点和进行重定位的工作
          // Tracker. It receives a frame and computes the associated camera pose.
          // It also decides when to insert a new keyframe, create some new MapPoints and
          // performs relocalization if tracking fails.
          Tracking* mpTracker;
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
  #include "MapDrawer.h"
  #include "Tracking.h"
  
  
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
  
          // 追踪器, 除了进行运动追踪外还要负责创建关键帧, 创建新地图点和进行重定位的工作
          // Tracker. It receives a frame and computes the associated camera pose.
          // It also decides when to insert a new keyframe, create some new MapPoints and
          // performs relocalization if tracking fails.
          Tracking* mpTracker;
  
          // The viewer draws the map and the current camera pose. It uses Pangolin.
          // 查看器, 可视化界面
          Viewer* mpViewer;
  
          // 帧绘制器
          FrameDrawer* mpFrameDrawer;
          // 地图绘制器
          MapDrawer* mpMapDrawer;
  
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

  - Build from scratch - Changed 7
   
  - 在代码最后加上
 
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
          mpMapDrawer = new MapDrawer(mpMap, strSettingsFile);
  
          // 在本主进程中初始化追踪器
          // Initialize the Tracking thread
          // (it will live in the main thread of execution, the one that called this constructor)
          // Tracking 类的构造函数输入的参数如下: this, 字典, 帧绘制器, 地图绘制器, 地图, 关键帧地图, 配置文件路径, 传感器类型
          // this 代表 System 类的当前对象指针
          // 其作用为, Tracking 类的构造函数中的 pSys 参数会接收到 this，也就是当前 System 对象的指针
          // 通过将 this 作为参数传递给 Tracking，能获得 System 类实例的指针，从而可以在 Tracking 类的内部使用它
          mpTracker = new Tracking(this, mpVocabulary, mpFrameDrawer, mpMapDrawer,
                                   mpMap, mpKeyFrameDatabase, strSettingsFile, mSensor);
  
      }
  
  }
  
  ```


- ### 5. CMakeLists.txt

  - Build from scratch - Changed 6
 
  - 在文件以下位置进行修改, 将 Tracking.cc 源文件添加到库中
 
  ```cmake
  # 创建一个名为${PROJECT_SOURCE_DIR}的共享库(SHARED表示生成动态链接库), 并将指定的源文件添加到库中
  add_library(${PROJECT_NAME} SHARED
          src/System.cpp
          src/KeyFrameDatabase.cpp
          src/Map.cpp
          src/FrameDrawer.cpp
          src/MapDrawer.cpp
          src/Tracking.cpp
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
          src/KeyFrameDatabase.cpp
          src/Map.cpp
          src/FrameDrawer.cpp
          src/MapDrawer.cpp
          src/Tracking.cpp
  )
  
  # 指定${PROJECT_SOURCE_DIR}库链接的其他库
  target_link_libraries(${PROJECT_NAME}
          ${OpenCV_LIBS}  # OpenCV库
          ${EIGEN3_LIBS}  # Eigen3库
          ${Pangolin_LIBRARIES}  # Pangolin库
          # 还链接了位于Thirdparty/DBoW2和Thirdparty/g2o的第三方库
          ${PROJECT_SOURCE_DIR}/Thirdparty/DBoW3/lib/libDBoW3.so
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
