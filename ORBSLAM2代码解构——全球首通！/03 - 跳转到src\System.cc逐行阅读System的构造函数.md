# System.cc文件内的构造函数



在类内的成员变量这一块，就已经需要跳转到其他的文件内了



```c++
    // 系统的构造函数, 将会启动其他的线程
    // 第一个System是类名, 表示这是ORB_SLAM2::System类的构造函数
    // 第二个System是构造函数的名称, 必须与类名相同
    // 构造函数的参数如下: 词典文件路径, 配置文件路径, 传感器类型, 是否使用可视化界面
    System::System(const string &strVocFile, const string &strSettingsFile,
                   eSensor sensor, bool bUseViewer):
                   // 在构造函数体内, 成员初始化列表用于初始化类的成员变量
                   // 在构造函数执行前设置变量的初始值, 比在构造函数体内赋值更高效
                   mSensor(sensor), mpViewer(static_cast<Viewer*>(nullptr)), mbReset(false),
                   mbActivateLocalizationMode(false), mbDeactivateLocalizationMode(false)
```



### Examples/Stereo/stereo_kitti.cpp

这里主要是 include 了 System.h

```c++

#include <fstream>
#include <iomanip>
#include <iostream>
#include <opencv2/core/core.hpp>

#include "System.h"

using namespace std;


// 加载图像
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
    ORB_SLAM2::System SLAM(argv[1],argv[2],ORB_SLAM2::System::STEREO,true);
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

```c++
    // 系统的构造函数, 将会启动其他的线程
    // 第一个System是类名, 表示这是ORB_SLAM2::System类的构造函数
    // 第二个System是构造函数的名称, 必须与类名相同
    // 构造函数的参数如下: 词典文件路径, 配置文件路径, 传感器类型, 是否使用可视化界面
    System::System(const string &strVocFile, const string &strSettingsFile,
                   eSensor sensor, bool bUseViewer):
                   // 在构造函数体内, 成员初始化列表用于初始化类的成员变量
                   // 在构造函数执行前设置变量的初始值, 比在构造函数体内赋值更高效
                   mSensor(sensor), mpViewer(static_cast<Viewer*>(nullptr)), mbReset(false),
                   mbActivateLocalizationMode(false), mbDeactivateLocalizationMode(false)
```
