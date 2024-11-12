# 跳转到 src/SPextractor.cc 阅读 SPextractor 类构造函数的具体实现

主要阅读该文件中 `SPextractor` 类的构造函数


## 重点代码逐行解析


- ### 1. 成员变量初始化列表

    - `SPextractor` 类的构造函数

    - 在 `SPextractor` 类构造函数体外, 是部分成员变量的初始化列表, 用于初始化类的部分成员变量
  
    ```c++
        // 特征点提取器的构造函数
        // 构造函数输入的参数:
        // 指定要提取的特征点数目, 指定图像金字塔的缩放系数, 指定图像金字塔的层数
        // _iniThFAST: 指定初始的 FAST 特征点提取参数, 用于提取出最明显的角点
        // _minTHFAST: 如果初始阈值没有检测到角点, 降低到这个阈值提取出弱一点的角点
        SPextractor::SPextractor(int _nfeatures, float _scaleFactor, int _nlevels, float _iniThFAST, float _minThFAST):
            nfeatures(_nfeatures), scaleFactor(_scaleFactor), nlevels(_nlevels),
            iniThFAST(_iniThFAST), minThFAST(_minThFAST)  // 初始化成员变量列表
    ```

    - 在初始化列表中, 总共设置了:

      - `nfeatures`: 希望提取的总特征点数量
      - `scaleFactor`: 图像金字塔的缩放系数(控制图像逐层缩小的倍数)
      - `nLevels`: 图像金字塔的层数
      - `iniThFAST` 和 `minThFAST`: `FAST` 特征提取的阈值, 用于控制特征点的角点强度
     
    - 这些参数被直接赋值给成员变量
 
    - 其中, `SPextractor` 类的构造函数是在 `include/SPextractor.h` 中声明的
 
```c++

```
 
    - 变量 `nfeatures`, `scaleFactor`, `nlevels`, `iniThFAST` 和 `minThFAST` 是 `SPextractor` 类的成员变量, 同样地, 它们是在 `include/SPextractor.h` 中声明的

```c++

```

    - 要注意 **定义** 和 **声明** 的区别:

      - **声明(Declaration)**: 告诉编译器变量的类型和名字, 但不分配内存或赋值. 例如, `extern int x;` 是声明, 仅告知编译器有一个名为 `x` 的 `int` 类型变量, 它的定义在其他地方

      - **定义(Definition)**: 在声明的基础上, 同时分配内存, 并可选择性地赋值. 例如, `int x = 10;` 是定义, 既分配了内存也赋值为 `10`  

    

    
 

```c++
    {
        // 加载 SuperPoint 模型
        model = make_shared<SuperPoint>();
        torch::load(model, "superpoint.pt");

        // 存储每层图像缩放系数的vector,调整为符合图层数目的大小
        mvScaleFactor.resize(nlevels);
        // 每层图像相对初始图像缩放因子的平方
        mvLevelSigma2.resize(nlevels);
        // 对于初始图像, 这两个参数都是1
        mvScaleFactor[0] = 1.0f;
        mvLevelSigma2[0] = 1.0f;
        // 然后逐层计算图像金字塔中图像相当于初始图像的缩放系数
        for(int i=1; i<nlevels; i++)
        {
            // 通过累乘计算得来的
            mvScaleFactor[i] = static_cast<float>(mvScaleFactor[i-1] * scaleFactor);
            // 每层图像相对于初始图像缩放因子的平方
            mvLevelSigma2[i] = mvScaleFactor[i] * mvScaleFactor[i];
        }

        // 下面的两个参数保存的时上面两个参数的倒数
        mvInvScaleFactor.resize(nlevels);
        mvInvLevelSigma2.resize(nlevels);
        for(int i=0; i<nlevels; i++)
        {
            mvInvScaleFactor[i] = 1.0f/mvScaleFactor[i];
            mvInvLevelSigma2[i] = 1.0f/mvLevelSigma2[i];
        }

        // 调整图像金字塔 vector 以使得其符合设定的图像层数
        mvImagePyramid.resize(nlevels);

        // 每层需要提取出来的特征点个数, 要根据图像金字塔设定的层数进行调整
        mnFeaturesPerLevel.resize(nlevels);
        // 图片降采样缩放系数的倒数
        const auto factor = static_cast<float>(1.0f / scaleFactor);
        // 第0层图像应该分配的特征点数
        float nDesiredFeaturesPerScale = static_cast<float>(nfeatures)*(1-factor) /
            (1-static_cast<float>(pow(static_cast<double>(factor), static_cast<double>(nlevels))));

        // 用于在特征点个数分配的, 特征点的累计计数清空
        int sumFeatures = 0;
        // 开始逐层计算要分配的特征点个书, 顶层图像除外
        for( int level = 0; level < nlevels-1; level++ )
        {
            // 分配 cvRound: 返回跟参数最接近的整数值
            mnFeaturesPerLevel[level] = cvRound(nDesiredFeaturesPerScale);
            // 累计
            sumFeatures += mnFeaturesPerLevel[level];
            // 乘系数
            nDesiredFeaturesPerScale *= factor;
        }
        // 由于前面的特征点个数取整操作, 可能会导致剩余一些特征点个数没有被分配, 所以这里就将这个余出来的特征点分配到最高的图层中
        mnFeaturesPerLevel[nlevels-1] = std::max(nfeatures - sumFeatures, 0);
    }
```

