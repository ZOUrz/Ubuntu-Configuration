# 跳转到 src/Map.cc 阅读 Map 类构造函数的具体实现

- `Map` 类的构造函数非常简单, 无需多言


## 重点代码逐行解析


- ### 1. 构造函数

```c++

```

  - 其中, 构造函数以及其成员变量是在 include/Map.h 中声明的

```c++

```

```c++

```


## 重头开始构建 ORBSLAM2

- 如果是从零开始构建 `ORBSLAM2` 系统, 就按照下面给出的文件内容进行代码的编写


- ### 1. include/Map.h

  - Build from scratch - Changed 0

```c++

```


- ### 2. src/Map.cc

  - Build from scratch - Changed 0

```c++

```


- ### 3. include/System.h

  - Build from scratch - Changed 4
 
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

  - Build from scratch - Changed 4
 
  - 在代码最后加上
 
```c++

```

  - 完整代码

```c++

```


- ### 5. CMakeLists

  - Build from scratch - Changed 3
 
  - 在文件以下位置进行修改, 将 `Map.cc` 源文件添加到库中
 
```cmake

```

  - 完整代码

```cmake

```









