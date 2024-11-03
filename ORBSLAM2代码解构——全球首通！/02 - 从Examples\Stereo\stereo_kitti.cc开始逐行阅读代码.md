# 先从stereo_kitti.cc这个文件开始逐行阅读

## 注: 

**注:** 我阅读代码的习惯是从零开始阅读, 因此在文件一开始对于外部库的引入这部分, 是根据所阅读到的代码段需要什么库, 再引入什么库, 而不是一开始就把所有可能用的库引入

**现在开始梳理 ORB-SLAM2 实现在KITTI数据集上使用双目进行定位的完整流程!!!**

首先是预先声明了函数 LoadImage

```c++
void LoadImages (const string &strPathToSequence, vector<string> &vstrImageLeft,
                 vector<string> &vstrImageRight, vector<double> &vTimestamps);
```

具体实现在文件的最后面

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
