# QFNUCourseSelector

> QFNU 抢课脚本 | 曲阜师范大学抢课脚本 | 强智教务抢课脚本 | 强智教务 2017 | 大学抢课脚本 | 学院抢课脚本 | 光速抢课 | 毫秒级抢课
>
> 本脚本以强智教务系统 2017 版本为基础，支持 2017 版本的所有功能，包括选修选课、专业内跨年级选课、本学期计划选课、公选课选课、计划外选课，其他版本未测试，但基本的请求 API 几乎类似，可以参考本脚本实现

<p align="center">
    <img src="https://img.shields.io/github/stars/W1ndys/QFNUCourseSelector?style=flat-square" alt="Stars">
    <img src="https://img.shields.io/github/issues/W1ndys/QFNUCourseSelector?style=flat-square" alt="Issues">
    <img src="https://img.shields.io/badge/Python-3.12.3-blue.svg" alt="Python">
    <img src="https://img.shields.io/badge/状态-开发完成-green.svg" alt="Status">
    <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
    <img src="https://img.shields.io/github/forks/W1ndys/QFNUCourseSelector?style=flat-square" alt="Forks">
    <img src="https://img.shields.io/github/watchers/W1ndys/QFNUCourseSelector?style=flat-square" alt="Watchers">
    <img src="https://img.shields.io/github/last-commit/W1ndys/QFNUCourseSelector?style=flat-square" alt="Last Commit">
</p>

<div align="center">
    <h3>
        ✨ <b>请给我一个 Star!  Please give me a Star!</b> ✨
    </h3>
</div>

## 本脚本初衷是为了告别卡顿页面，还学生一个流畅的选课体验，请谨慎使用，请勿滥用，请勿在大陆范围内所有社交媒体平台软件等传播

## 本脚本正在重构，可能不稳定，不推荐使用，重构维护期间造成的后果与本项目无关（重构进度1%）

## ✨ 功能

- 🚀 通过发送请求包的方式选课，不依赖浏览器页面渲染，速度快的起飞
- 🎯 支持多种选课功能（选修选课、专业内跨年级选课、本学期计划选课、公选课选课、计划外选课）
- 📱 支持多种通知方式（钉钉、飞书）
- 🔄 支持多种选课模式（高速模式、普通模式、蹲课模式）
- 👥 支持多账号执行（批量启动）
- 📚 支持多课程执行（courses 数组）
- 💻 支持多系统执行（Windows、Linux、MacOS）
- ⏰ 支持多种节次配置
- 📅 支持多种周次配置
- ✅ 支持选课成功自动退出
- 🔄 支持选课失败自动重试
- 📝 支持日志记录，不会因为程序运行结束而丢失日志
- 🛠️ 支持环境部署脚本化，就算是傻瓜也可以一键部署~
- ⚡ 已实现抢课 0 耗时
- 🛠️ 提供网页版配置生成器，轻松生成配置文件

## 🌐 在线配置生成器

为了方便用户使用，我们提供了一个在线的配置生成器，您可以通过以下链接访问：

```
https://w1ndys.github.io/QFNUCourseSelector/web/
```

- 🖥️ 直观的Web界面，无需手动编写JSON
- 💾 自动保存表单数据到本地浏览器
- 📋 一键复制生成的配置
- 🔒 所有数据仅保存在本地，不会上传到任何服务器

## 📝 免责声明

> ⚠️ 使用本脚本前请仔细阅读以下声明

1. 本脚本初衷是为了告别卡顿页面，还学生一个流畅的选课体验，
2. 本脚本仅供学习和研究目的，用于了解网络编程和自动化技术的实现原理，禁止用于真实的选课环境。

3. 使用本脚本可能违反学校相关规定。使用者应自行承担因使用本脚本而产生的一切后果，包括但不限于：

   - 账号被封禁
   - 选课资格被取消
   - 受到学校纪律处分
   - 其他可能产生的不良影响

4. 严禁将本脚本用于：

   - 商业用途
   - 干扰教务系统正常运行
   - 影响其他同学正常选课
   - 其他任何非法或不当用途

5. 下载本脚本即视为您已完全理解并同意本免责声明。请在下载后 24 小时内删除。

6. 开发者对使用本脚本造成的任何直接或间接损失和后果不承担任何责任。

## 🔧 环境要求

- Python 3.12.3（其他版本未测试，最高版本支持 3.12）
- pip 包管理器
- 支持 Windows/Linux/MacOS

