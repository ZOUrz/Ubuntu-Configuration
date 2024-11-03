# 先从stereo_kitti.cc这个文件开始逐行阅读

**注:** 我阅读代码的习惯是从零开始阅读, 因此在文件一开始对于外部库的引入这部分, 是根据所阅读到的代码段需要什么库, 再引入什么库, 而不是一开始就把所有可能用的库引入

**现在开始梳理 ORB-SLAM2 实现在KITTI数据集上使用双目进行定位的完整流程!!!**

## 1. LoadImage

首先是预先声明了函数 LoadImage

```c++
void LoadImages (const string &strPathToSequence, vector<string> &vstrImageLeft,
                 vector<string> &vstrImageRight, vector<double> &vTimestamps);
```

具体的函数实现在文件的最后面

```c++
void LoadImages(const string &strPathToSequence, vector<string> &vstrImageLeft,
                vector<string> &vstrImageRight, vector<double> &vTimestamps)
{
    // Step 0 读取时间戳文件
    ifstream fTimes;
    string strPathTimeFile = strPathToSequence + "/times.txt";
    fTimes.open(strPathTimeFile.c_str());
    while(!fTimes.eof())
    {
        string s;
        getline(fTimes,s);
        // 当该行不为空的时候执行
        if(!s.empty())
        {
            stringstream ss;
            ss << s;
            double t;
            ss >> t;
            // 保存时间戳
            vTimestamps.push_back(t);
        }
    }

    // Step 1 生成左右目图像序列中每一张图像的文件名
    string strPrefixLeft = strPathToSequence + "/image_0/";
    string strPrefixRight = strPathToSequence + "/image_1/";

    const int nTimes = static_cast<int>(vTimestamps.size());
    vstrImageLeft.resize(nTimes);
    vstrImageRight.resize(nTimes);

    for(int i=0; i<nTimes; i++)
    {
        stringstream ss;
        ss << setfill('0') << setw(6) << i;
        vstrImageLeft[i] = strPrefixLeft + ss.str() + ".png";
        vstrImageRight[i] = strPrefixRight + ss.str() + ".png";
    }
}
```

## 2. 初始化 SLAM 系统前的步骤

进入 main() 函数后, 首先进行终端输入参数的检查, 然后根据输入的数据集路径加载图像

终端命令行输入的指令标准形式为: 

```
./stereo_kitti 词典路径 配置文件路径 数据集图像序列路径
```

```c++
int main(int argc, char **argv)
{
    // Step 0 检查输入参数个数是否足够
    if(argc != 4)
    {
        cerr << endl << "Usage: ./stereo_kitti path_to_vocabulary path_to_settings path_to_sequence" << endl;
        return 1;
    }

    // Step 1 加载图像
    // Retrieve paths to images
    // 用于存储左右目每张图像的路径
    vector<string> vstrImageLeft;
    vector<string> vstrImageRight;
    // 用于存储每张图像的时间戳
    vector<double> vTimestamps;
    LoadImages(string(argv[3]), vstrImageLeft, vstrImageRight, vTimestamps);

    const int nImages = static_cast<int>(vstrImageLeft.size());
}
```

## 3. 加载SLAM系统

下面这这行代码创建一了个 ORB_SLAM2::System 对象, 调用了 ORB_SLAM2::System 类的构造函数

```c++
    // Step 2 加载SLAM系统
    // Create SLAM system. It initializes all system threads and gets ready to process frames.
    ORB_SLAM2::System SLAM(argv[1],argv[2],ORB_SLAM2::System::STEREO,true);
```

这个构造函数是在 System.cc 文件内定义的, 所以我们现在要跳转到 System.cc 这个文件了, stereo_kitti.cc的阅读先告一段落

## 4. 不完整代码

以下是当前对 stereo_kitti.cc 已阅读的部分代码, **注意里include的库是这部分代码所需要的库, 而不是完整文件代码所需要的库**

```c++
#include <opencv2/core/core.hpp>

#include <fstream>
#include <iomanip>
#include <iostream>


using namespace std;


void LoadImages (const string &strPathToSequence, vector<string> &vstrImageLeft,
                 vector<string> &vstrImageRight, vector<double> &vTimestamps);


int main(int argc, char **argv)
{
    // Step 0 检查输入参数个数是否足够
    if(argc != 4)
    {
        cerr << endl << "Usage: ./stereo_kitti path_to_vocabulary path_to_settings path_to_sequence" << endl;
        return 1;
    }

    // Step 1 加载图像
    // Retrieve paths to images
    // 用于存储左右目每张图像的路径
    vector<string> vstrImageLeft;
    vector<string> vstrImageRight;
    // 用于存储每张图像的时间戳
    vector<double> vTimestamps;
    LoadImages(string(argv[3]), vstrImageLeft, vstrImageRight, vTimestamps);

    const int nImages = static_cast<int>(vstrImageLeft.size());

    // Step 2 加载SLAM系统
    // Create SLAM system. It initializes all system threads and gets ready to process frames.
    // ORB_SLAM2::System SLAM(argv[1],argv[2],ORB_SLAM2::System::STEREO,true);
}


void LoadImages(const string &strPathToSequence, vector<string> &vstrImageLeft,
                vector<string> &vstrImageRight, vector<double> &vTimestamps)
{
    // Step 0 读取时间戳文件
    ifstream fTimes;
    string strPathTimeFile = strPathToSequence + "/times.txt";
    fTimes.open(strPathTimeFile.c_str());
    while(!fTimes.eof())
    {
        string s;
        getline(fTimes,s);
        // 当该行不为空的时候执行
        if(!s.empty())
        {
            stringstream ss;
            ss << s;
            double t;
            ss >> t;
            // 保存时间戳
            vTimestamps.push_back(t);
        }
    }

    // Step 1 生成左右目图像序列中每一张图像的文件名
    string strPrefixLeft = strPathToSequence + "/image_0/";
    string strPrefixRight = strPathToSequence + "/image_1/";

    const int nTimes = static_cast<int>(vTimestamps.size());
    vstrImageLeft.resize(nTimes);
    vstrImageRight.resize(nTimes);

    for(int i=0; i<nTimes; i++)
    {
        stringstream ss;
        ss << setfill('0') << setw(6) << i;
        vstrImageLeft[i] = strPrefixLeft + ss.str() + ".png";
        vstrImageRight[i] = strPrefixRight + ss.str() + ".png";
    }
}
```
