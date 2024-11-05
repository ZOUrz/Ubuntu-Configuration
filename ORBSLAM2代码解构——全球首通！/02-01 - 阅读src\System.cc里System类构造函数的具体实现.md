# src\System.cc

主要阅读该文件中 **System 类的构造函数**


## 逐行解析

### 1. 部分成员变量的初始化

```c++
    // 系统的构造函数, 将会启动其他线程
    // 第一个 System 是类名, 表示这是 ORB_SLAM2::System 类的构造函数
    // 第二个 System 是构造函数的名称, 必须与类名相同
    // 构造函数的参数如下: 词典文件路径, 配置文件路径, 传感器类型, 是否使用可视化界面
    System::System(const string &strVocFile, const string &strSettingsFile,
                   const eSensor sensor, const bool bUseViewer):
        // System 类构造函数的成员初始化列表, 用于初始化类的部分成员变量
        mSensor(sensor), mpViewer(static_cast<Viewer*>(nullptr)), mbReset(false),
        mbActivateLocalizationMode(false), mbDeactivateLocalizationMode(false)
```

其中, mSensor, mpViewer, mbReset, mbActivateLocalizationMode, mbDeactivateLocalizationMode 是 System 类的 成员变量

#### ORBSLAM2中变量遵循的命名规则

遵循的命名规则也被称作**匈牙利命名法**

* 变量名的第一个字母为 m 表示该变量为某类的成员变量
* 变量名的第一, 第二个字母表示数据类型:
    * p 表示指针类型
    * n 表示 int 类型
    * b 表示 bool 类型
    * s 表示 std::set 类型
    * v 表示 std::vector 类型
    * l 表示 std::list 类型
    * KF 表示 KeyFrame 类型

```c++
        // 传感器类型
        // Input sensor
        eSensor mSensor;



```


