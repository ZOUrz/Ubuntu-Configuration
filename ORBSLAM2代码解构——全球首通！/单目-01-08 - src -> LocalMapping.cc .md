# 跳转到 src/LocalMapping.cc 阅读 LocalMapping 类构造函数和其成员函数 `Run` 的具体实现

- 主要阅读该文件中 `LocalMapping` 类的构造函数和 `Run` 函数


## 重点代码逐行解析


- ### 1. 构造函数

    - 主要作用是初始化 `LocalMapping` 类的部分成员变量, 确保 `LocalMapping` 对象在创建时具有适当的默认状态
 
        ```c++
            // 构造函数
            LocalMapping::LocalMapping(Map *pMap, const float bMonocular):
                mbMonocular(static_cast<bool>(bMonocular)), mbResetRequested(false), mbFinishRequested(false),
                mbFinished(true), mpMap(pMap), mbAbortBA(false), mbStopped(false), mbStopRequested(false),
                mbNotStop(false), mbAcceptKeyFrames(true)
            {
                // mbResetRequested: 请求当前线程复位的标志. True: 表示一直请求复位, 但复位还未完成; False: 表示复位完成
                // mbFinishRequested: 请求终止当前线程的标志, 注意只是请求, 不一定终止, 终止要看 mbFinished
                // mbFinished: 判断最终 LocalMapping::Run() 是否完成的标志
                // mbAbortBA: 是否放弃 BA 优化的标志位
                // mbStopped: True: 表示可以终止 LocalMapping 线程
                // mbStopRequested: 外部线程调用, True: 表示外部线程请求停止 LocalMapping
                // mbNotStop: 表示不要停止 LocalMapping 线程, 因为要插入关键帧了, 需要与 mbStopped 结合使用
                // mbAcceptKeyFrames: True: 允许接受关键帧, Tracking 和 LocalMapping 之间的关键帧调度
            }
        ```

    - 其中, 构造函数以及其成员变量是在 `include/LocalMapping.h` 中声明的

        ```c++
                // 构造函数
                LocalMapping(Map* pMap, float bMonocular);
        ```

        ```c++
                // 当前系统输入是单目还是双目 RGB-D 的标志
                bool mbMonocular;
        
                // 当前系统是否收到了请求复位的信号
                bool mbResetRequested;
                // 和复位信号有关的互斥锁
                std::mutex mMutexReset;
        
                // 当前线程是否收到了请求终止的信号
                bool mbFinishRequested;
                // 当前线程的主函数是否已经终止
                bool mbFinished;
                // 和 "线程真正结束" 有关的互斥锁
                std::mutex mMutexFinish;
        
                // 指向局部地图的句柄
                Map* mpMap;
        
                // 终止 BA 的标志
                bool mbAbortBA;
        
                // 当前线程是否已经真正地终止了
                bool mbStopped;
                // 终止当前线程的请求
                bool mbStopRequested;
                // 标志当前线程还不能够停止工作, 优先级比 mbStopRequested 要高
                // 只有这个变量和 mbStopRequested 都满足要求的时候, 线程才会进行一系列的终止操作
                bool mbNotStop;
                // 和终止线程相关的互斥锁
                std::mutex mMutexStop;
        
                // 当前局部建图线程是否运行关键帧输入
                bool mbAcceptKeyFrames;
                // 和是否运行关键帧输入有关的互斥锁
                std::mutex mMutexAccept;
        ```


