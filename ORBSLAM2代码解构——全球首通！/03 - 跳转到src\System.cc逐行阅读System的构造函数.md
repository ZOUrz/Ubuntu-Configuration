```c++
    // 系统的构造函数, 将会启动其他的线程
    // 第一个System是类名, 表示这是ORB_SLAM2::System类的构造函数
    // 第二个System是构造函数的名称, 必须与类名相同
    // 构造函数的参数如下: 词典文件路径, 配置文件路径, 传感器类型, 是否使用可视化界面
    System::System(const string &strVocFile, const string &strSettingsFile,
                   eSensor sensor, bool bUseViewer):
                   // 在构造函数体内, 成员初始化列表用于初始化类的成员变量
                   // 在构造函数执行前设置变量的初始值, 比在构造函数体内赋值更高效
                   mSensor(sensor), mpViewer(static_cast<Viewer*>(nullptr)), mbReset(false),
                   mbActivateLocalizationMode(false), mbDeactivateLocalizationMode(false)
```
