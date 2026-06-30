#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Toddy 安装打包工具
==================
生成可分发的安装包

使用方法：
1. 双击运行此脚本
2. 使用上下键选择模式，回车确认
3. 自动生成 target 文件夹并压缩为 zip（ZIP 放在 target 目录下）
"""

import os
import sys
import shutil
import zipfile
import json
from pathlib import Path


def print_log(message):
    """打印日志"""
    print(f"[LOG] {message}")


def clear_target(target_dir: Path):
    """删除旧的 target 目录"""
    if target_dir.exists():
        print_log(f"删除旧的 target 目录: {target_dir}")
        shutil.rmtree(target_dir)
    else:
        print_log("target 目录不存在，无需清理")


def merge_settings(user_settings_path: Path, default_settings_path: Path, output_path: Path):
    """
    智能合并 settings.json
    - 保留用户的所有配置
    - 添加默认配置中新增的字段
    - 不覆盖用户已有的配置值
    """
    # 读取用户配置
    user_settings = {}
    if user_settings_path.exists():
        try:
            with open(user_settings_path, 'r', encoding='utf-8') as f:
                user_settings = json.load(f)
            print_log(f"   读取用户配置: {len(user_settings)} 个字段")
        except Exception as e:
            print_log(f"   警告: 读取用户配置失败 ({e})，使用空配置")
    
    # 读取默认配置
    default_settings = {}
    if default_settings_path.exists():
        try:
            with open(default_settings_path, 'r', encoding='utf-8') as f:
                default_settings = json.load(f)
            print_log(f"   读取默认配置: {len(default_settings)} 个字段")
        except Exception as e:
            print_log(f"   警告: 读取默认配置失败 ({e})，使用空配置")
    
    # 合并：以用户配置为基础，添加默认配置中缺失的字段
    merged_settings = {**default_settings, **user_settings}
    
    # 写入合并后的配置
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged_settings, f, ensure_ascii=False, indent=2)
    
    print_log(f"   合并完成: {len(merged_settings)} 个字段 (用户:{len(user_settings)}, 新增:{len(default_settings) - len(set(default_settings.keys()) & set(user_settings.keys()))})")
    
    return merged_settings


def create_target_structure(target_dir: Path, include_data: bool):
    """创建 target 目录结构"""
    print_log(f"创建 target 目录: {target_dir}")
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # 复制核心文件
    core_files = [
        "smart_assistant.py",
        "run.bat",
        "stop.bat",
        "README.md",
        "INSTALL_GUIDE.md",
    ]
    
    for filename in core_files:
        src = Path(__file__).parent / filename
        dst = target_dir / filename
        if src.exists():
            shutil.copy2(src, dst)
            print_log(f"   复制: {filename}")
        else:
            print_log(f"   跳过不存在的文件: {filename}")
    
    # 复制 img 文件夹
    img_src = Path(__file__).parent / "img"
    img_dst = target_dir / "img"
    if img_src.exists():
        if img_dst.exists():
            shutil.rmtree(img_dst)
        shutil.copytree(img_src, img_dst)
        print_log(f"   复制: img/")
    
    # 根据模式处理数据目录
    if include_data:
        print_log("迁移模式：包含用户数据")
        
        # 复制 .work_data
        work_data_src = Path(__file__).parent / ".work_data"
        work_data_dst = target_dir / ".work_data"
        if work_data_src.exists():
            if work_data_dst.exists():
                shutil.rmtree(work_data_dst)
            shutil.copytree(work_data_src, work_data_dst)
            print_log(f"   复制: .work_data/ (包含任务数据)")
            
            # 智能合并 settings.json
            user_settings = work_data_dst / "settings.json"
            default_settings = Path(__file__).parent / ".work_data" / "settings.json"
            if user_settings.exists() and default_settings.exists():
                print_log("   智能合并 settings.json...")
                merge_settings(user_settings, default_settings, user_settings)
        else:
            print_log(f"   .work_data 不存在，创建空目录")
            work_data_dst.mkdir(parents=True, exist_ok=True)
            # 创建默认 settings.json
            settings_file = work_data_dst / "settings.json"
            if not settings_file.exists():
                with open(settings_file, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)
        
        # 复制 workLog
        worklog_src = Path(__file__).parent / "workLog"
        worklog_dst = target_dir / "workLog"
        if worklog_src.exists():
            if worklog_dst.exists():
                shutil.rmtree(worklog_dst)
            shutil.copytree(worklog_src, worklog_dst)
            print_log(f"   复制: workLog/ (包含历史报告)")
        else:
            print_log(f"   workLog 不存在，创建空目录")
            worklog_dst.mkdir(parents=True, exist_ok=True)
    else:
        print_log("新包模式：不包含用户数据")
        
        # 创建空的 .work_data
        work_data_dst = target_dir / ".work_data"
        work_data_dst.mkdir(parents=True, exist_ok=True)
        # 创建默认 settings.json
        settings_file = work_data_dst / "settings.json"
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
        print_log(f"   创建: .work_data/ (空目录 + 默认配置)")
        
        # 创建空的 workLog
        worklog_dst = target_dir / "workLog"
        worklog_dst.mkdir(parents=True, exist_ok=True)
        print_log(f"   创建: workLog/ (空目录)")


def create_zip_archive(target_dir: Path):
    """将 target 目录压缩为 zip 文件（放在 target 目录下）"""
    print_log(f"开始压缩...")
    
    # 生成 zip 文件名（带时间戳）
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"Toddy_{timestamp}.zip"
    zip_path = target_dir / zip_filename
    
    # 创建 zip 文件
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(target_dir):
            for file in files:
                file_path = Path(root) / file
                # 跳过 zip 文件本身
                if file.endswith('.zip'):
                    continue
                arcname = file_path.relative_to(target_dir.parent)
                zipf.write(file_path, arcname)
                print_log(f"   添加: {arcname}")
    
    print_log(f"压缩完成: {zip_path}")
    return zip_path


def interactive_menu():
    """交互式菜单选择（支持上下键）"""
    options = [
        "[1] 新包模式（不包含用户数据）",
        "[2] 迁移模式（包含用户数据）"
    ]
    
    selected = 0  # 默认选中第一个
    
    # Windows 需要 msvcrt
    import msvcrt
    
    def clear_screen():
        os.system('cls')
    
    def render_menu():
        clear_screen()
        print("\n" + "=" * 60)
        print("Toddy 安装打包工具")
        print("=" * 60)
        print("\n请使用 上/下箭头键 选择，回车确认:\n")
        
        for i, option in enumerate(options):
            if i == selected:
                print(f"  >> {option}")
            else:
                print(f"     {option}")
        
        print("\n" + "=" * 60)
    
    def get_key():
        """获取按键（Windows）"""
        key = msvcrt.getch()
        
        # 如果是扩展键（箭头键等），需要再读一个字节
        if key == b'\xe0' or key == b'\x00':
            key2 = msvcrt.getch()
            return key + key2
        
        return key
    
    render_menu()
    
    while True:
        key = get_key()
        
        # 上箭头: \xe0H
        if key == b'\xe0H':
            selected = (selected - 1) % len(options)
            render_menu()
        # 下箭头: \xe0P
        elif key == b'\xe0P':
            selected = (selected + 1) % len(options)
            render_menu()
        # 回车: \r
        elif key == b'\r':
            return selected == 1  # True = 迁移模式, False = 新包模式


def main():
    """主函数"""
    # 获取项目根目录
    project_root = Path(__file__).parent
    target_dir = project_root / "target"
    
    print("\n" + "=" * 60)
    print("开始打包流程")
    print("=" * 60)
    
    try:
        # 步骤1: 选择模式
        include_data = interactive_menu()
        mode_name = "迁移模式（包含数据）" if include_data else "新包模式（不包含数据）"
        print_log(f"选择模式: {mode_name}")
        
        # 步骤2: 清理旧 target
        print_log("\n步骤 1/4: 清理旧文件")
        clear_target(target_dir)
        
        # 步骤3: 生成新 target
        print_log("\n步骤 2/4: 生成安装包")
        create_target_structure(target_dir, include_data)
        
        # 步骤4: 压缩为 zip（放在 target 目录下）
        print_log("\n步骤 3/4: 压缩为 ZIP")
        zip_path = create_zip_archive(target_dir)
        
        # 完成
        print_log("\n步骤 4/4: 完成")
        print("\n" + "=" * 60)
        print("打包完成！")
        print("=" * 60)
        print(f"\n压缩包位置: {zip_path}")
        print(f"解压后目录: {target_dir}")
        print("\n提示:")
        print("   - 新包模式：适合首次安装的用户")
        print("   - 迁移模式：适合已有数据的用户升级")
        print("   - settings.json 已智能合并，保留用户配置")
        print("   - 请勿直接覆盖安装目录，请使用压缩包内的文件")
        print("\n" + "=" * 60)
        
        # 暂停等待用户按键
        try:
            input("\n按任意键关闭此窗口...")
        except (EOFError, KeyboardInterrupt):
            pass
        
    except Exception as e:
        print_log(f"\n打包失败: {e}")
        import traceback
        traceback.print_exc()
        print("\n按任意键关闭此窗口...")
        try:
            input()
        except:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()
