


```c++
    // 特征点提取器的构造函数
    // 构造函数输入的参数:
    // 指定要提取的特征点数目, 指定图像金字塔的缩放系数, 指定图像金字塔的层数
    // _iniThFAST: 指定初始的FAST特征点提取参数, 用于提取出最明显的角点
    // _minTHFAST: 如果初始阈值没有检测到角点, 降低到这个阈值提取出弱一点的角点
    ORBextractor::ORBextractor(int _nfeatures, float _scaleFactor, int _nlevels, float _iniThFAST, float _minThFAST):
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

        // 成员变量pattern的长度, 也就是点的个数, 这里的512表示512个点(所以上面的数组中存储的坐标是256*2*2)
        const int npoints = 512;
        // 获取用于计算BRIEF描述子的随机采样点 点集 头指针
        // 注意到pattern0的数据类型为Points*, bit_pattern_31_是int[]型, 所以这里需要进行强制类型转换
        const auto pattern0 = reinterpret_cast<const Point*>(bit_pattern_31_);
        // 使用std::back_inserter的目的是可以快覆盖掉这个容器pattern之前的数据
        // 将在全局变量区域的、int格式的随机采样点以cv::point格式复制到当前类对象中的成员变量中
        std::copy_n(pattern0, pattern0 + npoints, std::back_inserter(pattern));

        // This is for orientation
        // 下面的内容是和特征点的旋转计算有关的
        // pre-compute the end of a row in a circular patch
        // 预先计算圆形patch中行的结束位置
        umax.resize(HALF_PATCH_SIZE + 1);  // +1中的1表示那个圆的中间行

        // cvFloor返回不大于参数的最大整数值, cvCeil返回不小于参数的最小整数值, cvRound则是四舍五入
        int v, v0;
        // 计算圆的最大行号, +1是把中间行也给考虑进去了
        int vmax = cvFloor(HALF_PATCH_SIZE * sqrt(2.f) / 2 + 1);
        int vmin = cvCeil(HALF_PATCH_SIZE * sqrt(2.f) / 2);
        // 半径的平方
        const double hp2 = HALF_PATCH_SIZE * HALF_PATCH_SIZE;

        // 利用圆的方程计算每行像素的u坐标边界(max)
        for(v=0; v<=vmax; v++)
        {
            umax[v] = cvRound(sqrt(hp2 - v * v));  // 结果都是大于0的结果, 表示x坐标在这一行的边界
        }

        // Make sure we are symmetric
        // 使用对称的方式计算上四分之一的圆周上的umax, 目的是为了保持严格的对称
        for(v=HALF_PATCH_SIZE, v0=0; v>=vmin; v--)
        {
            while(umax[v0]==umax[v0+1])
            {
                v0++;
            }
            umax[v] = v0;
            v0++;
        }
    }
```

```c++
    // ORB特征点提取器
    class ORBextractor
    {
    public:
        enum {HARRIS_SCORE=0, FAST_SCORE=1};

        // 构造函数
        // nfeatures: 指定要提取出来的特征点数目
        // scaleFactor: 图像金字塔的缩放系数
        // nlevels: 指定需要提取特征点的图像金字塔层
        // iniThFAST: 初始的默认 FAST 响应值阈值
        // minThFAST: 较小的 FAST 响应值阈值
        ORBextractor(int nfeatures, float scaleFactor, int nlevels, float iniThFAST, float minThFAST);

        // 析构函数
        ~ORBextractor(){};

        // 用来存储图像金字塔的变量, 一个元素存储一层图像
        std::vector<cv::Mat> mvImagePyramid;

    protected:

        std::vector<cv::Point> pattern;  // 用于计算描述子的随机采样点集合

        int nfeatures;  // 整个图像金字塔中, 要提取的特征点数目
        double scaleFactor;  // 图像金字塔中, 层与层之间的缩放因子
        int nlevels;  // 图像金字塔的层数
        float iniThFAST;  // 初始的 FAST 响应值阈值
        float minThFAST;  // 最小的 FAST 响应值阈值

        std::vector<int> mnFeaturesPerLevel;  // 分配到每层图像中, 要提取的特征点数目

        std::vector<int> umax;  // 计算特征点方向时, 有个圆形的图像区域, vector 中存储了每行 u 轴的边界 (四分之一, 其他部分通过对称获得)

        std::vector<float> mvScaleFactor;  // 每层图像的缩放因子
        std::vector<float> mvInvScaleFactor;  // 每层缩放因子的倒数
        std::vector<float> mvLevelSigma2;  // Sigma2: 每层图像相对于底层图像缩放倍数的平方
        std::vector<float> mvInvLevelSigma2;  // Sigma2 的倒数
     };
```



