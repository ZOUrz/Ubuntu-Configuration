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


         
        - #### 2-2. 检查是否有待处理关键帧

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


        - #### 2-3. 检查是否有停止请求

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

            - #### 2-3-1. 检查状态
         
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
                
            - #### 2-3-2. 退出主循环

                - `CheckFinish()` 若返回 `true`, 则退出主循环, 线程准备结束
             
                    ```c++
                                    // 然后确定终止了就跳出这个线程的主循环
                                    if(CheckFinish())
                                        break;
                    ```


        - ### 2-4. 检查是否有复位请求
     
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

        - ### 2-5. 重新设置允许插入关键帧
     
            - 重新设置 `mbAcceptKeyFrames` 为 `true`, 允许 `Tracking` 插入关键帧
     
                ```
                            // Tracking will see that Local Mapping is busy
                            SetAcceptKeyFrames(true);
                ```

        - ### 2-6. 检查线程是否应结束
     
            - 如果有终止请求, 则退出主循环, 结束线程
     
                ```c++
                            // 如果当前线程已经结束了就跳出主循环
                            if(CheckFinish())
                                break;
                ```

        - ### 2-7. 每隔 3 毫秒检查一次
     
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

