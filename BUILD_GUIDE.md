# Toddy 打包指南

## 📦 使用 Nuitka 打包为单文件 exe

### 前置条件

确保已安装以下依赖：

```bash
pip install nuitka ordered-set zstandard pyperclip
```

### 打包步骤

#### 方法一：使用打包脚本（推荐）

双击运行 `build_exe.bat`，会自动完成所有步骤。

#### 方法二：手动执行命令

```bash
python -m nuitka \
    --standalone \
    --onefile \
    --windows-console-mode=disable \
    --enable-plugin=tk-inter \
    --include-package=pyperclip \
    --output-dir=dist \
    --output-filename=Toddy.exe \
    --assume-yes-for-downloads \
    smart_assistant.py
```

### 首次编译说明

首次编译时，Nuitka 会自动下载：
1. **Dependency Walker** - 用于分析依赖
2. **MinGW64 GCC 编译器** - 用于编译 C 代码

下载和安装可能需要几分钟，请耐心等待。

### 输出结果

打包成功后，会在 `dist/` 目录下生成：

```
dist/
└── Toddy.exe    # 单文件可执行程序（约 6-7 MB）
```

### 分发方式

#### 方案 A：仅分发 exe 文件

用户只需获得 `Toddy.exe`，双击即可运行。

**优点：**
- ✅ 最简单，只有一个文件
- ✅ 可以放在任意位置

**缺点：**
- ❌ 首次启动需要几秒解压
- ❌ 无法自定义图标等资源

#### 方案 B：分发完整目录结构

创建如下目录结构并压缩为 zip：

```
Toddy_v1.0/
├── Toddy.exe          # 主程序
├── img/               # 图标等资源（可选）
│   └── icon.png
├── .work_data/        # 用户数据目录（空）
│   └── settings.json
└── workLog/           # 日志目录（空）
```

**优点：**
- ✅ 用户可以预置资源文件
- ✅ 目录结构清晰

**缺点：**
- ❌ 多个文件，稍复杂

### 用户升级流程

#### 新包模式（首次安装）

1. 用户获得 `Toddy.exe`
2. 双击运行
3. 程序自动在同目录创建 `.work_data/` 和 `workLog/`

#### 迁移模式（升级）

1. 备份用户的 `.work_data/` 目录
2. 替换新的 `Toddy.exe`
3. 将备份的 `.work_data/` 复制回去
4. 重新启动程序

### 注意事项

1. **文件大小**：生成的 exe 约 6-7 MB（包含 Python 运行时和 Tkinter）
2. **首次启动**：单文件模式首次启动需要解压，可能较慢（2-5秒）
3. **杀毒软件**：某些杀毒软件可能误报，需要将 exe 加入白名单
4. **系统要求**：Windows 7 及以上版本

### 常见问题

#### Q: 编译失败怎么办？

A: 检查是否有足够的磁盘空间（至少 2GB），并确保网络连接正常（需要下载编译器）。

#### Q: 如何减小 exe 体积？

A: 可以尝试：
- 移除不必要的依赖
- 使用 `--remove-output` 清理临时文件
- 考虑使用 UPX 压缩（但可能影响启动速度）

#### Q: 能否在其他电脑上运行？

A: 可以！Nuitka 打包的 exe 包含了完整的 Python 运行时，无需安装 Python 即可运行。

### 性能对比

| 方式 | 启动速度 | 文件大小 | 需要 Python |
|------|---------|---------|------------|
| Python 源码 | 快 | 小 | ✅ 需要 |
| PyInstaller | 中等 | 大 (50-100MB) | ❌ 不需要 |
| **Nuitka** | **快** | **小 (6-7MB)** | **❌ 不需要** |

Nuitka 在性能和体积上都有优势，是最佳选择！🎉
