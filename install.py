#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Toddy 安装包生成器
==================
生成干净的安装包，用于分发或更新

功能：
1. 删除旧的 target 文件夹
2. 创建新的 target 文件夹
3. 复制核心文件（不包含个人数据、备份、临时文件）
4. 用户可以直接运行，或者替换已有安装的文件进行更新
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

# ================= 配置区域 =================

# 开发目录（源代码位置）
DEV_DIR = Path(__file__).parent

# 目标目录（安装包输出位置）
TARGET_DIR = DEV_DIR / "target"

# 核心文件列表（需要打包的文件）
CORE_FILES = [
    "smart_assistant.py",      # 主程序
    "run.bat",                  # 启动脚本
    "stop.bat",                 # 停止脚本
    "README.md",                # 说明文档
]

# 核心文件夹
CORE_FOLDERS = [
    "img",                      # 图标和图片
]

# 需要排除的文件/文件夹模式
EXCLUDE_PATTERNS = [
    ".git",
    ".work_data",
    "__pycache__",
    "*.pyc",
    "*.bak",
    "*.sync_fix.bak",
    "build",
    "dist",
    "*.spec",
    "_*.py",                     # 临时脚本
    "*.md",                      # 文档文件（除了README.md）
    "apply_performance_fix.py",
    "fix_sync_issue.py",
    "monitor_performance.py",
    "deploy_packager.py",
    "updater_stable.py",
    "patch_data.zip",
    "workLog",
]


def should_exclude(path: Path) -> bool:
    """检查文件或文件夹是否应该被排除"""
    name = path.name
    
    # 检查精确匹配
    if name in EXCLUDE_PATTERNS:
        return True
    
    # 检查通配符模式
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith("*"):
            suffix = pattern[1:]  # 去掉 *
            if name.endswith(suffix):
                return True
        elif pattern.endswith("*"):
            prefix = pattern[:-1]  # 去掉 *
            if name.startswith(prefix):
                return True
    
    return False


def clean_directory(path: Path):
    """清空目录内容"""
    print(f"🧹 清空目录: {path}")
    if path.exists():
        for item in path.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
    else:
        path.mkdir(parents=True, exist_ok=True)


def copy_core_files():
    """复制核心文件到 target 目录"""
    print("\n📦 开始打包核心文件...")
    print("=" * 60)
    
    # 确保 target 目录存在且为空
    if TARGET_DIR.exists():
        clean_directory(TARGET_DIR)
    else:
        TARGET_DIR.mkdir(parents=True, exist_ok=True)
    
    copied_count = 0
    
    # 复制核心文件
    for filename in CORE_FILES:
        src = DEV_DIR / filename
        dst = TARGET_DIR / filename
        
        if src.exists():
            shutil.copy2(src, dst)
            print(f"   ✅ {filename}")
            copied_count += 1
        else:
            print(f"   ⚠️  {filename} (不存在，跳过)")
    
    # 复制核心文件夹
    for foldername in CORE_FOLDERS:
        src = DEV_DIR / foldername
        dst = TARGET_DIR / foldername
        
        if src.exists() and src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"   ✅ {foldername}/")
            copied_count += 1
        else:
            print(f"   ⚠️  {foldername}/ (不存在，跳过)")
    
    # 注意：不复制 .work_data 和 workLog，这些是用户数据
    # 只创建空目录结构，供首次安装使用
    print("\n📝 注意：用户数据目录已跳过")
    print("   - .work_data/ (用户任务数据)")
    print("   - workLog/ (用户日报)")
    print("   更新时请保留这些文件夹！")
    
    print("=" * 60)
    print(f"✅ 打包完成！共复制 {copied_count} 个文件/文件夹")
    print(f"📁 安装包位置: {TARGET_DIR}")
    print()


