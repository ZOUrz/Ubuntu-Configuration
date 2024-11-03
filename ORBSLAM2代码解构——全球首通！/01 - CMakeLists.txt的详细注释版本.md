# CMakeLists.txt的详细注释版本

### 对CMakeLists.txt的每一行语句进行了注释, 解释了其含义和作用, 有助于理清ORBSLAM2整体的项目文件框架和结构, 有助于后续对ORBSLAM2的代码进行更改

```cmake
# 指定 CMake 的最低版本要求为2.8
cmake_minimum_required(VERSION 2.8)
# 定义一个名为 ORB_SLAM2 的项目
project(ORB_SLAM2)

# 检查 CMAKE_BUILD_TYPE 是否被定义, 如果没有, 则将其设置为 Release
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

# 设置 C 和 C++ 编译器的 Flags
# -Wall: 开启所有警告, -03: 进行最高级别的优化, -march=native: 优化代码以适应当前的处理器架构
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS}  -Wall  -O3 -march=native ")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall   -O3 -march=native")

# Check C++11 or C++0x support
# 引入 CheckCXXCompilerFlag 模块, 用于检查编译器是否支持特定的 C++ Flag
include(CheckCXXCompilerFlag)
# 检查编译器是否支持 C++11(-std=c++11) 和 C++0x(-std=c++0x)
# 这两个检查的结果将分别存储在 COMPILER_SUPPORTS_CXX11 和 COMPILER_SUPPORTS_CXX0X
CHECK_CXX_COMPILER_FLAG("-std=c++11" COMPILER_SUPPORTS_CXX11)
CHECK_CXX_COMPILER_FLAG("-std=c++0x" COMPILER_SUPPORTS_CXX0X)
# 如果支持 C++11, 则将 C++ 编译 Flag 设置为 -std=c++11, 并定义一个宏 COMPILEDWITHC11
# 如果不支持 C++11但支持 C++0x, 则将 C++编译 Flag设置为 -std=c++0x, 定义 COMPILEDWITHC0X
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

# 将 ${PROJECT_SOURCE_DIR}/cmake_modules 添加到 CMake 模块搜索路径中, 使得 CMake 可以在该目录下查找自定义的 CMake 模块
# ORBSLAM2 项目中自定义了 FindEigen3.cmake, 该文件存放于项目路径内的 cmake_modules 文件夹中
# 将该目录添加到 CMake 搜索路径中, 则 CMake 可以在构建过程中找到并使用这些自定义模块
LIST(APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake_modules)

# find_package 会在系统的标准路径和用户指定的路径中查找指定的库或包, 它会搜索库的头文件和二进制文件(如共享库或静态库), 并根据指定版本要求进行匹配
# 尝试查找 OpenCV 库, 要求版本至少为 3.0, QUIET 表示在没有找到库时不会输出警告信息
find_package(OpenCV 3.0 QUIET)
# 如果第一个未找到 OpenCV, 则尝试查找版本为 2.4.3 的 OpenCV, 如果仍未找到, 则输出致命错误信息, 终止构建过程
if(NOT OpenCV_FOUND)
   find_package(OpenCV 2.4.3 QUIET)
   if(NOT OpenCV_FOUND)
      message(FATAL_ERROR "OpenCV > 2.4.3 not found.")
   endif()
endif()

# 查找 Eigen3 和 Pangolin 库, REQUIRED 表示如果找不到这些库, CMake 会报错并终止构建
find_package(Eigen3 3.1.0 REQUIRED)
find_package(Pangolin REQUIRED)

# include_directories 用于指定编译器在编译源文件时查找头文件的目录
# 这些目录的路径会被添加到编译器的搜索路径中, 当编译器遇到 #include 指令时, 会在这些目录中查找所需的头文件
# 指定要包含的头文件目录:
include_directories(
        ${PROJECT_SOURCE_DIR}  # 项目的根目录
        ${PROJECT_SOURCE_DIR}/include  # 项目的 include 目录, 通常用于存放公共头文件
        ${EIGEN3_INCLUDE_DIR}  # Eigen3 库的头文件目录
        ${Pangolin_INCLUDE_DIRS}  # Pangolin 库的头文件目录
)

# 设置库文件的输出目录为 ${PROJECT_SOURCE_DIR}/lib, 即编译生成的共享库将存放在该目录中
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/lib)

# 创建一个名为 ${PROJECT_SOURCE_DIR} 的共享库( SHARED 表示生成动态链接库), 并将指定的源文件添加到库中
add_library(${PROJECT_NAME} SHARED
        src/System.cc
        src/Tracking.cc
        src/LocalMapping.cc
        src/LoopClosing.cc
        src/ORBextractor.cc
        src/ORBmatcher.cc
        src/FrameDrawer.cc
        src/Converter.cc
        src/MapPoint.cc
        src/KeyFrame.cc
        src/Map.cc
        src/MapDrawer.cc
        src/Optimizer.cc
        src/PnPsolver.cc
        src/Frame.cc
        src/KeyFrameDatabase.cc
        src/Sim3Solver.cc
        src/Initializer.cc
        src/Viewer.cc
)

# 指定 ${PROJECT_SOURCE_DIR} 库链接的其他库
target_link_libraries(${PROJECT_NAME}
        ${OpenCV_LIBS}  # OpenCV 库
        ${EIGEN3_LIBS}  # Eigen3 库
        ${Pangolin_LIBRARIES}  # Pangolin 库
        # 还链接了位于 Thirdparty/DBoW2 和 Thirdparty/g2o 的第三方库
        ${PROJECT_SOURCE_DIR}/Thirdparty/DBoW2/lib/libDBoW2.so
        ${PROJECT_SOURCE_DIR}/Thirdparty/g2o/lib/libg2o.so
)

# Build examples

# 设置可执行文件的输出目录为 ${PROJECT_SOURCE_DIR}/Examples/RGB-D
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/Examples/RGB-D)
# 创建一个名为 rgbd_tum 的可执行文件, 并指定其源文件为 Examples/RGB-D/rgbd_tum.cc
add_executable(rgbd_tum Examples/RGB-D/rgbd_tum.cc)
# 将 rgbd_tum 可执行文件链接到 ${PROJECT_SOURCE_DIR} 库, 使得可执行文件可以使用库中的功能
target_link_libraries(rgbd_tum ${PROJECT_NAME})

# 以下代码也是相同的逻辑
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/Examples/Stereo)
add_executable(stereo_kitti Examples/Stereo/stereo_kitti.cc)
target_link_libraries(stereo_kitti ${PROJECT_NAME})
add_executable(stereo_euroc Examples/Stereo/stereo_euroc.cc)
target_link_libraries(stereo_euroc ${PROJECT_NAME})

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/Examples/Monocular)
add_executable(mono_tum Examples/Monocular/mono_tum.cc)
target_link_libraries(mono_tum ${PROJECT_NAME})
add_executable(mono_kitti Examples/Monocular/mono_kitti.cc)
target_link_libraries(mono_kitti ${PROJECT_NAME})
add_executable(mono_euroc Examples/Monocular/mono_euroc.cc)
target_link_libraries(mono_euroc ${PROJECT_NAME})

```
