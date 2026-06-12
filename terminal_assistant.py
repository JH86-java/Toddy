#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
终端版工作助手（无需GUI）
=========================
适合在终端中使用，功能与GUI版相同
"""

import json
import sys
from datetime import datetime, date, timedelta
from pathlib import Path


class TerminalAssistant:
    def __init__(self):
        self.data_dir = Path(__file__).parent / ".work_data"
        self.data_dir.mkdir(exist_ok=True)
        self.tasks_file = self.data_dir / "smart_tasks.json"
        self.tasks = self._load_tasks()
    
    def _load_tasks(self):
        if self.tasks_file.exists():
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "completed": [],
            "in_progress": [],
            "upcoming": [],
            "important": [],
            "history": []
        }
    
    def _save_tasks(self):
        with open(self.tasks_file, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)
    
    def add_task(self, category, text):
        """添加任务"""
        task = {
            "id": len(self.tasks.get(category, [])) + 1,
            "text": text,
            "timestamp": datetime.now().isoformat(),
            "date": date.today().isoformat(),
            "completed": False
        }
        
        if category not in self.tasks:
            self.tasks[category] = []
        
        self.tasks[category].append(task)
        
        if category == "completed":
            self.tasks["history"].append(task)
        
        self._save_tasks()
        print(f"✅ 已添加到 [{category}]: {text}")
    
    def list_tasks(self, category=None):
        """列出任务"""
        if category:
            tasks = self.tasks.get(category, [])
            print(f"\n📋 {category} ({len(tasks)}项):")
            for i, task in enumerate(tasks, 1):
                print(f"  {i}. [{task['date']}] {task['text']}")
        else:
            for cat in ["completed", "in_progress", "upcoming", "important"]:
                tasks = self.tasks.get(cat, [])
                if tasks:
                    print(f"\n📋 {cat} ({len(tasks)}项):")
                    for task in tasks:
                        print(f"  • [{task['date']}] {task['text']}")
    
    def delete_task(self, category, index):
        """删除任务"""
        if category in self.tasks and 0 <= index < len(self.tasks[category]):
            removed = self.tasks[category].pop(index)
            self._save_tasks()
            print(f"✅ 已删除: {removed['text']}")
        else:
            print("❌ 无效的任务编号")
    
    def generate_summary(self):
        """生成总结"""
        today = date.today().isoformat()
        
        print(f"\n{'='*60}")
        print(f"📊 今日工作总结 ({today})")
        print(f"{'='*60}\n")
        
        # 已完成
        completed = [t for t in self.tasks["completed"] if t["date"] == today]
        print(f"✅ 已完成 ({len(completed)}项):")
        for task in completed:
            print(f"  • {task['text']}")
        
        # 进行中
        in_progress = [t for t in self.tasks["in_progress"] if t["date"] == today]
        print(f"\n🔄 进行中 ({len(in_progress)}项):")
        for task in in_progress:
            print(f"  • {task['text']}")
        
        # 即将做
        upcoming = [t for t in self.tasks["upcoming"] if t["date"] == today]
        print(f"\n📅 即将做 ({len(upcoming)}项):")
        for task in upcoming:
            print(f"  • {task['text']}")
        
        # 重要事项
        important = self.tasks["important"]
        print(f"\n⭐ 重要事项 ({len(important)}项):")
        for task in important:
            print(f"  • {task['text']}")
        
        print(f"\n{'='*60}")
    
    def morning_reminder(self):
        """早上提醒"""
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        today = date.today().isoformat()
        next_3_days = [(date.today() + timedelta(days=i)).isoformat() for i in range(1, 4)]
        
        print(f"\n{'='*60}")
        print(f"⏰ 早安提醒 ({today})")
        print(f"{'='*60}\n")
        
        # 昨天完成的工作
        yesterday_completed = [t for t in self.tasks["completed"] if t["date"] == yesterday]
        print(f"📅 昨天完成 ({len(yesterday_completed)}项):")
        for task in yesterday_completed:
            print(f"  ✓ {task['text']}")
        
        # 今天要做的事
        today_upcoming = [t for t in self.tasks["upcoming"] if t["date"] == today]
        print(f"\n📌 今天待办 ({len(today_upcoming)}项):")
        for task in today_upcoming:
            print(f"  • {task['text']}")
        
        # 未来3天的事
        print(f"\n🔮 未来3天:")
        for day in next_3_days:
            day_tasks = [t for t in self.tasks["upcoming"] if t["date"] == day]
            if day_tasks:
                print(f"  {day}: {len(day_tasks)}项任务")
        
        # 重要事项
        important = self.tasks["important"]
        if important:
            print(f"\n⭐ 重要事项 ({len(important)}项):")
            for task in important:
                print(f"  ⚠ {task['text']}")
        
        print(f"\n{'='*60}")


def main():
    assistant = TerminalAssistant()
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python terminal_assistant.py add <category> <text>")
        print("  python terminal_assistant.py list [category]")
        print("  python terminal_assistant.py delete <category> <index>")
        print("  python terminal_assistant.py summary")
        print("  python terminal_assistant.py reminder")
        print()
        print("分类: completed, in_progress, upcoming, important")
        return
    
    command = sys.argv[1]
    
    if command == "add":
        if len(sys.argv) < 4:
            print("用法: python terminal_assistant.py add <category> <text>")
            return
        category = sys.argv[2]
        text = " ".join(sys.argv[3:])
        assistant.add_task(category, text)
    
    elif command == "list":
        category = sys.argv[2] if len(sys.argv) > 2 else None
        assistant.list_tasks(category)
    
    elif command == "delete":
        if len(sys.argv) < 4:
            print("用法: python terminal_assistant.py delete <category> <index>")
            return
        category = sys.argv[2]
        index = int(sys.argv[3]) - 1
        assistant.delete_task(category, index)
    
    elif command == "summary":
        assistant.generate_summary()
    
    elif command == "reminder":
        assistant.morning_reminder()
    
    else:
        print(f"未知命令: {command}")


if __name__ == "__main__":
    main()
