# 跳转到 src/SPextractor.cc 阅读 SPextractor 类构造函数的具体实现

- 主要阅读该文件中 `SPextractor` 类的构造函数


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
      - **!!!! 这里的 `iniThFAST` 和 `minThFAST` 的含义不是下面写的这个, 具体要等看到后面才知道, 另外在 `ORBSLAM2` 源码中, 这两个成员变量的类型为 `int`**
      - `iniThFAST` 和 `minThFAST`: `FAST` 特征提取的阈值, 用于控制特征点的角点强度
     
    - 这些参数被直接赋值给成员变量
 
    - 其中, `SPextractor` 类的构造函数是在 `include/SPextractor.h` 中声明的
 
    ```c++
            // 构造函数
            // nfeatures: 指定要提取出来的特征点数目
            // scaleFactor: 图像金字塔的缩放系数
            // nlevels: 指定需要提取特征点的图像金字塔层
            // iniThFAST: 初始的默认FAST响应值阈值
            // minThFAST: 较小的FAST响应值阈值
            SPextractor(int nfeatures, float scaleFactor, int nlevels, float iniThFAST, float minThFAST);
    ```
 
    - 变量 `nfeatures`, `scaleFactor`, `nlevels`, `iniThFAST` 和 `minThFAST` 是 `SPextractor` 类的成员变量, 同样地, 它们是在 `include/SPextractor.h` 中声明的

    ```c++
            int nfeatures;  // 整个图像金字塔中, 要提取的特征点数目
            double scaleFactor;  // 图像金字塔中, 层与层之间的缩放因子
            int nlevels;  // 图像金字塔的层数
            float iniThFAST;  // 初始的FAST响应值阈值
            float minThFAST;  // 最小的FAST响应值阈值
    ```

    - 要注意 **定义** 和 **声明** 的区别:

      - **声明(Declaration)**: 告诉编译器变量的类型和名字, 但不分配内存或赋值. 例如, `extern int x;` 是声明, 仅告知编译器有一个名为 `x` 的 `int` 类型变量, 它的定义在其他地方

      - **定义(Definition)**: 在声明的基础上, 同时分配内存, 并可选择性地赋值. 例如, `int x = 10;` 是定义, 既分配了内存也赋值为 `10`


- ### 2. 加载 SuperPoint 模型

    - 加载了预训练的 `SuperPoint` 模型文件 "`superpoint.pt`", 并将模型对象赋给 model 指针, 以完成模型的初始化
 
    ```c++
            // 加载 SuperPoint 模型
            model = make_shared<SuperPoint>();
            torch::load(model, "superpoint.pt");
    ```

    - 这段代码首先创建了一个 `SuperPoint` 类的对象, 并将它存储在一个 `shared_ptr` 智能指针中

        - `make_shared<SuperPoint>()` 是一种简便的智能指针创建方法:
            - 创建了一个 `shared_ptr<SuperPoint>` 对象, `shared_ptr` 是 `C++11` 中的智能指针之一, 用于管理动态分配的内存
            - `shared_ptr` 的特点是**引用计数**, 可以在多个地方共享同一个对象, 当最后一个 `shared_ptr`指针离开作用域时, 对象会自动销毁, 释放内存, 避免手动管理内存和内存泄露的问题
        - `model` 是一个 `shared_ptr<SuperPoint>`, 它指向一个动态分配的 `SuperPoint` 对象, 这样可以在类的其他成员函数中访问和使用 `SuperPoint` 的方法和属性
    
    - 然后使用 `libtorch` ('PyTorch C++' 接口)将预训练的模型权重文件 "`superpoint.pt`" 加载到 `model` 中
        
        - `torch::load` 是 `libtorch` 提供的一个函数, 用于加载模型的参数
        - `model` 是一个指向 `SuperPoint` 对象的智能指针, `torch::load` 会将 "`superpoint.pt`" 文件中的权重数据加载到 `model` 所指的 `SuperPoint` 对象中
     
    - 其中, 成员变量 `model` 是在 `include/SPextractor.h` 中声明的
     
    ```c++
            std::shared_ptr<SuperPoint> model;
    ```


- ### 3. 计算缩放因子

    - 计算图像金字塔的缩放因子
 
    - `mvScaleFactor` 和 `mvLevelSigma2` 是两个 `vector`, 用来存储每层图像相对于初始图像的缩放系数及其平方

    ```c++
            // 存储每层图像缩放系数的 vector,调整为符合图层数目的大小
            mvScaleFactor.resize(nlevels);
            // 每层图像相对初始图像缩放因子的平方
            mvLevelSigma2.resize(nlevels);
            // 对于初始图像, 这两个参数都是 1
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
    ```

    - 第 `0` 层表示原图, 因此缩放因子为 `1`
 
    - 从第 `1` 层开始, 每层缩放因子逐步乘上 `scaleFactor`
 
    - `mvLevelSigma2` 是缩放因子的平方, 用于后续运算
 
    - 其中, 成员变量 `mvScaleFactor` 和 `mvLevelSigma2` 是在 `include/SPextractor.h` 中声明的

     ```c++
            std::vector<float> mvScaleFactor;  // 每层图像的缩放因子
            std::vector<float> mvLevelSigma2;  // Sigma2: 每层图像相对于底层图像缩放倍数的平方
    ```


 - ### 4. 计算缩放因子的倒数

    - `mvInvScaleFactor` 和 `mvInvLevelSigma2` 分别存储了缩放因子和缩放因子平方的倒数, 便于在图像重采样和特征点计算中进行更高效的逆运算
  
    ```c++
            // 下面的两个参数保存的是上面两个参数的倒数
            mvInvScaleFactor.resize(nlevels);
            mvInvLevelSigma2.resize(nlevels);
            for(int i=0; i<nlevels; i++)
            {
                mvInvScaleFactor[i] = 1.0f/mvScaleFactor[i];
                mvInvLevelSigma2[i] = 1.0f/mvLevelSigma2[i];
            }
    ```

    - 其中, 成员变量 `mvInvScaleFactor` 和 `mvInvLevelSigma2` 是在 `include/SPextractor.h` 中声明的

    ```c++
        std::vector<float> mvInvScaleFactor;  // 每层缩放因子的倒数
        std::vector<float> mvInvLevelSigma2;  // Sigma2 的倒数
    ```


- ### 5. 设置图像金字塔

    - `mvImagePyramid` 是一个 `vector`, 预留空间给每一层的图像
 
    - 这一步确保了金字塔中每一层图像在运行时可以直接访问和处理
 
    ```c++
            // 调整图像金字塔 vector 以使得其符合设定的图像层数
            mvImagePyramid.resize(nlevels);
    ```

    - 其中, 成员变量 `mvImagePyramid` 是在 `include/SPextractor.h` 中声明的
 
    ```c++
            // 用来存储图像金字塔的变量, 一个元素存储一层图像
            std::vector<cv::Mat> mvImagePyramid;
    ```


