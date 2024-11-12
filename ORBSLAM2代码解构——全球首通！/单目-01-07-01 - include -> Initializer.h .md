# 跳转到 include/Initializer.h

- 跟 `单目-01-01` 里的操作类似, 目前不用阅读 `Initializer` 类的构造函数, 因为暂时还没有调用, 所以目前暂时不用进行代码的解析


## 重头开始构建 ORBSLAM2

- 如果是从零开始构建 `ORBSLAM2` 系统, 就按照下面给出的文件内容进行代码的编写


- ### 1. include/Initializer.h

  - Build from scratch - Changed 0
 
  - 其实这里就是定义了一个空的 `Initializer` 类
 
```c++

```


- ### 2. include/Tracking.h

  - Build from scratch - Changed 2
 
  - 文件开头加上:
 
```c++

```

  - 然后加上成员变量 `mpInitializer` 的声明, 实际上是一个 `Initializer` 类的指针, 但并未分配内存或调用构造函数

```c++

```

  - 完整代码

```c++

```


- ### 3. src/Tracking.cc

  - Build from scratch - Changed 1
 
  - 在 `成员变量初始化列表` 中加上:
 
```c++

```

  - 完整代码

```c++

```
