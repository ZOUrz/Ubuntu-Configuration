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