- ### 6. 特征点数量分配

    - 特征点分配是通过等比递减的方式来确定每层的特征点数, 保证较低分辨率的图像层中提取较少的特征点
 
    ```c++
            // 每层需要提取出来的特征点个数, 要根据图像金字塔设定的层数进行调整
            mnFeaturesPerLevel.resize(nlevels);
            // 图片降采样缩放系数的倒数
            const auto factor = static_cast<float>(1.0f / scaleFactor);
            // 第0层图像应该分配的特征点数
            float nDesiredFeaturesPerScale = static_cast<float>(nfeatures)*(1-factor) /
                (1-static_cast<float>(pow(static_cast<double>(factor), static_cast<double>(nlevels))));
    ```

    - `factor` 是 `scaleFactor` 的倒数, `nDesiredFeaturesPerScale` 计算每层的目标特征点数量
 
    - 通过循环分配每层的特征点, 除去最高层, 其余层依次按比例减少, 由于取整可能导致最后的分配数不足, 所以将剩余的特征点分配到最高层, 以保证总特征点数满足要求
 
    ```c++
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
    ```

    - 其中, 成员变量 `mnFeaturesPerLevel` 是在 `include/SPextractor.h` 中声明的

    ```c++
            std::vector<int> mnFeaturesPerLevel;  // 分配到每层图像中, 要提取的特征点数目
    ```


- ### 7. 定义类别名

    - 在 `include/SPextractor.h` 文件的最后, 作者还写了以下这段代码:

    ```c++
        typedef SPextractor ORBextractor;
    ```

    - 这行代码将 `ORBextractor` 定义为 `SPextractor` 的一个类型别名, 所以在后续代码中使用的 `ORBextractor` 实际上指向的是 `SPextractor`
 
    - 这样做的目的是为了减少后续代码的更改, 减少工作量, 否则需要把项目内的所有文件都进行检查和更改
    

## ORBSLAM2 源码补充

- 上述的代码是 `SuperPoint + ORBSLAM2` 项目里的源码, `SuperPoint` 能够在提取特征点的同时, 输出相应的描述子
    
- 而 `ORB` 特征点使用的是 `BRIEF` 特征描述子, 还需要一些预处理的步骤

- 以下代码解析的是在 `ORBSLAM2` 源码中, `ORBextractor` 类构造函数余下的内容


- ### 1. 采样点数量

    - 定义了常量 `npoints`, 值为 `512`, 表示 `BRIEF` 描述子中需要的采样点数量

    - 也是 `pattern` 的长度, 这里的 `512` 表示 `512` 个点, 上面的 `bit_pattern_31` 数组中存储的坐标是 `256 * 2 * 2`
 
    ```c++
        // 成员变量 pattern 的长度, 也就是点的个数, 这里的 512 表示 512 个点(所以上面的数组中存储的坐标是 256*2*2)
        constexpr int npoints = 512;
    ```


- ### 2. 强制类型转换

    - `bit_pattern_31` 是一个 `int [ ]` 数组, 存储的是 `BRIEF` 描述子所需的随机采样点的坐标
 
    - 使用 `reinterpret_cast` 强制将 `bit_pattern_31` 转换为 `Point*` 类型的指针, 以便后续处理
 
    - `cv::Point` 通常表示一个二维坐标类型, 每个点包含 `x` 和 `y` 坐标, 这样就可以通过 `pattern0` 指针按 `Point` 的格式来访问采样点的坐标信息
 
    ```c++
        // 获取用于计算 BRIEF 描述子的随机采样点 点集 头指针
        // 注意到pattern0的数据类型为Points*, bit_pattern_31_是int[]型, 所以这里需要进行强制类型转换
        const auto pattern0 = reinterpret_cast<const Point*>(bit_pattern_31_);
    ```


- ### 3. 给成员变量 pattern 赋值

    - `std::copy` 将 `pattern0` 指向的 `npoints` 个采样点复制到 `pattern` 容器中
 
    - `std::back_inserter` 是一种迭代器, 保证数据会被添加到 `pattern` 的末尾, 避免覆盖容器中已有的数据
 
    ```c++
        // 使用 std::back_inserte r的目的是可以快覆盖掉这个容器 pattern 之前的数据
        // 将在全局变量区域的, int 格式的随机采样点以 cv::point 格式复制到当前类对象中的成员变量中
        std::copy(pattern0, pattern0 + npoints, std::back_inserter(pattern));
    ```

    - 其中, 成员变量 `pattern` 是在 `include/SPextractor.h` 中声明的

    ```c++
            std::vector<cv::Point> pattern;  // 用于计算描述子的随机采样点集合
    ```


- ### 4. 初始化 umax

    - `umax` 是一个向量, 用来存储 `BRIEF` 特征点的一个计算值, 在图像旋转时保持不变性
 
    - `HALF_PATCH_SIZE` 定义了描述子计算中要使用的图像区域半径, 这样 `umax` 就是长度为 `HALF_PATCH_SIZE + 1` 的向量
 
    ```c++
        // 下面的内容是和特征点的旋转计算有关的
        // This is for orientation
        // 预先计算图像 patch 中行的结束位置
        // pre-compute the end of a row in a circular patch
        // + 1 中的 1 表示那个圆的中间行
        umax.resize(HALF_PATCH_SIZE + 1);
    ```

    - 其中, 成员变量 `umax` 是在 `include/SPextractor.h` 中声明的

    ```c++
        std::vector<int> umax;  // 计算特征点方向的时候, 这个 vector 中存储了每行 u 轴的边界 (四分之一, 其他部分通过对称获得)
    ```
 

- ### 5. 计算 umax 的前半部分

    - `vmax` 和 `vmin` 定义了对称的计算范围, 用于计算图像旋转时每一行的最右边界(半径)
 
    - `hp2` 是半径的平方, `sqrt(hp2 - v * v)` 得到给定 `v` 值对应的最大水平距离 u, 存储在 `umax[v]` 中
 
    - `umax[v]` 最终代表的是一个圆形区域的边界, 即旋转 `patch` 的每行都能到达的最右侧像素位置(这里不太懂???)
 
    ```c++
        // cvFloor 返回不大于参数的最大整数值, cvCeil 返回不小于参数的最小整数值, cvRound 则是四舍五入
        // v: 循环辅助变量, v0: 辅助变量, vmax: 计算圆的最大行号, + 1 是把中间行也考虑进行了
        // NOTICE: 注意这里的最大行号指的是计算时的最大行号, 此行和圆的角点在 45 度圆心角的一边上
        // NOTICE：之所以这样选择是因为圆周上的对称特性 
        int v, v0, vmax = cvFloor(HALF_PATCH_SIZE * sqrt(2.f) / 2 + 1);
        // 二分之根号二就是对应 45 度圆心角
        int vmin = cvCeil(HALF_PATCH_SIZE * sqrt(2.f) / 2);
        // 半径的平方
        const double hp2 = HALF_PATCH_SIZE*HALF_PATCH_SIZE;
        // 利用圆的方程计算每行像素的 u 坐标边界( max )
        for (v = 0; v <= vmax; ++v)
            // 结果都是大于 0 的结果, 表示 x 坐标在这一行的边界
            umax[v] = cvRound(sqrt(hp2 - v * v));
    ```


