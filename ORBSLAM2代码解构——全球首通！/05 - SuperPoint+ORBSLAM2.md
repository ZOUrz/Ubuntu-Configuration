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

```c++
desc = torch::grid_sampler(desc, grid, 0, 0, true);
```

```c++
auto fkpts = torch::from_blob(kpt_mat.data, {static_cast<int64_t>(keypoints.size()), 2}, torch::kFloat);
```
