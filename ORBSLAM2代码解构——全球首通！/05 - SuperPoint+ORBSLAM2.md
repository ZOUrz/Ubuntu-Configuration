```cmake
# Check C++14 support
include(CheckCXXCompilerFlag)

# Check if the compiler supports C++14 (-std=c++14)
CHECK_CXX_COMPILER_FLAG("-std=c++14" COMPILER_SUPPORTS_CXX14)

# Set the C++ compilation flag and define macros based on support
if(COMPILER_SUPPORTS_CXX11)
   set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++14")
   add_definitions(-DCOMPILEDWITHC14)
   message(STATUS "Using flag -std=c++14.")
else()
   message(FATAL_ERROR "The compiler ${CMAKE_CXX_COMPILER} has no C++14 support. Please use a different C++ compiler.")
endif()
```

### CMakeLists.txt

```cmake
# 引入 CheckCXXCompilerFlag 模块, 用于检查编译器是否支持特定的 C++ Flag
include(CheckCXXCompilerFlag)
# 检查编译器是否支持 C++17(-std=c++17), 检查结果存储在 COMPILER_SUPPORTS_CXX17
CHECK_CXX_COMPILER_FLAG("-std=c++17" COMPILER_SUPPORTS_CXX17)
# 如果支持 C++17, 则将 C++ 编译 Flag 设置为 -std=c++17, 并定义一个宏 COMPILEDWITHC17
if(COMPILER_SUPPORTS_CXX17)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++17")
    add_definitions(-DCOMPILEDWITHC17)
    message(STATUS "Using flag -std=c++17.")
# 如果不支持, 则输出一个致命错误信息, 提示用户更换编译器
else()
    message(FATAL_ERROR "The compiler ${CMAKE_CXX_COMPILER} has no C++17 support. Please use a different C++ compiler.")
endif()
```

### Thirdparty/DBoW3/src/Vocabulary.h

```c++
void toStream(  std::ostream &str, bool compressed=true) const;
```

```c++
void fromStream(  std::istream &str );
```

```c++
void load_fromtxt(const std::string &filename);
```

把在 Vocabulary.cc 对应的函数改一下


### src/SuperPoint.cc

```c++
desc = torch::grid_sampler(desc, grid, 0, 0, true);
```

```c++
auto fkpts = torch::from_blob(kpt_mat.data, {static_cast<int64_t>(keypoints.size()), 2}, torch::kFloat);
```

```c++
auto desc = torch::grid_sampler(mDesc, grid, 0, 0, true); 
```


### include/LoopClosing.h

```c++
int mnFullBAIdx;
```


### Examples/Monocular/mono_kitti.cc

```c++
        std::chrono::steady_clock::time_point t1 = std::chrono::steady_clock::now();

        // Pass the image to the SLAM system
        SLAM.TrackMonocular(im,tframe);
        
        std::chrono::steady_clock::time_point t2 = std::chrono::steady_clock::now();
        
        double ttrack= std::chrono::duration_cast<std::chrono::duration<double> >(t2 - t1).count();
```
