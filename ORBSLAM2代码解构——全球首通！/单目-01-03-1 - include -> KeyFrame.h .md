# 跳转到 include/KeyFrame.h

- 目前先不用阅读 `KeyFrame` 类的构造函数, 因为暂时还没有调用, 所以就不用解析代码了


## 重头开始构建ORBSLAM2

- 如果是从零开始构建 `ORBSLAM2` 系统, 就按照下面给出的文件内容进行代码的编写


- ### 1. KeyFrame.h

    - Build from scratch - Changed 0

    - 定义了一个空的 `KeyFrame` 类

    ```c++
    #ifndef KEYFRAME_H
    #define KEYFRAME_H
    
    namespace ORB_SLAM2
    {
        class KeyFrame
        {
    
        };
    }
    
    #endif //KEYFRAME_H
    
    ```


- ### 2. KeyFrameDatabase.h

    - Build from scratch - Changed 1
 
    - 文件开头加上:
 
    ```c++
    #include "KeyFrame.h"
    ```

    - 完整代码

    ```c++
    #ifndef KEYFRAMEDATABASE_H
    #define KEYFRAMEDATABASE_H
    
    
    #include "ORBVocabulary.h"
    #include "KeyFrame.h"
    
    
    namespace ORB_SLAM2
    {
    
        // 关键帧数据库
        class KeyFrameDatabase
        {
        public:
    
            // 构造函数
            explicit KeyFrameDatabase(const ORBVocabulary &voc);
    
            // 允许类内部和派生类访问, 但不允许外部访问
        protected:
    
            // 预先训练好的词典
            // Associated vocabulary
            const ORBVocabulary* mpVoc;
    
            // 倒排索引, mvInvertedFile[i] 表示包含了第 i 个 word id 的所有关键帧
            // Inverted file
            std::vector<std::list<KeyFrame*>> mvInvertedFile;
    
        };
    
    }
    
    #endif //KEYFRAMEDATABASE_H
    
    ```


- ### 3. KeyFrameDatabase.cc

    - Build from scratch - Changed 1
 
    - 文件开头加上:
 
    ```c++
    #include "KeyFrame.h"
    ```

    - 其实有点没必要, 因为 `KeyFrameDatabase.h` 中已经 `inlcude` 了
 
    - 完整代码


    ```c++
    // 关键帧数据库, 用于回环检测和重定位
    
    
    #include "KeyFrameDatabase.h"
    #include "KeyFrame.h"
    
    
    using namespace std;
    
    
    namespace ORB_SLAM2
    {
    
        // 构造函数
        KeyFrameDatabase::KeyFrameDatabase (const ORBVocabulary &voc):
            mpVoc(&voc)
        {
            // 数据库的主要内容
            mvInvertedFile.resize(voc.size());
        }
    }
    
    ```