- ### 6. 确保 umax 对称

    - 通过对称化 `umax`, 保证计算 `BRIEF` 描述子时具有旋转不变性, 使得在不同角度上特征提取结果一致

    ```c++
        // Make sure we are symmetric
        // 使用对称的方式计算上四分之一的圆周上的umax, 目的是为了保持严格的对称
        // 如果使用 cvRound 就会很容易出现不对称, 就无法满足旋转不变性
        for (v = HALF_PATCH_SIZE, v0 = 0; v >= vmin; --v)
        {
            while (umax[v0] == umax[v0 + 1])
                ++v0;
            umax[v] = v0;
            ++v0;
    ```
 
```c++
#ifndef ORBEXTRACTOR_H
#define ORBEXTRACTOR_H


#include <list>
#include <vector>
#include <opencv/cv.h>


#ifdef EIGEN_MPL2_ONLY
#undef EIGEN_MPL2_ONLY
#endif


// 主要负责进行 ORB 特征点的提取和数目分配功能

namespace ORB_SLAM2
{
    // ORB特征点提取器
    class ORBextractor
    {
    public:
        // 构造函数
        // nfeatures: 指定要提取出来的特征点数目
        // scaleFactor: 图像金字塔的缩放系数
        // nlevels: 指定需要提取特征点的图像金字塔层
        // iniThFAST: 初始的默认FAST响应值阈值
        // minThFAST: 较小的FAST响应值阈值
        ORBextractor(int nfeatures, float scaleFactor, int nlevels, int iniThFAST, int minThFAST);

        // 析构函数
        ~ORBextractor(){};

        // 用来存储图像金字塔的变量, 一个元素存储一层图像
        std::vector<cv::Mat> mvImagePyramid;

    protected:
        std::vector<cv::Point> pattern;  // 用于计算描述子的随机采样点集合

        int nfeatures;  // 整个图像金字塔中, 要提取的特征点数目
        double scaleFactor;  // 图像金字塔中, 层与层之间的缩放因子
        int nlevels;  // 图像金字塔的层数
        int iniThFAST;  // 初始的FAST响应值阈值
        int minThFAST;  // 最小的FAST响应值阈值

        std::vector<int> mnFeaturesPerLevel;  // 分配到每层图像中, 要提取的特征点数目

        std::vector<int> umax;  // 计算特征点方向的时候, 这个 vector 中存储了每行 u 轴的边界 (四分之一, 其他部分通过对称获得)

        std::vector<float> mvScaleFactor;  // 每层图像的缩放因子
        std::vector<float> mvInvScaleFactor;  // 每层缩放因子的倒数
        std::vector<float> mvLevelSigma2;  // Sigma2: 每层图像相对于底层图像缩放倍数的平方
        std::vector<float> mvInvLevelSigma2;  // Sigma2 的倒数

    };

}

#endif //ORBEXTRACTOR_H

```