- ### 2. Run 函数

    - 这是 `LocalMapping` 类的主线程函数, 负责处理关键帧队列, 响应停止或复位请求等操作

 
    - #### 1. 线程开始执行
 
        ```
                std::cout << "Runing LocalMapping::Run()" << std::endl;
                // 标记状态, 表示当前 Run 函数正在运行, 尚未结束
                mbFinished = false;
        ```

        - `mbFinished` 标志被设为 `false`, 表示线程正在运行
     
    - #### 2. 主循环
 
        - ##### 2-1. 停止接收关键帧

            - 设置 `mbAcceptKeyFrames` 标志为 `false`, 表示当前线程处于忙碌状态, 不接受新的关键帧

                ```c++
                            // Step 1 告诉 Tracking, LocalMapping 正处于繁忙状态, 请不要发送关键帧打扰
                            // Tracking will see that Local Mapping is busy
                            SetAcceptKeyFrames(false);
                ```
            
            - 其中, 函数 `SetAcceptKeyFrames` 的具体实现以及声明为:
         
                ```c++
                    // 设置 "允许接受关键帧" 的状态标标志
                    void LocalMapping::SetAcceptKeyFrames(bool flag)
                    {
                        unique_lock<mutex> lock(mMutexAccept);
                        mbAcceptKeyFrames=flag;
                    }
                ```

                ```c++
                        // 设置 "允许接受关键帧" 的状态标志
                        void SetAcceptKeyFrames(bool flag);
                ```


         
        - ##### 2-2. 检查是否有待处理关键帧

            - **注意: 现在还处于系统初始化阶段, 因此不可能有新的关键帧, 因此 `if` 里面的代码先不用管, 等到后面需要处理关键帧的时候再回来, 这里就只写一行代码作为省略**
         
            - 检查关键帧队列是否有待处理的关键帧, 如果有, 则需要继续处理
     
                ```
                            // 等待处理的关键帧列表不为空
                            // Check if there are keyframes in the queue
                            if(CheckNewKeyFrames())
                            {
                                std::cout << "There are keyframes in the queue!" << std::endl;
                            }
                ```

            - 其中, 函数 `CheckNewKeyFrames` 的具体实现以及声明为:
         
                ```c++
                    // 查看列表中是否有等待被插入的关键帧
                    bool LocalMapping::CheckNewKeyFrames()
                    {
                        unique_lock<mutex> lock(mMutexNewKFs);
                        return(!mlNewKeyFrames.empty());
                    }
                ```
                
                ```c++
                        // 查看列表中是否有等待被插入的关键帧
                        bool CheckNewKeyFrames();
                ```

            - 此外, 成员变量 `mlNewKeyFrames` 和 `mMutexNewKFs` 的声明为:
                
                ```c++
                        // Tracking 线程向 LocalMapping 中插入关键帧是先插入到该队列中
                        // 等待处理的关键帧列表
                        std::list<KeyFrame*> mlNewKeyFrames;
                
                        // 操作关键帧列表时使用的互斥锁
                        std::mutex mMutexNewKFs;
                ```


        - ##### 2-3. 检查是否有停止请求

            - 如果没有关键帧需要处理, 检查是否有停止请求
         
                ```c++
                            else if(Stop())  // 当要终止当前线程的时候
                ```
     
            - `Stop()` 会在 `mbStopRequested` 标志为 `true` 且 `mbNotStop` 为 `false` 时, 将线程标记为停止状态, 并返回 `true`

            - 其中, 函数 `Stop` 的具体实现以及声明为:

                ```c++
                    // 检查是否要把当前的局部建图线程停止工作, 运行的时候要检查是否有终止请求, 如果有就执行. 由 Run 函数调用
                    bool LocalMapping::Stop()
                    {
                        unique_lock<mutex> lock(mMutexStop);
                        // 如果当前线程还没有准备停止, 但是已经有终止请求了, 那么就准备停止当前线程
                        if(mbStopRequested && !mbNotStop)
                        {
                            mbStopped = true;
                            cout << "Local Mapping STOP" << endl;
                            return true;
                        }
                ```

                ```c++
                        // 检查是否要把当前的局部建图线程停止, 如果当前线程没有那么检查请求标志, 如果请求标志被置位那么就设置为停止工作. 由 Run 函数调用
                        bool Stop();
                ```

            - ###### 2-3-1. 检查状态
         
                - 当线程处于停止状态且没有收到终止请求时, 每隔 `3` 毫秒检查一次状态, 等待恢复
         
                    ```c++
                                    // Safe area to stop
                                    while(isStopped() && !CheckFinish())
                                    {
                                        // 如果还没有结束利索, 那么等3毫秒
                                        // usleep(3000);
                                        std::this_thread::sleep_for(std::chrono::milliseconds(3));
                                    }
                    ```

                - 其中, 函数 `isStopped` 和 `CheckFinish` 的具体实现以及声明为:
             
                    ```c++
                        // 检查 mbStopped 是否为 true, 为 true 表示可以终止 LocalMapping 线程
                        bool LocalMapping::isStopped()
                        {
                            unique_lock<mutex> lock(mMutexStop);
                            return mbStopped;
                        }
                    ```
                    
                    ```c++
                            // 检查 mbStopped 是否被置位了
                            bool isStopped();
                    ```
                    
                    ```c++
                        // 检查是否已经有外部线程请求终止当前线程
                        bool LocalMapping::CheckFinish()
                        {
                            unique_lock<mutex> lock(mMutexFinish);
                            return mbFinishRequested;
                        }
                    ```
                    
                    ```c++
                            // 检查是否已经有外部线程请求终止当前线程
                            bool CheckFinish();
                    ```
                
            - ###### 2-3-2. 退出主循环

                - `CheckFinish()` 若返回 `true`, 则退出主循环, 线程准备结束
             
                    ```c++
                                    // 然后确定终止了就跳出这个线程的主循环
                                    if(CheckFinish())
                                        break;
                    ```


        - ##### 2-4. 检查是否有复位请求
     
            - 检查是否有复位请求, 并在请求存在时清空关键帧队列, 清空新增的地图点, 同时将 `mbResetRequested` 重置为 `false`
         
                ```c++
                            // 查看是否有复位线程的请求
                            ResetIfRequested();
                ```

            - 其中, 函数 `ResetIfRequested` 的具体实现以及声明为:
         
                ```c++
                    // 检查是否有复位线程的请求
                    void LocalMapping::ResetIfRequested()
                    {
                        unique_lock<mutex> lock(mMutexReset);
                        // 执行复位操作: 清空关键帧缓冲区, 清空待 cull 的地图点缓冲
                        if(mbResetRequested)
                        {
                            mlNewKeyFrames.clear();
                            mlpRecentAddedMapPoints.clear();
                            // 恢复为 False 表示复位过程完成
                            mbResetRequested=false;
                        }
                    }
                ```
                
                ```c++
                        // 检查当前是否有复位线程的请求
                        void ResetIfRequested();
                ```
         
            - 此外, 成员变量 `mlpRecentAddedMapPoints` 的声明为:
                
                ```c++
                        // 存储当前关键帧生成的地图点, 也是等待检查的地图点列表
                        std::list<MapPoint*> mlpRecentAddedMapPoints;
                ```

        - ##### 2-5. 重新设置允许插入关键帧
     
            - 重新设置 `mbAcceptKeyFrames` 为 `true`, 允许 `Tracking` 插入关键帧
     
                ```
                            // Tracking will see that Local Mapping is busy
                            SetAcceptKeyFrames(true);
                ```

        - ##### 2-6. 检查线程是否应结束
     
            - 如果有终止请求, 则退出主循环, 结束线程
     
                ```c++
                            // 如果当前线程已经结束了就跳出主循环
                            if(CheckFinish())
                                break;
                ```

        - ##### 2-7. 每隔 3 毫秒检查一次
     
            - 在主循环中每隔 3 毫秒暂停一次, 降低 `CPU` 使用率
         
                ```
                            std::this_thread::sleep_for(std::chrono::milliseconds(3));
                ```


    - #### 3. 结束线程
 
        - 设置线程已完成状态, 将 `mbFinished` 和 `mbStopped` 都设为 `true`, 表示线程已完成其任务并安全地结束
 
            ```c++
                    // 设置线程已经终止
                    SetFinish();
            ```

        - 其中, 函数 `SetFinish` 的具体实现以及声明为:
     
            ```c++
                // 设置当前线程已经真正地结束了
                void LocalMapping::SetFinish()
                {
                    unique_lock<mutex> lock(mMutexFinish);
                    mbFinished = true;
                    unique_lock<mutex> lock2(mMutexStop);
                    mbStopped = true;
                }
            ```
            
            ```c++
                    // 设置当前线程已经真正地结束了, 由本线程 Run 函数调用
                    void SetFinish();
            ```


