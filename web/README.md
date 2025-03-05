# QFNU 抢课配置生成器

这是一个用于生成 QFNUCourseSelector 配置文件的网页工具。

## 目录结构

```
web/
├── css/            # CSS 样式文件
│   └── styles.css
├── js/             # JavaScript 脚本文件
│   └── scripts.js
├── images/         # 图片资源目录
└── index.html      # 主页面
```

## 使用方法

1. 打开 `index.html` 文件，或直接访问 GitHub Pages 网站
2. 填写基本配置信息（学号、密码等）
3. 添加需要抢的课程信息
4. 点击"复制"按钮复制生成的 JSON 配置
5. 将配置粘贴到 QFNUCourseSelector 的配置文件中

## GitHub Pages 访问

本工具已通过 GitHub Actions 自动部署到 GitHub Pages，您可以通过以下链接访问：

```
https://w1ndys.github.io/QFNUCourseSelector/web/
```

## 功能特点

- 支持多课程配置
- 自动保存表单数据到本地存储
- 实时预览 JSON 配置
- 支持钉钉和飞书通知配置
- 多种选课模式选择

## 注意事项

- 所有数据仅保存在本地浏览器中，不会上传到任何服务器
- 请确保填写正确的课程信息，特别是课程 ID 和教师姓名
- 如果已知 jx02id 和 jx0404id，可以直接填写，无需填写上课时间信息