```c++
#include "ORBextractor.h"

#include <vector>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/features2d/features2d.hpp>
#include <opencv2/imgproc/imgproc.hpp>


using namespace cv;
using namespace std;


namespace ORB_SLAM2
{

    const int HALF_PATCH_SIZE = 15;  // 图像块大小的一半, 即半径

    // 预先定义好的随机点集, 256 是指可以提取出 256bit 的描述子信息, 每个 bit 由一对点比较得来
    // 4 = 2 * 2, 前面的 2 是需要两个点(一对点)进行比较, 后面的 2 是一个点有两个坐标
    static int bit_pattern_31_[256*4] =
    {
        8,-3, 9,5/*mean (0), correlation (0)*/,
        4,2, 7,-12/*mean (1.12461e-05), correlation (0.0437584)*/,
        -11,9, -8,2/*mean (3.37382e-05), correlation (0.0617409)*/,
        7,-12, 12,-13/*mean (5.62303e-05), correlation (0.0636977)*/,
        2,-13, 2,12/*mean (0.000134953), correlation (0.085099)*/,
        1,-7, 1,6/*mean (0.000528565), correlation (0.0857175)*/,
        -2,-10, -2,-4/*mean (0.0188821), correlation (0.0985774)*/,
        -13,-13, -11,-8/*mean (0.0363135), correlation (0.0899616)*/,
        -13,-3, -12,-9/*mean (0.121806), correlation (0.099849)*/,
        10,4, 11,9/*mean (0.122065), correlation (0.093285)*/,
        -13,-8, -8,-9/*mean (0.162787), correlation (0.0942748)*/,
        -11,7, -9,12/*mean (0.21561), correlation (0.0974438)*/,
        7,7, 12,6/*mean (0.160583), correlation (0.130064)*/,
        -4,-5, -3,0/*mean (0.228171), correlation (0.132998)*/,
        -13,2, -12,-3/*mean (0.00997526), correlation (0.145926)*/,
        -9,0, -7,5/*mean (0.198234), correlation (0.143636)*/,
        12,-6, 12,-1/*mean (0.0676226), correlation (0.16689)*/,
        -3,6, -2,12/*mean (0.166847), correlation (0.171682)*/,
        -6,-13, -4,-8/*mean (0.101215), correlation (0.179716)*/,
        11,-13, 12,-8/*mean (0.200641), correlation (0.192279)*/,
        4,7, 5,1/*mean (0.205106), correlation (0.186848)*/,
        5,-3, 10,-3/*mean (0.234908), correlation (0.192319)*/,
        3,-7, 6,12/*mean (0.0709964), correlation (0.210872)*/,
        -8,-7, -6,-2/*mean (0.0939834), correlation (0.212589)*/,
        -2,11, -1,-10/*mean (0.127778), correlation (0.20866)*/,
        -13,12, -8,10/*mean (0.14783), correlation (0.206356)*/,
        -7,3, -5,-3/*mean (0.182141), correlation (0.198942)*/,
        -4,2, -3,7/*mean (0.188237), correlation (0.21384)*/,
        -10,-12, -6,11/*mean (0.14865), correlation (0.23571)*/,
        5,-12, 6,-7/*mean (0.222312), correlation (0.23324)*/,
        5,-6, 7,-1/*mean (0.229082), correlation (0.23389)*/,
        1,0, 4,-5/*mean (0.241577), correlation (0.215286)*/,
        9,11, 11,-13/*mean (0.00338507), correlation (0.251373)*/,
        4,7, 4,12/*mean (0.131005), correlation (0.257622)*/,
        2,-1, 4,4/*mean (0.152755), correlation (0.255205)*/,
        -4,-12, -2,7/*mean (0.182771), correlation (0.244867)*/,
        -8,-5, -7,-10/*mean (0.186898), correlation (0.23901)*/,
        4,11, 9,12/*mean (0.226226), correlation (0.258255)*/,
        0,-8, 1,-13/*mean (0.0897886), correlation (0.274827)*/,
        -13,-2, -8,2/*mean (0.148774), correlation (0.28065)*/,
        -3,-2, -2,3/*mean (0.153048), correlation (0.283063)*/,
        -6,9, -4,-9/*mean (0.169523), correlation (0.278248)*/,
        8,12, 10,7/*mean (0.225337), correlation (0.282851)*/,
        0,9, 1,3/*mean (0.226687), correlation (0.278734)*/,
        7,-5, 11,-10/*mean (0.00693882), correlation (0.305161)*/,
        -13,-6, -11,0/*mean (0.0227283), correlation (0.300181)*/,
        10,7, 12,1/*mean (0.125517), correlation (0.31089)*/,
        -6,-3, -6,12/*mean (0.131748), correlation (0.312779)*/,
        10,-9, 12,-4/*mean (0.144827), correlation (0.292797)*/,
        -13,8, -8,-12/*mean (0.149202), correlation (0.308918)*/,
        -13,0, -8,-4/*mean (0.160909), correlation (0.310013)*/,
        3,3, 7,8/*mean (0.177755), correlation (0.309394)*/,
        5,7, 10,-7/*mean (0.212337), correlation (0.310315)*/,
        -1,7, 1,-12/*mean (0.214429), correlation (0.311933)*/,
        3,-10, 5,6/*mean (0.235807), correlation (0.313104)*/,
        2,-4, 3,-10/*mean (0.00494827), correlation (0.344948)*/,
        -13,0, -13,5/*mean (0.0549145), correlation (0.344675)*/,
        -13,-7, -12,12/*mean (0.103385), correlation (0.342715)*/,
        -13,3, -11,8/*mean (0.134222), correlation (0.322922)*/,
        -7,12, -4,7/*mean (0.153284), correlation (0.337061)*/,
        6,-10, 12,8/*mean (0.154881), correlation (0.329257)*/,
        -9,-1, -7,-6/*mean (0.200967), correlation (0.33312)*/,
        -2,-5, 0,12/*mean (0.201518), correlation (0.340635)*/,
        -12,5, -7,5/*mean (0.207805), correlation (0.335631)*/,
        3,-10, 8,-13/*mean (0.224438), correlation (0.34504)*/,
        -7,-7, -4,5/*mean (0.239361), correlation (0.338053)*/,
        -3,-2, -1,-7/*mean (0.240744), correlation (0.344322)*/,
        2,9, 5,-11/*mean (0.242949), correlation (0.34145)*/,
        -11,-13, -5,-13/*mean (0.244028), correlation (0.336861)*/,
        -1,6, 0,-1/*mean (0.247571), correlation (0.343684)*/,
        5,-3, 5,2/*mean (0.000697256), correlation (0.357265)*/,
        -4,-13, -4,12/*mean (0.00213675), correlation (0.373827)*/,
        -9,-6, -9,6/*mean (0.0126856), correlation (0.373938)*/,
        -12,-10, -8,-4/*mean (0.0152497), correlation (0.364237)*/,
        10,2, 12,-3/*mean (0.0299933), correlation (0.345292)*/,
        7,12, 12,12/*mean (0.0307242), correlation (0.366299)*/,
        -7,-13, -6,5/*mean (0.0534975), correlation (0.368357)*/,
        -4,9, -3,4/*mean (0.099865), correlation (0.372276)*/,
        7,-1, 12,2/*mean (0.117083), correlation (0.364529)*/,
        -7,6, -5,1/*mean (0.126125), correlation (0.369606)*/,
        -13,11, -12,5/*mean (0.130364), correlation (0.358502)*/,
        -3,7, -2,-6/*mean (0.131691), correlation (0.375531)*/,
        7,-8, 12,-7/*mean (0.160166), correlation (0.379508)*/,
        -13,-7, -11,-12/*mean (0.167848), correlation (0.353343)*/,
        1,-3, 12,12/*mean (0.183378), correlation (0.371916)*/,
        2,-6, 3,0/*mean (0.228711), correlation (0.371761)*/,
        -4,3, -2,-13/*mean (0.247211), correlation (0.364063)*/,
        -1,-13, 1,9/*mean (0.249325), correlation (0.378139)*/,
        7,1, 8,-6/*mean (0.000652272), correlation (0.411682)*/,
        1,-1, 3,12/*mean (0.00248538), correlation (0.392988)*/,
        9,1, 12,6/*mean (0.0206815), correlation (0.386106)*/,
        -1,-9, -1,3/*mean (0.0364485), correlation (0.410752)*/,
        -13,-13, -10,5/*mean (0.0376068), correlation (0.398374)*/,
        7,7, 10,12/*mean (0.0424202), correlation (0.405663)*/,
        12,-5, 12,9/*mean (0.0942645), correlation (0.410422)*/,
        6,3, 7,11/*mean (0.1074), correlation (0.413224)*/,
        5,-13, 6,10/*mean (0.109256), correlation (0.408646)*/,
        2,-12, 2,3/*mean (0.131691), correlation (0.416076)*/,
        3,8, 4,-6/*mean (0.165081), correlation (0.417569)*/,
        2,6, 12,-13/*mean (0.171874), correlation (0.408471)*/,
        9,-12, 10,3/*mean (0.175146), correlation (0.41296)*/,
        -8,4, -7,9/*mean (0.183682), correlation (0.402956)*/,
        -11,12, -4,-6/*mean (0.184672), correlation (0.416125)*/,
        1,12, 2,-8/*mean (0.191487), correlation (0.386696)*/,
        6,-9, 7,-4/*mean (0.192668), correlation (0.394771)*/,
        2,3, 3,-2/*mean (0.200157), correlation (0.408303)*/,
        6,3, 11,0/*mean (0.204588), correlation (0.411762)*/,
        3,-3, 8,-8/*mean (0.205904), correlation (0.416294)*/,
        7,8, 9,3/*mean (0.213237), correlation (0.409306)*/,
        -11,-5, -6,-4/*mean (0.243444), correlation (0.395069)*/,
        -10,11, -5,10/*mean (0.247672), correlation (0.413392)*/,
        -5,-8, -3,12/*mean (0.24774), correlation (0.411416)*/,
        -10,5, -9,0/*mean (0.00213675), correlation (0.454003)*/,
        8,-1, 12,-6/*mean (0.0293635), correlation (0.455368)*/,
        4,-6, 6,-11/*mean (0.0404971), correlation (0.457393)*/,
        -10,12, -8,7/*mean (0.0481107), correlation (0.448364)*/,
        4,-2, 6,7/*mean (0.050641), correlation (0.455019)*/,
        -2,0, -2,12/*mean (0.0525978), correlation (0.44338)*/,
        -5,-8, -5,2/*mean (0.0629667), correlation (0.457096)*/,
        7,-6, 10,12/*mean (0.0653846), correlation (0.445623)*/,
        -9,-13, -8,-8/*mean (0.0858749), correlation (0.449789)*/,
        -5,-13, -5,-2/*mean (0.122402), correlation (0.450201)*/,
        8,-8, 9,-13/*mean (0.125416), correlation (0.453224)*/,
        -9,-11, -9,0/*mean (0.130128), correlation (0.458724)*/,
        1,-8, 1,-2/*mean (0.132467), correlation (0.440133)*/,
        7,-4, 9,1/*mean (0.132692), correlation (0.454)*/,
        -2,1, -1,-4/*mean (0.135695), correlation (0.455739)*/,
        11,-6, 12,-11/*mean (0.142904), correlation (0.446114)*/,
        -12,-9, -6,4/*mean (0.146165), correlation (0.451473)*/,
        3,7, 7,12/*mean (0.147627), correlation (0.456643)*/,
        5,5, 10,8/*mean (0.152901), correlation (0.455036)*/,
        0,-4, 2,8/*mean (0.167083), correlation (0.459315)*/,
        -9,12, -5,-13/*mean (0.173234), correlation (0.454706)*/,
        0,7, 2,12/*mean (0.18312), correlation (0.433855)*/,
        -1,2, 1,7/*mean (0.185504), correlation (0.443838)*/,
        5,11, 7,-9/*mean (0.185706), correlation (0.451123)*/,
        3,5, 6,-8/*mean (0.188968), correlation (0.455808)*/,
        -13,-4, -8,9/*mean (0.191667), correlation (0.459128)*/,
        -5,9, -3,-3/*mean (0.193196), correlation (0.458364)*/,
        -4,-7, -3,-12/*mean (0.196536), correlation (0.455782)*/,
        6,5, 8,0/*mean (0.1972), correlation (0.450481)*/,
        -7,6, -6,12/*mean (0.199438), correlation (0.458156)*/,
        -13,6, -5,-2/*mean (0.211224), correlation (0.449548)*/,
        1,-10, 3,10/*mean (0.211718), correlation (0.440606)*/,
        4,1, 8,-4/*mean (0.213034), correlation (0.443177)*/,
        -2,-2, 2,-13/*mean (0.234334), correlation (0.455304)*/,
        2,-12, 12,12/*mean (0.235684), correlation (0.443436)*/,
        -2,-13, 0,-6/*mean (0.237674), correlation (0.452525)*/,
        4,1, 9,3/*mean (0.23962), correlation (0.444824)*/,
        -6,-10, -3,-5/*mean (0.248459), correlation (0.439621)*/,
        -3,-13, -1,1/*mean (0.249505), correlation (0.456666)*/,
        7,5, 12,-11/*mean (0.00119208), correlation (0.495466)*/,
        4,-2, 5,-7/*mean (0.00372245), correlation (0.484214)*/,
        -13,9, -9,-5/*mean (0.00741116), correlation (0.499854)*/,
        7,1, 8,6/*mean (0.0208952), correlation (0.499773)*/,
        7,-8, 7,6/*mean (0.0220085), correlation (0.501609)*/,
        -7,-4, -7,1/*mean (0.0233806), correlation (0.496568)*/,
        -8,11, -7,-8/*mean (0.0236505), correlation (0.489719)*/,
        -13,6, -12,-8/*mean (0.0268781), correlation (0.503487)*/,
        2,4, 3,9/*mean (0.0323324), correlation (0.501938)*/,
        10,-5, 12,3/*mean (0.0399235), correlation (0.494029)*/,
        -6,-5, -6,7/*mean (0.0420153), correlation (0.486579)*/,
        8,-3, 9,-8/*mean (0.0548021), correlation (0.484237)*/,
        2,-12, 2,8/*mean (0.0616622), correlation (0.496642)*/,
        -11,-2, -10,3/*mean (0.0627755), correlation (0.498563)*/,
        -12,-13, -7,-9/*mean (0.0829622), correlation (0.495491)*/,
        -11,0, -10,-5/*mean (0.0843342), correlation (0.487146)*/,
        5,-3, 11,8/*mean (0.0929937), correlation (0.502315)*/,
        -2,-13, -1,12/*mean (0.113327), correlation (0.48941)*/,
        -1,-8, 0,9/*mean (0.132119), correlation (0.467268)*/,
        -13,-11, -12,-5/*mean (0.136269), correlation (0.498771)*/,
        -10,-2, -10,11/*mean (0.142173), correlation (0.498714)*/,
        -3,9, -2,-13/*mean (0.144141), correlation (0.491973)*/,
        2,-3, 3,2/*mean (0.14892), correlation (0.500782)*/,
        -9,-13, -4,0/*mean (0.150371), correlation (0.498211)*/,
        -4,6, -3,-10/*mean (0.152159), correlation (0.495547)*/,
        -4,12, -2,-7/*mean (0.156152), correlation (0.496925)*/,
        -6,-11, -4,9/*mean (0.15749), correlation (0.499222)*/,
        6,-3, 6,11/*mean (0.159211), correlation (0.503821)*/,
        -13,11, -5,5/*mean (0.162427), correlation (0.501907)*/,
        11,11, 12,6/*mean (0.16652), correlation (0.497632)*/,
        7,-5, 12,-2/*mean (0.169141), correlation (0.484474)*/,
        -1,12, 0,7/*mean (0.169456), correlation (0.495339)*/,
        -4,-8, -3,-2/*mean (0.171457), correlation (0.487251)*/,
        -7,1, -6,7/*mean (0.175), correlation (0.500024)*/,
        -13,-12, -8,-13/*mean (0.175866), correlation (0.497523)*/,
        -7,-2, -6,-8/*mean (0.178273), correlation (0.501854)*/,
        -8,5, -6,-9/*mean (0.181107), correlation (0.494888)*/,
        -5,-1, -4,5/*mean (0.190227), correlation (0.482557)*/,
        -13,7, -8,10/*mean (0.196739), correlation (0.496503)*/,
        1,5, 5,-13/*mean (0.19973), correlation (0.499759)*/,
        1,0, 10,-13/*mean (0.204465), correlation (0.49873)*/,
        9,12, 10,-1/*mean (0.209334), correlation (0.49063)*/,
        5,-8, 10,-9/*mean (0.211134), correlation (0.503011)*/,
        -1,11, 1,-13/*mean (0.212), correlation (0.499414)*/,
        -9,-3, -6,2/*mean (0.212168), correlation (0.480739)*/,
        -1,-10, 1,12/*mean (0.212731), correlation (0.502523)*/,
        -13,1, -8,-10/*mean (0.21327), correlation (0.489786)*/,
        8,-11, 10,-6/*mean (0.214159), correlation (0.488246)*/,
        2,-13, 3,-6/*mean (0.216993), correlation (0.50287)*/,
        7,-13, 12,-9/*mean (0.223639), correlation (0.470502)*/,
        -10,-10, -5,-7/*mean (0.224089), correlation (0.500852)*/,
        -10,-8, -8,-13/*mean (0.228666), correlation (0.502629)*/,
        4,-6, 8,5/*mean (0.22906), correlation (0.498305)*/,
        3,12, 8,-13/*mean (0.233378), correlation (0.503825)*/,
        -4,2, -3,-3/*mean (0.234323), correlation (0.476692)*/,
        5,-13, 10,-12/*mean (0.236392), correlation (0.475462)*/,
        4,-13, 5,-1/*mean (0.236842), correlation (0.504132)*/,
        -9,9, -4,3/*mean (0.236977), correlation (0.497739)*/,
        0,3, 3,-9/*mean (0.24314), correlation (0.499398)*/,
        -12,1, -6,1/*mean (0.243297), correlation (0.489447)*/,
        3,2, 4,-8/*mean (0.00155196), correlation (0.553496)*/,
        -10,-10, -10,9/*mean (0.00239541), correlation (0.54297)*/,
        8,-13, 12,12/*mean (0.0034413), correlation (0.544361)*/,
        -8,-12, -6,-5/*mean (0.003565), correlation (0.551225)*/,
        2,2, 3,7/*mean (0.00835583), correlation (0.55285)*/,
        10,6, 11,-8/*mean (0.00885065), correlation (0.540913)*/,
        6,8, 8,-12/*mean (0.0101552), correlation (0.551085)*/,
        -7,10, -6,5/*mean (0.0102227), correlation (0.533635)*/,
        -3,-9, -3,9/*mean (0.0110211), correlation (0.543121)*/,
        -1,-13, -1,5/*mean (0.0113473), correlation (0.550173)*/,
        -3,-7, -3,4/*mean (0.0140913), correlation (0.554774)*/,
        -8,-2, -8,3/*mean (0.017049), correlation (0.55461)*/,
        4,2, 12,12/*mean (0.01778), correlation (0.546921)*/,
        2,-5, 3,11/*mean (0.0224022), correlation (0.549667)*/,
        6,-9, 11,-13/*mean (0.029161), correlation (0.546295)*/,
        3,-1, 7,12/*mean (0.0303081), correlation (0.548599)*/,
        11,-1, 12,4/*mean (0.0355151), correlation (0.523943)*/,
        -3,0, -3,6/*mean (0.0417904), correlation (0.543395)*/,
        4,-11, 4,12/*mean (0.0487292), correlation (0.542818)*/,
        2,-4, 2,1/*mean (0.0575124), correlation (0.554888)*/,
        -10,-6, -8,1/*mean (0.0594242), correlation (0.544026)*/,
        -13,7, -11,1/*mean (0.0597391), correlation (0.550524)*/,
        -13,12, -11,-13/*mean (0.0608974), correlation (0.55383)*/,
        6,0, 11,-13/*mean (0.065126), correlation (0.552006)*/,
        0,-1, 1,4/*mean (0.074224), correlation (0.546372)*/,
        -13,3, -9,-2/*mean (0.0808592), correlation (0.554875)*/,
        -9,8, -6,-3/*mean (0.0883378), correlation (0.551178)*/,
        -13,-6, -8,-2/*mean (0.0901035), correlation (0.548446)*/,
        5,-9, 8,10/*mean (0.0949843), correlation (0.554694)*/,
        2,7, 3,-9/*mean (0.0994152), correlation (0.550979)*/,
        -1,-6, -1,-1/*mean (0.10045), correlation (0.552714)*/,
        9,5, 11,-2/*mean (0.100686), correlation (0.552594)*/,
        11,-3, 12,-8/*mean (0.101091), correlation (0.532394)*/,
        3,0, 3,5/*mean (0.101147), correlation (0.525576)*/,
        -1,4, 0,10/*mean (0.105263), correlation (0.531498)*/,
        3,-6, 4,5/*mean (0.110785), correlation (0.540491)*/,
        -13,0, -10,5/*mean (0.112798), correlation (0.536582)*/,
        5,8, 12,11/*mean (0.114181), correlation (0.555793)*/,
        8,9, 9,-6/*mean (0.117431), correlation (0.553763)*/,
        7,-4, 8,-12/*mean (0.118522), correlation (0.553452)*/,
        -10,4, -10,9/*mean (0.12094), correlation (0.554785)*/,
        7,3, 12,4/*mean (0.122582), correlation (0.555825)*/,
        9,-7, 10,-2/*mean (0.124978), correlation (0.549846)*/,
        7,0, 12,-2/*mean (0.127002), correlation (0.537452)*/,
        -1,-6, 0,-11/*mean (0.127148), correlation (0.547401)*/
    };

    // 特征点提取器的构造函数
    // 构造函数输入的参数:
    // 指定要提取的特征点数目, 指定图像金字塔的缩放系数, 指定图像金字塔的层数
    // _iniThFAST: 指定初始的 FAST 特征点提取参数, 用于提取出最明显的角点
    // _minTHFAST: 如果初始阈值没有检测到角点, 降低到这个阈值提取出弱一点的角点
    ORBextractor::ORBextractor(int _nfeatures, float _scaleFactor, int _nlevels, int _iniThFAST, int _minThFAST):
        nfeatures(_nfeatures), scaleFactor(_scaleFactor), nlevels(_nlevels),
        iniThFAST(_iniThFAST), minThFAST(_minThFAST)  // 初始化成员变量列表
    {

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

        // 下面的两个参数保存的是上面两个参数的倒数
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

        // 成员变量 pattern 的长度, 也就是点的个数, 这里的 512 表示 512 个点(所以上面的数组中存储的坐标是 256 * 2 * 2)
        constexpr int npoints = 512;
        // 获取用于计算 BRIEF 描述子的随机采样点 点集 头指针
        // 注意到 pattern0 的数据类型为 Points*, bit_pattern_31_ 是 int[] 型, 所以这里需要进行强制类型转换
        const auto pattern0 = reinterpret_cast<const Point*>(bit_pattern_31_);
        // 使用 std::back_inserter 的目的是可以快覆盖掉这个容器 pattern 之前的数据
        // 将在全局变量区域的, int 格式的随机采样点以 cv::point 格式复制到当前类对象中的成员变量中
        std::copy(pattern0, pattern0 + npoints, std::back_inserter(pattern));

        // 下面的内容是和特征点的旋转计算有关的
        // This is for orientation
        // 预先计算图像 patch 中行的结束位置
        // pre-compute the end of a row in a circular patch
        // + 1 中的 1 表示那个圆的中间行
        umax.resize(HALF_PATCH_SIZE + 1);

        // cvFloor 返回不大于参数的最大整数值, cvCeil 返回不小于参数的最小整数值, cvRound 则是四舍五入
        // v: 循环辅助变量, v0: 辅助变量, vmax: 计算圆的最大行号, + 1 是把中间行也考虑进行了
        // NOTICE: 注意这里的最大行号指的是计算时的最大行号, 此行和圆的角点在 45 度圆心角的一边上
        // NOTICE：之所以这样选择是因为圆周上的对称特性
        int v, v0, vmax = cvFloor(HALF_PATCH_SIZE * sqrt(2.f) / 2 + 1);
        // 二分之根号二就是对应 45 度圆心角
        int vmin = cvCeil(HALF_PATCH_SIZE * sqrt(2.f) / 2);
        // 半径的平方
        const double hp2 = HALF_PATCH_SIZE * HALF_PATCH_SIZE;
        // 利用圆的方程计算每行像素的 u 坐标边界( max )
        for (v = 0; v <= vmax; ++v)
            // 结果都是大于 0 的结果, 表示 x 坐标在这一行的边界
                umax[v] = cvRound(sqrt(hp2 - v * v));

        // Make sure we are symmetric
        // 使用对称的方式计算上四分之一的圆周上的umax, 目的是为了保持严格的对称
        // 如果使用 cvRound 就会很容易出现不对称, 就无法满足旋转不变性
        for (v = HALF_PATCH_SIZE, v0 = 0; v >= vmin; --v)
        {
            while (umax[v0] == umax[v0 + 1])
                ++v0;
            umax[v] = v0;
            ++v0;
        }

    }

}

```

