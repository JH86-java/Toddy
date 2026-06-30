#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复任务同步问题 - 防止已完成任务重复出现
==============================================
问题：关闭程序几天后再次打开，已完成的任务会重新出现在今天的进行中列表
原因：last_sync_date 未保存，导致每次都重新同步历史任务
"""

from pathlib import Path
import json

def apply_fix():
    """应用修复"""
    
    file_path = Path(__file__).parent / "smart_assistant.py"
    
    if not file_path.exists():
        print("❌ 找不到 smart_assistant.py")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 备份原文件
    backup_path = file_path.with_suffix('.py.sync_fix.bak')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ 已备份到 {backup_path}")
    
    # 修复1: 在 __init__ 中确保 last_sync_date 有默认值
    old_settings_load = """        # 加载当天任务
        self.tasks = self._load_tasks(self.current_view_date)
        
        # 窗口配置（必须在同步之前，因为同步提示需要屏幕尺寸）"""
    
    new_settings_load = """        # 加载当天任务
        self.tasks = self._load_tasks(self.current_view_date)
        
        # 性能修复：确保 last_sync_date 有默认值，避免重复同步
        if "last_sync_date" not in self.settings:
            self.settings["last_sync_date"] = date.today().isoformat()
            self._save_settings()
            print(f"📝 初始化 last_sync_date 为今天: {self.settings['last_sync_date']}\")
        
        # 窗口配置（必须在同步之前，因为同步提示需要屏幕尺寸）"""
    
    if old_settings_load in content:
        content = content.replace(old_settings_load, new_settings_load)
        print("✅ 修复1: 确保 last_sync_date 有默认值")
    else:
        print("⚠️  修复1: 未找到目标代码，可能已修改")
    
    # 修复2: 优化 _sync_missing_dates，只同步真正未完成的任务
    # 关键改进：检查任务的 completed 标志，避免同步已完成的任务
    old_sync_logic = """            # 收集所有历史未完成任务（从 last_sync_date 当天开始）
            all_unfinished = []
            collect_d = last_sync_date
            while collect_d < today:
                day_tasks = self._load_tasks(collect_d.isoformat())
                for task in day_tasks.get(\"in_progress\", []):
                    all_unfinished.append((\"in_progress\", task))
                for task in day_tasks.get(\"upcoming\", []):
                    all_unfinished.append((\"upcoming\", task))
                collect_d = collect_d + timedelta(days=1)"""
    
    new_sync_logic = """            # 收集所有历史未完成任务（从 last_sync_date 当天开始）
            # 修复：跳过已完成的任务，只同步真正未完成的任务
            all_unfinished = []
            collect_d = last_sync_date
            while collect_d < today:
                day_tasks = self._load_tasks(collect_d.isoformat())
                for task in day_tasks.get(\"in_progress\", []):
                    # 跳过已标记为完成的任务
                    if not task.get(\"completed\", False):
                        all_unfinished.append((\"in_progress\", task))
                for task in day_tasks.get(\"upcoming\", []):
                    # 跳过已标记为完成的任务
                    if not task.get(\"completed\", False):
                        all_unfinished.append((\"upcoming\", task))
                collect_d = collect_d + timedelta(days=1)"""
    
    if old_sync_logic in content:
        content = content.replace(old_sync_logic, new_sync_logic)
        print("✅ 修复2: 优化同步逻辑，跳过已完成的任务")
    else:
        print("⚠️  修复2: 未找到目标代码，可能已修改")
    
    # 修复3: 在程序退出时确保保存 last_sync_date
    # 查找 quit_app 方法并添加保存逻辑
    old_quit = """    def quit_app(self):
        self._stop_event.set()
        self._save_tasks()
        self.settings[\"icon_position\"] = [self.root.winfo_x(), self.root.winfo_y()]
        self._save_settings()
        self.root.destroy()"""
    
    new_quit = """    def quit_app(self):
        self._stop_event.set()
        self._save_tasks()
        self.settings[\"icon_position\"] = [self.root.winfo_x(), self.root.winfo_y()]
        # 修复：退出时更新 last_sync_date 为今天，避免下次启动时重复同步
        self.settings[\"last_sync_date\"] = date.today().isoformat()
        self._save_settings()
        self.root.destroy()"""
    
    if old_quit in content:
        content = content.replace(old_quit, new_quit)
        print("✅ 修复3: 退出时保存 last_sync_date")
    else:
        print("⚠️  修复3: 未找到 quit_app 方法，可能已修改")
    
    # 保存修改后的文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n" + "="*60)
    print("🎉 任务同步问题修复完成！")
    print("="*60)
    print("\n主要改进:")
    print("1. ✅ 确保 last_sync_date 始终有值")
    print("2. ✅ 同步时跳过已完成的任务")
    print("3. ✅ 退出时更新 last_sync_date")
    print("\n请重启程序以应用更改。")
    print("如果出现问题，可以从备份恢复: smart_assistant.py.sync_fix.bak")
    
    return True

if __name__ == "__main__":
    apply_fix()