## 🚀 使用指南

### 1. 克隆项目

```bash
git clone git@github.com:W1ndys/QFNUCourseSelector.git
```

> 直接下载 zip 包也可以，但是需要把 bat 文件的行位序列改成 CRLF，否则会报错

### 2. 安装依赖

Windows 用户双击 `create_venv_windows.bat` 并等待安装完成

Linux 用户执行 `bash create_venv_linux.sh` 安装依赖

### 3. 首次运行

Windows 用户双击 `run_app_in_venv_windows.bat`，系统将自动生成配置文件 `config.json`

Linux 用户执行 `bash run_app_in_venv_linux.sh`，系统将自动生成配置文件 `config.json`

### 4. 配置文件说明

`config.json` 配置示例：

```json
{
  "user_account": "你的学号", // 必填
  "user_password": "你的密码", // 必填
  "select_semester": "你的选课学期，例如：2024-2025-2学期2021级选课", // 选填
  "dingtalk_webhook": "你的钉钉机器人webhook", // 选填
  "dingtalk_secret": "你的钉钉机器人secret", // 选填
  "feishu_webhook": "你的飞书机器人webhook", // 选填
  "feishu_secret": "你的飞书机器人secret", // 选填
  "mode": "选课模式", // 选课模式，fast: 高速模式，normal: 普通模式，snipe: 蹲课模式
  "course": [
    {
      "course_id_or_name": "课程id", // 必填
      "teacher_name": "教师名称", // 必填
      "week_day": "上课星期", // 选填(1-7)
      "weeks": "上课周次", // 选填，支持多种格式，例如："1-12"、"1-12,13-14"、"1,3,5,7,9,11,13,15,17"
      "class_period": "上课节次", // 选填
      "jx02id": "jx02id", // 选填
      "jx0404id": "jx0404id" // 选填
    }
    //...
    // 可以添加多个课程，脚本执行的时候从第一个开始依次执行
  ]
}
```

#### 选课模式说明：

| 模式     | 值     | 说明                                                                   |
| -------- | ------ | ---------------------------------------------------------------------- |
| 高速模式 | fast   | 以最快速度持续尝试选课，适用于系统即将开放选课时抢课，抢课耗时几乎为 0 |
| 普通模式 | normal | 每 5 秒一次选课，适用于害怕高速抢课被 ban 的用户                       |
| 蹲课模式 | snipe  | 每 2 秒一次持续选课，适用于补选中退选轮次的临界时间和正选中全天候蹲课  |

> 如果不填填错，脚本会默认使用蹲课模式

#### 配置项说明：

| 字段              | 说明                           | 是否必填 | 示例                                          |
| ----------------- | ------------------------------ | -------- | --------------------------------------------- |
| course_id_or_name | 课程编号或名称（推荐使用编号） | ✅       | g20062389                                     |
| teacher_name      | 教师姓名                       | ✅       | 张三                                          |
| week_day          | 上课星期                       | ⭕       | 1-7 之间的数字                                |
| weeks             | 上课周次                       | ⭕       | "1-12"、"1-12,13-14"、"1,3,5,7,9,11,13,15,17" |
| class_period      | 上课节次                       | ⭕       | 1-2,1-3,1-4,9-10,9-11                         |
| jx02id            | 公选课 jx02id                  | ⭕       | -                                             |
| jx0404id          | 公选课 jx0404id                | ⭕       | -                                             |