```c++
#include "ORBextractor.h"
```

```c++
#ifndef TRACKING_H
#define TRACKING_H


#include<opencv2/core/core.hpp>
#include<opencv2/features2d/features2d.hpp>

#include "System.h"
#include "Viewer.h"
#include "KeyFrameDatabase.h"
#include "Map.h"
#include "FrameDrawer.h"
#include "MapDrawer.h"
#include "Initializer.h"

#include "ORBVocabulary.h"
#include "ORBextractor.h"


using namespace std;


namespace ORB_SLAM2
{
    // 要用到的其他类的前向声明
    // 在该项目代码中，类之间可能存在复杂的相互依赖关系
    // 例如, System 类可能需要引用 Viewer 类, 而 Viewer 类可能又引用 System 类, 前向声明能够打破这种直接的依赖关系
    // 如果不使用前向声明, 而直接包含头文件, 可能会导致头文件之间的循环依赖, 进而导致编译错误或头文件包含的死循环
    // 通过前向声明, 编译器不会立即要求完整定义, 只需要一个简单的类声明, 防止了这些问题
    class Viewer;
    class FrameDrawer;
    class Map;
    class LocalMapping;
    class LoopClosing;
    class System;

    class Tracking
    {
    public:
        // 构造函数
        // 构造函数的参数如下: 系统实例, BOW字典, 帧绘制器, 地图点绘制器, 地图句柄, 关键帧产生的词袋数据库, 配置文件路径, 传感器类型
        Tracking(System* pSys, ORBVocabulary* pVoc, FrameDrawer* pFrameDrawer, MapDrawer* pMapDrawer,
                 Map* pMap, KeyFrameDatabase* pKFDB, const string &strSettingPath, int sensor);

        // 跟踪状态类型
        // Tracking states
        enum eTrackingState
        {
            SYSTEM_NOT_READY=-1,  // 系统没有准备好的状态, 一般就是在启动后加载配置文件和词典文件时候的状态
            NO_IMAGES_YET=0,  // 当前无图像
            NOT_INITIALIZED=1,  // 有图像但是没有完成初始化
            OK=2,  // 正常时候的工作状态
            LOST=3  // 系统已经跟丢了的状态
        };

        // 跟踪状态
        eTrackingState mState;

        // 传感器类型: MONOCULAR, STEREO, RGBD
        // Input sensor
        int mSensor;

        // 标记当前系统是处于 SLAM 状态还是纯定位状态
        // True if local mapping is deactivated and we are performing only localization
        bool mbOnlyTracking;

    protected:

        // 当进行纯定位时才会有的一个变量, 为 false 表示该帧匹配了很多的地图点, 跟踪是正常的
        // 如果少于10个则为 true, 表示快要完蛋了
        // In case of performing only localization, this flag is true when there are no matches to points in the map.
        // Still tracking will continue if there are enough matches with temporal points.
        // In that case we are doing visual odometry.
        // The system will try to do relocalization to recover "zero-drift" localization to the map.
        bool mbVO;

        // ORB 特征提取器, 不管是单目还是双目, mpORBextractorLeft 都要用到
        // 如果是双目, 则要用到 mpORBextractorRight
        // NOTICE: 如果是单目, 在初始化的时候使用 mpIniORBextractor 而不是 mpORBextractorLeft
        // mpIniORBextractor 提取的特征点个数是 mpORBextractorLeft 的两倍

        // 作者自己编写和改良的 ORB 特征点提取器
        // ORB
        ORBextractor *mpORBextractorLeft, *mpORBextractorRight;
        // 在初始化的时候使用的特征点提取器, 其提取道德特征点个数会更多
        ORBextractor *mpIniORBextractor;

        // BoW 词袋模型相关
        // BoW
        // ORB 特征字典
        ORBVocabulary *mpORBVocabulary;
        // 当前系统运行的时候, 关键帧所产生的数据库
        KeyFrameDatabase *mpKeyFrameDB;

        // 单目初始器
        // Initalization (only for monocular)
        Initializer* mpInitializer;

        // 指向系统实例的指针
        // System
        System *mpSystem;

        // 可视化器相关
        // Drawers
        // 可视化器对象句柄
        Viewer *mpViewer;
        // 帧绘制器句柄
        FrameDrawer *mpFrameDrawer;
        // 地图绘制器句柄
        MapDrawer *mpMapDrawer;

        // (全局)地图句柄
        // Map
        Map *mpMap;

        // 相机的参数矩阵相关
        // Calibration matrix
        // 相机的内参数矩阵
        cv::Mat mK;
        // 相机的去畸变参数
        cv::Mat mDistCoef;
        // 相机的基线长度 * 相机的焦距
        float mbf;

        // New KeyFrame rules (according to fps)
        // 新建关键帧和重定位中用来判断最小最大时间间隔, 和帧率有关
        int mMinFrames;
        int mMaxFrames;

        // 用于区分远点和金点的阈值, 近点认为可信度比较高, 远点则要求在两个关键帧中得到匹配
        // Threshold close/far points.
        // Points seen as close by the stereo/RGBD sensor are considered reliable and inserted from just one frame.
        // Far points requiere a match in two keyframes.
        float mThDepth;

        // 深度缩放因子, 链接深度值和具体深度值的参数, 只对 RGBD 输入有效
        // For RGB-D inputs only. For some datasets (e.g. TUM) the depthmap values are scaled.
        float mDepthMapFactor;

        // 上一次重定位的那一帧的ID
        unsigned int mnLastRelocFrameId;

        // RGB 图像的颜色通道顺序
        // Color order (true RGB, false BGR, ignored if grayscale)
        bool mbRGB;

      };

}

#endif //TRACKING_H

```

