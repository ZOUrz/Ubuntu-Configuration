# 跳转到 src/KeyFrameDatabase.cc 阅读 KeyFrameDatabase 类构造函数的具体实现

- `KeyFrameDatabase` 类的构造函数就几行代码, 比较简单

- 重点是其中的成员变量 `mvInvertedFile`


## 重点代码逐行解析


- ### 1. 构造函数

    ```c++
        // 构造函数
        KeyFrameDatabase::KeyFrameDatabase (const ORBVocabulary &voc):
            mpVoc(&voc)
        {
            // 数据库的主要内容
            mvInvertedFile.resize(voc.size());
        }
    ```

    - 其中, 构造函数以及其成员变量是在 `include/KeyFrameDatabase.h` 中声明的

    ```c++
            // 构造函数
            explicit KeyFrameDatabase(const ORBVocabulary &voc);
    ```
    
    ```c++
            // 预先训练好的词典
            // Associated vocabulary
            const ORBVocabulary* mpVoc;
    
            // 倒排索引, mvInvertedFile[i] 表示包含了第 i 个 word id 的所有关键帧
            // Inverted file
            std::vector<std::list<KeyFrame*>> mvInvertedFile;
    ```

- ### 2. protected 与 private 的区别

    - 在 `KeyFrameDatabase.h` 中, 其成员变量被设为 `protected`, 以下是 `protected` 和 `private` 的区别:

    - 在 `C++` 中, `protected` 和 `private` 是访问控制修饰符，用来控制类成员(变量, 函数等)对外部代码的可访问性, 它们的区别如下：

        - 1. `private` (私有成员)
            - 访问限制: `private` 成员只能在类的内部被访问, 无法在类的外部或继承类中访问
        - 2. protected(受保护成员)
            - 访问限制: `protected` 成员只能在类的内部和派生类中访问, 但无法在类的外部直接访问


## 需要进行跳转阅读的位置


- ### 1. mvInvertedFile[i]

    ```c++
            // 倒排索引, mvInvertedFile[i] 表示包含了第 i 个 word id 的所有关键帧
            // Inverted file
            std::vector<std::list<KeyFrame*> > mvInvertedFile;
    ```

    - 其中, `std::vector<std::list<KeyFrame*>>` 是一个 `vector` 容器, 其每个元素都是一个 `list`, 而这个 `list` 存储的是指向 `KeyFrame` 类型对象的指针
 
    - 由于 `mvInvertedFile` 只定义了一个存放指针的容器, 并没有实际创建 `KeyFrame` 对象，因此在这行代码中并没有调用 `KeyFrame` 的构造函数

    - `mvInvertedFile` 只是声明了一个向量和链表的结构, 存储的是 `KeyFrame` 类型的指针, 并不会触发 `KeyFrame` 实例的创建
 
    - 因此这行代码不会调用 `KeyFrame` 类的构造函数, 因此只需要跳转到 `include/KeyFrame.h` 查看


## 重头开始构建 ORBSLAM2

- 如果是从零开始构建 `ORBSLAM2` 系统, 就按照下面给出的文件内容进行代码的编写

- ### 1. include/KeyFrameDatabase.h

    - Build from scratch - Changed 0

    ```c++
    #ifndef KEYFRAMEDATABASE_H
    #define KEYFRAMEDATABASE_H
        
    #include "ORBVocabulary.h"
    
    namespace ORB_SLAM2
    {
        // 要用到的其他类的前向声明
        // 在该项目代码中，类之间可能存在复杂的相互依赖关系
        // 例如, System 类可能需要引用 Viewer 类, 而 Viewer 类可能又引用 System 类, 前向声明能够打破这种直接的依赖关系
        // 如果不使用前向声明, 而直接包含头文件, 可能会导致头文件之间的循环依赖, 进而导致编译错误或头文件包含的死循环
        // 通过前向声明, 编译器不会立即要求完整定义, 只需要一个简单的类声明, 防止了这些问题
        class KeyFrame;
        class Frame;

        // 关键帧数据库
        class KeyFrameDatabase
        {
        public:
    
            // 构造函数
            explicit KeyFrameDatabase(const ORBVocabulary &voc);
    
            // 允许类内部和派生类访问, 但不允许外部访问
        protected:
    
            // 预先训练好的词典
            // Associated vocabulary
            const ORBVocabulary* mpVoc;
    
            // 倒排索引, mvInvertedFile[i] 表示包含了第 i 个 word id 的所有关键帧
            // Inverted file
            std::vector<std::list<KeyFrame*>> mvInvertedFile;
    
        };
    
    }
    
    #endif //KEYFRAMEDATABASE_H
    
    ```

- ### 2. src/KeyFrameDatabase.cc

    - Build from scratch - Changed 0

    ```c++
    // 关键帧数据库, 用于回环检测和重定位
    
    #include "KeyFrameDatabase.h"
    
    using namespace std;
    
    namespace ORB_SLAM2
    {
    
        // 构造函数
        KeyFrameDatabase::KeyFrameDatabase (const ORBVocabulary &voc):
            mpVoc(&voc)
        {
            // 数据库的主要内容
            mvInvertedFile.resize(voc.size());
        }
    }
    ```

- ### 3. include/System.h

    - Build from scratch - Changed 3
 
    - 文件开头加上
 
    ```c++
    #include "KeyFrameDatabase.h"
    ```

    - 然后添加成员变量
 
    ```
            // 关键帧数据库的指针, 这个数据库用于重定位和回环检测
            // KeyFrame database for place recognition (relocalization and loop detection).
            KeyFrameDatabase* mpKeyFrameDatabase;
    ```

    - 完整代码

    ```c++
    #ifndef SYSTEM_H
    #define SYSTEM_H
    
    
    #include <mutex>
    
    #include "Viewer.h"
    #include "ORBVocabulary.h"
    #include "KeyFrameDatabase.h"
    
    
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

- ### 4. src/System.cpp

    - Build from scratch - Changed 3
     
    - 在代码最后加上:
 
    ```c++
            // Create KeyFrame Database
            mpKeyFrameDatabase = new KeyFrameDatabase(*mpVocabulary);
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
    
        }
    
    }
    
    ```

- ### 5. CMakeLists.txt

    - Build from scratch - Changed 2

    - 在文件以下位置进行修改, 将 `KeyFrameDatabase.cc` 源文件添加到库中
 
    ```cmake
    # 创建一个名为${PROJECT_SOURCE_DIR}的共享库(SHARED表示生成动态链接库), 并将指定的源文件添加到库中
    add_library(${PROJECT_NAME} SHARED
            src/System.cpp
            src/KeyFrameDatabase.cpp
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
