# 地球 Online 游戏看板 Earth Online Kanban

![GitHub stars](https://img.shields.io/github/stars/JyiDeng/earth-online-kanban?style=social)
![GitHub license](https://img.shields.io/github/license/JyiDeng/earth-online-kanban)
![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)

【地球Online看板】系统已绑定，宿主您当前的属性值是.......

关键词： **自我监控** **健康管理** **动机激励**
地球 Online 桌面游戏看板应用，可视化和跟踪人类您的日常生活中的各种属性状态，帮助你以游戏化的方式，更加量化地监控自己的生活状态。

## 效果图

看板：

<p align="center">
  <img src="pic/Kanban.png" alt="地球Online面板截图" width="700">
</p>

设置界面：

<p align="center">
  <img src="pic/Settings.png" alt="地球Online设置界面截图" width="700">
</p>

## 功能特点

- **简洁**的游戏风格界面，分类显示不同属性
- 进度条**不同颜色**（红色=危险，黄色=警告，绿色=健康）
- 多种属性状态**实时更新**，模拟真实生活状态的波动，自定义属性变化速率
- 可**自定义**玩家名称和初始属性值
- **保存和加载**玩家数据
- 非常**轻量级**，只需要运行单个 python 文件
- 本地运行，内容**安全**

## 属性列表

地球Online看板跟踪以下三大类15种属性：（未来必然会添加更多，分类也更加完善）

| 类别 | 属性 | 图标 | 
|------|------|------|
| **生理需求** | 饥饿 | 🍔 | 
| | 口渴 | 💧 | 
| | 上厕所 | 🚽 |
| | 肥胖指数 | ⚖️ | 
| | 心脏健康度 | ❤️ | 
| **情感状态** | 社交欲望 | 👥 | 
| | 情绪 | 😊 | 
| | 成就感 | 🏆 | 
| | 情商 | 🧠 |
| | 爱心 | 💖 |
| **能力属性** | 肌肉强度 | 💪 | 
| | 敏捷 | 🏃 | 
| | 抗击打能力 | 🛡️ | 
| | 魅力 | ✨ | 
| | 道德 | ⚖️ |  

## 安装运行方法

1. 克隆此仓库：

```bash
git clone https://github.com/JyiDeng/earth-online-kanban.git
cd earth-online-kanban
```

应当不需要安装额外依赖。

2. 执行以下命令启动应用程序：

```bash
python earth_online_kanban.py
```

你将看到弹窗！成功运行！

## 项目结构

```
earth-online-kanban/
├── earth_online_kanban.py  # 主程序文件
├── player_data.json        # 玩家数据存储文件
├── README.md               # 项目说明文档
└── pic/                    # 截图文件夹
```

## 扩展计划

未来计划添加的功能：

- [] ❗事件系统 - 用户输入事件，手动或自动影响属性值
- [] ❗穿戴智能 - 结合手表等健康数据，实时传入数据优化属性配置
- [] ❗自动学习用户数据 - 根据用户指标变化规律，接入大模型API，拟合属性变化趋势（恶魔低语：有一天，是否会完全模拟出你的行为？）
- [] ❗AI 教练 - 针对某个想控制的指标（譬如喝水口渴值），设定需要控制的范围（譬如介于40%-90%之间），程序提出个性化方案督促完成，监控指标变化效果
- [] 更多自带属性 - 天气与情绪、创造力、视疲劳程度......
- [] 更多自带栏目 - 将每一项分为大类、每一类目可折叠，譬如情绪分为快乐、愤怒、悲伤、无聊等，计算机技能拆成Leetcode、Python、科研能力......
- [] 自定义属性 - 用户增加个性化属性大类、属性细则，并支持调整参数变化速度
- [] 成就系统 - 达成特定条件获得成就，譬如属性数值本身、完成某事件的次数
- [] 任务系统 - 完成任务提升属性
- [] 统计和图表 - 可视化属性变化历史
- [] 通知系统 - 当属性达到危险值时发出提醒
- [] 多人系统 - 可选择向他人展示部分属性，增强互动性
- [] 定期总结 - 数据周报、月报；趋势图
- [] 多样化主题 - 支持黑夜模式和其他配色

## 贡献指南

欢迎对此项目做出贡献！可以通过以下方式参与：

0. 在 Issue 中提出创新的功能想法
1. Fork 仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建一个 Pull Request

## 使用许可

根据 MIT 许可证分发。查看 `LICENSE` 文件获取更多信息。

## 致谢

- 灵感来源于生活游戏化和RPG游戏系统
- Python Tkinter库提供的简洁GUI实现
- 所有关于"地球Online"概念的有趣讨论

## 联系方式

项目维护者: [Your Name](https://github.com/JyiDeng)

项目链接: [https://github.com/yourusername/earth-online-kanban](https://github.com/JyiDeng/earth-online-kanban) 