```c++
        // Tracking 过程都会用到 mpORBextractorLeft 作为特征点提取器
        mpORBextractorLeft = new ORBextractor(nFeatures,fScaleFactor,nLevels,fIniThFAST,fMinThFAST);

        // 如果是双目, Tracking 过程中还会用到 mpORBextractorRight 作为右目特征点提取器
        if(sensor==System::STEREO)
            mpORBextractorRight = new ORBextractor(nFeatures,fScaleFactor,nLevels,fIniThFAST,fMinThFAST);

        // 在单目初始化的时候, 会用 mpIniORBextractor 来作为特征点提取器
        if(sensor==System::MONOCULAR)
            mpIniORBextractor = new ORBextractor(2*nFeatures,fScaleFactor,nLevels,fIniThFAST,fMinThFAST);
```

```c++
// 追踪线程


#include "Tracking.h"

#include"Map.h"
#include"FrameDrawer.h"

// #include<mutex>
// #include<iostream>
#include <opencv2/core/core.hpp>
#include <opencv2/features2d/features2d.hpp>


using namespace std;

namespace ORB_SLAM2
{

    // 构造函数
    // 构造函数的参数如下: 系统实例, BOW字典, 帧绘制器, 地图点绘制器, 地图句柄, 关键帧产生的词袋数据库, 配置文件路径, 传感器类型
    Tracking::Tracking(System *pSys, ORBVocabulary* pVoc, FrameDrawer *pFrameDrawer, MapDrawer *pMapDrawer,
                       Map *pMap, KeyFrameDatabase* pKFDB, const string &strSettingPath, const int sensor):
        mState(NO_IMAGES_YET), mSensor(sensor), mbOnlyTracking(false), mbVO(false), mpORBVocabulary(pVoc),
        mpKeyFrameDB(pKFDB), mpInitializer(static_cast<Initializer*>(nullptr)), mpSystem(pSys), mpViewer(nullptr),
        mpFrameDrawer(pFrameDrawer), mpMapDrawer(pMapDrawer), mpMap(pMap), mnLastRelocFrameId(0)
    {
        // Step 1 从配置文件中加载相机参数
        // Load camera parameters from settings file
        cv::FileStorage fSettings(strSettingPath, cv::FileStorage::READ);
        float fx = fSettings["Camera.fx"];
        float fy = fSettings["Camera.fy"];
        float cx = fSettings["Camera.cx"];
        float cy = fSettings["Camera.cy"];

        // Step 1-1 构造相机内参矩阵
        //     |fx  0   cx|
        // K = |0   fy  cy|
        //     |0   0   1 |
        cv::Mat K = cv::Mat::eye(3,3,CV_32F);
        K.at<float>(0,0) = fx;
        K.at<float>(1,1) = fy;
        K.at<float>(0,2) = cx;
        K.at<float>(1,2) = cy;
        K.copyTo(mK);

        // Step 1-2 图像矫正系数
        // [k1, k2, p1, p2, k3]
        cv::Mat DistCoef(4,1,CV_32F);
        DistCoef.at<float>(0) = fSettings["Camera.k1"];
        DistCoef.at<float>(1) = fSettings["Camera.k2"];
        DistCoef.at<float>(2) = fSettings["Camera.p1"];
        DistCoef.at<float>(3) = fSettings["Camera.p2"];
        // 有些相机的畸变系数中会没有 k3 项
        const float k3 = fSettings["Camera.k3"];
        if(k3!=0)
        {
            DistCoef.resize(5);
            DistCoef.at<float>(4) = k3;
        }
        DistCoef.copyTo(mDistCoef);

        // 双目摄像头baseline * fx 50
        mbf = fSettings["Camera.bf"];

        float fps = fSettings["Camera.fps"];
        if(fps==0)
            fps=30;

        // Max/Min Frames to insert keyframes and to check relocalisation
        // 新建关键帧和重定位中用来判断最小最大时间间隔, 和帧率有关
        mMinFrames = 0;
        mMaxFrames = static_cast<int>(fps);

        // Step 1-3 输出
        cout << endl << "Camera Parameters: " << endl;
        cout << "- fx: " << fx << endl;
        cout << "- fy: " << fy << endl;
        cout << "- cx: " << cx << endl;
        cout << "- cy: " << cy << endl;
        cout << "- k1: " << DistCoef.at<float>(0) << endl;
        cout << "- k2: " << DistCoef.at<float>(1) << endl;
        if(DistCoef.rows==5)
            cout << "- k3: " << DistCoef.at<float>(4) << endl;
        cout << "- p1: " << DistCoef.at<float>(2) << endl;
        cout << "- p2: " << DistCoef.at<float>(3) << endl;
        cout << "- fps: " << fps << endl;

        // 1:RGB 0:BGR
        int nRGB = fSettings["Camera.RGB"];
        // RGB 图像的颜色通道顺序
        mbRGB = nRGB;

        if(mbRGB)
            cout << "- color order: RGB (ignored if grayscale)" << endl;
        else
            cout << "- color order: BGR (ignored if grayscale)" << endl;

        // Step 2 加载 ORB 特征点有关的参数, 并新建特征点提取器
        // Load ORB parameters

        // 每一帧提取的特征点数 1000
        int nFeatures = fSettings["ORBextractor.nFeatures"];
        // 图像建立金字塔时的变化尺度 1.2
        float fScaleFactor = fSettings["ORBextractor.scaleFactor"];
        // 尺度金字塔的层数 8
        int nLevels = fSettings["ORBextractor.nLevels"];
        // 提取FAST特征点的默认阈值 20
        int fIniThFAST = fSettings["ORBextractor.iniThFAST"];
        // 如果默认阈值提取不出足够的 FAST 特征点, 则使用最小阈值 8
        int fMinThFAST = fSettings["ORBextractor.minThFAST"];

        // Tracking 过程都会用到 mpORBextractorLeft 作为特征点提取器
        mpORBextractorLeft = new ORBextractor(nFeatures,fScaleFactor,nLevels,fIniThFAST,fMinThFAST);

        // 如果是双目, Tracking 过程中还会用到 mpORBextractorRight 作为右目特征点提取器
        if(sensor==System::STEREO)
            mpORBextractorRight = new ORBextractor(nFeatures,fScaleFactor,nLevels,fIniThFAST,fMinThFAST);

        // 在单目初始化的时候, 会用 mpIniORBextractor 来作为特征点提取器
        if(sensor==System::MONOCULAR)
            mpIniORBextractor = new ORBextractor(2*nFeatures,fScaleFactor,nLevels,fIniThFAST,fMinThFAST);

        cout << endl  << "ORB Extractor Parameters: " << endl;
        cout << "- Number of Features: " << nFeatures << endl;
        cout << "- Scale Levels: " << nLevels << endl;
        cout << "- Scale Factor: " << fScaleFactor << endl;
        cout << "- Initial Fast Threshold: " << fIniThFAST << endl;
        cout << "- Minimum Fast Threshold: " << fMinThFAST << endl;

        if(sensor==System::STEREO || sensor==System::RGBD)
        {
            // 判断一个 3D 点远/近的阈值 mbf * 35 / fx
            // ThDepth 其实就是表示基线长度的多少倍
            mThDepth = mbf*(float)fSettings["ThDepth"]/fx;
            cout << endl << "Depth Threshold (Close/Far Points): " << mThDepth << endl;
        }

        if(sensor==System::RGBD)
        {
            // 深度相机 disparity 转化为 depth 时的因子
            mDepthMapFactor = fSettings["DepthMapFactor"];
            if(fabs(mDepthMapFactor)<1e-5)
                mDepthMapFactor=1;
            else
                mDepthMapFactor = 1.0f/mDepthMapFactor;
        }

    }

}

```

