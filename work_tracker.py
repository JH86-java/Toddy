#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作追踪与日报生成系统
========================
功能：
1. 实时记录工作内容（避免忘记）
2. 自动生成日报草稿（减少写日报的痛苦）

使用方法：
    python work_tracker.py add "完成了XX功能开发"
    python work_tracker.py add "修复了XX bug" --category dev
    python work_tracker.py done 3
    python work_tracker.py list
    python work_tracker.py report
    python work_tracker.py report --date 2024-01-15
"""

import json
import os
import sys
from datetime import datetime, date
from pathlib import Path
import argparse


class WorkTracker:
    def __init__(self):
        self.data_dir = Path(__file__).parent / ".work_data"
        self.data_dir.mkdir(exist_ok=True)
        self.records_file = self.data_dir / "records.json"
        self.template_file = self.data_dir / "report_template.md"
        self.records = self._load_records()
        
    def _load_records(self):
        """加载工作记录"""
        if self.records_file.exists():
            with open(self.records_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"entries": []}
    
    def _save_records(self):
        """保存工作记录"""
        with open(self.records_file, 'w', encoding='utf-8') as f:
            json.dump(self.records, f, ensure_ascii=False, indent=2)
    
    def add_entry(self, content, category="general", status="doing"):
        """添加工作记录"""
        entry = {
            "id": len(self.records["entries"]) + 1,
            "timestamp": datetime.now().isoformat(),
            "date": date.today().isoformat(),
            "time": datetime.now().strftime("%H:%M"),
            "content": content,
            "category": category,
            "status": status,
            "tags": []
        }
        self.records["entries"].append(entry)
        self._save_records()
        print(f"✅ 已记录: [{entry['time']}] {content}")
        print(f"   ID: {entry['id']} | 分类: {category} | 状态: {status}")
        return entry
    
    def complete_entry(self, entry_id):
        """标记任务完成"""
        for entry in self.records["entries"]:
            if entry["id"] == entry_id:
                entry["status"] = "done"
                entry["completed_at"] = datetime.now().isoformat()
                self._save_records()
                print(f"✅ 已完成: {entry['content']}")
                return
        print(f"❌ 未找到ID为 {entry_id} 的记录")
    
    def list_entries(self, target_date=None, show_all=False):
        """列出工作记录"""
        if target_date:
            entries = [e for e in self.records["entries"] if e["date"] == target_date]
        else:
            entries = [e for e in self.records["entries"] if e["date"] == date.today().isoformat()]
        
        if not entries:
            print("📝 今日暂无记录")
            return
        
        print(f"\n{'='*60}")
        print(f"📅 工作记录 ({target_date or date.today().isoformat()})")
        print(f"{'='*60}\n")
        
        for entry in entries:
            status_icon = "✅" if entry["status"] == "done" else "🔄"
            print(f"{status_icon} [{entry['time']}] (#{entry['id']}) {entry['content']}")
            print(f"   分类: {entry['category']} | 状态: {entry['status']}")
            print()
    
    def generate_report(self, target_date=None, output_file=None):
        """生成日报"""
        if target_date:
            entries = [e for e in self.records["entries"] if e["date"] == target_date]
        else:
            entries = [e for e in self.records["entries"] if e["date"] == date.today().isoformat()]
        
        if not entries:
            print("📝 指定日期暂无记录，无法生成日报")
            return None
        
        # 按分类分组
        categorized = {}
        for entry in entries:
            cat = entry["category"]
            if cat not in categorized:
                categorized[cat] = []
            categorized[cat].append(entry)
        
        # 生成报告内容
        report_date = target_date or date.today().isoformat()
        report = f"# 工作日报\n\n"
        report += f"**日期**: {report_date}\n"
        report += f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report += "---\n\n"
        
        # 今日完成工作
        report += "## ✅ 今日完成工作\n\n"
        done_entries = [e for e in entries if e["status"] == "done"]
        doing_entries = [e for e in entries if e["status"] == "doing"]
        
        if done_entries:
            for entry in done_entries:
                report += f"- [{entry['time']}] **{entry['content']}** ({entry['category']})\n"
        else:
            report += "- （暂无已完成项）\n"
        
        report += "\n"
        
        # 进行中工作
        if doing_entries:
            report += "## 🔄 进行中工作\n\n"
            for entry in doing_entries:
                report += f"- [{entry['time']}] {entry['content']} ({entry['category']})\n"
            report += "\n"
        
        # 按分类统计
        report += "## 📊 工作分类统计\n\n"
        for category, cat_entries in categorized.items():
            count = len(cat_entries)
            done_count = len([e for e in cat_entries if e["status"] == "done"])
            report += f"- **{category}**: {count} 项 (已完成 {done_count} 项)\n"
        
        report += "\n---\n\n"
        report += "*此日报由工作追踪系统自动生成*\n"
        
        # 输出报告
        if output_file:
            output_path = Path(output_file)
        else:
            output_path = self.data_dir / f"report_{report_date}.md"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 日报已生成: {output_path}")
        print(f"\n{report}")
        
        return report
    
    def quick_add(self, text):
        """快速添加（智能识别）"""
        # 简单的智能识别逻辑
        keywords_map = {
            "dev": ["开发", "代码", "功能", "bug", "修复", "调试", "测试"],
            "meeting": ["会议", "讨论", "沟通", "评审"],
            "doc": ["文档", "报告", "方案", "设计"],
            "research": ["调研", "研究", "学习", "查阅"],
            "other": ["其他", "杂项", "行政"]
        }
        
        category = "general"
        for cat, keywords in keywords_map.items():
            if any(kw in text for kw in keywords):
                category = cat
                break
        
        return self.add_entry(text, category=category)


def main():
    parser = argparse.ArgumentParser(description="工作追踪与日报生成系统")
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # add 命令
    add_parser = subparsers.add_parser("add", help="添加工作记录")
    add_parser.add_argument("content", help="工作内容描述")
    add_parser.add_argument("--category", "-c", default="general", 
                           help="分类: dev/meeting/doc/research/other/general")
    add_parser.add_argument("--status", "-s", default="doing",
                           choices=["doing", "done"], help="状态")
    
    # done 命令
    done_parser = subparsers.add_parser("done", help="标记任务完成")
    done_parser.add_argument("id", type=int, help="任务ID")
    
    # list 命令
    list_parser = subparsers.add_parser("list", help="列出今日工作记录")
    list_parser.add_argument("--date", "-d", help="指定日期 (YYYY-MM-DD)")
    list_parser.add_argument("--all", "-a", action="store_true", help="显示所有记录")
    
    # report 命令
    report_parser = subparsers.add_parser("report", help="生成日报")
    report_parser.add_argument("--date", "-d", help="指定日期 (YYYY-MM-DD)")
    report_parser.add_argument("--output", "-o", help="输出文件路径")
    
    # quick 命令（快速添加）
    quick_parser = subparsers.add_parser("quick", help="快速添加（智能识别分类）")
    quick_parser.add_argument("text", help="工作内容")
    
    args = parser.parse_args()
    tracker = WorkTracker()
    
    if args.command == "add":
        tracker.add_entry(args.content, args.category, args.status)
    elif args.command == "done":
        tracker.complete_entry(args.id)
    elif args.command == "list":
        tracker.list_entries(args.date, args.all)
    elif args.command == "report":
        tracker.generate_report(args.date, args.output)
    elif args.command == "quick":
        tracker.quick_add(args.text)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
