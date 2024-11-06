# src/KeyFrameDatabase

在C++中，protected和private是访问控制修饰符，用来控制类成员（变量、函数等）对外部代码的可访问性。它们的区别如下：

1. private（私有成员）
访问限制：private成员只能在类的内部被访问，无法在类的外部或继承类中访问。
用途：通常用来封装类的内部实现，避免外部直接访问和修改，确保数据的安全性和完整性。

2. protected（受保护成员）
访问限制：protected成员只能在类的内部和派生类中访问，但无法在类的外部直接访问。
用途：允许派生类访问基类的成员，适用于那些派生类可能需要访问的内部数据，但不希望外部直接访问。

总结：
private：仅允许类内部访问。
protected：允许类内部和派生类访问，但不允许外部访问。

```c++
    // 构造函数
    KeyFrameDatabase::KeyFrameDatabase (const ORBVocabulary &voc):
        mpVoc(&voc)
    {
        // 数据库的主要内容
        mvInvertedFile.resize(voc.size());
    }
```

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
        std::vector<std::list<KeyFrame*> > mvInvertedFile;
```

