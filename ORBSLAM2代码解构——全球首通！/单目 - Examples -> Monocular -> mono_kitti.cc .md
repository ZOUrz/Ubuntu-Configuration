# 从 Examples/Monocular/mono_kitti.cc 开始梳理代码

* 该文件是 `SuperPoint + ORBSLAM2` 系统在 `KITTI` 数据集上使用单目传感器进行定位的整体流程

* 我们先从这个文件开始阅读!


## 重点代码逐行解析


- ### LoadImages

    - 获取图像序列中每一张图像的路径和时间戳

    ```c++
    // 获取图像序列中每一张图像的路径和时间戳
    void LoadImages(const string &strPathToSequence, vector<string> &vstrImageFilenames, vector<double> &vTimestamps);
    ```

    - 这行代码是 `LoadImages` 函数的声明, 因此这个函数的具体实现在文件最后面, 所以需要在文件开头进行函数的声明, 否则在 `main` 里无法调用

    - `LoadImages` 函数的具体实现:

    ```c++
    // 获取图像序列中每一张图像的路径和时间戳
    void LoadImages(const string &strPathToSequence, vector<string> &vstrImageFilenames, vector<double> &vTimestamps)
    {
        // Step 1 读取时间戳文件
        ifstream fTimes;
        string strPathTimeFile = strPathToSequence + "/times.txt";
        fTimes.open(strPathTimeFile.c_str());
        while(!fTimes.eof())
        {
            string s;
            getline(fTimes,s);
            // 当该行不为空时执行
            if(!s.empty())
            {
                stringstream ss;
                ss << s;
                double t;
                ss >> t;
                // 保存时间戳
                vTimestamps.push_back(t);
            }
        }
    
        // Step 2 使用左目图像, 生成左目图像序列中每一张图像的文件名
        string strPrefixLeft = strPathToSequence + "/image_0/";
    
        //const int nTimes = vTimestamps.size();
        const int nTimes = static_cast<int>(vTimestamps.size());
        vstrImageFilenames.resize(nTimes);
    
        for(int i=0; i<nTimes; i++)
        {
            stringstream ss;
            ss << setfill('0') << setw(6) << i;
            vstrImageFilenames[i] = strPrefixLeft + ss.str() + ".png";
        }
    }
    ```


- ### 1. 输入参数检查

    - 检查输入参数个数是否足够, 对于 `mono_kitti.cc` 来说, 在终端命令行输入的参数为

    - ` ./mono_kitti 词典文件路径 配置文件路径 数据集路径`

    ```c++
        // Step 1 检查输入参数个数是否足够
        if(argc != 4)
        {
            cerr << endl << "Usage: ./mono_kitti path_to_vocabulary path_to_settings path_to_sequence" << endl;
            return 1;
        }
    ```


- ### 2. 加载图像和时间戳

    - 使用 `LoadImages` 函数, 获取图像序列中每张图像的文件路径以及对应的时间戳
 
    - 然后获取当前图像序列的图像数目

    ```c++
        // Step 2 加载图像
        // Retrieve paths to images
        // 图像序列的文件名, 字符串序列
        vector<string> vstrImageFilenames;
        // 时间戳
        vector<double> vTimestamps;
        LoadImages(string(argv[3]), vstrImageFilenames, vTimestamps);
    
        // 当前图像序列的图片数目
        // int nImages = vstrImageFilenames.size();
        int nImages = static_cast<int>(vstrImageFilenames.size());
    ```


- ### 3. 加载 SLAM 系统

    - 输入的参数如下: 输入的参数如下: `词典文件路径`, `配置文件路径`, `传感器类型`, `是否使用可视化界面`
 
    - 下面这行代码的作用是, 调用 `ORB-SLAM2` 中 `System` 类的构造函数，初始化一个名为 `SLAM` 的实例
 
    ```c++
        // Step 3 加载 SLAM 系统
        // Create SLAM system. It initializes all system threads and gets ready to process frames.
        // 输入的参数如下: 词典文件路径, 配置文件路径, 传感器类型, 是否使用可视化界面
        ORB_SLAM2::System SLAM(argv[1],argv[2],ORB_SLAM2::System::MONOCULAR,true);
    ```


- ### 4. 运行前准备

    - 变量 `vTimesTrack` 是为了保存追踪一帧图像(仅 `Tracker`)所花费的时间

    ```c++
        // Step 4 运行前准备
        // Vector for tracking time statistics
        // 统计追踪一帧耗时(仅 Tracker 线程)
        vector<float> vTimesTrack;
        vTimesTrack.resize(nImages);
    ```