```c++
# 创建一个名为${PROJECT_SOURCE_DIR}的共享库(SHARED表示生成动态链接库), 并将指定的源文件添加到库中
add_library(${PROJECT_NAME} SHARED
        src/System.cpp
        src/KeyFrameDatabase.cpp
        src/Map.cpp
        src/FrameDrawer.cpp
        src/MapDrawer.cpp
        src/Tracking.cpp
        src/ORBextractor.cpp
)
```

```c++
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

# 创建一个名为${PROJECT_SOURCE_DIR}的共享库(SHARED表示生成动态链接库), 并将指定的源文件添加到库中
add_library(${PROJECT_NAME} SHARED
        src/System.cpp
        src/KeyFrameDatabase.cpp
        src/Map.cpp
        src/FrameDrawer.cpp
        src/MapDrawer.cpp
        src/Tracking.cpp
        src/ORBextractor.cpp
)

# 指定${PROJECT_SOURCE_DIR}库链接的其他库
target_link_libraries(${PROJECT_NAME}
        ${OpenCV_LIBS}  # OpenCV库
        ${EIGEN3_LIBS}  # Eigen3库
        ${Pangolin_LIBRARIES}  # Pangolin库
        # 还链接了位于Thirdparty/DBoW2和Thirdparty/g2o的第三方库
        ${PROJECT_SOURCE_DIR}/Thirdparty/DBoW3/lib/libDBoW3.so
        #${PROJECT_SOURCE_DIR}/Thirdparty/g2o/lib/libg2o.so
)

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
target_link_libraries(mono_kitti ${PROJECT_NAME})
#add_executable(mono_euroc Examples/Monocular/mono_euroc.cc)
#target_link_libraries(mono_euroc ${PROJECT_NAME})

```