## 重头开始构建 ORBSLAM2

- 如果是从零开始构建 `ORBSLAM2` 系统, 就按照下面给出的文件内容进行代码的编写


- ### 1. include/LocalMapping.h

    - Build from scratch - Changed 0
 
        ```c++
        #ifndef LOCALMAPPING_H
        #define LOCALMAPPING_H
        
        // 局部建图线程
        
        
        #include "KeyFrameDatabase.h"
        #include "KeyFrame.h"
        #include "Map.h"
        #include "Tracking.h"
        
        #include <mutex>
        
        
        namespace ORB_SLAM2
        {
        
            class Tracking;
            class LoopClosing;
            class Map;
        
            class LocalMapping
            {
            public:
                // 构造函数
                LocalMapping(Map* pMap, float bMonocular);
        
                // 检查是否要把当前的局部建图线程停止, 如果当前线程没有那么检查请求标志, 如果请求标志被置位那么就设置为停止工作. 由 Run 函数调用
                bool Stop();
                // 线程主函数
                void Run();
        
                // 检查 mbStopped 是否被置位了
                bool isStopped();
                // 设置 "允许接受关键帧" 的状态标志
                void SetAcceptKeyFrames(bool flag);
        
            protected:
                // 查看列表中是否有等待被插入的关键帧
                bool CheckNewKeyFrames();
        
                // 当前系统输入是单目还是双目 RGB-D 的标志
                bool mbMonocular;
        
                // 检查当前是否有复位线程的请求
                void ResetIfRequested();
                // 当前系统是否收到了请求复位的信号
                bool mbResetRequested;
                // 和复位信号有关的互斥锁
                std::mutex mMutexReset;
        
                // 检查是否已经有外部线程请求终止当前线程
                bool CheckFinish();
                // 设置当前线程已经真正地结束了, 由本线程 Run 函数调用
                void SetFinish();
                // 当前线程是否收到了请求终止的信号
                bool mbFinishRequested;
                // 当前线程的主函数是否已经终止
                bool mbFinished;
                // 和 "线程真正结束" 有关的互斥锁
                std::mutex mMutexFinish;
        
                // 指向局部地图的句柄
                Map* mpMap;
        
                // Tracking 线程向 LocalMapping 中插入关键帧是先插入到该队列中
                // 等待处理的关键帧列表
                std::list<KeyFrame*> mlNewKeyFrames;
        
                // 存储当前关键帧生成的地图点, 也是等待检查的地图点列表
                std::list<MapPoint*> mlpRecentAddedMapPoints;
        
                // 操作关键帧列表时使用的互斥锁
                std::mutex mMutexNewKFs;
        
                // 终止 BA 的标志
                bool mbAbortBA;
        
                // 当前线程是否已经真正地终止了
                bool mbStopped;
                // 终止当前线程的请求
                bool mbStopRequested;
                // 标志当前线程还不能够停止工作, 优先级比 mbStopRequested 要高
                // 只有这个变量和 mbStopRequested 都满足要求的时候, 线程才会进行一系列的终止操作
                bool mbNotStop;
                // 和终止线程相关的互斥锁
                std::mutex mMutexStop;
        
                // 当前局部建图线程是否运行关键帧输入
                bool mbAcceptKeyFrames;
                // 和是否运行关键帧输入有关的互斥锁
                std::mutex mMutexAccept;
        
             };
        
        }
        
        #endif //LOCALMAPPING_H
        
        ```


