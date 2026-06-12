# 🌸 智能桌面工作助手

> 可爱风格的桌面任务管理工具，支持任务追踪、定时提醒、自动日报生成

---

## ✨ 功能特性

- 🎯 **任务管理** — 进行中 / 即将做 / 已完成 / 回收站，四分类清晰管理
- ⏰ **定时提醒** — 可视化日期时间选择器，到点自动弹窗提醒
- 📊 **一键总结** — 自动生成当日工作总结，支持复制
- 📅 **按天存储** — 每天独立数据文件，0点自动迁移未完成任务
- 🌸 **动漫可爱风** — 粉紫配色、自定义弹窗、可视化选择器
- 🖱️ **悬浮图标** — 右侧悬浮，点击展开，可拖动，位置记忆

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Windows 操作系统（支持 tkinter）

### 安装步骤

1. **克隆或下载项目**
   ```bash
   git clone <repository-url>
   cd work_tracker
   ```

2. **确认 Python 环境**
   ```bash
   python --version
   python -c "import tkinter; print('tkinter OK')"
   ```

### 启动助手

```bash
# 方式1：双击 run.bat（Windows）
# 方式2：命令行启动
pythonw smart_assistant.py
```

### 停止助手

```bash
# 方式1：双击 stop.bat（Windows）
# 方式2：任务管理器结束 pythonw.exe 进程
```

### 命令行工具

```bash
# 添加任务
w.bat add "工作内容"

# 快速添加（智能识别分类）
w.bat quick "开会讨论需求"

# 完成任务
w.bat done 3

# 查看列表
w.bat list

# 生成日报
w.bat report
```

---

## 📁 项目结构

```
work_tracker/
├── smart_assistant.py      # 🌸 主程序（桌面助手 GUI）
├── work_tracker.py         # 命令行工作追踪工具
├── terminal_assistant.py   # 终端版助手（无 GUI）
├── img/
│   └── icon.png            # 悬浮图标
├── run.bat                 # 启动助手（后台运行）
├── stop.bat                # 停止助手
├── w.bat                   # 命令行快捷方式
├── .work_data/             # 数据存储目录
│   ├── settings.json       # 全局配置
│   └── yyyy-MM-dd/         # 每日数据目录
│       └── tasks.json      # 当日任务数据
└── workLog/                # 日报输出目录
```

---

## 🎮 使用说明

### 任务操作

| 操作 | 说明 |
|------|------|
| 点击圆形勾选框 | 进行中 → 已完成 / 即将做 → 开始任务 |
| 点击 ⏰ 闹钟 | 打开时间选择器，重新设置提醒 |
| 点击 ✕ 删除 | 移入回收站 |
| 回收站点击 ↩️ | 恢复到原分类 |

### 日期切换

- 点击标题栏 **◀ ▶** 箭头：前后翻一天
- 点击 **紫色日期按钮**：打开日历选择器，可跳任意日期
- 日历选择器支持快捷按钮 + 月历翻页

### 定时提醒

- 添加"即将做"任务时自动弹出时间选择器
- 支持：日期按钮选择 + 时分滚轮 + 快捷按钮（1小时后/2小时后/明天9点等）
- 到点弹窗提醒，可选择"开始"或"延迟1小时"

### 自动日报

- 每天 18:00（可配置）自动生成昨日日报
- 日报保存在 `workLog/` 目录

---

## ⚙️ 设置

点击标题栏 ⚙️ 按钮打开设置：

- 🚀 开机自启动
- ⏰ 日报生成时间
- 📂 日报保存目录

---

## 🔧 故障排查

### GUI 无法显示？

如果你通过远程桌面或 SSH 连接，GUI 窗口可能无法显示。建议使用终端版：

```bash
python terminal_assistant.py add upcoming "任务内容"
python terminal_assistant.py list
python terminal_assistant.py summary
```

### Python tkinter 问题？

```bash
# 检查 tkinter 是否可用
python -c "import tkinter; print('OK')"

# 如果报错，请重新安装 Python 并确保勾选 tcl/tk 选项
```

详见 [启动问题解决.md](启动问题解决.md)

---

## 📝 数据备份

所有数据存储在 `.work_data/` 目录下，备份此目录即可保留所有任务和配置。

---

**祝你工作效率大幅提升！** 🚀🌸
