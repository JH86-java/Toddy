# 安装包生成器使用说明

## 📦 install.py - 安装包生成器

### 功能说明

`install.py` 是一个用于生成干净安装包的脚本，它会：

1. **删除旧的 target 文件夹**（如果存在）
2. **创建新的 target 文件夹**
3. **复制核心文件**（不包含个人数据、备份、临时文件）
4. **生成默认配置**（空的 `.work_data` 目录和默认 `settings.json`）
5. **创建安装说明文档**

### 使用方法

```bash
cd D:\AISkill\Toddy
python install.py
```

运行后会在 `D:\AISkill\Toddy\target` 目录下生成完整的安装包。

---

## 📁 生成的安装包结构

```
target/
├── smart_assistant.py    # 主程序（最新版本）
├── run.bat               # 启动脚本
├── stop.bat              # 停止脚本
├── README.md             # 项目说明
├── INSTALL_GUIDE.md      # 安装指南
├── img/                  # 图标和图片
│   └── icon.png          # 桌面图标
├── .work_data/           # 数据目录（空）
│   └── settings.json     # 默认配置
└── workLog/              # 日报保存目录（空）
```

---

## 🎯 使用场景

### 场景1: 首次分发给新用户

1. 运行 `python install.py` 生成安装包
2. 将 `target` 文件夹打包成 ZIP
3. 分发给用户
4. 用户解压后双击 `run.bat` 即可运行

### 场景2: 更新已有用户的版本

**方法A: 完整替换（推荐）**
1. 用户备份 `.work_data` 文件夹
2. 用新的 `target` 文件夹替换整个旧文件夹
3. 将备份的 `.work_data` 复制回去
4. 重新启动程序

**方法B: 增量更新**
1. 从 `target` 文件夹中复制以下文件到用户的安装目录：
   - `smart_assistant.py`
   - `run.bat`
   - `stop.bat`
   - `img/` 文件夹
2. 保留用户的 `.work_data` 文件夹不变
3. 重新启动程序

---

## ⚙️ 配置说明

### 修改打包的文件列表

编辑 `install.py` 中的以下配置：

```python
# 核心文件列表
CORE_FILES = [
    "smart_assistant.py",
    "run.bat",
    "stop.bat",
    "README.md",
]

# 核心文件夹
CORE_FOLDERS = [
    "img",
]
```

### 修改排除的文件模式

```python
EXCLUDE_PATTERNS = [
    ".git",
    ".work_data",
    "__pycache__",
    "*.pyc",
    "*.bak",
    # ... 更多模式
]
```

---

## 🔧 高级用法

### 自定义目标目录

修改 `install.py` 中的 `TARGET_DIR`：

```python
TARGET_DIR = Path(r"D:\Your\Custom\Path\target")
```

### 添加更多文件到安装包

在 `CORE_FILES` 或 `CORE_FOLDERS` 中添加：

```python
CORE_FILES = [
    "smart_assistant.py",
    "your_new_script.py",  # 添加新文件
    "run.bat",
]
```

---

## 📊 与 deploy_packager.py 的区别

| 特性 | install.py | deploy_packager.py |
|------|-----------|-------------------|
| 用途 | 生成安装包供分发 | 部署到本地工作目录 |
| 目标位置 | `target/` 文件夹 | `D:\Hermes\deskTop\WorkSpeace\work_tracker` |
| 数据处理 | 创建空的数据目录 | 保留并重置现有数据 |
| 适用场景 | 分发给新用户 | 本地开发测试 |

---

## 💡 最佳实践

1. **每次发布新版本前**，运行 `install.py` 生成干净的包
2. **测试安装包**：在另一台电脑上测试是否能正常运行
3. **版本管理**：在 `INSTALL_GUIDE.md` 中记录版本号
4. **备份建议**：提醒用户更新前备份 `.work_data`

---

## 🐛 常见问题

**Q: 为什么 target 文件夹被忽略了？**
A: `target/` 已添加到 `.gitignore`，因为它是生成的产物，不需要提交到 Git。

**Q: 如何查看生成的安装包内容？**
A: 直接打开 `D:\AISkill\Toddy\target` 文件夹即可查看。

**Q: 安装包太大怎么办？**
A: 检查 `CORE_FILES` 和 `CORE_FOLDERS`，移除不必要的文件。

**Q: 能否自动压缩成 ZIP？**
A: 可以，在 `install.py` 末尾添加压缩逻辑即可。

---

## 📝 更新日志

- **v1.0 (2026-06-30)**: 初始版本
  - 支持生成干净的安装包
  - 自动处理文件复制和配置生成
  - 创建详细的安装说明

---

**最后更新**: 2026-06-30
