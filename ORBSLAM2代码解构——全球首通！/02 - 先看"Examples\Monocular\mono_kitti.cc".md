# Examples/Monocular/mono_kitti.cc


该文件是 **SuperPoint+ORBSLAM2** 系统在 **KITTI** 数据集上使用单目传感器进行定位的整体流程


## 完整代码

```c++
/**
* This file is part of ORB-SLAM2.
*
* Copyright (C) 2014-2016 Raúl Mur-Artal <raulmur at unizar dot es> (University of Zaragoza)
* For more information see <https://github.com/raulmur/ORB_SLAM2>
*
* ORB-SLAM2 is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* ORB-SLAM2 is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with ORB-SLAM2. If not, see <http://www.gnu.org/licenses/>.
**/

#include <chrono>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <algorithm>

#include<opencv2/core/core.hpp>

#include"System.h"


using namespace std;


// 获取图像序列中每一张图像的路径和时间戳
void LoadImages(const string &strPathToSequence, vector<string> &vstrImageFilenames, vector<double> &vTimestamps);


int main(int argc, char **argv)
{
    // Step 1 检查输入参数个数是否足够
    if(argc != 4)
    {
        cerr << endl << "Usage: ./mono_kitti path_to_vocabulary path_to_settings path_to_sequence" << endl;
        return 1;
    }

    // Step 2 加载图像
    // Retrieve paths to images
    // 图像序列的文件名, 字符串序列
    vector<string> vstrImageFilenames;
    // 时间戳
    vector<double> vTimestamps;
    LoadImages(string(argv[3]), vstrImageFilenames, vTimestamps);

    // 当前图像序列的图片数目
    // int nImages = vstrImageFilenames.size();
    int nImages = static_cast<int>(vstrImageFilenames.size());

    cout << "Creating ORB-SLAM2 system ..." << endl;

    // Step 2 加载 SLAM 系统
    // Create SLAM system. It initializes all system threads and gets ready to process frames.
    ORB_SLAM2::System SLAM(argv[1],argv[2],ORB_SLAM2::System::MONOCULAR,true);

    // Step 3 运行前准备
    // Vector for tracking time statistics
    // 统计追踪一帧耗时(仅 Tracker 线程)
    vector<float> vTimesTrack;
    vTimesTrack.resize(nImages);

    cout << endl << "-------" << endl;
    cout << "Start processing sequence ..." << endl;
    cout << "Images in the sequence: " << nImages << endl << endl;

    // Step 4 依次追踪图像序列中的每一张图像
    // Main loop
    cv::Mat im;
    for(int ni=0; ni<nImages; ni++)
    {
        // Step 4.1 根据前面获得的图像文件名读取图像, 读取过程中不改变图像的格式
        // Read image from file
        im = cv::imread(vstrImageFilenames[ni],CV_LOAD_IMAGE_UNCHANGED);
        double tframe = vTimestamps[ni];

        // Step 4.2 图像的合法性检查
        if(im.empty())
        {
            cerr << endl << "Failed to load image at: " << vstrImageFilenames[ni] << endl;
            return 1;
        }

        // Step 4.3 开始计时
        #ifdef COMPILEDWITHC14
        std::chrono::steady_clock::time_point t1 = std::chrono::steady_clock::now();
        #else
        std::chrono::monotonic_clock::time_point t1 = std::chrono::monotonic_clock::now();
        #endif

        // Step 4.4 追踪当前图像
        // Pass the image to the SLAM system
        SLAM.TrackMonocular(im,tframe);

        // Step 4.5 追踪完成, 停止当前帧的图像计时, 并计算追踪耗时
        #ifdef COMPILEDWITHC14
        std::chrono::steady_clock::time_point t2 = std::chrono::steady_clock::now();
        #else
        std::chrono::monotonic_clock::time_point t2 = std::chrono::monotonic_clock::now();
        #endif

        double ttrack= std::chrono::duration_cast<std::chrono::duration<double> >(t2 - t1).count();

        // vTimesTrack[ni]=ttrack;
        vTimesTrack[ni] = static_cast<float>(ttrack);

        // Step 4.6 根据图像时间戳中记录的两张图像之间的时间和现在追踪当前图像所耗费的时间
        // 使得下一张图像能够按照时间戳被送入到 SLAM 系统中进行跟踪
        // Wait to load the next frame
        double T=0;
        if(ni<nImages-1)
            T = vTimestamps[ni+1]-tframe;
        else if(ni>0)
            T = tframe-vTimestamps[ni-1];

        if(ttrack<T)
            // usleep((T - ttrack) * 1e6);
            usleep(static_cast<unsigned int>((T-ttrack)*1e6));
    }

    // Step 5 如果所有图像都追踪完毕, 就终止当前的 SLAM 系统
    // Stop all threads
    SLAM.Shutdown();

    // Step 6 计算平均耗时
    // Tracking time statistics
    sort(vTimesTrack.begin(),vTimesTrack.end());
    float totaltime = 0;
    for(int ni=0; ni<nImages; ni++)
    {
        totaltime+=vTimesTrack[ni];
    }
    cout << "-------" << endl << endl;
    cout << "median tracking time: " << vTimesTrack[nImages/2] << endl;
    cout << "mean tracking time: " << totaltime/nImages << endl;

    // Step 7 保存 TUM 格式的相机轨迹
    // Save camera trajectory
    SLAM.SaveKeyFrameTrajectoryTUM("KeyFrameTrajectory.txt");    

    return 0;
}

// 获取图像序列中每一张图像的路径和时间戳
void LoadImages(const string &strPathToSequence, vector<string> &vstrImageFilenames, vector<double> &vTimestamps)
{
    // Step 1 读取时间戳文件
    ifstream fTimes;
    string strPathTimeFile = strPathToSequence + "/times.txt";
    fTimes.open(strPathTimeFile.c_str());
    while(!fTimes.eof())
    {
        string s;
        getline(fTimes,s);
        // 当该行不为空时执行
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

    // Step 2 使用左目图像, 生成左目图像序列中每一张图像的文件名
    string strPrefixLeft = strPathToSequence + "/image_0/";

    //const int nTimes = vTimestamps.size();
    const int nTimes = static_cast<int>(vTimestamps.size());
    vstrImageFilenames.resize(nTimes);

    for(int i=0; i<nTimes; i++)
    {
        stringstream ss;
        ss << setfill('0') << setw(6) << i;
        vstrImageFilenames[i] = strPrefixLeft + ss.str() + ".png";
    }
}

```

