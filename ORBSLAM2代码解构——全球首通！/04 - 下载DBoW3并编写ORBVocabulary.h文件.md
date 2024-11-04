# include/ORBVocabulary.h

### src/System.cc

前一步卡在src/System.cc文件里的代码

```c++
        // 建立一个新的ORB字典
        mpVocabulary = new ORBVocabulary();
```

### include/System.h

在include/System.h里定义成员变量mpVocabulary

```c++
        // ORB vocabulary used for place recognition and feature matching.
        // 一个指向ORB字典的指针
        ORBVocabulary* mpVocabulary;
```

### include/ORBVocabulary.h

ORBVocabulary是在include/ORBVocabulary.h里定义的

```c++
#ifndef VOCABULARY_H
#define VOCABULARY_H

#include "Thirdparty/DBoW3/src/DBoW3.h"

namespace ORB_SLAM2
{
    typedef DBoW3::Vocabulary ORBVocabulary;
}

#endif //VOCABULARY_H
```

ORBSLAM2源码使用的时DBoW2, 并且是经过作者修改的, 因此适配性比较差, 所以我选择使用DBoW3这个库

### Thirdparth/DBoW3

需要下载DBoW3到Thirdparty文件夹内, 然后删除utils文件夹和orboc.dbow3文件

然后修改DBoW3的CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 2.8)
project(DBoW3)

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS}  -Wall  -O3 -march=native ")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall   -O3 -march=native")

set(HDRS_DBOW3
        src/BowVector.h
        src/Database.h
        src/DBoW3.h
        src/DescManip.h
        src/exports.h
        src/FeatureVector.h
        src/QueryResults.h
        src/quicklz.h
        src/ScoringObject.h
        src/timers.h
        src/Vocabulary.h
)
set(SRCS_DBOW3
        src/BowVector.cpp
        src/Database.cpp
        src/DescManip.cpp
        src/FeatureVector.cpp
        src/QueryResults.cpp
        src/quicklz.c
        src/ScoringObject.cpp
        src/Vocabulary.cpp
)

find_package(OpenCV 3.0 QUIET)
if(NOT OpenCV_FOUND)
    find_package(OpenCV 2.4.3 QUIET)
    if(NOT OpenCV_FOUND)
        message(FATAL_ERROR "OpenCV > 2.4.3 not found.")
    endif()
endif()

set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/lib)

include_directories(${OpenCV_INCLUDE_DIRS})
add_library(DBoW3 SHARED ${SRCS_DBOW3})
target_link_libraries(DBoW3 ${OpenCV_LIBS})

```

然后编写 build.sh 文件

```shell
echo "Configuring and buildding Thirdparty/FBoW ..."

cd Thirdparty/DBoW3
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j

cd ../../../

echo "Configuring and building ORB_SLAM2 ..."

mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j

```

在项目的 CMakeLists.txt 文件中要修改以下这段代码

```cmake
# 指定${PROJECT_SOURCE_DIR}库链接的其他库
target_link_libraries(${PROJECT_NAME}
        ${OpenCV_LIBS}  # OpenCV库
        ${EIGEN3_LIBS}  # Eigen3库
        ${Pangolin_LIBRARIES}  # Pangolin库
        # 还链接了位于Thirdparty/DBoW2和Thirdparty/g2o的第三方库
        ${PROJECT_SOURCE_DIR}/Thirdparty/DBoW3/lib/libDBoW3.so
        #${PROJECT_SOURCE_DIR}/Thirdparty/g2o/lib/libg2o.so
)
```

然后再进行编译, 在终端依次输入

```
chmod +x build.sh
./build.sh
```

后续对代码进行修改后, 需要重新执行上面的命令才能正确执行修改后的代码

### 修改src/System.cc

```c++
// 主进程的实现文件

#include <iostream>
#include <opencv2/core/core.hpp>  // 在System.h已经include了

#include "System.h"


using namespace std;


namespace ORB_SLAM2
{
    // 系统的构造函数, 将会启动其他的线程
    // 第一个System是类名, 表示这是ORB_SLAM2::System类的构造函数
    // 第二个System是构造函数的名称, 必须与类名相同
    // 构造函数的参数如下: 词典文件路径, 配置文件路径, 传感器类型, 是否使用可视化界面
    System::System(const string &strVocFile, const string &strSettingsFile,
                   eSensor sensor, bool bUseViewer):
                   // 在构造函数体内, 成员初始化列表用于初始化类的成员变量
                   // 在构造函数执行前设置变量的初始值, 比在构造函数体内赋值更高效
                   mSensor(sensor), mpViewer(static_cast<Viewer*>(nullptr)), mbReset(false),
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
        catch (const exception &e)
        {
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

然后卡在了以下这段代码, 需要进行跳转

```c++
        // Create KeyFrame Database
        mpKeyFrameDatabase = new KeyFrameDatabase(*mpVocabulary);
```