> [!WARNING]
>
> 你的配置一定是下面两种情况之一：
>
> 1. 你已经手动获取了 jx02id 和 jx0404id，则只需要填写 `course_id_or_name` 、 `teacher_name` 、 `jx02id` 、 `jx0404id` 这四个字段，脚本会根据这四个字段直接选课
>
> 2. 你未手动获取 jx02id 和 jx0404id，则需要填写 `course_id_or_name` 、 `teacher_name` 、 `class_period` 、 `week_day` 、 `weeks` 这五个字段，脚本会根据这五个字段搜索课程，并获取课程的 `jx02id` 和 `jx0404id`
>
> `course_id_or_name` 、 `teacher_name` 是必填项，将用于获取课程的 jx02id 和 jx0404id
>
> `class_period` 和 `week_day` 是选填项，如果你未填写 `jx02id` 和 `jx0404id`，则需要填写这两个字段，脚本会根据这两个字段搜索课程，并获取课程的 `jx02id` 和 `jx0404id`
>
> `class_period` 是上课节次，可以与教务系统对应，例如：1-2,1-3,1-4,9-10,9-11
>
> > 此处配置旧版脚本强制要求为 1-2- 等固定格式，由于 2025 年 2 月 18 日晚上发现非正常发包，即直接发课程节次也可以正常搜索，所以 [新版脚本](https://github.com/W1ndys/QFNUCourseSelector/commit/f42d9dd4fddafa27cd95dfdd7f46898efabfe9a1) 已支持直接发课程节次，遵循配置节次的范围为搜索结果的子集，例如搜 1-2，也可以搜到 1-3,1-4 的符合条件的课程
>
> `weeks` 支持多种格式的周次配置：
>
> - 连续周次：如 "1-12"、"1-18" 等
> - 多个周次范围：如 "1-12,13-14"、"1-9,11-18" 等
> - 不连续周次：如 "1,3,5,7,9,11,13,15,17"（单周）、"2,4,6,8,10,12,14,16,18"（双周）等
>
> 如果填写了 jx02id 和 jx0404id，则不需要填写 `class_period` 和 `week_day`，脚本会根据这两个字段直接选课

> [!NOTE]
>
> 关于 jx02id 和 jx0404id 的 **手动** 获取方法，请参考 [详细说明文档](./assets/docs/how_to_get_jx02id_and_jx0404id.md)
>
> jx02id 和 jx0404id 是教务系统中课程的唯一标识，在配置文件中选填，如果不填，脚本会根据 API 搜索自动获取，可能(极少情况)会遇到获取失败的情况，并且抢课速度会慢 10-50ms
>
> 手动获取请确保在配置文件中填写正确，不要填反了，否则无法正常选课（返回 None）
>
> **脚本运行过程中不要异地登录，否则会把脚本踢下线**

### 5. 运行脚本

Windows 用户双击 `run_app_in_venv_windows.bat` 运行脚本

Linux 用户执行 `bash run_app_in_venv_linux.sh` 运行脚本

## 程序流程图

```mermaid
flowchart TB
    Start([开始]) --> LoadEnv[加载环境变量和配置]
    LoadEnv --> Login{登录尝试}

    Login -->|失败| RetryLogin[等待1秒后重试]
    RetryLogin --> Login

    Login -->|成功| GetSemester[获取选课轮次ID]
    GetSemester -->|失败| RetryLogin

    GetSemester -->|成功| CheckMode{检查选课模式}

    CheckMode -->|Fast模式| FastMode[快速选课]
    CheckMode -->|Normal模式| NormalMode[普通选课]
    CheckMode -->|Snipe模式| SnipeMode[蹲课模式]

    subgraph FastMode[快速模式]
        F1[遍历课程列表] --> F2{尝试选课}
        F2 -->|成功| F3[更新课程状态]
        F2 -->|失败| F1
        F3 --> F4{所有课程已选?}
        F4 -->|是| Exit
        F4 -->|否| F1
    end

    subgraph NormalMode[普通模式]
        N1[遍历课程列表] --> N2{尝试选课}
        N2 -->|成功| N3[更新课程状态]
        N2 -->|失败| N4[等待5秒]
        N3 --> N5{所有课程已选?}
        N4 --> N1
        N5 -->|是| Exit
        N5 -->|否| N1
    end

    subgraph SnipeMode[蹲课模式]
        S1[刷新选课轮次] --> S2[遍历课程列表]
        S2 --> S3{尝试选课}
        S3 -->|成功| S4[更新课程状态]
        S3 -->|失败| S5[继续下一个课程]
        S4 --> S6{所有课程已选?}
        S5 --> S6
        S6 -->|是| Exit
        S6 -->|否| S7[等待2秒]
        S7 --> S1
    end

    FastMode & NormalMode & SnipeMode --> Exit([结束])

    subgraph CourseSelection[选课流程]
        CS1[获取课程信息] --> CS2{检查jx02id和jx0404id}
        CS2 -->|已配置| CS3[直接选课]
        CS2 -->|未配置| CS4[搜索课程信息]
        CS4 --> CS5[尝试不同选课接口]
        CS5 --> CS6{选课结果}
        CS6 -->|成功| CS7[发送成功通知]
        CS6 -->|失败| CS8[发送失败通知]
    end
```

### 流程说明

1. **初始化阶段**

   - 加载环境变量和配置文件
   - 初始化日志系统
   - 建立会话连接

2. **登录阶段**

   - 获取验证码并识别
   - 尝试登录，失败后重试
   - 成功后获取选课轮次 ID

3. **选课模式**

   - Fast 模式：以最快速度持续尝试选课
   - Normal 模式：每次选课后等待 5 秒
   - Snipe 模式：持续刷新选课轮次并尝试选课

4. **选课流程**

   - 获取课程信息
   - 检查是否已配置课程 ID
   - 尝试不同类型的选课接口
   - 发送选课结果通知

5. **通知系统**
   - 支持钉钉通知
   - 支持飞书通知
   - 实时反馈选课状态

## 🔧 扩展使用

### ⏰ 定时执行

Linux 系统可以使用 `crontab` 命令，Windows 系统可以使用 `任务计划程序` 来实现，但不建议使用 Windows

Windows 性能好的情况下可以考虑使用命令行 Linux 虚拟机实现定时执行

### 👥 多账号执行

Windows 可以使用 bat 脚本调用执行每个配置文件，Linux 可以使用 shell 脚本调用执行每个配置文件

## 📝 配置生成器

为了方便用户生成配置文件，本项目提供了一个网页版的配置生成器：

1. 打开 `web/index.html` 文件
2. 填写基本配置信息（学号、密码等）
3. 添加需要抢的课程信息
4. 点击"复制"按钮复制生成的 JSON 配置
5. 将配置粘贴到 `config.json` 文件中

配置生成器的详细说明请参考 [web/README.md](web/README.md)

## ⚠️ 异常情况

### 报错下面内容

```py
TypeError:DdddOcr.__init__()got an unexpected keyword argument 'show_ad'
```

解决办法：https://github.com/W1ndys/QFNUCourseSelector/issues/8

## 🌐 关于用啥选的快

直接点题：QFNU（这里指曲阜师范大学校园 WiFi 校园网），比其他网络更容易访问教务系统

cmd 命令行输入 `ping zhjw.qfnu.edu.cn`

![Windows10 测试环境](./assets/images/wifi_test_win10.png)

![手机测试环境](./assets/images/wifi_test_mobile.png)

![Pad 测试环境](./assets/images/wifi_test_pad.png)

可以很明显的看到，QFNU 的网络环境比其他网络环境更容易访问教务系统

以上环境是在网络通畅的情况下测试，所以几十毫秒的差距对正常使用来说几乎无感，在网络拥堵的情况下差距将进一步扩大

但是当选课服务器接近崩溃的时候，两者的差距几乎可以忽略不计，就变成大家都进不去

## 🏆 战绩

<div style="display: flex; flex-wrap: wrap; gap: 10px; justify-content: center;">
    <img src="./assets/images/Achievement/1.png" style="max-width: 100%; height: auto;" alt="选课成功截图">
    <img src="./assets/images/Achievement/2.png" style="max-width: 100%; height: auto;" alt="选课成功截图">
</div>

## 🌟 Star History

<!-- 添加 Star History -->
<p align="center">
  <a href="https://star-history.com/#W1ndys/QFNUCourseSelector&Date">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=W1ndys/QFNUCourseSelector&type=Date&theme=dark" />
      <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=W1ndys/QFNUCourseSelector&type=Date" />
      <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=W1ndys/QFNUCourseSelector&type=Date" />
    </picture>
  </a>
</p>

## 🙏 致谢

特别感谢以下贡献者：

- [nakaii](https://github.com/nakaii-002) - 技术指导
- [上杉九月](https://github.com/sakurasep) - 技术指导
- [AuroBreeze](https://github.com/AuroBreeze) - 登录算法优化
- 超级大猫猫头头 - 测试支持
- [Cursor](https://www.cursor.com/) - 开发工具支持

## 🔗 友情链接

- [QFNU 抢课脚本增强版](https://github.com/Swcmb/QFNUCourseSelector-Pro)

  > 注：该项目为本项目的衍生版本，功能更新可能不及时，请自行验证代码可用性和安全性
  >
  > 本项目开发者未参与其项目开发，请以本项目功能更新为准

- [使用 Python 实现的抢课脚本](https://github.com/AuroBreeze/QFNUClassSelector)

  > 注：该项目是另一位开发者的版本，借鉴了本项目部分代码，与本项目无从属关系，本项目开发者未参与该项目的开发

## 📄 许可证

本项目采用 [GNU General Public License v3 (GPLv3)](./LICENSE)。

特别说明：

1. 本项目仅供学习和研究使用
2. 严禁用于商业用途
3. 任何衍生项目必须使用相同许可证开源
