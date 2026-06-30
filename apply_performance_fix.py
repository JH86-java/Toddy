#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Toddy 性能优化补丁 - 修复线程安全问题
========================================
应用此补丁可以解决后台线程直接操作Tkinter UI导致的卡顿问题
"""

import json
from pathlib import Path

def apply_fix():
    """应用性能修复"""
    
    file_path = Path(__file__).parent / "smart_assistant.py"
    
    if not file_path.exists():
        print("❌ 找不到 smart_assistant.py")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 备份原文件
    backup_path = file_path.with_suffix('.py.bak')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ 已备份到 {backup_path}")
    
    # 修复1: 添加队列支持
    old_init = """        # 跟踪即将显示弹窗的任务ID，防止重复弹窗
        self.pending_reminder_tasks = set()
        # 跟踪已预告过的任务ID（15分钟预告），防止重复
        self.pre_reminded_tasks = set()"""
    
    new_init = """        # 跟踪即将显示弹窗的任务ID，防止重复弹窗
        self.pending_reminder_tasks = set()
        # 跟踪已预告过的任务ID（15分钟预告），防止重复
        self.pre_reminded_tasks = set()
        
        # 性能优化：使用队列机制避免跨线程操作UI
        import queue
        self.reminder_queue = queue.Queue()"""
    
    if old_init in content:
        content = content.replace(old_init, new_init)
        print("✅ 修复1: 添加提醒队列")
    else:
        print("⚠️  修复1: 未找到目标代码，可能已修改")
    
    # 修复2: 修改 scheduled_check 方法，不直接弹窗
    old_scheduled = """    def scheduled_check(self):
        while not self._stop_event.is_set():
            if self._stop_event.wait(timeout=30):
                break
            now = datetime.now()
            current_time_str = now.strftime("%H:%M")
            self._check_reminders(now)
            if current_time_str == self.settings.get("reminder_time", "18:00"):
                if not hasattr(self, '_last_report_gen') or self._last_report_gen != now.date():
                    self.generate_daily_report()
                    self._last_report_gen = now.date()
            if current_time_str == "00:00":
                if not hasattr(self, '_last_migration_date') or self._last_migration_date != now.date():
                    self.migrate_tasks_to_new_day()
                    self._last_migration_date = now.date()"""
    
    new_scheduled = """    def scheduled_check(self):
        while not self._stop_event.is_set():
            if self._stop_event.wait(timeout=30):
                break
            now = datetime.now()
            current_time_str = now.strftime("%H:%M")
            
            # 性能优化：收集需要提醒的任务，不直接在后台线程弹窗
            reminders_to_show = []
            pre_reminders_to_show = []
            
            upcoming = self.tasks.get("upcoming", [])
            for task in upcoming[:]:
                remind_at_str = task.get("remind_at")
                if not remind_at_str:
                    continue
                try:
                    remind_time = datetime.fromisoformat(remind_at_str)
                except:
                    continue
                
                task_id = task.get("id")
                
                # 1. 到期提醒：时间到了，加入队列
                if now >= remind_time:
                    if task_id not in self.pending_reminder_tasks:
                        reminders_to_show.append(task)
                # 2. 15分钟预告：还有15分钟，加入队列
                elif now >= remind_time - timedelta(minutes=15):
                    if task_id not in self.pre_reminded_tasks:
                        pre_reminders_to_show.append((task, remind_time))
            
            # 在主线程中显示弹窗（通过队列）
            if reminders_to_show or pre_reminders_to_show:
                self.root.after(0, lambda r=reminders_to_show, p=pre_reminders_to_show: 
                               self._process_reminder_queue(r, p))
            
            if current_time_str == self.settings.get("reminder_time", "18:00"):
                if not hasattr(self, '_last_report_gen') or self._last_report_gen != now.date():
                    self.generate_daily_report()
                    self._last_report_gen = now.date()
            if current_time_str == "00:00":
                if not hasattr(self, '_last_migration_date') or self._last_migration_date != now.date():
                    self.migrate_tasks_to_new_day()
                    self._last_migration_date = now.date()"""
    
    if old_scheduled in content:
        content = content.replace(old_scheduled, new_scheduled)
        print("✅ 修复2: 优化定时检查逻辑")
    else:
        print("⚠️  修复2: 未找到目标代码，可能已修改")
    
    # 修复3: 添加 _process_reminder_queue 方法
    # 在 __init__ 方法末尾添加启动队列处理
    old_thread_start = """        # 启动后台线程
        self._stop_event = threading.Event()
        threading.Thread(target=self.scheduled_check, daemon=True).start()
        self.update_display()"""
    
    new_thread_start = """        # 启动后台线程
        self._stop_event = threading.Event()
        threading.Thread(target=self.scheduled_check, daemon=True).start()
        
        # 性能优化：启动主线程队列处理器
        self.root.after(100, self._process_reminder_queue_loop)
        
        self.update_display()"""
    
    if old_thread_start in content:
        content = content.replace(old_thread_start, new_thread_start)
        print("✅ 修复3a: 添加队列处理器启动")
    else:
        print("⚠️  修复3a: 未找到目标代码，可能已修改")
    
    # 在类中添加新方法
    new_methods = '''
    def _process_reminder_queue_loop(self):
        """在主线程中循环处理提醒队列"""
        self._process_reminder_queue([], [])
        # 每100ms检查一次队列
        self.root.after(100, self._process_reminder_queue_loop)
    
    def _process_reminder_queue(self, reminders=None, pre_reminders=None):
        """处理提醒队列中的任务（在主线程中调用）"""
        # 处理后台线程放入队列的提醒
        try:
            import queue
            while not self.reminder_queue.empty():
                item = self.reminder_queue.get_nowait()
                if item[0] == "reminder":
                    if reminders is None:
                        reminders = []
                    reminders.append(item[1])
                elif item[0] == "pre_reminder":
                    if pre_reminders is None:
                        pre_reminders = []
                    pre_reminders.append((item[1], item[2]))
        except (queue.Empty, Exception):
            pass
        
        # 显示提醒弹窗
        if reminders:
            for task in reminders:
                self._show_start_dialog_from_reminder(task)
        
        if pre_reminders:
            for task, remind_time in pre_reminders:
                task_id = task.get("id")
                self.pre_reminded_tasks.add(task_id)
                self._show_pre_reminder(task, remind_time)
'''
    
    # 在 _check_reminders 方法之前插入新方法
    check_reminders_pos = content.find("    def _check_reminders(self, now):")
    if check_reminders_pos != -1:
        content = content[:check_reminders_pos] + new_methods + "\n" + content[check_reminders_pos:]
        print("✅ 修复3b: 添加队列处理方法")
    else:
        print("⚠️  修复3b: 未找到插入位置")
    
    # 修复4: 优化 _check_reminders，不再直接弹窗
    old_check = """    def _check_reminders(self, now):
        upcoming = self.tasks.get("upcoming", [])
        for task in upcoming[:]:
            remind_at_str = task.get("remind_at")
            if not remind_at_str:
                continue
            try:
                remind_time = datetime.fromisoformat(remind_at_str)
            except:
                continue
            
            task_id = task.get("id")
            
            # 1. 到期提醒：时间到了，弹窗问是否开始
            if now >= remind_time:
                if task_id in self.pending_reminder_tasks:
                    continue
                self._show_start_dialog_from_reminder(task)
            # 2. 15分钟预告：还有15分钟，温柔提醒
            elif now >= remind_time - timedelta(minutes=15):
                if task_id in self.pre_reminded_tasks:
                    continue
                self.pre_reminded_tasks.add(task_id)
                self._show_pre_reminder(task, remind_time)"""
    
    new_check = '''    def _check_reminders(self, now):
        """性能优化：不再直接弹窗，而是将任务加入队列"""
        upcoming = self.tasks.get("upcoming", [])
        for task in upcoming[:]:
            remind_at_str = task.get("remind_at")
            if not remind_at_str:
                continue
            try:
                remind_time = datetime.fromisoformat(remind_at_str)
            except:
                continue
            
            task_id = task.get("id")
            
            # 1. 到期提醒：时间到了，加入队列
            if now >= remind_time:
                if task_id not in self.pending_reminder_tasks:
                    self.reminder_queue.put(("reminder", task))
            # 2. 15分钟预告：还有15分钟，加入队列
            elif now >= remind_time - timedelta(minutes=15):
                if task_id not in self.pre_reminded_tasks:
                    self.reminder_queue.put(("pre_reminder", task, remind_time))'''
    
    if old_check in content:
        content = content.replace(old_check, new_check)
        print("✅ 修复4: 优化提醒检查逻辑")
    else:
        print("⚠️  修复4: 未找到目标代码，可能已修改")
    
    # 保存修改后的文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n" + "="*60)
    print("🎉 性能优化补丁应用完成！")
    print("="*60)
    print("\n主要改进:")
    print("1. ✅ 后台线程不再直接操作Tkinter UI")
    print("2. ✅ 使用队列机制在主线程中处理提醒")
    print("3. ✅ 避免了跨线程操作导致的卡顿和崩溃")
    print("\n请重启程序以应用更改。")
    print("如果出现问题，可以从备份恢复: smart_assistant.py.bak")
    
    return True

if __name__ == "__main__":
    apply_fix()
