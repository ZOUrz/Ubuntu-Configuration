# src/KeyFrame.cc

与 src/KeyFrameDatabase.cc类似, KeyFrame 类构造函数的代码比较简单, 重点是其成员变量的初始化列表中使用了大量来自其他文件的类


## 重点代码逐行解析


### src/KeyFrame.cc代码

无需多言

```c++
    KeyFrame::KeyFrame(Frame &F, Map *pMap, KeyFrameDatabase *pKFDB):
        mnFrameId(F.mnId),  mTimeStamp(F.mTimeStamp), mnGridCols(FRAME_GRID_COLS), mnGridRows(FRAME_GRID_ROWS),
        mfGridElementWidthInv(Frame::mfGridElementWidthInv), mfGridElementHeightInv(Frame::mfGridElementHeightInv),
        mnTrackReferenceForFrame(0), mnFuseTargetForKF(0), mnBALocalForKF(0), mnBAFixedForKF(0),
        mnLoopQuery(0), mnLoopWords(0), mnRelocQuery(0), mnRelocWords(0), mnBAGlobalForKF(0),
        fx(Frame::fx), fy(Frame::fy), cx(Frame::cx), cy(Frame::cy), invfx(Frame::invfx), invfy(Frame::invfy),
        mbf(F.mbf), mb(F.mb), mThDepth(F.mThDepth), N(F.N), mvKeys(F.mvKeys), mvKeysUn(F.mvKeysUn),
        mvuRight(F.mvuRight), mvDepth(F.mvDepth), mDescriptors(F.mDescriptors.clone()),
        mBowVec(F.mBowVec), mFeatVec(F.mFeatVec), mnScaleLevels(F.mnScaleLevels), mfScaleFactor(F.mfScaleFactor),
        mfLogScaleFactor(F.mfLogScaleFactor), mvScaleFactors(F.mvScaleFactors), mvLevelSigma2(F.mvLevelSigma2),
        mvInvLevelSigma2(F.mvInvLevelSigma2),
        mnMinX(static_cast<int>(Frame::mnMinX)), mnMinY(static_cast<int>(Frame::mnMinY)),
        mnMaxX(static_cast<int>(Frame::mnMaxX)), mnMaxY(static_cast<int>(Frame::mnMaxY)),
        mK(F.mK), mvpMapPoints(F.mvpMapPoints), mpKeyFrameDB(pKFDB),
        mpORBvocabulary(F.mpORBvocabulary), mbFirstConnection(true), mpParent(nullptr), mbNotErase(false),
        mbToBeErased(false), mbBad(false), mHalfBaseline(F.mb/2), mpMap(pMap)
    {
        // 获取 ID
        mnId=nNextId++;

        // 根据指定的普通帧, 初始化用于加速匹配的网格对象信息
        // 其实就是把每个网格中有的特征点的索引复制过来
        mGrid.resize(mnGridCols);
        for(int i=0; i<mnGridCols;i++)
        {
            mGrid[i].resize(mnGridRows);
            for(int j=0; j<mnGridRows; j++)
                mGrid[i][j] = F.mGrid[i][j];
        }

        // 设置当前关键帧的位姿
        SetPose(F.mTcw);
    }
```


### include/KeyFrame.h

上面所出现的成员变量均在 include/KeyFrame.h 中定义