- ### 2. src/LocalMapping.cc

    - Build from scratch - Changed 0
 
        ```c++
        // 局部建图器
        
        
        #include "LocalMapping.h"
        
        #include<mutex>
        
        
        namespace ORB_SLAM2
        {
            // 构造函数
            LocalMapping::LocalMapping(Map *pMap, const float bMonocular):
                mbMonocular(static_cast<bool>(bMonocular)), mbResetRequested(false), mbFinishRequested(false),
                mbFinished(true), mpMap(pMap), mbAbortBA(false), mbStopped(false), mbStopRequested(false),
                mbNotStop(false), mbAcceptKeyFrames(true)
            {
                // mbResetRequested: 请求当前线程复位的标志. True: 表示一直请求复位, 但复位还未完成; False: 表示复位完成
                // mbFinishRequested: 请求终止当前线程的标志, 注意只是请求, 不一定终止, 终止要看 mbFinished
                // mbFinished: 判断最终 LocalMapping::Run() 是否完成的标志
                // mbAbortBA: 是否放弃 BA 优化的标志位
                // mbStopped: True: 表示可以终止 LocalMapping 线程
                // mbStopRequested: 外部线程调用, True: 表示外部线程请求停止 LocalMapping
                // mbNotStop: 表示不要停止 LocalMapping 线程, 因为要插入关键帧了, 需要与 mbStopped 结合使用
                // mbAcceptKeyFrames: True: 允许接受关键帧, Tracking 和 LocalMapping 之间的关键帧调度
            }
        
            // 线程主函数
            void LocalMapping::Run()
            {
                std::cout << "Runing LocalMapping::Run()" << std::endl;
                // 标记状态, 表示当前 Run 函数正在运行, 尚未结束
                mbFinished = false;
        
                // 主循环
                while(true)
                {
                    // Step 1 告诉 Tracking, LocalMapping 正处于繁忙状态, 请不要发送关键帧打扰
                    // Tracking will see that Local Mapping is busy
                    SetAcceptKeyFrames(false);
        
                    // 等待处理的关键帧列表不为空
                    // Check if there are keyframes in the queue
                    if(CheckNewKeyFrames())
                    {
                        std::cout << "There are keyframes in the queue!" << std::endl;
                    }
                    else if(Stop())  // 当要终止当前线程的时候
                    {
                        // Safe area to stop
                        while(isStopped() && !CheckFinish())
                        {
                            // 如果还没有结束利索, 那么等3毫秒
                            // usleep(3000);
                            std::this_thread::sleep_for(std::chrono::milliseconds(3));
                        }
                        // 然后确定终止了就跳出这个线程的主循环
                        if(CheckFinish())
                            break;
                    }
        
                    // 查看是否有复位线程的请求
                    ResetIfRequested();
        
                    // Tracking will see that Local Mapping is busy
                    SetAcceptKeyFrames(true);
        
                    // 如果当前线程已经结束了就跳出主循环
                    if(CheckFinish())
                        break;
        
                    std::this_thread::sleep_for(std::chrono::milliseconds(3));
                }
        
                // 设置线程已经终止
                SetFinish();
            }
        
            // 设置 "允许接受关键帧" 的状态标标志
            void LocalMapping::SetAcceptKeyFrames(bool flag)
            {
                unique_lock<mutex> lock(mMutexAccept);
                mbAcceptKeyFrames=flag;
            }
        
            // 查看列表中是否有等待被插入的关键帧
            bool LocalMapping::CheckNewKeyFrames()
            {
                unique_lock<mutex> lock(mMutexNewKFs);
                return(!mlNewKeyFrames.empty());
            }
        
            // 检查是否要把当前的局部建图线程停止工作, 运行的时候要检查是否有终止请求, 如果有就执行. 由 Run 函数调用
            bool LocalMapping::Stop()
            {
                unique_lock<mutex> lock(mMutexStop);
                // 如果当前线程还没有准备停止, 但是已经有终止请求了, 那么就准备停止当前线程
                if(mbStopRequested && !mbNotStop)
                {
                    mbStopped = true;
                    cout << "Local Mapping STOP" << endl;
                    return true;
                }
        
                return false;
            }
        
            // 检查 mbStopped 是否为 true, 为 true 表示可以终止 LocalMapping 线程
            bool LocalMapping::isStopped()
            {
                unique_lock<mutex> lock(mMutexStop);
                return mbStopped;
            }
        
            // 检查是否已经有外部线程请求终止当前线程
            bool LocalMapping::CheckFinish()
            {
                unique_lock<mutex> lock(mMutexFinish);
                return mbFinishRequested;
            }
        
            // 检查是否有复位线程的请求
            void LocalMapping::ResetIfRequested()
            {
                unique_lock<mutex> lock(mMutexReset);
                // 执行复位操作: 清空关键帧缓冲区, 清空待 cull 的地图点缓冲
                if(mbResetRequested)
                {
                    mlNewKeyFrames.clear();
                    mlpRecentAddedMapPoints.clear();
                    // 恢复为 False 表示复位过程完成
                    mbResetRequested=false;
                }
            }
        
            // 设置当前线程已经真正地结束了
            void LocalMapping::SetFinish()
            {
                unique_lock<mutex> lock(mMutexFinish);
                mbFinished = true;
                unique_lock<mutex> lock2(mMutexStop);
                mbStopped = true;
            }
        
        }
        
        ```


