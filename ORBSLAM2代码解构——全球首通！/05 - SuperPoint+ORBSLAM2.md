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

### src/SuperPoint.cc

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

```c++
desc = torch::grid_sampler(desc, grid, 0, 0, true);
```

```c++
auto fkpts = torch::from_blob(kpt_mat.data, {static_cast<int64_t>(keypoints.size()), 2}, torch::kFloat);
```
