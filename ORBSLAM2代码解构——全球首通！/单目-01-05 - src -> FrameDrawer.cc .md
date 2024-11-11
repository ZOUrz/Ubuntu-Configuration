# 跳转到 src/FrameDrawer.cc 阅读 FrameDrawer 类构造函数的具体实现

- `FrameDrawer` 类的构造函数就几行代码, 比较简单

- 重点是其中的成员变量 `mState` 被设置为 `Tracking:SYSTEM_NOT_READY`, 这里需要进行跳转


## 重点代码逐行解析

- ### 1. 构造函数

```c++

```

 - 其中, 构造函数以及其成员变量是在 `include/FrameDrawer` 中声明的


## 需要进行跳转阅读的位置

- ### 1. Tracking:SYSTEM_NOT_READY

```c++

```

  - 这一行代码将系统状态 `mState` 设置为 `Tracking::SYSTEM_NOT_READY`

  - 其中, `Tracking` 类中定义了枚举类型 `eTrackingState`, 而 `SYSTEM_NOT_READY` 是枚举类型的一个成员

  - 由于定义的代码位于 `include/Tracking.h`中, 因此只需要跳转到该文件中即可


## 重头开始构建 ORBSLAM2

- 如果是从零开始构建 `ORBSLAM2` 系统, 就按照下面给出的文件内容进行代码的编写


- ### 1. include/FrameDrawer.h

 - Build from scratch - Changed 0

```c++

```


- ### 2. src/FrameDrawer.cc

 - Build from scratch - Changed 0

```c++

```


- ### 3. include/System.h

 - Build from scratch - Changed 5

 - 文件开头加上

```c++

```

 - 然后添加成员变量

```c++

```

 - 完整代码

```c++

```


- ### 4. src/System.cc

 - Build from scratch - Changed 5

 - 在代码最后加上

```c++

```

 - 完整代码

```c++

```
