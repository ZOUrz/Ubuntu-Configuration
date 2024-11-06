# src/KeyFrameDatabase

KeyFrameDatabase 类的构造函数就几行代码, 难点在于其使用的成员变量 mvInvertedFile 的数据类型是来由其他文件中定义的


## 重点代码逐行解析

```c++
    // 构造函数
    KeyFrameDatabase::KeyFrameDatabase (const ORBVocabulary &voc):
        mpVoc(&voc)
    {
        // 数据库的主要内容
        mvInvertedFile.resize(voc.size());
    }
```

其中, 构造函数以及其成员变量是在 include/KeyFrameDatabase.h 中定义的

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

在 KeyFrameDatabase.h 中, 其成员变量被设为 protected, 以下是 protected 和 private的区别:

* 在 C++ 中，protected 和 private 是访问控制修饰符，用来控制类成员(变量, 函数等)对外部代码的可访问性, 它们的区别如下：

    * 1. private (私有成员)
        * 访问限制: private 成员只能在类的内部被访问, 无法在类的外部或继承类中访问
    * 2. protected(受保护成员)
        * 访问限制: protected成员只能在类的内部和派生类中访问, 但无法在类的外部直接访问


## 需要进行跳转阅读的位置

### 1. mvInvertedFile[i]

```c++
        // 倒排索引, mvInvertedFile[i] 表示包含了第 i 个 word id 的所有关键帧
        // Inverted file
        std::vector<std::list<KeyFrame*> > mvInvertedFile;
```

其中, std::vector<std::list<KeyFrame*>> 是一个 vector 容器, 其每个元素都是一个 list, 而这个 list 存储的是指向 KeyFrame 类型对象的指针
