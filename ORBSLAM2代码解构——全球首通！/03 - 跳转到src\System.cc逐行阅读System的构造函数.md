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



### Examples/Stereo/stereo_kitti.cc

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

### src/System.cc

需要定义ORBVocabulary()

```c++
// 主进程的实现文件

// 系统

#include <iostream>
#include <opencv2/core/core.hpp>  // 在System.h已经include了

#include "System.h"


using namespace std;


namespace ORB_SLAM2
{
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
    {
        // Output welcome message
        cout << endl <<
        "ORB-SLAM2 Copyright (C) 2014-2016 Raul Mur-Artal, University of Zaragoza." << endl <<
        "This program comes with ABSOLUTELY NO WARRANTY;" << endl  <<
        "This is free software, and you are welcome to redistribute it" << endl <<
        "under certain conditions. See LICENSE.txt." << endl << endl;

        // 输出当前传感器类型
        cout << "Input sensor was set to: ";

        if (mSensor==MONOCULAR)
            cout << "Monocular" << endl;
        else if (mSensor==STEREO)
            cout << "Stereo" << endl;
        else if (mSensor==RGBD)
            cout << "RGB-D" << endl;

        // Check settings file
        // 先将配置文件的路径转换成为字符串, 以只读的方式打开
        cv::FileStorage fsSettings(strSettingsFile.c_str(), cv::FileStorage::READ);
        // 如果打开失败, 就输出调试信息
        if (!fsSettings.isOpened())
        {
            cerr << "Failed to open settings file at: " << strSettingsFile << endl;
            // 然后退出
            exit(-1);
        }

        // Load ORB Vocabulary
        cout << endl << "Loading ORB Vocabulary. This could take a while..." << endl;

        // 建立一个新的ORB字典
        mpVocabulary = new ORBVocabulary();
    }
}

```

### include/System.h

```c++
#ifndef SYSTEM_H
#define SYSTEM_H


#include <mutex>

#include "Viewer.h"


namespace ORB_SLAM2
{


    // 本类的定义
    class System
    {

    public:
        // Input sensor
        // 这个枚举类型用于表示本系统所使用的传感器类型
        enum eSensor
        {
            MONOCULAR = 0,
            STEREO = 1,
            RGBD = 2
        };

        // Initialize the SLAM system. It launches the Local Mapping, Loop Closing and Viewer threads.
        // 构造函数, 用来初始化整个系统
        // 构造函数的参数如下: 词典文件路径, 配置文件路径, 传感器类型, 是否使用可视化界面
        System(const std::string &strVocFile, const std::string &strSettingsFile,
               eSensor sensor, bool bUseViewer = true);

    private:

        // 变量名的命名方式: 类的变量名有前缀m, 如果这个变量是指针类型还要多加个前缀p, 如果是进程那么加个前缀t

        // Input sensor
        // 传感器类型
        eSensor mSensor;

        // The viewer draws the map and the current camera pose. It uses Pangolin.
        // 查看器, 可视化界面
        Viewer* mpViewer;

        // Reset flag
        // 复位标志
        std::mutex mMutexReset;  // 用于实现互斥锁
        bool mbReset;

        // Change mode flags
        // 模式改变标志
        std::mutex mMutexMode;  // 用于实现互斥锁
        bool mbActivateLocalizationMode;
        bool mbDeactivateLocalizationMode;

    };

}


#endif //SYSTEM_H

```

### include/Viewer.h

```c++
#ifndef VIEWER_H
#define VIEWER_H

namespace ORB_SLAM2
{

class Viewer
  {

  };


}

#endif //VIEWER_H

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