- ### 5. SLAM 系统的主循环

    - 依次追踪图像序列中的每一张图像
 
    ```c++
        // Step 5 依次追踪图像序列中的每一张图像
        // Main loop
        cv::Mat im;
        for(int ni=0; ni<nImages; ni++)
    ```
    - #### 5.1 读取图像
         
        - 根据前面获得的图像文件名读取图像, 读取过程中不改变图像的格式

        ```c++
                // Step 5.1 根据前面获得的图像文件名读取图像, 读取过程中不改变图像的格式
                // Read image from file
                im = cv::imread(vstrImageFilenames[ni],CV_LOAD_IMAGE_UNCHANGED);
                double tframe = vTimestamps[ni];
        ```

    - #### 5.2 检查是否读取到图像

        - 图像的合法性检查

        ```c++
                // Step 5.2 图像的合法性检查
                if(im.empty())
                {
                    cerr << endl << "Failed to load image at: " << vstrImageFilenames[ni] << endl;
                    return 1;
                }
        ```

    - #### 5.3 开始计时

        - `std::chrono::steady_clock` 是 `C++11` 和 `C++14` 中的稳定计时器, 适用于测量时间间隔, 因为它不会受到系统时间的调整而影响

        ```c++
                // Step 5.3 开始计时
                std::chrono::steady_clock::time_point t1 = std::chrono::steady_clock::now();
        ```

    - #### 5.4 追踪当前图像

        - 调用了 `SLAM` 中的 `TrackMonocular` 函数, 其中, `SLAM` 是上面经过初始化后的 `System` 类实例

        - `im`: 这是当前帧的图像数据, 是 `cv::Mat` 类型

        - `tframe`: 这是该帧的时间戳(double 类型)

        ```c++
                // Step 5.4 追踪当前图像
                // Pass the image to the SLAM system
                SLAM.TrackMonocular(im,tframe);
        ```

    - #### 5.5 计算追踪一帧图像的耗时

        - 追踪完成, 停止当前帧的图像计时, 并计算追踪耗时
     
        ```c++
                // Step 5.5 追踪完成, 停止当前帧的图像计时, 并计算追踪耗时
                std::chrono::steady_clock::time_point t2 = std::chrono::steady_clock::now();
        
                double ttrack= std::chrono::duration_cast<std::chrono::duration<double> >(t2 - t1).count();
        
                // vTimesTrack[ni]=ttrack;
                vTimesTrack[ni] = static_cast<float>(ttrack);
        ```

    - #### 5.6 匹配图像采集时的时间间隔

        - 根据图像时间戳中记录的两张图像之间的时间和现在追踪当前图像所耗费的时间, 使得下一张图像能够按照时间戳被送入到 `SLAM` 系统中进行跟踪

        ```c++
                // Step 5.6 根据图像时间戳中记录的两张图像之间的时间和现在追踪当前图像所耗费的时间
                // 使得下一张图像能够按照时间戳被送入到 SLAM 系统中进行跟踪
                // Wait to load the next frame
                double T=0;
                if(ni<nImages-1)
                    T = vTimestamps[ni+1]-tframe;
                else if(ni>0)
                    T = tframe-vTimestamps[ni-1];
        
                if(ttrack<T)
                    // usleep((T - ttrack) * 1e6);
                    usleep(static_cast<unsigned int>((T-ttrack)*1e6));
        ```


- ### 6. 关闭 SLAM 系统

    - 如果所有图像都追踪完毕, 就终止当前的 `SLAM` 系统

    ```c++
        // Step 6 如果所有图像都追踪完毕, 就终止当前的 SLAM 系统
        // Stop all threads
        SLAM.Shutdown();
    ```


- ### 7. 计算平均耗时

    - 计算平均耗时
 
    ```c++
        // Step 7 计算平均耗时
        // Tracking time statistics
        sort(vTimesTrack.begin(),vTimesTrack.end());
        float totaltime = 0;
        for(int ni=0; ni<nImages; ni++)
        {
            totaltime+=vTimesTrack[ni];
        }
        cout << "-------" << endl << endl;
        cout << "median tracking time: " << vTimesTrack[nImages/2] << endl;
        cout << "mean tracking time: " << totaltime/nImages << endl;
    ```


- ### 8. 保存轨迹

    - 保存 TUM 格式的相机轨迹
    
    ```
        // Step 8 保存 TUM 格式的相机轨迹
        // Save camera trajectory
        SLAM.SaveKeyFrameTrajectoryTUM("KeyFrameTrajectory.txt"); 
    ```

整个看下来, 其实文件内的代码比较简单, 因为这只是一个将 `SLAM` 系统进行定位的步骤串起来的流程文件

因此我们需要重点关注的是, 在这个文件中, 调用了哪些在其他文件定义类和函数, 以及这些类的构造函授以及函数的具体实现


## 需要进行跳转阅读的位置


在 moni_kitti.cc 中, 所调用的来自其他文件的函数


