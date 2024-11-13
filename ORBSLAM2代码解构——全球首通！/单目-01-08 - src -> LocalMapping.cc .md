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


- #### SetAcceptKeyFrames

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

- ####  CheckNewKeyFrames

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

```c++
        // Tracking 线程向 LocalMapping 中插入关键帧是先插入到该队列中
        // 等待处理的关键帧列表
        std::list<KeyFrame*> mlNewKeyFrames;

        // 操作关键帧列表时使用的互斥锁
        std::mutex mMutexNewKFs;
```

- #### Stop

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

- #### isStopped

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

- #### CheckFinish

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

- #### ResetIfRequested

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

```c++
        // 存储当前关键帧生成的地图点, 也是等待检查的地图点列表
        std::list<MapPoint*> mlpRecentAddedMapPoints;
```

- #### SetFinish

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



