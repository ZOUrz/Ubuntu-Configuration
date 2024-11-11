# 跳转到 include/Tracking.h

- 目前先不用阅读 `Tracking` 类的构造函数, 因为暂时还没有调用, 所以就不用解析代码了


## 重头开始构建 ORBSLAM2

- 如果是从零开始构建 `ORBSLAM2` 系统, 就按照下面给出的文件内容进行代码的编写


- ### 1. include/Tracking

  - Build from scratch - Changed 0
 
  - 定义了 `Tracking` 类, 并定义了枚举类型 `eTrackingState`
 
  ```c++
  #ifndef TRACKING_H
  #define TRACKING_H
  
  
  #include<opencv2/core/core.hpp>
  #include<opencv2/features2d/features2d.hpp>
  
  #include "System.h"
  #include"Viewer.h"
  #include"KeyFrameDatabase.h"
  #include"Map.h"
  #include"FrameDrawer.h"
  
  
  #include "ORBVocabulary.h"
  
  
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
  
        };
  
  }
  
  #endif //TRACKING_H
  
  ```


- ### 2. include/FrameDrawer.h

  - Build from scratch - Changed 1
 
  - 文件开头加上:

  ```c++
  #include "Tracking.h"
  ```

  - 完整代码

  ```c++
  #ifndef FRAMEDRAWER_H
  #define FRAMEDRAWER_H
  
  #include "Map.h"
  #include "Tracking.h"
  
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



  