- ### 3. include/System.h

    - Build from scratch - Changed 8
 
    - 文件开头加上
 
        ```c++
        #include "LocalMapping.h"
        ```

    - 然后添加成员变量

        ```c++
                // 局部建图器, 局部BA由它进行
                // Local Mapper. It manages the local map and performs local bundle adjustment.
                LocalMapping* mpLocalMapper;
        
                // 系统除了在主进程中进行运动追踪外, 会创建局部建图线程, 回环检测线程和可视化线程
                // System threads: Local Mapping, Loop Closing, Viewer.
                // The Tracking thread "lives" in the main execution thread that creates the System object.
                std::thread* mptLocalMapping;
        ```

    - 完整代码

        ```c++
        #ifndef SYSTEM_H
        #define SYSTEM_H
        
        
        #include <mutex>
        
        #include "Viewer.h"
        #include "ORBVocabulary.h"
        #include "KeyFrameDatabase.h"
        #include "Map.h"
        #include "FrameDrawer.h"
        #include "MapDrawer.h"
        #include "Tracking.h"
        #include "LocalMapping.h"
        
        #include <thread>
        
        
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
            class Tracking;  // 源码是注释调的, 不注释也能正常运行, 目前不清楚作者注释的动机
            class LocalMapping;
            class LoopClosing;
        
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
        
                // ORB vocabulary used for place recognition and feature matching.
                // 一个指向ORB字典的指针
                ORBVocabulary* mpVocabulary;
        
                // 关键帧数据库的指针, 这个数据库用于重定位和回环检测
                // KeyFrame database for place recognition (relocalization and loop detection).
                KeyFrameDatabase* mpKeyFrameDatabase;
        
                // 指向地图(数据库)的指针
                // Map structure that stores the pointers to all KeyFrames and MapPoints.
                Map* mpMap;
        
                // 追踪器, 除了进行运动追踪外还要负责创建关键帧, 创建新地图点和进行重定位的工作
                // Tracker. It receives a frame and computes the associated camera pose.
                // It also decides when to insert a new keyframe, create some new MapPoints and
                // performs relocalization if tracking fails.
                Tracking* mpTracker;
        
                // 局部建图器, 局部BA由它进行
                // Local Mapper. It manages the local map and performs local bundle adjustment.
                LocalMapping* mpLocalMapper;
        
                // The viewer draws the map and the current camera pose. It uses Pangolin.
                // 查看器, 可视化界面
                Viewer* mpViewer;
        
                // 帧绘制器
                FrameDrawer* mpFrameDrawer;
                // 地图绘制器
                MapDrawer* mpMapDrawer;
        
                // 系统除了在主进程中进行运动追踪外, 会创建局部建图线程, 回环检测线程和可视化线程
                // System threads: Local Mapping, Loop Closing, Viewer.
                // The Tracking thread "lives" in the main execution thread that creates the System object.
                std::thread* mptLocalMapping;
        
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


- ### 4. src/System.cc

    - Build from scratch - Changed 8
 
    - 在代码最后加上

        ```c++
                // 初始化局部建图器并运行局部建图线程
                // Initialize the Local Mapping thread and launch
                mpLocalMapper = new LocalMapping(mpMap, mSensor==MONOCULAR);
                mptLocalMapping = new thread(&ORB_SLAM2::LocalMapping::Run,mpLocalMapper);
        ```

    - 完整代码

        ```c++
        // 主进程的实现文件
        
        #include <iostream>
        #include <opencv2/core/core.hpp>
        
        #include "System.h"
        
        
        using namespace std;
        
        
        namespace ORB_SLAM2
        {
            // 系统的构造函数, 将会启动其他线程
            // 第一个 System 是类名, 表示这是 ORB_SLAM2::System 类的构造函数
            // 第二个 System 是构造函数的名称, 必须与类名相同
            // 构造函数的参数如下: 词典文件路径, 配置文件路径, 传感器类型, 是否使用可视化界面
            System::System(const string &strVocFile, const string &strSettingsFile,
                           const eSensor sensor, const bool bUseViewer):
                // System 类构造函数的成员初始化列表, 用于初始化类的部分成员变量
                mSensor(sensor), // Origin: mpViewer(static_cast<Viewer*>(NULL)),
                mpViewer(static_cast<Viewer*>(nullptr)), mbReset(false),
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
                // 尝试加载字典
                try
                {
                    mpVocabulary->load(strVocFile);
                    cout << "Vocabulary loaded!" << endl << endl;
                }
                // 如果加载失败, 就输出调试信息
                catch (const exception &e) {
                    cerr << "Wrong path to vocabulary. " << endl;
                    cerr << "Falied to open at: " << strVocFile << endl;
                    // 然后退出
                    exit(-1);
                }
        
                // Create KeyFrame Database
                mpKeyFrameDatabase = new KeyFrameDatabase(*mpVocabulary);
        
                // Create the Map
                mpMap = new Map();
        
                // 这里的帧绘制器和地图绘制器将会被可视化的 Viewer 所使用
                // Create Drawers. These are used by the Viewer
                mpFrameDrawer = new FrameDrawer(mpMap);
                mpMapDrawer = new MapDrawer(mpMap, strSettingsFile);
        
                // 在本主进程中初始化追踪器
                // Initialize the Tracking thread
                // (it will live in the main thread of execution, the one that called this constructor)
                // Tracking 类的构造函数输入的参数如下: this, 字典, 帧绘制器, 地图绘制器, 地图, 关键帧地图, 配置文件路径, 传感器类型
                // this 代表 System 类的当前对象指针
                // 其作用为, Tracking 类的构造函数中的 pSys 参数会接收到 this，也就是当前 System 对象的指针
                // 通过将 this 作为参数传递给 Tracking，能获得 System 类实例的指针，从而可以在 Tracking 类的内部使用它
                mpTracker = new Tracking(this, mpVocabulary, mpFrameDrawer, mpMapDrawer,
                                         mpMap, mpKeyFrameDatabase, strSettingsFile, mSensor);
        
                // 初始化局部建图器并运行局部建图线程
                // Initialize the Local Mapping thread and launch
                mpLocalMapper = new LocalMapping(mpMap, mSensor==MONOCULAR);
                mptLocalMapping = new thread(&ORB_SLAM2::LocalMapping::Run,mpLocalMapper);
        
            }
        
        }
        
        ```


- ### 5. CMakeLists.txt

    - Build from scratch - Changed 8
 
    - 在文件以下位置进行修改, 将 `LocalMapping.cc` 源文件添加到库中
 
        ```cmake
        # 创建一个名为${PROJECT_SOURCE_DIR}的共享库(SHARED表示生成动态链接库), 并将指定的源文件添加到库中
        add_library(${PROJECT_NAME} SHARED
                src/System.cpp
                src/KeyFrameDatabase.cpp
                src/Map.cpp
                src/FrameDrawer.cpp
                src/MapDrawer.cpp
                src/Tracking.cpp
                src/ORBextractor.cpp
                src/LocalMapping.cpp
        )
        ```

    - 完整代码

        ```cmake
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
                src/LocalMapping.cpp
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