- ### 1. 加载 SLAM 系统

    ```c++
        // Step 2 加载 SLAM 系统
        // Create SLAM system. It initializes all system threads and gets ready to process frames.
        // 输入的参数如下: 词典文件路径, 配置文件路径, 传感器类型, 是否使用可视化界面
        ORB_SLAM2::System SLAM(argv[1],argv[2],ORB_SLAM2::System::MONOCULAR,true);
    ```

    - 该 System 类的构造函数是在 `include/System.h` 里声明的

    ```c++
            // 构造函数, 用来初始化整个系统
            // 第一个 System 是类名, 表示这是 ORB_SLAM2::System 类的构造函数
            // 第二个 System 是构造函数的名称, 必须与类名相同
            // 构造函数的参数如下: 词典文件路径, 配置文件路径, 传感器类型, 是否使用可视化界面
            // Initialize the SLAM system. It launches the Local Mapping, Loop Closing and Viewer threads.
            System(const string &strVocFile, const string &strSettingsFile,
                   eSensor sensor, bool bUseViewer = true);
    ```

    - 具体实现是在 `src/System.cc` 里, 所以需要去到该文件里面看看 `System` 类的构造函数的具体实现


- ### 2.  对每一帧图像进行追踪

    ```c++
            // Step 4.4 追踪当前图像
            // Pass the image to the SLAM system
            SLAM.TrackMonocular(im,tframe);
    ```


- ### 3.  终止 SLAM 系统

    ```c++
        // Step 5 如果所有图像都追踪完毕, 就终止当前的 SLAM 系统
        // Stop all threads
        SLAM.Shutdown();
    ```


- ### 4. 保存轨迹

    ```c++
        // Step 7 保存 TUM 格式的相机轨迹
        // Save camera trajectory
        SLAM.SaveKeyFrameTrajectoryTUM("KeyFrameTrajectory.txt"); 
    ```


## 重头开始构建 ORBSLAM2

- 如果需要从零开始构建 `ORBSLAM2` 系统, 就按照下面给出的文件内容进行代码的编写 

- ### 1. mono_kitti.cc

    - Build from scratch - Changed 0

    - 先写到 "加载 `SLAM` 系统那一步即可"

    ```c++
    
    #include <fstream>
    #include <iomanip>
    #include <iostream>
    #include <opencv2/core/core.hpp>
    

    using namespace std;
    
    
    // 获取图像序列中每一张图像的路径和时间戳
    void LoadImages (const string &strPathToSequence, vector<string> &vstrImageFilenames, vector<double> &vTimestamps);
    
    
    int main(int argc, char **argv)
    {
        // Step 1 检查输入参数个数是否足够
        if(argc != 4)
        {
            cerr << endl << "Usage: ./mono_kitti path_to_vocabulary path_to_settings path_to_sequence" << endl;
            return 1;
        }
    
        // Step 2 加载图像
        // Retrieve paths to images
        // 图像序列的文件名, 字符串序列
        vector<string> vstrImageFilenames;
        // 时间戳
        vector<double> vTimestamps;
        LoadImages(string(argv[3]), vstrImageFilenames, vTimestamps);
    
        // 当前图像序列的图片数目
        // int nImages = vstrImageFilenames.size();
        int nImages = static_cast<int>(vstrImageFilenames.size());

    }
    
    
    // 获取图像序列中每一张图像的路径和时间戳
    void LoadImages(const string &strPathToSequence, vector<string> &vstrImageFilenames, vector<double> &vTimestamps)
    {
        // Step 1 读取时间戳文件
        ifstream fTimes;
        string strPathTimeFile = strPathToSequence + "/times.txt";
        fTimes.open(strPathTimeFile.c_str());
        while(!fTimes.eof())
        {
            string s;
            getline(fTimes,s);
            // 当该行不为空时执行
            if(!s.empty())
            {
                stringstream ss;
                ss << s;
                double t;
                ss >> t;
                // 保存时间戳
                vTimestamps.push_back(t);
            }
        }
    
        // Step 2 使用左目图像, 生成左目图像序列中每一张图像的文件名
        string strPrefixLeft = strPathToSequence + "/image_0/";
    
        //const int nTimes = vTimestamps.size();
        const int nTimes = static_cast<int>(vTimestamps.size());
        vstrImageFilenames.resize(nTimes);
    
        for(int i=0; i<nTimes; i++)
        {
            stringstream ss;
            ss << setfill('0') << setw(6) << i;
            vstrImageFilenames[i] = strPrefixLeft + ss.str() + ".png";
        }
    }
    ```


- ### 2. CMakeLists.txt

    - Build from scrath - Changed 0

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
    #target_link_libraries(mono_kitti ${PROJECT_NAME})
    #add_executable(mono_euroc Examples/Monocular/mono_euroc.cc)
    #target_link_libraries(mono_euroc ${PROJECT_NAME})
    
    ```