```c++
// 关键帧类
    class KeyFrame
    {
    public:
        // 构造函数
        KeyFrame(Frame &F, Map* pMap, KeyFrameDatabase* pKFDB);


        // The following variables are accessed from only 1 thread or never change (no mutex needed).

        // nNextID 名字改为 nLastID更合适, 表示上一个KeyFrame的 ID
        static long unsigned int nNextId;
        // 在 nNextID 的基础上加 1 就得到了mnID, 为当前KeyFrame的 ID
        long unsigned int mnId;
        // 每个 KeyFrameId 基本属性是它是一个 Frame, KeyFrame 初始化的时候需要 Frame
        // mnFrameId 记录了该 KeyFrame 是由哪个 Frame 初始化的
        const long unsigned int mnFrameId;

        // 时间戳
        const double mTimeStamp;

        // 和 Frame 类中的定义相同
        // Grid (to speed up feature matching)
        const int mnGridCols;
        const int mnGridRows;
        const float mfGridElementWidthInv;
        const float mfGridElementHeightInv;

        // Variables used by the tracking
        long unsigned int mnTrackReferenceForFrame;  // 记录它
        long unsigned int mnFuseTargetForKF;  // 标记在局部建图线程中, 和哪个关键帧进行融合的操作

        // Variables used by the local mapping
        // LocalMapping 中记录当前处理的关键帧的 mnId, 表示当前局部 BA 的关键帧 id, mnBALocalForKF 在 MapPoint.h 里也有同名的变量
        long unsigned int mnBALocalForKF;
        // LocalMapping 中记录当前处理的关键帧的 mnId, 只是提供约束信息但却不会去优化这个关键帧
        long unsigned int mnBAFixedForKF;

        // Variables used by the keyframe database 下面这些变量都是临时的, 由外部调用暂时存放一些数据
        // 标记了当前关键帧是 id 为 mnLoopQuery 的回环检测的候选关键帧
        long unsigned int mnLoopQuery;
        // 当前关键帧和这个形成回环的候选关键帧中, 具有相同的 word 个数
        int mnLoopWords;
        // 与那个形成回环的关键帧的词袋匹配程度的评分
        float mLoopScore;
        // 用来存储在辅助进行重定位的时候, 要进行重定位的那个帧的 id
        long unsigned int mnRelocQuery;
        // 当前关键帧和那个要进行重定位的帧, 具有相同的 word 个数
        int mnRelocWords;
        // 与那个要进行重定位的帧的词袋匹配程度的评分
        float mRelocScore;


        // 记录是由于哪个"当前关键帧"触发的全局BA, 用来防止重复写入
        long unsigned int mnBAGlobalForKF;

        // Calibration parameters
        const float fx, fy, cx, cy, invfx, invfy, mbf, mb, mThDepth;

        // Number of KeyPoints
        const int N;

        // 与 Frame 类中的定义相同
        // KeyPoints, stereo coordinate and descriptors (all associated by an index)
        const std::vector<cv::KeyPoint> mvKeys;
        const std::vector<cv::KeyPoint> mvKeysUn;
        const std::vector<float> mvuRight;  // negative value for monocular points
        const std::vector<float> mvDepth;  // negative value for monocular points
        const cv::Mat mDescriptors;

        // BoW
        // Origin:
        // DBoW2::BowVector mBowVec;
        // DBoW2::FeatureVector mFeatVec;

        // Vector of words to represent images
        // mBowVec 内部实际存储的是 std::map<WordId, WordValue>
        // WordId 和 WordValue 表示 Word 在叶子中的 id 和权重
        DBoW3::BowVector mBowVec;
        // Vector of nodes with indexes of local features
        // 内部实际存储 std::map<NodeId, std::vector<unsigned int>>
        // NodeId 表示节点 id, std::vector<unsigned int> 中实际存的是该节点 id 下所有特征点在图像中的索引
        DBoW3::FeatureVector mFeatVec;

        // Grid over the image to speed up feature matching
        std::vector< std::vector <std::vector<size_t>>> mGrid;  // 可以认为是二维的, 第三维的 vector 中保存这个网格内特征点的索引

        // Scale
        const int mnScaleLevels;
        const float mfScaleFactor;
        const float mfLogScaleFactor;
        const std::vector<float> mvScaleFactors;  // 尺度因子, scale^n, scale=1.2, n为层数
        const std::vector<float> mvLevelSigma2;  // 尺度因子的平方
        const std::vector<float> mvInvLevelSigma2;

        // Image bounds and calibration
        const int mnMinX;
        const int mnMinY;
        const int mnMaxX;
        const int mnMaxY;
        const cv::Mat mK;


    // The following variables need to be accessed through a mutex to be thread safe.
    protected:

        // MapPoints associated to keypoints
        std::vector<MapPoint*> mvpMapPoints;

        // BoW
        KeyFrameDatabase* mpKeyFrameDB;
        // 词袋对象
        ORBVocabulary* mpORBvocabulary;

        // Spanning Tree and Loop Edges
        bool mbFirstConnection;  // 是否是第一次生成树
        KeyFrame* mpParent;  // 当前关键帧的父关键帧(共视程度最高的)

        // Bad flags
        bool mbNotErase;  // 当前关键帧已经和其他的关键帧形成了回环关系, 因此在各种优化的过程中不应该被删除
        bool mbToBeErased;
        bool mbBad;

        float mHalfBaseline;  // 对于双目相机, 双目相机基线长度的一半, Only for visualization

        Map* mpMap;

    };
```

## 需要进行跳转阅读的位置

### 1. Frame 类构造函数


