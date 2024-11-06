


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