def create_readme():
    """在安装包中创建使用说明"""
    readme_content = """# Toddy - 智能桌面工作助手 🌸

## 📦 安装说明

### 首次安装
1. 将整个 `target` 文件夹复制到你想安装的位置
2. 双击 `run.bat` 启动程序
3. 桌面会出现一个可爱的樱花图标 🌸

### 更新已有安装

**⚠️ 重要：保护你的数据！**

有两种更新方式：

#### 方法A：安全更新（推荐）✅
1. **备份数据**：复制 `.work_data` 文件夹到安全位置
2. 从新的 `target` 文件夹中，**只复制以下文件**到你的安装目录：
   - `smart_assistant.py`
   - `run.bat`
   - `stop.bat`
   - `img/` 文件夹
3. **不要覆盖** `.work_data/` 和 `workLog/` 文件夹
4. 重新启动程序

#### 方法B：完整替换（需谨慎）
1. **备份整个安装目录**（包括 `.work_data`）
2. 删除旧的安装目录
3. 将新的 `target` 文件夹复制到原位置
4. 从备份中恢复 `.work_data` 文件夹
5. 重新启动程序

**❌ 错误做法**：直接用 `target` 文件夹覆盖整个安装目录，这会丢失所有任务数据！

## 🎯 主要功能

- ✅ 任务管理：添加、完成、延迟任务
- 🔔 智能提醒：定时提醒即将开始的任务
- 📊 日报生成：自动生成工作日报
- 📅 周视图：按周查看任务分布
- 🌸 可爱UI：动漫风格的界面设计

## 📂 目录结构

```
target/
├── smart_assistant.py    # 主程序
├── run.bat               # 启动脚本
├── stop.bat              # 停止脚本
├── README.md             # 说明文档
├── img/                  # 图标和图片
│   └── icon.png          # 桌面图标
├── .work_data/           # 数据目录（不要删除！）
│   ├── settings.json     # 配置文件
│   └── YYYY-MM-DD/       # 每日任务数据
└── workLog/              # 日报保存目录
```

## ⚙️ 系统要求

- Windows 10/11
- Python 3.8+ （如果使用 .py 文件）
- 或使用打包后的 .exe 文件（无需 Python）

## 🐛 常见问题

**Q: 程序启动后没有反应？**
A: 检查是否安装了 Python，或者使用打包后的 .exe 文件

**Q: 任务数据丢失了？**
A: 检查 `.work_data` 文件夹是否存在，这是存储任务数据的地方

**Q: 如何备份数据？**
A: 复制整个 `.work_data` 文件夹即可

## 📞 技术支持

如有问题，请查看项目仓库或联系开发者。

---

**版本**: 1.0  
**更新日期**: 2026-06-30
"""
    
    readme_path = TARGET_DIR / "INSTALL_GUIDE.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ 创建安装说明: INSTALL_GUIDE.md")


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 Toddy 安装包生成器")
    print("=" * 60)
    print()
    
    # 检查开发目录
    if not DEV_DIR.exists():
        print(f"❌ 开发目录不存在: {DEV_DIR}")
        return
    
    # 检查关键文件
    required_files = ["smart_assistant.py", "run.bat"]
    missing_files = []
    for file in required_files:
        if not (DEV_DIR / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少必要文件: {', '.join(missing_files)}")
        return
    
    # 执行打包
    try:
        copy_core_files()
        create_readme()
        
        print()
        print("=" * 60)
        print("🎉 安装包生成成功！")
        print("=" * 60)
        print()
        print("📦 安装包位置:")
        print(f"   {TARGET_DIR}")
        print()
        print("💡 使用方法:")
        print("   1. 将 target 文件夹分发给用户")
        print("   2. 用户可以直接运行 run.bat")
        print("   3. 或者用 target 中的文件替换已有安装")
        print()
        print("⚠️  注意事项:")
        print("   - 用户的任务数据在 .work_data 文件夹中")
        print("   - 更新时只需替换代码文件，保留 .work_data")
        print("   - 建议先备份 .work_data 再更新")
        print()
        
    except Exception as e:
        print(f"\n❌ 打包失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
