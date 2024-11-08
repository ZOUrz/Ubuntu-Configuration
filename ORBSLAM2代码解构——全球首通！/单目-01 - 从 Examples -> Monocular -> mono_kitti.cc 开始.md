# Examples/Monocular/mono_kitti.cc

* 该文件是 `SuperPoint + ORBSLAM2` 系统在 `KITTI` 数据集上使用单目传感器进行定位的整体流程

* 我们先从这个文件开始阅读!


## 重点代码逐行解析


- ### LoadImages

    - 获取图像序列中每一张图像的路径和时间戳

    ```c++
    // 获取图像序列中每一张图像的路径和时间戳
    void LoadImages(const string &strPathToSequence, vector<string> &vstrImageFilenames, vector<double> &vTimestamps);
    ```

    - 这行代码是 `LoadImages` 函数的声明, 因此这个函数的具体实现在文件最后面, 所以需要在文件开头进行函数的声明, 否则在 `main` 里无法调用

    - `LoadImages` 函数的具体实现:

    ```c++
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


- ### 1. 输入参数检查

    - 检查输入参数个数是否足够, 对于 `mono_kitti.cc` 来说, 在终端命令行输入的参数为

    - ` ./mono_kitti 词典文件路径 配置文件路径 数据集路径`

    ```c++
        // Step 1 检查输入参数个数是否足够
        if(argc != 4)
        {
            cerr << endl << "Usage: ./mono_kitti path_to_vocabulary path_to_settings path_to_sequence" << endl;
            return 1;
        }
    ```


- ### 2. 加载图像和时间戳

    - 使用 `LoadImages` 函数, 获取图像序列中每张图像的文件路径以及对应的时间戳
 
    - 然后获取当前图像序列的图像数目

    ```c++
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
    ```


- ### 3. 加载 SLAM 系统

    - 输入的参数如下: 输入的参数如下: `词典文件路径`, `配置文件路径`, `传感器类型`, `是否使用可视化界面`
 
    - 下面这行代码的作用是, 调用 `ORB-SLAM2` 中 `System` 类的构造函数，初始化一个名为 `SLAM` 的实例
 
    ```c++
        // Step 3 加载 SLAM 系统
        // Create SLAM system. It initializes all system threads and gets ready to process frames.
        // 输入的参数如下: 词典文件路径, 配置文件路径, 传感器类型, 是否使用可视化界面
        ORB_SLAM2::System SLAM(argv[1],argv[2],ORB_SLAM2::System::MONOCULAR,true);
    ```


- ### 4. 运行前准备

    - 变量 `vTimesTrack` 是为了保存追踪一帧图像(仅 `Tracker`)所花费的时间

    ```c++
        // Step 4 运行前准备
        // Vector for tracking time statistics
        // 统计追踪一帧耗时(仅 Tracker 线程)
        vector<float> vTimesTrack;
        vTimesTrack.resize(nImages);
    ```

- ### 5. SLAM 系统的主循环

    - 依次追踪图像序列中的每一张图像
 
    ```c++
        // Step 5 依次追踪图像序列中的每一张图像
        // Main loop
        cv::Mat im;
        for(int ni=0; ni<nImages; ni++)
    ```
    - #### 5.1 读取图像
         
        - 根据前面获得的图像文件名读取图像, 读取过程中不改变图像的格式

        ```c++
                // Step 5.1 根据前面获得的图像文件名读取图像, 读取过程中不改变图像的格式
                // Read image from file
                im = cv::imread(vstrImageFilenames[ni],CV_LOAD_IMAGE_UNCHANGED);
                double tframe = vTimestamps[ni];
        ```

    - #### 5.2 检查是否读取到图像

        - 图像的合法性检查

        ```c++
                // Step 5.2 图像的合法性检查
                if(im.empty())
                {
                    cerr << endl << "Failed to load image at: " << vstrImageFilenames[ni] << endl;
                    return 1;
                }
        ```

    - #### 5.3 开始计时

        - `std::chrono::steady_clock` 是 `C++11` 和 `C++14` 中的稳定计时器, 适用于测量时间间隔, 因为它不会受到系统时间的调整而影响

        ```c++
                // Step 5.3 开始计时
                std::chrono::steady_clock::time_point t1 = std::chrono::steady_clock::now();
        ```

    - #### 5.4 追踪当前图像

        - 调用了 `SLAM` 中的 `TrackMonocular` 函数, 其中, `SLAM` 是上面经过初始化后的 `System` 类实例

        - `im`: 这是当前帧的图像数据, 是 `cv::Mat` 类型

        - `tframe`: 这是该帧的时间戳(double 类型)

        ```c++
                // Step 5.4 追踪当前图像
                // Pass the image to the SLAM system
                SLAM.TrackMonocular(im,tframe);
        ```

    - #### 5.5 计算追踪一帧图像的耗时

        - 追踪完成, 停止当前帧的图像计时, 并计算追踪耗时
     
        ```c++
                // Step 5.5 追踪完成, 停止当前帧的图像计时, 并计算追踪耗时
                std::chrono::steady_clock::time_point t2 = std::chrono::steady_clock::now();
        
                double ttrack= std::chrono::duration_cast<std::chrono::duration<double> >(t2 - t1).count();
        
                // vTimesTrack[ni]=ttrack;
                vTimesTrack[ni] = static_cast<float>(ttrack);
        ```

    - #### 5.6 匹配图像采集时的时间间隔

        - 根据图像时间戳中记录的两张图像之间的时间和现在追踪当前图像所耗费的时间, 使得下一张图像能够按照时间戳被送入到 `SLAM` 系统中进行跟踪

        ```c++
                // Step 5.6 根据图像时间戳中记录的两张图像之间的时间和现在追踪当前图像所耗费的时间
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
        ```


- ### 6. 关闭 SLAM 系统

    - 如果所有图像都追踪完毕, 就终止当前的 `SLAM` 系统

    ```c++
        // Step 6 如果所有图像都追踪完毕, 就终止当前的 SLAM 系统
        // Stop all threads
        SLAM.Shutdown();
    ```


- ### 7. 计算平均耗时

    - 计算平均耗时
 
    ```c++
        // Step 7 计算平均耗时
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
    ```


- ### 8. 保存轨迹

    - 保存 TUM 格式的相机轨迹
    
    ```
        // Step 8 保存 TUM 格式的相机轨迹
        // Save camera trajectory
        SLAM.SaveKeyFrameTrajectoryTUM("KeyFrameTrajectory.txt"); 
    ```

整个看下来, 其实文件内的代码比较简单, 因为这只是一个将 `SLAM` 系统进行定位的步骤串起来的流程文件

因此我们需要重点关注的是, 在这个文件中, 调用了哪些在其他文件定义类和函数, 以及这些类的构造函授以及函数的具体实现


## 需要进行跳转阅读的位置


在 moni_kitti.cc 中, 所调用的来自其他文件的函数


- ### 1. 加载 SLAM 系统

    ```c++
        // Step 2 加载 SLAM 系统
        // Create SLAM system. It initializes all system threads and gets ready to process frames.
        // 输入的参数如下: 词典文件路径, 配置文件路径, 传感器类型, 是否使用可视化界面
        ORB_SLAM2::System SLAM(argv[1],argv[2],ORB_SLAM2::System::MONOCULAR,true);
    ```

    - 该 System 类的构造函数是在 `include/System.h` 里声明的

    ```c++
            // 构造函数, 用来初始化整个系统
            // 第一个 System 是类名, 表示这是 ORB_SLAM2::System 类的构造函数
            // 第二个 System 是构造函数的名称, 必须与类名相同
            // 构造函数的参数如下: 词典文件路径, 配置文件路径, 传感器类型, 是否使用可视化界面
            // Initialize the SLAM system. It launches the Local Mapping, Loop Closing and Viewer threads.
            System(const string &strVocFile, const string &strSettingsFile,
                   eSensor sensor, bool bUseViewer = true);
    ```

    - 具体实现是在 `src/System.cc` 里, 所以需要去到该文件里面看看 `System` 类的构造函数的具体实现


- ### 2.  对每一帧图像进行追踪

    ```c++
            // Step 4.4 追踪当前图像
            // Pass the image to the SLAM system
            SLAM.TrackMonocular(im,tframe);
    ```


- ### 3.  终止 SLAM 系统

    ```c++
        // Step 5 如果所有图像都追踪完毕, 就终止当前的 SLAM 系统
        // Stop all threads
        SLAM.Shutdown();
    ```


- ### 4. 保存轨迹

    ```c++
        // Step 7 保存 TUM 格式的相机轨迹
        // Save camera trajectory
        SLAM.SaveKeyFrameTrajectoryTUM("KeyFrameTrajectory.txt"); 
    ```


## 重头开始构建 ORBSLAM2

如果需要从零开始构建 `ORBSLAM2` 系统, 就先写到 **"加载 `SLAM` 系统那一步即可"** 

- ### mono_kitti.cc (Build from scratch - Changed 0)

    ```c++
    
    #include <fstream>
    #include <iomanip>
    #include <iostream>
    #include <opencv2/core/core.hpp>
    

    using namespace std;
    
    
    // 获取图像序列中每一张图像的路径和时间戳
    void LoadImages (const string &strPathToSequence, vector<string> &vstrImageFilenames, vector<double> &vTimestamps);
    
    
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
