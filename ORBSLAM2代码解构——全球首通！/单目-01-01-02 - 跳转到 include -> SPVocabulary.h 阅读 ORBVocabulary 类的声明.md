# include/SPVocabulary.h


## 重点代码逐行解析


### 1. include DBoW3

注意, SuperPoint + ORBSLAM2 这个项目使用的是DBoW3, 而 ORBSLAM2 源码使用的是 DBoW2

所以如果想从头开始写代码的话, 是要注意把 DBoW3 的源码放在文件夹 Thirdparty 里, 而且要修改 DBoW3 的 CMakeLists 以及 整个项目的 CMakeList

** 具体的实现细节以及流程等后续有时间的话, 有可能出一个从头开始写 ORBSLAM2 代码的教程 (暂定)**

```c++
// 这个项目使用的是 DBoW3, ORBSLAM2 源码使用的是 DBoW2
// 因为 DBoW3 对于 OpenCV3 的兼容性较好, 且编译和使用都比较容易上手, 也适用于那些使用其他特征点替代 ORB 特征点的项目
// ORBSLAM2 源码中的 DBoW2 是经过作者修改的, 修改起来比较麻烦
#include "Thirdparty/DBoW3/src/DBoW3.h"
```


### 2. 设置 Vocabulary 类的别名

DBoW3::Vocabulary 是 DBoW3 库中的一个类, 用于表示一个词汇表, 常用于视觉特征的匹配和查询

使用 typedef, 将 SPVocabulary 设置为 DBoW3::Vocabulary  的别名, 方便后续使用

使用第二个 typedef, 将 ORBVocabulary 设置为 SPVocabulary  的别名, 实际上 ORBVocabulary 也是 DBoW3::Vocabulary 的别名

实际上, 作者一开始可能只是想将 SPVocabulary 定义为 DBoW3::Vocabulary 的别名, 但 ORBSLAM2 的代码中大量使用了 ORBVocabulary 这个类名

为了减少修改的工作量, 所以才这样写, 你也可以只设置 SPVocabulary, 但是需要将整个项目用到 ORBVocabulary 的地方全部进行替换

```c++
    // 定义了 SPVocabulary 为 DBoW3::Vocabulary 类型的别名
    typedef DBoW3::Vocabulary SPVocabulary;

    // 定义了 ORBVocabulary 为 SPVocabulary 类型的别名
    typedef SPVocabulary ORBVocabulary;
```


## 完整代码

```c++
#ifndef SPVOCABULARY_H
#define SPVOCABULARY_H

// #include"Thirdparty/DBoW2/DBoW2/FSP.h"
// #include"Thirdparty/DBoW2/DBoW2/TemplatedVocabulary.h"

// 这个项目使用的是 DBoW3, ORBSLAM2 源码使用的是 DBoW2
// 因为 DBoW3 对于 OpenCV3 的兼容性较好, 且编译和使用都比较容易上手, 也适用于那些使用其他特征点替代 ORB 特征点的项目
// ORBSLAM2 源码中的 DBoW2 是经过作者修改的, 修改起来比较麻烦
#include "Thirdparty/DBoW3/src/DBoW3.h"

namespace ORB_SLAM2
{

    // typedef DBoW2::TemplatedVocabulary<DBoW2::FSP::TDescriptor, DBoW2::FSP> SPVocabulary;

    // 定义了 SPVocabulary 为 DBoW3::Vocabulary类型的别名
    typedef DBoW3::Vocabulary SPVocabulary;

    // 定义了 ORBVocabulary 为 SPVocabulary 类型的别名
    typedef SPVocabulary ORBVocabulary;

} //namespace ORB_SLAM

#endif // SPVOCABULARY_H
```
