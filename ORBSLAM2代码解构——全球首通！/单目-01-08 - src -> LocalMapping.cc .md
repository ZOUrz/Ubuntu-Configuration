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

```c++

```



