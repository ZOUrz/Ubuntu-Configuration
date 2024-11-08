# include/SPVocabulary.h


## 重点代码逐行解析


- ### 1. include DBoW3

    - 注意, `SuperPoint + ORBSLAM2` 这个项目使用的是 `DBoW3`, 而 `ORBSLAM2` 源码使用的是 `DBoW2`
 
    - 如果是从头开始写的话, 是要注意把 `DBoW3` 的源码放在文件夹 `Thirdparty` 里, 而且要修改 `DBoW3` 的 `CMakeLists` 以及 整个项目的 `CMakeList`

    ```c++
    // 这个项目使用的是 DBoW3, ORBSLAM2 源码使用的是 DBoW2
    // 因为 DBoW3 对于 OpenCV3 的兼容性较好, 且编译和使用都比较容易上手, 也适用于那些使用其他特征点替代 ORB 特征点的项目
    // ORBSLAM2 源码中的 DBoW2 是经过作者修改的, 修改起来比较麻烦
    #include "Thirdparty/DBoW3/src/DBoW3.h"
    ```


- ### 2. 设置 Vocabulary 类的别名

    - `DBoW3::Vocabulary` 是 `DBoW3` 库中的一个类, 用于表示一个词汇表, 常用于视觉特征的匹配和查询

    - 使用 `typedef`, 将 `SPVocabulary` 设置为 `DBoW3::Vocabulary` 的别名, 方便后续使用

    - 使用第二个 `typedef`, 将 `ORBVocabulary` 设置为 `SPVocabulary` 的别名, 实际上 `ORBVocabulary` 也是 `DBoW3::Vocabulary` 的别名

    - 实际上, 作者一开始可能只是想将 `SPVocabulary` 定义为 `DBoW3::Vocabulary` 的别名, 但 `ORBSLAM2` 的代码中大量使用了 `ORBVocabulary` 这个类名, 为了减少修改的工作量, 所以才这样写, 也可以只设置 `SPVocabulary`, 但是需要将整个项目用到 `ORBVocabulary` 的地方全部进行替换

    ```c++
        // 定义了 SPVocabulary 为 DBoW3::Vocabulary 类型的别名
        typedef DBoW3::Vocabulary SPVocabulary;
    
        // 定义了 ORBVocabulary 为 SPVocabulary 类型的别名
        typedef SPVocabulary ORBVocabulary;
    ```


## 完整代码

```c++
#ifndef VOCABULARY_H
#define VOCABULARY_H

// #include"Thirdparty/DBoW2/DBoW2/FSP.h"
// #include"Thirdparty/DBoW2/DBoW2/TemplatedVocabulary.h"

// 这个项目使用的是 DBoW3, ORBSLAM2 源码使用的是 DBoW2
// 因为 DBoW3 对于 OpenCV3 的兼容性较好, 且编译和使用都比较容易上手, 也适用于那些使用其他特征点替代 ORB 特征点的项目
// ORBSLAM2 源码中的 DBoW2 是经过作者修改的, 修改起来比较麻烦
#include "Thirdparty/DBoW3/src/DBoW3.h"

namespace ORB_SLAM2
{

    // typedef DBoW2::TemplatedVocabulary<DBoW2::FSP::TDescriptor, DBoW2::FSP> SPVocabulary;

    // 定义了 SPVocabulary 为 DBoW3::Vocabulary 类型的别名
    typedef DBoW3::Vocabulary ORBVocabulary;
    
} //namespace ORB_SLAM

#endif //VOCABULARY_H
```


## 重头开始构建 ORBSLAM2

- 如果需要从零开始构建 `ORBSLAM2` 系统, 就按照下面给出的文件内容进行代码的编写

- `ORBSLAM2` 源码使用的是 `DBoW2`, 并且是经过作者修改的, 因此适配性比较差, 所以选择使用 `DBoW3`

- ### 1. DBoW3

    - #### 1.1 下载源码

        - 需要下载 `DBoW3` 的源码到 `Thirdparty` 文件夹内, 然后源码中删除 `utils` 文件夹和 `orbvoc.dbow3文件
 
    - #### 1.2 修改 CMakeLists.txt

        - 然后修改 `DBoW3` 的 `CMakeLists.txt` 

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

- ### 2. build.sh

    - 编写 `build.sh` 文件
 
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



