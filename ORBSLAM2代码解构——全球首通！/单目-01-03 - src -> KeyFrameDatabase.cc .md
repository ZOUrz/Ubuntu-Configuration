# 跳转到 src/KeyFrameDatabase.cc 阅读 KeyFrameDatabase 类构造函数的具体实现

- `KeyFrameDatabase` 类的构造函数就几行代码, 比较简单

- 重点是其中的成员变量 `mvInvertedFile`


## 重点代码逐行解析


- ### 1. 构造函数

    ```c++
        // 构造函数
        KeyFrameDatabase::KeyFrameDatabase (const ORBVocabulary &voc):
            mpVoc(&voc)
        {
            // 数据库的主要内容
            mvInvertedFile.resize(voc.size());
        }
    ```

    - 其中, 构造函数以及其成员变量是在 include/KeyFrameDatabase.h 中声明的

    ```c++
            // 构造函数
            explicit KeyFrameDatabase(const ORBVocabulary &voc);
    ```
    
    ```c++
            // 预先训练好的词典
            // Associated vocabulary
            const ORBVocabulary* mpVoc;
    
            // 倒排索引, mvInvertedFile[i] 表示包含了第 i 个 word id 的所有关键帧
            // Inverted file
            std::vector<std::list<KeyFrame*>> mvInvertedFile;
    ```

- ### 2. protected 与 private 的区别

    - 在 `KeyFrameDatabase.h` 中, 其成员变量被设为 `protected`, 以下是 `protected` 和 `private` 的区别:

    - 在 `C++` 中, `protected` 和 `private` 是访问控制修饰符，用来控制类成员(变量, 函数等)对外部代码的可访问性, 它们的区别如下：

        - 1. `private` (私有成员)
            - 访问限制: `private` 成员只能在类的内部被访问, 无法在类的外部或继承类中访问
        - 2. protected(受保护成员)
            - 访问限制: `protected` 成员只能在类的内部和派生类中访问, 但无法在类的外部直接访问


## 需要进行跳转阅读的位置


- ### 1. mvInvertedFile[i]

    ```c++
            // 倒排索引, mvInvertedFile[i] 表示包含了第 i 个 word id 的所有关键帧
            // Inverted file
            std::vector<std::list<KeyFrame*> > mvInvertedFile;
    ```

    - 其中, `std::vector<std::list<KeyFrame*>>` 是一个 `vector` 容器, 其每个元素都是一个 `list`, 而这个 `list` 存储的是指向 `KeyFrame` 类型对象的指针
 
    - 由于 `mvInvertedFile` 只定义了一个存放指针的容器, 并没有实际创建 `KeyFrame` 对象，因此在这行代码中并没有调用 `KeyFrame` 的构造函数

    - `mvInvertedFile` 只是声明了一个向量和链表的结构, 存储的是 `KeyFrame` 类型的指针, 并不会触发 `KeyFrame` 实例的创建
 
    - 因此这行代码不会调用 `KeyFrame` 类的构造函数, 因此只需要跳转到 include/KeyFrame.h 查看