整个文件内的代码比较简单, 因为这只是一个将 SLAM 系统进行定位的步骤串起来的流程文件

因此我们关注的重点是在这个文件内, 调用了哪些在其他文件内的函数, 以及这些函数构造以及具体实现是哪些文件写的


## 所调用的其他文件里的函数


### 1. 初始化 SLAM 系统

```c++
    // Step 2 加载 SLAM 系统
    // Create SLAM system. It initializes all system threads and gets ready to process frames.
    ORB_SLAM2::System SLAM(argv[1],argv[2],ORB_SLAM2::System::MONOCULAR,true);
```

该 System 类的构造函数是在 **include/System.h** 里声明的

```c++
        // 构造函数, 用来初始化整个系统
        // 第一个 System 是类名, 表示这是 ORB_SLAM2::System 类的构造函数
        // 第二个 System 是构造函数的名称, 必须与类名相同
        // 构造函数的参数如下: 词典文件路径, 配置文件路径, 传感器类型, 是否使用可视化界面
        // Initialize the SLAM system. It launches the Local Mapping, Loop Closing and Viewer threads.
        System(const string &strVocFile, const string &strSettingsFile,
               eSensor sensor, bool bUseViewer = true);
```

具体实现是在 **src/System.cc** 里, 所以需要去到该文件里面看看 System 类的构造函数的具体实现


### 2.  对每一帧图像进行追踪

```c++
        // Step 4.4 追踪当前图像
        // Pass the image to the SLAM system
        SLAM.TrackMonocular(im,tframe);
```


### 3.  终止 SLAM 系统

```c++
    // Step 5 如果所有图像都追踪完毕, 就终止当前的 SLAM 系统
    // Stop all threads
    SLAM.Shutdown();
```


### 4. 保存轨迹

```c++
    // Step 7 保存 TUM 格式的相机轨迹
    // Save camera trajectory
    SLAM.SaveKeyFrameTrajectoryTUM("KeyFrameTrajectory.txt"); 
```
