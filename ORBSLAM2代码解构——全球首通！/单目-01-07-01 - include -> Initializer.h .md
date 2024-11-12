# 跳转到 include/Initializer.h

- 跟 `单目-01-01` 里的操作类似, 目前不用阅读 `Initializer` 类的构造函数, 因为暂时还没有调用, 所以目前暂时不用进行代码的解析


## 重头开始构建 ORBSLAM2

- 如果是从零开始构建 `ORBSLAM2` 系统, 就按照下面给出的文件内容进行代码的编写


- ### 1. include/Initializer.h

  - Build from scratch - Changed 0
 
  - 其实这里就是定义了一个空的 `Initializer` 类
 
  ```c++
  #ifndef INITIALIZER_H
  #define INITIALIZER_H
  
  
  // 单目初始化部分的声明, 双目和 RGBD 输入的情况下, 不会使用这个类
  
  
  namespace ORB_SLAM2
  {
  
      // 单目 SLAM 初始化相关, 双目和 RGBD 不会使用这个类
      // THIS IS THE INITIALIZER FOR MONOCULAR SLAM. NOT USED IN THE STEREO OR RGBD CASE.
      class Initializer
      {
  
      };
  
  }
  
  #endif //INITIALIZER_H
  
  ```


- ### 2. include/Tracking.h

  - Build from scratch - Changed 2
 
  - 文件开头加上:
 
  ```c++
  #include "Initializer.h"
  ```

  - 然后加上成员变量 `mpInitializer` 的声明, 实际上是一个 `Initializer` 类的指针, 但并未分配内存或调用构造函数
  
  ```c++
          // 单目初始器
          // Initalization (only for monocular)
          Initializer* mpInitializer;
  ```

  - 完整代码

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
  #include "Initializer.h"
  
  
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
  
          // 单目初始器
          // Initalization (only for monocular)
          Initializer* mpInitializer;
  
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


- ### 3. src/Tracking.cc

  - Build from scratch - Changed 1
 
  - 在 `成员变量初始化列表` 中加上:
 
  ```c++
          mpInitializer(static_cast<Initializer*>(nullptr))
  ```

  - 完整代码

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
          mpKeyFrameDB(pKFDB), mpInitializer(static_cast<Initializer*>(nullptr)), mpSystem(pSys), mpViewer(nullptr),
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