```c++
    // 特征点提取器的构造函数
    // 构造函数输入的参数:
    // 指定要提取的特征点数目, 指定图像金字塔的缩放系数, 指定图像金字塔的层数
    // _iniThFAST: 指定初始的 FAST 特征点提取参数, 用于提取出最明显的角点
    // _minTHFAST: 如果初始阈值没有检测到角点, 降低到这个阈值提取出弱一点的角点
    SPextractor::SPextractor(int _nfeatures, float _scaleFactor, int _nlevels, float _iniThFAST, float _minThFAST):
        nfeatures(_nfeatures), scaleFactor(_scaleFactor), nlevels(_nlevels),
        iniThFAST(_iniThFAST), minThFAST(_minThFAST)  // 初始化成员变量列表
    {
        // 加载 SuperPoint 模型
        model = make_shared<SuperPoint>();
        torch::load(model, "superpoint.pt");

        // 存储每层图像缩放系数的vector,调整为符合图层数目的大小
        mvScaleFactor.resize(nlevels);
        // 每层图像相对初始图像缩放因子的平方
        mvLevelSigma2.resize(nlevels);
        // 对于初始图像, 这两个参数都是1
        mvScaleFactor[0] = 1.0f;
        mvLevelSigma2[0] = 1.0f;
        // 然后逐层计算图像金字塔中图像相当于初始图像的缩放系数
        for(int i=1; i<nlevels; i++)
        {
            // 通过累乘计算得来的
            mvScaleFactor[i] = static_cast<float>(mvScaleFactor[i-1] * scaleFactor);
            // 每层图像相对于初始图像缩放因子的平方
            mvLevelSigma2[i] = mvScaleFactor[i] * mvScaleFactor[i];
        }

        // 下面的两个参数保存的时上面两个参数的倒数
        mvInvScaleFactor.resize(nlevels);
        mvInvLevelSigma2.resize(nlevels);
        for(int i=0; i<nlevels; i++)
        {
            mvInvScaleFactor[i] = 1.0f/mvScaleFactor[i];
            mvInvLevelSigma2[i] = 1.0f/mvLevelSigma2[i];
        }

        // 调整图像金字塔 vector 以使得其符合设定的图像层数
        mvImagePyramid.resize(nlevels);

        // 每层需要提取出来的特征点个数, 要根据图像金字塔设定的层数进行调整
        mnFeaturesPerLevel.resize(nlevels);
        // 图片降采样缩放系数的倒数
        const auto factor = static_cast<float>(1.0f / scaleFactor);
        // 第0层图像应该分配的特征点数
        float nDesiredFeaturesPerScale = static_cast<float>(nfeatures)*(1-factor) /
            (1-static_cast<float>(pow(static_cast<double>(factor), static_cast<double>(nlevels))));

        // 用于在特征点个数分配的, 特征点的累计计数清空
        int sumFeatures = 0;
        // 开始逐层计算要分配的特征点个书, 顶层图像除外
        for( int level = 0; level < nlevels-1; level++ )
        {
            // 分配 cvRound: 返回跟参数最接近的整数值
            mnFeaturesPerLevel[level] = cvRound(nDesiredFeaturesPerScale);
            // 累计
            sumFeatures += mnFeaturesPerLevel[level];
            // 乘系数
            nDesiredFeaturesPerScale *= factor;
        }
        // 由于前面的特征点个数取整操作, 可能会导致剩余一些特征点个数没有被分配, 所以这里就将这个余出来的特征点分配到最高的图层中
        mnFeaturesPerLevel[nlevels-1] = std::max(nfeatures - sumFeatures, 0);
    }
```
