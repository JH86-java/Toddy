#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Toddy 安全更新工具（GUI版本）
==============================
帮助用户安全地更新 Toddy，保护用户数据

使用方法：
1. 双击运行此脚本
2. 选择已安装的 Toddy 目录
3. 选择新的 target 文件夹
4. 自动备份并更新
"""

import os
import sys
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path


def backup_data(install_dir: Path, backup_dir: Path):
    """备份用户数据"""
    print(f"📦 备份用户数据...")
    
    # 创建备份目录
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # 备份 .work_data
    work_data_src = install_dir / ".work_data"
    if work_data_src.exists():
        work_data_dst = backup_dir / ".work_data"
        if work_data_dst.exists():
            shutil.rmtree(work_data_dst)
        shutil.copytree(work_data_src, work_data_dst)
        print(f"   ✅ 备份 .work_data/")
    
    # 备份 workLog
    worklog_src = install_dir / "workLog"
    if worklog_src.exists():
        worklog_dst = backup_dir / "workLog"
        if worklog_dst.exists():
            shutil.rmtree(worklog_dst)
        shutil.copytree(worklog_src, worklog_dst)
        print(f"   ✅ 备份 workLog/")


def update_files(install_dir: Path, new_target_dir: Path):
    """更新文件（不覆盖用户数据）"""
    print(f"🔄 更新文件...")
    
    # 需要更新的文件列表
    files_to_update = [
        "smart_assistant.py",
        "run.bat",
        "stop.bat",
        "README.md",
    ]
    
    # 需要更新的文件夹
    folders_to_update = [
        "img",
    ]
    
    updated_count = 0
    
    # 更新文件
    for filename in files_to_update:
        src = new_target_dir / filename
        dst = install_dir / filename
        
        if src.exists():
            shutil.copy2(src, dst)
            print(f"   ✅ 更新: {filename}")
            updated_count += 1
    
    # 更新文件夹
    for foldername in folders_to_update:
        src = new_target_dir / foldername
        dst = install_dir / foldername
        
        if src.exists() and src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"   ✅ 更新: {foldername}/")
            updated_count += 1
    
    return updated_count


class SafeUpdateGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🔄 Toddy 安全更新工具")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # 变量
        self.install_dir = tk.StringVar()
        self.target_dir = tk.StringVar()
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建界面组件"""
        # 标题
        title_frame = tk.Frame(self.root, bg="#FFB7C5", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame, text="🔄 Toddy 安全更新工具", 
                font=("Microsoft YaHei", 16, "bold"),
                fg="white", bg="#FFB7C5").pack(pady=15)
        
        # 主内容区域
        main_frame = tk.Frame(self.root, bg="#FFF0F5", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 安装目录选择
        dir_frame1 = tk.Frame(main_frame, bg="#FFF0F5")
        dir_frame1.pack(fill=tk.X, pady=10)
        
        tk.Label(dir_frame1, text="📁 已安装的 Toddy 目录:", 
                font=("Microsoft YaHei", 10), bg="#FFF0F5", anchor="w").pack(anchor="w")
        
        entry_frame1 = tk.Frame(dir_frame1, bg="#FFF0F5")
        entry_frame1.pack(fill=tk.X, pady=5)
        
        tk.Entry(entry_frame1, textvariable=self.install_dir, 
                font=("Consolas", 9), width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        tk.Button(entry_frame1, text="浏览...", command=self.browse_install_dir,
                 bg="#FF69B4", fg="white", font=("Microsoft YaHei", 9),
                 relief=tk.FLAT, cursor="hand2", padx=10, pady=3).pack(side=tk.RIGHT)
        
        # target 目录选择
        dir_frame2 = tk.Frame(main_frame, bg="#FFF0F5")
        dir_frame2.pack(fill=tk.X, pady=10)
        
        tk.Label(dir_frame2, text="📦 新的 target 文件夹:", 
                font=("Microsoft YaHei", 10), bg="#FFF0F5", anchor="w").pack(anchor="w")
        
        entry_frame2 = tk.Frame(dir_frame2, bg="#FFF0F5")
        entry_frame2.pack(fill=tk.X, pady=5)
        
        tk.Entry(entry_frame2, textvariable=self.target_dir, 
                font=("Consolas", 9), width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        tk.Button(entry_frame2, text="浏览...", command=self.browse_target_dir,
                 bg="#FF69B4", fg="white", font=("Microsoft YaHei", 9),
                 relief=tk.FLAT, cursor="hand2", padx=10, pady=3).pack(side=tk.RIGHT)
        
        # 说明文本
        info_text = """💡 使用说明：
1. 选择你当前安装 Toddy 的目录（包含 .work_data 的文件夹）
2. 选择新生成的 target 文件夹（运行 install.py 生成的）
3. 点击"开始更新"按钮

⚠️ 此工具会：
- 自动备份你的任务数据
- 只更新程序文件
- 保留所有个人数据不变"""
        
        tk.Label(main_frame, text=info_text, font=("Microsoft YaHei", 9),
                bg="#FFF0F5", fg="#5D4157", justify="left", anchor="w").pack(anchor="w", pady=15)
        
        # 按钮区域
        btn_frame = tk.Frame(main_frame, bg="#FFF0F5")
        btn_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(btn_frame, text="🚀 开始更新", command=self.start_update,
                 bg="#7ED4AD", fg="white", font=("Microsoft YaHei", 11, "bold"),
                 relief=tk.FLAT, cursor="hand2", padx=30, pady=8).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="❌ 取消", command=self.root.destroy,
                 bg="#FF6B6B", fg="white", font=("Microsoft YaHei", 11),
                 relief=tk.FLAT, cursor="hand2", padx=20, pady=8).pack(side=tk.RIGHT, padx=10)
    
    def browse_install_dir(self):
        """选择安装目录"""
        directory = filedialog.askdirectory(title="选择已安装的 Toddy 目录")
        if directory:
            self.install_dir.set(directory)
    
    def browse_target_dir(self):
        """选择 target 目录"""
        directory = filedialog.askdirectory(title="选择新的 target 文件夹")
        if directory:
            self.target_dir.set(directory)
    
    def start_update(self):
        """开始更新"""
        install_path = self.install_dir.get().strip()
        target_path = self.target_dir.get().strip()
        
        # 验证输入
        if not install_path:
            messagebox.showerror("错误", "请选择已安装的 Toddy 目录！")
            return
        
        if not target_path:
            messagebox.showerror("错误", "请选择新的 target 文件夹！")
            return
        
        install_dir = Path(install_path)
        target_dir = Path(target_path)
        
        # 验证目录存在
        if not install_dir.exists():
            messagebox.showerror("错误", f"安装目录不存在：\n{install_path}")
            return
        
        if not target_dir.exists():
            messagebox.showerror("错误", f"target 目录不存在：\n{target_path}")
            return
        
        # 确认操作
        confirm = messagebox.askyesno(
            "确认更新",
            f"即将执行以下操作：\n\n"
            f"1. 备份 {install_dir.name} 中的用户数据\n"
            f"2. 更新程序文件（不覆盖用户数据）\n\n"
            f"是否继续？"
        )
        
        if not confirm:
            return
        
        try:
            # 执行更新
            self.do_update(install_dir, target_dir)
        except Exception as e:
            messagebox.showerror("更新失败", f"更新过程中出错：\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def do_update(self, install_dir: Path, target_dir: Path):
        """执行更新操作"""
        # 创建进度窗口
        progress_win = tk.Toplevel(self.root)
        progress_win.title("更新中...")
        progress_win.geometry("400x200")
        progress_win.transient(self.root)
        progress_win.grab_set()
        
        # 居中显示
        progress_win.update_idletasks()
        x = (progress_win.winfo_screenwidth() - 400) // 2
        y = (progress_win.winfo_screenheight() - 200) // 2
        progress_win.geometry(f"+{x}+{y}")
        
        tk.Label(progress_win, text="🔄 正在更新...", 
                font=("Microsoft YaHei", 14, "bold")).pack(pady=20)
        
        status_label = tk.Label(progress_win, text="准备中...", 
                               font=("Microsoft YaHei", 10))
        status_label.pack(pady=10)
        
        progress_win.update()
        
        try:
            # 步骤1: 备份
            status_label.config(text="正在备份用户数据...")
            progress_win.update()
            
            backup_dir = install_dir.parent / f"{install_dir.name}_backup"
            backup_data(install_dir, backup_dir)
            
            # 步骤2: 更新
            status_label.config(text="正在更新程序文件...")
            progress_win.update()
            
            updated_count = update_files(install_dir, target_dir)
            
            # 完成
            progress_win.destroy()
            
            messagebox.showinfo(
                "更新成功",
                f"✅ 更新完成！\n\n"
                f"共更新 {updated_count} 个文件/文件夹\n"
                f"数据备份位置：\n{backup_dir}\n\n"
                f"💡 提示：\n"
                f"- 如果更新后有问题，可以从备份恢复\n"
                f"- 现在可以重新启动程序了"
            )
            
            self.root.destroy()
            
        except Exception as e:
            progress_win.destroy()
            raise e


def main():
    """主函数"""
    root = tk.Tk()
    app = SafeUpdateGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
