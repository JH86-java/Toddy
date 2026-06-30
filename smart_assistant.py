#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能桌面工作助手 (Kawaii V3) 🌸
========================================
动漫可爱风格 UI，交互更现代流畅
"""

import tkinter as tk
from tkinter import filedialog, simpledialog
import json
import sys
import os
from datetime import datetime, date, timedelta
from pathlib import Path
import threading
import time

# ==================== 可爱主题配色 ====================
class KawaiiTheme:
    """动漫可爱风格主题"""
    # 主色调 - 柔和粉紫系
    BG_MAIN = "#FFF0F5"          # 薰衣草腮红 (主背景)
    BG_CARD = "#FFFFFF"          # 纯白 (卡片背景)
    BG_HEADER = "#FFB7C5"       # 樱花粉 (标题栏)
    BG_TAB = "#FFE4E1"           # 薄雾玫瑰 (Tab背景)
    BG_TAB_ACTIVE = "#FF69B4"    # 热粉红 (选中Tab)
    BG_INPUT = "#FFF5EE"        # 贝壳白 (输入框)
    BG_TASK_ROW = "#FFFFFF"      # 白色 (任务行)
    BG_TASK_ROW_ALT = "#FFF8FA"  # 极淡粉 (交替行)
    BG_TASK_HOVER = "#FFE4EC"    # 淡粉 (悬停)
    
    # 文字色
    FG_MAIN = "#5D4157"          # 深紫棕 (主文字)
    FG_LIGHT = "#9B8A9E"        # 淡紫灰 (次要文字)
    FG_WHITE = "#FFFFFF"         # 白色
    FG_PLACEHOLDER = "#C9B1C9"   # 淡紫 (提示语)
    FG_DATE = "#FF69B4"         # 热粉红 (日期)
    FG_ALARM = "#FF8C00"        # 深橙 (闹钟)
    FG_DELETE = "#FF6B6B"       # 珊瑚红 (删除)
    
    # 按钮色
    BTN_ADD = "#FF69B4"          # 热粉红 (添加)
    BTN_ADD_HOVER = "#FF1493"   # 深粉红
    BTN_START = "#7ED4AD"       # 薄荷绿 (开始)
    BTN_START_HOVER = "#5CBF90" # 深薄荷
    BTN_DELAY = "#FFB347"       # 杏橙 (延迟)
    BTN_DELAY_HOVER = "#FF9F1C" # 深杏
    BTN_DANGER = "#FF6B6B"      # 珊瑚红 (危险)
    BTN_DANGER_HOVER = "#FF4757"
    BTN_SUMMARY = "#A78BFA"     # 薰衣草紫 (总结)
    BTN_SUMMARY_HOVER = "#8B5CF6"
    BTN_EXIT = "#F8A5C2"        # 淡粉 (退出)
    BTN_EXIT_HOVER = "#F78FB3"
    BTN_SETTINGS = "#DDA0DD"    # 梅紫 (设置)
    BTN_CLOSE = "#FFB7C5"       # 樱花粉 (关闭)
    
    # 勾选框
    CHECK_BG = "#7ED4AD"        # 薄荷绿 (已完成)
    CHECK_OUTLINE = "#DDA0DD"   # 梅紫 (未完成)
    
    # 滚动条
    SCROLLBAR_BG = "#FFE4E1"
    SCROLLBAR_THUMB = "#FFB7C5"
    
    # 圆角
    RADIUS = 12
    RADIUS_SM = 8
    RADIUS_BTN = 15
    
    # 字体
    FONT_MAIN = "Microsoft YaHei"
    FONT_MONO = "Consolas"


class SmartDesktopAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("🌸 智能助手")
        self.theme = KawaiiTheme()
        
        # 数据根目录
        self.data_dir = Path(__file__).parent / ".work_data"
        self.data_dir.mkdir(exist_ok=True)
        
        # 全局配置文件（公共）
        self.settings_file = self.data_dir / "settings.json"
        self.settings = self._load_settings()
        
        # 当前查看日期
        self.current_view_date = date.today().isoformat()
        
        # 加载当天任务
        self.tasks = self._load_tasks(self.current_view_date)
        
        # 性能修复：确保 last_sync_date 有默认值，避免重复同步
        if "last_sync_date" not in self.settings:
            self.settings["last_sync_date"] = date.today().isoformat()
            self._save_settings()
            print(f"📝 初始化 last_sync_date 为今天: {self.settings['last_sync_date']}")
        
        # 窗口配置（必须在同步之前，因为同步提示需要屏幕尺寸）
        self.window_width = 400
        self.window_height = 680
        self.icon_size = 64
        
        # 屏幕信息
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        
        # 检查并同步缺失日期的任务
        self._sync_missing_dates()
        
        # 状态变量
        self.is_expanded = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.has_moved = False
        
        # 视图模式: "day" 或 "week"
        self.view_mode = "day"
        # 按周视图时，当前周的周一日期
        self.week_start_date = self._get_monday(date.today()).isoformat()
        # 按周视图时，缓存一周7天的任务数据
        self.week_tasks_cache = {}
        
        # 跟踪正在显示弹窗的任务ID，防止重复弹窗
        self.pending_reminder_tasks = set()
        # 跟踪已预告过的任务ID（15分钟预告），防止重复
        self.pre_reminded_tasks = set()
        
        # 初始位置：从配置读取上次关闭的位置，如果没有则居中
        saved_pos = self.settings.get("icon_position")
        if saved_pos and isinstance(saved_pos, list) and len(saved_pos) == 2:
            self.last_icon_x = saved_pos[0]
            self.last_icon_y = saved_pos[1]
        else:
            self.last_icon_x = (self.screen_width - self.icon_size) // 2
            self.last_icon_y = (self.screen_height - self.icon_size) // 2
        
        # 设置窗口
        self.root.geometry(f"{self.icon_size}x{self.icon_size}+{self.last_icon_x}+{self.last_icon_y}")
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.95)
        
        # 创建UI
        self.create_icon_ui()
        self.create_panel_ui()
        
        # 初始显示
        self.root.withdraw()
        self.show_icon()
        self.root.deiconify()
        
        # 启动后台线程
        self._stop_event = threading.Event()
        threading.Thread(target=self.scheduled_check, daemon=True).start()
        
        # 性能优化：启动主线程队列处理器
        self.root.after(100, self._process_reminder_queue_loop)
        
        self.update_display()
    
    # ==================== 可爱 UI 辅助方法 ====================
    
    def _make_rounded_rect(self, canvas, x1, y1, x2, y2, r, **kwargs):
        """在 Canvas 上绘制圆角矩形"""
        points = [
            x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1,
            x2, y1, x2, y1+r, x2, y1+r, x2, y2-r,
            x2, y2-r, x2, y2, x2-r, y2, x2-r, y2,
            x1+r, y2, x1+r, y2, x1, y2, x1, y2-r,
            x1, y2-r, x1, y1+r, x1, y1+r, x1, y1
        ]
        return canvas.create_polygon(points, smooth=True, **kwargs)
    
    def _make_cute_btn(self, parent, text, bg_color, fg_color="#FFFFFF", command=None, font_size=9, padx=12, pady=4, hover_color=None):
        """创建可爱风格的按钮"""
        btn = tk.Button(parent, text=text, font=(self.theme.FONT_MAIN, font_size, "bold"),
                       bg=bg_color, fg=fg_color, relief=tk.FLAT, cursor="hand2",
                       activebackground=hover_color or bg_color, activeforeground=fg_color,
                       command=command, padx=padx, pady=pady, bd=0,
                       highlightthickness=0)
        # 悬停效果
        if hover_color:
            btn.bind("<Enter>", lambda e, b=btn, c=hover_color: b.config(bg=c))
            btn.bind("<Leave>", lambda e, b=btn, c=bg_color: b.config(bg=c))
        return btn
    
    def _make_cute_dialog(self, title, width=420, height=None):
        """创建可爱风格的弹窗，height=None 时自适应内容高度"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        if height:
            dialog.geometry(f"{width}x{height}")
        else:
            dialog.geometry(f"{width}x1")
        dialog.configure(bg=self.theme.BG_MAIN)
        dialog.attributes('-topmost', True)
        dialog.resizable(False, False)
        
        # 居中
        sw = dialog.winfo_screenwidth()
        sh = dialog.winfo_screenheight()
        if height:
            x = (sw - width) // 2
            y = (sh - height) // 2
        else:
            x = (sw - width) // 2
            y = max(50, (sh - 400) // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # 顶部装饰条
        header = tk.Frame(dialog, bg=self.theme.BG_HEADER, height=6)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # 自适应高度：延迟调整窗口大小以适应内容
        if not height:
            def _auto_resize():
                dialog.update_idletasks()
                req_height = dialog.winfo_reqheight()
                # 限制最大高度不超过屏幕80%
                max_h = int(sh * 0.8)
                final_h = min(req_height + 20, max_h)
                dialog.geometry(f"{width}x{final_h}")
                # 重新居中
                new_y = max(50, (sh - final_h) // 2)
                dialog.geometry(f"+{x}+{new_y}")
            dialog.after(50, _auto_resize)
        
        return dialog
    
    def _show_copy_popup(self, text):
        """双击任务时弹出可选中复制的弹窗"""
        dialog = self._make_cute_dialog("📋 任务内容", 400)
        
        tk.Label(dialog, text="可以选中复制哦~", font=(self.theme.FONT_MAIN, 9), 
                fg=self.theme.FG_LIGHT, bg=self.theme.BG_MAIN).pack(pady=(8, 4))
        
        # 用 Text 组件支持选中高亮复制
        text_widget = tk.Text(dialog, font=(self.theme.FONT_MAIN, 10), 
                             fg=self.theme.FG_MAIN, bg=self.theme.BG_CARD, relief=tk.FLAT,
                             wrap=tk.WORD, height=3, padx=10, pady=8,
                             selectbackground=self.theme.BG_TAB_ACTIVE, 
                             selectforeground=self.theme.FG_WHITE,
                             highlightthickness=0, bd=0)
        text_widget.insert("1.0", text)
        text_widget.config(state=tk.NORMAL)  # 允许选中复制
        text_widget.pack(fill=tk.X, padx=20, pady=5)
        text_widget.focus_set()
        text_widget.tag_add(tk.SEL, "1.0", tk.END)
        
        self._make_cute_btn(dialog, "✅ 关闭", self.theme.BTN_ADD, hover_color=self.theme.BTN_ADD_HOVER,
                           command=dialog.destroy, font_size=9, padx=20, pady=4).pack(pady=8)
        
        dialog.grab_set()
    
    def _cute_messagebox(self, title, message, msg_type="info"):
        """可爱风格的消息弹窗"""
        dialog = self._make_cute_dialog(title, 380, 220)
        
        # 图标
        icons = {"info": "🌸", "warning": "⚠️", "error": "💫", "success": "✨"}
        icon = icons.get(msg_type, "🌸")
        
        tk.Label(dialog, text=icon, font=("Segoe UI Emoji", 28), bg=self.theme.BG_MAIN).pack(pady=(15, 5))
        tk.Label(dialog, text=message, font=(self.theme.FONT_MAIN, 10), fg=self.theme.FG_MAIN, 
                bg=self.theme.BG_MAIN, wraplength=320, justify="center").pack(pady=10)
        
        self._make_cute_btn(dialog, "好的~", self.theme.BTN_ADD, command=dialog.destroy, font_size=10, padx=30, pady=6).pack(pady=10)
        
        dialog.grab_set()
        dialog.wait_window()
    
    def _cute_confirm(self, title, message):
        """可爱风格的确认弹窗，返回 True/False"""
        result = [False]
        dialog = self._make_cute_dialog(title, 380, 240)
        
        tk.Label(dialog, text="🤔", font=("Segoe UI Emoji", 28), bg=self.theme.BG_MAIN).pack(pady=(15, 5))
        tk.Label(dialog, text=message, font=(self.theme.FONT_MAIN, 10), fg=self.theme.FG_MAIN, 
                bg=self.theme.BG_MAIN, wraplength=320, justify="center").pack(pady=10)
        
        btn_frame = tk.Frame(dialog, bg=self.theme.BG_MAIN)
        btn_frame.pack(pady=10)
        
        def on_yes():
            result[0] = True
            dialog.destroy()
        
        def on_no():
            result[0] = False
            dialog.destroy()
        
        self._make_cute_btn(btn_frame, "取消", self.theme.BTN_EXIT, hover_color=self.theme.BTN_EXIT_HOVER, command=on_no).pack(side=tk.LEFT, padx=10)
        self._make_cute_btn(btn_frame, "确定", self.theme.BTN_ADD, hover_color=self.theme.BTN_ADD_HOVER, command=on_yes).pack(side=tk.RIGHT, padx=10)
        
        dialog.grab_set()
        dialog.wait_window()
        return result[0]
    
    # ==================== 数据层 ====================
    
    def _get_day_dir(self, date_str):
        day_dir = self.data_dir / date_str
        day_dir.mkdir(exist_ok=True)
        return day_dir
    
    def _load_tasks(self, date_str):
        tasks_file = self._get_day_dir(date_str) / "tasks.json"
        if tasks_file.exists():
            try:
                with open(tasks_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {"completed": [], "in_progress": [], "upcoming": [], "trash": []}
    
    def _sync_missing_dates(self):
        """检查并同步缺失日期的任务到当天（兼容老版本，自动检测最后使用日期）"""
        today = date.today()
        today_str = today.isoformat()
        
        # 从配置文件读取上次同步的日期
        last_sync_str = self.settings.get("last_sync_date", "")
        
        if not last_sync_str:
            # 老版本没有记录，扫描文件系统找到最新有数据的日期
            print("🔍 未找到同步记录，正在扫描历史数据...")
            existing_dates = []
            if self.data_dir.exists():
                for item in self.data_dir.iterdir():
                    if item.is_dir():
                        try:
                            d = date.fromisoformat(item.name)
                            # 只考虑今天及之前的日期
                            if d <= today:
                                tasks_file = item / "tasks.json"
                                if tasks_file.exists():
                                    # 检查是否有实际任务数据
                                    day_tasks = self._load_tasks(item.name)
                                    has_tasks = (len(day_tasks.get("in_progress", [])) > 0 or
                                                 len(day_tasks.get("upcoming", [])) > 0 or
                                                 len(day_tasks.get("completed", [])) > 0)
                                    if has_tasks:
                                        existing_dates.append(d)
                        except ValueError:
                            continue
            
            if existing_dates:
                # 找到最新有数据的日期
                latest_date = max(existing_dates)
                last_sync_str = latest_date.isoformat()
                print(f"📅 检测到最新数据日期: {last_sync_str}")
            else:
                # 没有任何历史数据，记录今天为初始日期
                last_sync_str = today_str
                print("📝 无历史数据，已记录初始日期")
            
            # 保存检测到的日期
            self.settings["last_sync_date"] = last_sync_str
            self._save_settings()
        
        try:
            last_sync_date = date.fromisoformat(last_sync_str)
        except ValueError:
            # 日期格式错误，重置为今天
            self.settings["last_sync_date"] = today_str
            self._save_settings()
            return
        
        # 如果上次同步日期 >= 今天，无需同步
        if last_sync_date >= today:
            return
        
        # 计算需要同步的天数
        days_to_sync = (today - last_sync_date).days
        print(f"🔄 检测到 {days_to_sync} 天未同步，正在迁移任务...")
        
        # 在UI上显示临时提示
        sync_hint = tk.Toplevel(self.root)
        sync_hint.overrideredirect(True)
        sync_hint.attributes("-topmost", True)
        sync_hint.configure(bg=self.theme.BG_CARD)
        hint_text = f"🔄 正在同步 {days_to_sync} 天的任务..."
        tk.Label(sync_hint, text=hint_text, font=(self.theme.FONT_MAIN, 11),
                fg=self.theme.FG_DATE, bg=self.theme.BG_CARD, padx=20, pady=10).pack()
        
        w = 280
        h = 50
        x = (self.screen_width - w) // 2
        y = (self.screen_height - h) // 2
        sync_hint.geometry(f"{w}x{h}+{x}+{y}")
        self.root.update()
        
        try:
            # 收集所有历史未完成任务（从 last_sync_date 当天开始）
            # 修复：跳过已完成的任务，只同步真正未完成的任务
            all_unfinished = []
            collect_d = last_sync_date
            while collect_d < today:
                day_tasks = self._load_tasks(collect_d.isoformat())
                for task in day_tasks.get("in_progress", []):
                    # 跳过已标记为完成的任务
                    if not task.get("completed", False):
                        all_unfinished.append(("in_progress", task))
                for task in day_tasks.get("upcoming", []):
                    # 跳过已标记为完成的任务
                    if not task.get("completed", False):
                        all_unfinished.append(("upcoming", task))
                collect_d = collect_d + timedelta(days=1)
            
            # 将所有历史未完成任务追加到今天
            if all_unfinished:
                today_tasks = self._load_tasks(today_str)
                
                # 去重：检查今天是否已有同名任务
                existing_texts = set()
                for t in today_tasks.get("in_progress", []) + today_tasks.get("upcoming", []):
                    existing_texts.add(t.get("text", ""))
                
                added_count = 0
                for status, task in all_unfinished:
                    if task.get("text", "") not in existing_texts:
                        today_tasks[status].append(task)
                        existing_texts.add(task.get("text", ""))
                        added_count += 1
                
                if added_count > 0:
                    today_dir = self._get_day_dir(today_str)
                    today_dir.mkdir(parents=True, exist_ok=True)
                    with open(today_dir / "tasks.json", "w", encoding="utf-8") as f:
                        json.dump(today_tasks, f, ensure_ascii=False, indent=2)
                    print(f"📥 已追加 {added_count} 个任务到今天")
            
            # 更新最后同步日期为今天
            self.settings["last_sync_date"] = today_str
            self._save_settings()
            
            # 重新加载当天任务
            self.tasks = self._load_tasks(today_str)
            print("✅ 任务同步完成！")
        except Exception as e:
            print(f"⚠️ 同步出错: {e}")
        finally:
            try:
                sync_hint.destroy()
            except:
                pass

    def _save_tasks(self):
        tasks_file = self._get_day_dir(self.current_view_date) / "tasks.json"
        with open(tasks_file, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)
    
    def _load_settings(self):
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    if "report_dir" not in loaded:
                        loaded["report_dir"] = str(Path(__file__).parent / "workLog")
                    if "reminder_time" not in loaded:
                        loaded["reminder_time"] = "18:00"
                    return loaded
            except:
                pass
        default_dir = str(Path(__file__).parent / "workLog")
        return {"reminder_time": "18:00", "auto_summarize": True, "report_dir": default_dir, "auto_start": False}
    
    def _save_settings(self):
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)
    
    def _switch_date(self, date_str):
        self._save_tasks()
        self.current_view_date = date_str
        self.tasks = self._load_tasks(date_str)
        self.date_label_var.set(date_str)
        self.update_display()
    
    def _get_monday(self, d):
        """获取 d 所在周的周一日期"""
        return d - timedelta(days=d.weekday())
    
    def _get_week_range(self, monday):
        """返回周一到周日的日期列表"""
        return [monday + timedelta(days=i) for i in range(7)]
    
    def _get_week_label(self, monday):
        """返回周标签（短格式，不含年份）"""
        sunday = monday + timedelta(days=6)
        return f"{monday.strftime('%m/%d')} ~ {sunday.strftime('%m/%d')}"
    
    def _switch_week(self, monday_date):
        """切换到某一周的视图"""
        self.week_start_date = monday_date.isoformat()
        self.week_tasks_cache = {}
        for d in self._get_week_range(monday_date):
            ds = d.isoformat()
            self.week_tasks_cache[ds] = self._load_tasks(ds)
        self.date_label_var.set(self._get_week_label(monday_date))
        self.year_label_var.set(str(monday_date.year))
        self.update_display()
    
    # ==================== 设置窗口 ====================
    
    def open_settings(self):
        win = self._make_cute_dialog("⚙️ 系统设置", 420, 380)
        
        tk.Label(win, text="⚙️ 系统设置", font=(self.theme.FONT_MAIN, 14, "bold"), 
                fg=self.theme.FG_MAIN, bg=self.theme.BG_MAIN).pack(pady=(15, 10))
        
        # 设置卡片
        card = tk.Frame(win, bg=self.theme.BG_CARD, padx=20, pady=15)
        card.pack(fill=tk.X, padx=20, pady=5)
        
        # 1. 开机自启动
        row1 = tk.Frame(card, bg=self.theme.BG_CARD)
        row1.pack(fill=tk.X, pady=8)
        tk.Label(row1, text="🚀 开机自启动", font=(self.theme.FONT_MAIN, 10), fg=self.theme.FG_MAIN, bg=self.theme.BG_CARD).pack(side=tk.LEFT)
        auto_var = tk.BooleanVar(value=self.settings.get("auto_start", False))
        tk.Checkbutton(row1, variable=auto_var, bg=self.theme.BG_CARD, selectcolor=self.theme.BG_TAB,
                       activebackground=self.theme.BG_CARD).pack(side=tk.RIGHT)
        
        # 2. 日报生成时间
        row2 = tk.Frame(card, bg=self.theme.BG_CARD)
        row2.pack(fill=tk.X, pady=8)
        tk.Label(row2, text="⏰ 日报生成时间", font=(self.theme.FONT_MAIN, 10), fg=self.theme.FG_MAIN, bg=self.theme.BG_CARD).pack(side=tk.LEFT)
        time_var = tk.StringVar(value=self.settings.get("reminder_time", "18:00"))
        tk.Entry(row2, textvariable=time_var, font=(self.theme.FONT_MAIN, 10), bg=self.theme.BG_INPUT, 
                fg=self.theme.FG_MAIN, relief=tk.FLAT, width=8, justify="center").pack(side=tk.RIGHT)
        
        # 3. 日报保存目录
        row3 = tk.Frame(card, bg=self.theme.BG_CARD)
        row3.pack(fill=tk.X, pady=8)
        tk.Label(row3, text="📂 日报保存目录", font=(self.theme.FONT_MAIN, 10), fg=self.theme.FG_MAIN, bg=self.theme.BG_CARD).pack(anchor="w")
        current_dir = self.settings.get("report_dir", "") or str(Path(__file__).parent / "workLog")
        dir_var = tk.StringVar(value=current_dir)
        dir_entry = tk.Entry(row3, textvariable=dir_var, font=(self.theme.FONT_MAIN, 9), bg=self.theme.BG_INPUT, 
                            fg=self.theme.FG_MAIN, relief=tk.FLAT)
        dir_entry.pack(fill=tk.X, pady=5)
        
        def set_dir():
            d = filedialog.askdirectory()
            if d: dir_var.set(d)
        self._make_cute_btn(row3, "📁 选择", self.theme.BTN_DELAY, hover_color=self.theme.BTN_DELAY_HOVER, command=set_dir, font_size=8, padx=8, pady=2).pack(anchor="e")
        
        def save_settings_action():
            self.settings["auto_start"] = auto_var.get()
            self.settings["reminder_time"] = time_var.get()
            self.settings["report_dir"] = dir_var.get()
            self._save_settings()
            
            startup_path = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
            shortcut_path = os.path.join(startup_path, "SmartAssistant.lnk")
            target_script = os.path.join(Path(__file__).parent, "run.bat")
            
            if self.settings["auto_start"]:
                cmd = f'$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut("{shortcut_path}"); $Shortcut.TargetPath = "{target_script}"; $Shortcut.WorkingDirectory = "{Path(__file__).parent}"; $Shortcut.Save()'
                os.system(f'powershell -Command "{cmd}"')
            else:
                if os.path.exists(shortcut_path):
                    os.remove(shortcut_path)
            win.destroy()
            self._cute_messagebox("成功", "设置已保存~ 🎉", "success")
        
        self._make_cute_btn(win, "💾 保存设置", self.theme.BTN_ADD, hover_color=self.theme.BTN_ADD_HOVER, 
                           command=save_settings_action, font_size=10, padx=30, pady=6).pack(pady=15)
    
    # ==================== 日报生成 ====================
    
    def generate_daily_report(self):
        yesterday = date.today() - timedelta(days=1)
        y_str = yesterday.isoformat()
        yesterday_tasks = self._load_tasks(y_str)
        
        report_dir = self.settings.get("report_dir", "") or str(Path(__file__).parent / "workLog")
        Path(report_dir).mkdir(parents=True, exist_ok=True)
        
        completed = yesterday_tasks.get("completed", [])
        in_progress = yesterday_tasks.get("in_progress", [])
        upcoming = yesterday_tasks.get("upcoming", [])
        
        report_content = f"工作日报 - {yesterday.strftime('%Y年%m月%d日')}\n"
        report_content += "=" * 40 + "\n\n"
        report_content += f"✅ 今日完成 ({len(completed)}项):\n"
        for t in completed: report_content += f"  - {t['text']}\n"
        report_content += f"\n🔄 进行中 ({len(in_progress)}项):\n"
        for t in in_progress: report_content += f"  - {t['text']}\n"
        report_content += f"\n📅 计划中 ({len(upcoming)}项):\n"
        for t in upcoming: report_content += f"  - {t['text']}\n"
        
        filename = f"{yesterday.strftime('%Y%m%d')}日报.txt"
        filepath = os.path.join(report_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"[Auto Report] Generated: {filepath}")
    
    def migrate_tasks_to_new_day(self):
        yesterday = date.today() - timedelta(days=1)
        y_str = yesterday.isoformat()
        today_str = date.today().isoformat()
        yesterday_tasks = self._load_tasks(y_str)
        
        tasks_to_migrate = []
        for task in yesterday_tasks.get("in_progress", []):
            new_task = task.copy()
            new_task["date"] = today_str
            new_task["id"] = int(time.time() * 1000) + len(tasks_to_migrate)
            tasks_to_migrate.append(new_task)
        for task in yesterday_tasks.get("upcoming", []):
            new_task = task.copy()
            new_task["date"] = today_str
            new_task["id"] = int(time.time() * 1000) + len(tasks_to_migrate)
            tasks_to_migrate.append(new_task)
        
        if not tasks_to_migrate:
            print(f"[Migration] No tasks to migrate from {y_str}")
            return
        
        today_tasks = self._load_tasks(today_str)
        for task in tasks_to_migrate:
            original_key = task.get("from_key", "in_progress")
            if original_key == "upcoming":
                today_tasks["upcoming"].append(task)
            else:
                today_tasks["in_progress"].append(task)
        
        tasks_file = self._get_day_dir(today_str) / "tasks.json"
        with open(tasks_file, 'w', encoding='utf-8') as f:
            json.dump(today_tasks, f, ensure_ascii=False, indent=2)
        
        print(f"[Migration] Migrated {len(tasks_to_migrate)} tasks from {y_str} to {today_str}")
        if self.current_view_date == today_str:
            self.tasks = today_tasks
            self.update_display()
    
    # ==================== 定时任务 ====================
    
    def scheduled_check(self):
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
                    self._last_migration_date = now.date()
    

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

    def _check_reminders(self, now):
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
                    self.reminder_queue.put(("pre_reminder", task, remind_time))
    
    def _show_pre_reminder(self, task, remind_time):
        """15分钟预告弹窗：温柔提醒任务即将开始"""
        task_id = task.get("id")
        task_text = task.get("text", "未知任务")
        time_str = remind_time.strftime("%H:%M")
        
        dialog = self._make_cute_dialog("🔔 任务即将开始", 400, 260)
        
        tk.Label(dialog, text="🔔", font=("Segoe UI Emoji", 32), bg=self.theme.BG_MAIN).pack(pady=(12, 3))
        tk.Label(dialog, text="还有15分钟就要开始啦~", font=(self.theme.FONT_MAIN, 12, "bold"), 
                fg=self.theme.FG_MAIN, bg=self.theme.BG_MAIN).pack()
        
        # 任务内容卡片
        content_card = tk.Frame(dialog, bg=self.theme.BG_CARD, padx=15, pady=8)
        content_card.pack(fill=tk.X, padx=30, pady=8)
        tk.Label(content_card, text=f"📝 {task_text}", font=(self.theme.FONT_MAIN, 10), 
                fg=self.theme.FG_MAIN, bg=self.theme.BG_CARD, wraplength=300).pack()
        tk.Label(content_card, text=f"⏰ 预约时间 {time_str}", font=(self.theme.FONT_MONO, 9), 
                fg=self.theme.FG_ALARM, bg=self.theme.BG_CARD).pack(pady=(3, 0))
        
        # 按钮区
        btn_frame = tk.Frame(dialog, bg=self.theme.BG_MAIN)
        btn_frame.pack(pady=8)
        
        def on_reschedule():
            dialog.destroy()
            new_time_str = self._ask_remind_time(task.get("remind_at"))
            if new_time_str:
                try:
                    new_time = datetime.fromisoformat(new_time_str)
                    idx = self._find_task_index("upcoming", task_id)
                    if idx != -1:
                        self.tasks["upcoming"][idx]["remind_at"] = new_time_str
                        # 从预告集合中移除，以便新时间前15分钟再次预告
                        self.pre_reminded_tasks.discard(task_id)
                        self._save_tasks()
                        self.update_display()
                        self._cute_messagebox("已更新", f"提醒时间已更新为：\n{new_time.strftime('%Y-%m-%d %H:%M')} ✨", "success")
                except:
                    pass
        
        def on_know():
            dialog.destroy()
        
        self._make_cute_btn(btn_frame, "🕐 改时间", self.theme.BTN_DELAY, hover_color=self.theme.BTN_DELAY_HOVER,
                           command=on_reschedule, font_size=9, padx=12, pady=4).pack(side=tk.LEFT, padx=8)
        self._make_cute_btn(btn_frame, "知道啦~", self.theme.BTN_ADD, hover_color=self.theme.BTN_ADD_HOVER,
                           command=on_know, font_size=9, padx=12, pady=4).pack(side=tk.RIGHT, padx=8)
        
        dialog.grab_set()
    
    def _show_start_dialog_from_reminder(self, task):
        task_id = task.get("id")
        task_text = task.get("text", "未知任务")
        self.pending_reminder_tasks.add(task_id)
        
        dialog = self._make_cute_dialog(f"⏰ {task_text}", 420, 280)
        
        tk.Label(dialog, text="⏰", font=("Segoe UI Emoji", 36), bg=self.theme.BG_MAIN).pack(pady=(15, 5))
        tk.Label(dialog, text="预约时间到啦~", font=(self.theme.FONT_MAIN, 13, "bold"), 
                fg=self.theme.FG_MAIN, bg=self.theme.BG_MAIN).pack()
        tk.Label(dialog, text="是否开始这个任务呢？", font=(self.theme.FONT_MAIN, 10), 
                fg=self.theme.FG_LIGHT, bg=self.theme.BG_MAIN).pack(pady=2)
        
        # 任务内容卡片
        content_card = tk.Frame(dialog, bg=self.theme.BG_CARD, padx=15, pady=8)
        content_card.pack(fill=tk.X, padx=30, pady=10)
        tk.Label(content_card, text=f"📝 {task_text}", font=(self.theme.FONT_MAIN, 10), 
                fg=self.theme.FG_MAIN, bg=self.theme.BG_CARD, wraplength=320).pack()
        
        btn_frame = tk.Frame(dialog, bg=self.theme.BG_MAIN)
        btn_frame.pack(pady=10)
        
        def cleanup_and_close():
            self.pending_reminder_tasks.discard(task_id)
            dialog.destroy()
        
        def on_yes():
            try:
                idx = self._find_task_index("upcoming", task_id)
                if idx != -1:
                    removed_task = self.tasks["upcoming"].pop(idx)
                    removed_task["from_key"] = "in_progress"
                    self.tasks["in_progress"].append(removed_task)
                    self._save_tasks()
                    self.update_display()
            finally:
                cleanup_and_close()
        
        def on_delay():
            try:
                idx = self._find_task_index("upcoming", task_id)
                if idx != -1:
                    removed_task = self.tasks["upcoming"].pop(idx)
                    new_time = datetime.now() + timedelta(hours=1)
                    removed_task["remind_at"] = new_time.isoformat()
                    self.tasks["upcoming"].append(removed_task)
                    self._save_tasks()
                    self.update_display()
            finally:
                cleanup_and_close()
                self._cute_messagebox("已延迟", f"任务已延迟1小时~\n新提醒时间：{new_time.strftime('%Y-%m-%d %H:%M')} 🕐", "info")
        
        self._make_cute_btn(btn_frame, "🕐 延迟1小时", self.theme.BTN_DELAY, hover_color=self.theme.BTN_DELAY_HOVER, 
                           command=on_delay, font_size=10, padx=15, pady=5).pack(side=tk.LEFT, padx=8)
        self._make_cute_btn(btn_frame, "✅ 开始吧~", self.theme.BTN_START, hover_color=self.theme.BTN_START_HOVER, 
                           command=on_yes, font_size=10, padx=15, pady=5).pack(side=tk.RIGHT, padx=8)
        
        dialog.protocol("WM_DELETE_WINDOW", cleanup_and_close)
    
    # ==================== UI：图标 ====================
    
    def create_icon_ui(self):
        self.icon_frame = tk.Frame(self.root, bg=self.theme.BG_MAIN, cursor="fleur", 
                                   width=self.icon_size, height=self.icon_size)
        
        icon_path = Path(__file__).parent / "img" / "icon.png"
        if icon_path.exists():
            try:
                self.icon_img = tk.PhotoImage(file=str(icon_path))
                self.icon_img = self.icon_img.subsample(self.icon_img.width() // self.icon_size, 
                                                        self.icon_img.height() // self.icon_size)
                self.icon_label = tk.Label(self.icon_frame, image=self.icon_img, bg=self.theme.BG_MAIN)
            except Exception as e:
                print(f"Failed to load icon: {e}, falling back to emoji")
                self.icon_label = tk.Label(self.icon_frame, text="🌸", font=("Segoe UI Emoji", 28), bg=self.theme.BG_MAIN)
        else:
            self.icon_label = tk.Label(self.icon_frame, text="🌸", font=("Segoe UI Emoji", 28), bg=self.theme.BG_MAIN)
            
        self.icon_label.place(relx=0.5, rely=0.5, anchor="center")
        self.icon_frame.pack(fill=tk.BOTH, expand=True)
        
        for w in (self.icon_frame, self.icon_label):
            w.bind("<ButtonPress-1>", self.on_press)
            w.bind("<B1-Motion>", self.on_drag)
            w.bind("<ButtonRelease-1>", self.on_release)
    
    # ==================== UI：面板 ====================
    
    def create_panel_ui(self):
        self.panel_frame = tk.Frame(self.root, bg=self.theme.BG_MAIN, width=self.window_width, height=self.window_height)
        
        # --- 标题栏 ---
        title_frame = tk.Frame(self.panel_frame, bg=self.theme.BG_HEADER, height=50)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        left_frame = tk.Frame(title_frame, bg=self.theme.BG_HEADER)
        left_frame.pack(side=tk.LEFT, padx=8, pady=4)
        tk.Label(left_frame, text="🌸", font=("Segoe UI Emoji", 12), 
                fg=self.theme.FG_WHITE, bg=self.theme.BG_HEADER).pack(side=tk.LEFT, padx=(0, 2))
        
        self.date_label_var = tk.StringVar(value=self.current_view_date)
        self.year_label_var = tk.StringVar(value="")
        
        # 左箭头：前一天/上一周
        self.prev_btn = self._make_cute_btn(left_frame, "◀", self.theme.BTN_SUMMARY, fg_color=self.theme.FG_WHITE,
                           hover_color=self.theme.BTN_SUMMARY_HOVER, command=self.prev_period, 
                           font_size=8, padx=3, pady=1)
        self.prev_btn.pack(side=tk.LEFT, padx=(4, 0))
        
        # 日期/周标签按钮：紫色，可点击
        date_btn = tk.Button(left_frame, textvariable=self.date_label_var, font=(self.theme.FONT_MONO, 9, "bold"),
                           bg=self.theme.BTN_SUMMARY, fg=self.theme.FG_WHITE, relief=tk.FLAT, cursor="hand2", 
                           activebackground=self.theme.BTN_SUMMARY_HOVER, activeforeground=self.theme.FG_WHITE,
                           command=self.change_date, padx=6, pady=2, bd=0)
        date_btn.pack(side=tk.LEFT, padx=2)
        # 悬停效果
        date_btn.bind("<Enter>", lambda e: date_btn.config(bg=self.theme.BTN_SUMMARY_HOVER))
        date_btn.bind("<Leave>", lambda e: date_btn.config(bg=self.theme.BTN_SUMMARY))
        
        # 年份标签（周视图时显示）
        self.year_label = tk.Label(left_frame, textvariable=self.year_label_var, font=(self.theme.FONT_MONO, 8),
                           fg=self.theme.FG_WHITE, bg=self.theme.BG_HEADER)
        self.year_label.pack(side=tk.LEFT, padx=(2, 0))
        
        # 右箭头：后一天/下一周
        self.next_btn = self._make_cute_btn(left_frame, "▶", self.theme.BTN_SUMMARY, fg_color=self.theme.FG_WHITE,
                           hover_color=self.theme.BTN_SUMMARY_HOVER, command=self.next_period, 
                           font_size=8, padx=3, pady=1)
        self.next_btn.pack(side=tk.LEFT, padx=2)
        
        # 天/周切换按钮
        self.view_mode_btn = self._make_cute_btn(left_frame, "📅 周", self.theme.BTN_DELAY, fg_color=self.theme.FG_WHITE,
                           hover_color=self.theme.BTN_DELAY_HOVER, command=self.toggle_view_mode, 
                           font_size=7, padx=4, pady=1)
        self.view_mode_btn.pack(side=tk.LEFT, padx=(2, 0))
        
        self._make_cute_btn(title_frame, "✕", self.theme.BTN_CLOSE, fg_color=self.theme.FG_MAIN,
                           command=self.hide_panel, font_size=10, padx=8, pady=2).pack(side=tk.RIGHT, padx=8, pady=8)
        self._make_cute_btn(title_frame, "⚙️", self.theme.BTN_SETTINGS, fg_color=self.theme.FG_WHITE,
                           command=self.open_settings, font_size=10, padx=6, pady=2).pack(side=tk.RIGHT, padx=5, pady=8)
        
        # --- Tab 标签页 ---
        tab_frame = tk.Frame(self.panel_frame, bg=self.theme.BG_MAIN)
        tab_frame.pack(fill=tk.X, pady=(8, 4), padx=8)
        
        tabs = [("✅ 已完成", "completed"), ("🔄 进行中", "in_progress"), ("📅 即将做", "upcoming"), ("🗑️ 回收站", "trash")]
        self.selected_tab = tk.StringVar(value="🔄 进行中")
        
        def on_tab_change():
            self.update_display()
            self.update_input_ui_for_tab()
        
        for tab_text, tab_key in tabs:
            btn = tk.Radiobutton(tab_frame, text=tab_text, variable=self.selected_tab, value=tab_text,
                          font=(self.theme.FONT_MAIN, 8, "bold"), fg=self.theme.FG_MAIN, bg=self.theme.BG_TAB,
                          selectcolor=self.theme.BG_TAB_ACTIVE, activebackground=self.theme.BG_TAB,
                          activeforeground=self.theme.FG_WHITE,
                          command=on_tab_change, indicatoron=False, padx=8, pady=4, bd=0,
                          highlightthickness=0)
            btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        
        # --- 输入框 ---
        input_frame = tk.Frame(self.panel_frame, bg=self.theme.BG_MAIN)
        input_frame.pack(fill=tk.X, pady=4, padx=12)
        
        self.task_entry_placeholder = "✍️ 请输入任务内容~"
        self.task_entry_has_placeholder = True
        
        self.task_entry = tk.Entry(input_frame, font=(self.theme.FONT_MAIN, 10), bg=self.theme.BG_INPUT, 
                                   fg=self.theme.FG_PLACEHOLDER, insertbackground=self.theme.FG_MAIN, 
                                   relief=tk.FLAT, highlightthickness=1, highlightcolor=self.theme.BG_TAB_ACTIVE,
                                   highlightbackground=self.theme.BG_TAB)
        self.task_entry.insert(0, self.task_entry_placeholder)
        self.task_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=5)
        
        def on_entry_focus_in(event):
            if self.task_entry_has_placeholder:
                self.task_entry.delete(0, tk.END)
                self.task_entry.config(fg=self.theme.FG_MAIN)
                self.task_entry_has_placeholder = False
        
        def on_entry_focus_out(event):
            if not self.task_entry.get().strip():
                self.task_entry.insert(0, self.task_entry_placeholder)
                self.task_entry.config(fg=self.theme.FG_PLACEHOLDER)
                self.task_entry_has_placeholder = True
        
        self.task_entry.bind("<FocusIn>", on_entry_focus_in)
        self.task_entry.bind("<FocusOut>", on_entry_focus_out)
        self.task_entry.bind("<Return>", lambda e: self.add_task())
        
        self.input_frame = input_frame
        
        self.add_btn = self._make_cute_btn(input_frame, "➕ 添加", self.theme.BTN_ADD, 
                                           hover_color=self.theme.BTN_ADD_HOVER, command=self.add_task)
        self.add_btn.pack(side=tk.RIGHT)
        
        self.clear_trash_btn = self._make_cute_btn(input_frame, "🗑️ 清空回收站", self.theme.BTN_DANGER, 
                                                    hover_color=self.theme.BTN_DANGER_HOVER, command=self.clear_trash)
        self.clear_trash_btn.pack_forget()
        
        # --- 任务列表（Canvas 滚动） ---
        list_frame = tk.Frame(self.panel_frame, bg=self.theme.BG_MAIN)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=4, padx=8)
        self.list_frame = list_frame
        
        canvas = tk.Canvas(list_frame, bg=self.theme.BG_MAIN, highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview,
                                bg=self.theme.SCROLLBAR_BG, troughcolor=self.theme.SCROLLBAR_BG,
                                activebackground=self.theme.SCROLLBAR_THUMB)
        self.scrollable_frame = tk.Frame(canvas, bg=self.theme.BG_MAIN)
        
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 关键：让 scrollable_frame 宽度跟随 canvas 宽度，这样 Text 组件才能正确换行
        def _on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", _on_canvas_configure)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel(event):
            content_height = canvas.bbox("all")[3] if canvas.bbox("all") else 0
            view_height = canvas.winfo_height()
            if content_height > view_height:
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind("<Enter>", _bind_mousewheel)
        canvas.bind("<Leave>", _unbind_mousewheel)
        scrollbar.bind("<Enter>", _bind_mousewheel)
        scrollbar.bind("<Leave>", _unbind_mousewheel)
        
        self.task_container = self.scrollable_frame
        
        # --- 底部按钮 ---
        btn_frame = tk.Frame(self.panel_frame, bg=self.theme.BG_MAIN)
        btn_frame.pack(fill=tk.X, pady=8, padx=12)
        self._make_cute_btn(btn_frame, "📊 日报", self.theme.BTN_SUMMARY, hover_color=self.theme.BTN_SUMMARY_HOVER,
                           command=self.generate_summary, font_size=10, padx=12, pady=5).pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        self._make_cute_btn(btn_frame, "📋 周报", self.theme.BTN_DELAY, hover_color=self.theme.BTN_DELAY_HOVER,
                           command=self.generate_weekly_report, font_size=10, padx=12, pady=5).pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        self._make_cute_btn(btn_frame, "🚪 退出", self.theme.BTN_EXIT, hover_color=self.theme.BTN_EXIT_HOVER,
                           command=self.quit_app, font_size=10, padx=12, pady=5).pack(side=tk.RIGHT, padx=3, fill=tk.X, expand=True)
    
    # ==================== 交互：拖动与点击 ====================
    
    def on_press(self, event):
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root
        self.has_moved = False
    
    def on_drag(self, event):
        dx = abs(event.x_root - self.drag_start_x)
        dy = abs(event.y_root - self.drag_start_y)
        if dx > 5 or dy > 5:
            self.has_moved = True
            new_x = self.root.winfo_x() + (event.x_root - self.drag_start_x)
            new_y = self.root.winfo_y() + (event.y_root - self.drag_start_y)
            screen_w = self.root.winfo_screenwidth()
            screen_h = self.root.winfo_screenheight()
            new_x = max(0, min(new_x, screen_w - self.icon_size))
            new_y = max(0, min(new_y, screen_h - self.icon_size))
            self.root.geometry(f"+{new_x}+{new_y}")
            self.drag_start_x = event.x_root
            self.drag_start_y = event.y_root
    
    def on_release(self, event):
        if not self.has_moved:
            self.toggle_panel()
        else:
            self.last_icon_x = self.root.winfo_x()
            self.last_icon_y = self.root.winfo_y()
            self.settings["icon_position"] = [self.last_icon_x, self.last_icon_y]
            self._save_settings()
    
    def toggle_panel(self):
        if self.is_expanded:
            self.hide_panel()
        else:
            self.show_panel()
    
    def show_panel(self):
        self.is_expanded = True
        current_x = self.root.winfo_x()
        current_y = self.root.winfo_y()
        screen_w = self.root.winfo_screenwidth()
        new_x = screen_w - self.window_width - 10 if current_x + self.window_width > screen_w else current_x
        self.root.geometry(f"{self.window_width}x{self.window_height}+{new_x}+{current_y}")
        self.icon_frame.pack_forget()
        self.panel_frame.pack(fill=tk.BOTH, expand=True)
        self.root.attributes('-alpha', 1.0)
    
    def hide_panel(self):
        self.is_expanded = False
        self.panel_frame.pack_forget()
        self.icon_frame.pack(fill=tk.BOTH, expand=True)
        self.root.geometry(f"{self.icon_size}x{self.icon_size}+{self.last_icon_x}+{self.last_icon_y}")
        self.root.attributes('-alpha', 0.95)
    
    def show_icon(self):
        self.hide_panel()
    
    # ==================== 日期切换 ====================
    
    def prev_period(self):
        """切换到前一天或上一周"""
        if self.view_mode == "week":
            try:
                current_monday = date.fromisoformat(self.week_start_date)
                prev_monday = current_monday - timedelta(days=7)
                self._switch_week(prev_monday)
            except:
                pass
        else:
            self.prev_day()
    
    def next_period(self):
        """切换到后一天或下一周"""
        if self.view_mode == "week":
            try:
                current_monday = date.fromisoformat(self.week_start_date)
                next_monday = current_monday + timedelta(days=7)
                self._switch_week(next_monday)
            except:
                pass
        else:
            self.next_day()
    
    def toggle_view_mode(self):
        """切换天/周视图"""
        if self.view_mode == "day":
            self._save_tasks()
            self.view_mode = "week"
            monday = self._get_monday(date.fromisoformat(self.current_view_date))
            self._switch_week(monday)
            self.view_mode_btn.config(text="📅 天")
            self.task_entry.pack_forget()
            self.add_btn.pack_forget()
            if self.clear_trash_btn.winfo_ismapped():
                self.clear_trash_btn.pack_forget()
        else:
            self.view_mode = "day"
            try:
                monday = date.fromisoformat(self.week_start_date)
                self._switch_date(monday.isoformat())
            except:
                self._switch_date(date.today().isoformat())
            self.view_mode_btn.config(text="📅 周")
            self.year_label_var.set("")
            self.update_input_ui_for_tab()
    
    def prev_day(self):
        """切换到前一天"""
        try:
            current = datetime.fromisoformat(self.current_view_date)
            prev = current - timedelta(days=1)
            self._switch_date(prev.date().isoformat())
        except:
            pass
    
    def next_day(self):
        """切换到后一天"""
        try:
            current = datetime.fromisoformat(self.current_view_date)
            nxt = current + timedelta(days=1)
            self._switch_date(nxt.date().isoformat())
        except:
            pass
    
    def change_date(self):
        """弹出日期选择器，天视图选天，周视图选周"""
        if self.view_mode == "week":
            self._change_week()
            return
        self._change_day()
    
    def _change_day(self):
        """弹出可爱风格的日期选择器（天视图）"""
        result = [None]
        
        dialog = self._make_cute_dialog("📅 切换日期", 360)
        
        tk.Label(dialog, text="📅", font=("Segoe UI Emoji", 32), bg=self.theme.BG_MAIN).pack(pady=(10, 2))
        tk.Label(dialog, text="选择查看日期~", font=(self.theme.FONT_MAIN, 12, "bold"), 
                fg=self.theme.FG_MAIN, bg=self.theme.BG_MAIN).pack(pady=(0, 8))
        
        # === 快捷日期 ===
        quick_card = tk.Frame(dialog, bg=self.theme.BG_CARD, padx=15, pady=10)
        quick_card.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(quick_card, text="⚡ 快捷选择", font=(self.theme.FONT_MAIN, 9, "bold"), 
                fg=self.theme.FG_MAIN, bg=self.theme.BG_CARD).pack(anchor="w", pady=(0, 5))
        
        quick_row = tk.Frame(quick_card, bg=self.theme.BG_CARD)
        quick_row.pack(fill=tk.X)
        
        today = date.today()
        weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        
        quick_dates = []
        for d in range(-3, 4):
            target = today + timedelta(days=d)
            wd = weekday_names[target.weekday()]
            if d == 0:
                label = "📍今天"
            elif d == -1:
                label = "昨天"
            elif d == 1:
                label = "明天"
            elif d == -2:
                label = "前天"
            elif d == 2:
                label = "后天"
            else:
                label = f"{target.strftime('%m/%d')}{wd}"
            quick_dates.append((label, target.isoformat(), d == 0))
        
        quick_btn_refs = []
        
        for idx, (label, date_str, is_default) in enumerate(quick_dates):
            bg = self.theme.BG_TAB_ACTIVE if is_default else self.theme.BG_TAB
            fg = self.theme.FG_WHITE if is_default else self.theme.FG_MAIN
            btn = tk.Button(quick_row, text=label, font=(self.theme.FONT_MAIN, 8),
                           bg=bg, fg=fg, relief=tk.FLAT, cursor="hand2", padx=4, pady=3, bd=0)
            btn.grid(row=idx // 4, column=idx % 4, padx=2, pady=2, sticky="ew")
            quick_btn_refs.append(btn)
            
            def on_quick_click(i=idx, ds=date_str):
                result[0] = ds
                # 更新快捷按钮样式
                for j, b in enumerate(quick_btn_refs):
                    b.config(bg=self.theme.BG_TAB_ACTIVE if j == i else self.theme.BG_TAB,
                             fg=self.theme.FG_WHITE if j == i else self.theme.FG_MAIN)
                # 如果目标日期不在当前月份，翻到那个月
                try:
                    target_d = date.fromisoformat(ds)
                    if target_d.year != view_year[0] or target_d.month != view_month[0]:
                        view_year[0] = target_d.year
                        view_month[0] = target_d.month
                        draw_calendar()
                    else:
                        update_cal_highlight(ds)
                except:
                    update_cal_highlight(ds)
            
            btn.config(command=on_quick_click)
        
        for c in range(4):
            quick_row.columnconfigure(c, weight=1)
        
        # === 日历选择 ===
        month_card = tk.Frame(dialog, bg=self.theme.BG_CARD, padx=15, pady=10)
        month_card.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(month_card, text="📆 日历选择", font=(self.theme.FONT_MAIN, 9, "bold"), 
                fg=self.theme.FG_MAIN, bg=self.theme.BG_CARD).pack(anchor="w", pady=(0, 5))
        
        # 月份导航
        nav_row = tk.Frame(month_card, bg=self.theme.BG_CARD)
        nav_row.pack(fill=tk.X, pady=2)
        
        try:
            current_dt = datetime.fromisoformat(self.current_view_date)
        except:
            current_dt = datetime.now()
        
        view_year = [current_dt.year]
        view_month = [current_dt.month]
        
        month_label_var = tk.StringVar()
        
        def update_month_label():
            month_label_var.set(f"{view_year[0]}年{view_month[0]:02d}月")
        
        update_month_label()
        
        prev_btn = self._make_cute_btn(nav_row, "◀", self.theme.BG_TAB, fg_color=self.theme.FG_MAIN,
                                       font_size=8, padx=6, pady=1)
        prev_btn.pack(side=tk.LEFT)
        
        tk.Label(nav_row, textvariable=month_label_var, font=(self.theme.FONT_MAIN, 10, "bold"), 
                fg=self.theme.FG_MAIN, bg=self.theme.BG_CARD, width=10).pack(side=tk.LEFT, expand=True)
        
        next_btn = self._make_cute_btn(nav_row, "▶", self.theme.BG_TAB, fg_color=self.theme.FG_MAIN,
                                       font_size=8, padx=6, pady=1)
        next_btn.pack(side=tk.RIGHT)
        
        # 日历网格
        cal_frame = tk.Frame(month_card, bg=self.theme.BG_CARD)
        cal_frame.pack(fill=tk.X, pady=5)
        
        # 星期标题
        for i, wd in enumerate(["一", "二", "三", "四", "五", "六", "日"]):
            fg = self.theme.FG_DATE if i < 5 else self.theme.BTN_DANGER
            tk.Label(cal_frame, text=wd, font=(self.theme.FONT_MAIN, 8), fg=fg, bg=self.theme.BG_CARD, width=3).grid(row=0, column=i, padx=1, pady=1)
        
        # 用字典存储 {日期字符串: 按钮} 方便快速查找更新
        cal_btn_map = {}
        
        def draw_calendar():
            # 清除旧的日期按钮
            for btn in cal_btn_map.values():
                btn.destroy()
            cal_btn_map.clear()
            
            y, m = view_year[0], view_month[0]
            update_month_label()
            
            import calendar
            first_weekday = calendar.monthrange(y, m)[0]
            days_in_month = calendar.monthrange(y, m)[1]
            
            row_idx = 1
            col_idx = first_weekday
            
            for day in range(1, days_in_month + 1):
                d = date(y, m, day)
                ds = d.isoformat()
                is_today = (d == today)
                is_selected = (ds == (result[0] or self.current_view_date))
                is_future = (d > today)
                
                if is_selected:
                    bg = self.theme.BG_TAB_ACTIVE
                    fg = self.theme.FG_WHITE
                elif is_today:
                    bg = self.theme.BTN_DELAY
                    fg = self.theme.FG_WHITE
                elif is_future:
                    bg = self.theme.BG_TAB
                    fg = self.theme.FG_LIGHT
                else:
                    bg = self.theme.BG_TAB
                    fg = self.theme.FG_MAIN
                
                btn = tk.Button(cal_frame, text=str(day), font=(self.theme.FONT_MAIN, 8),
                               bg=bg, fg=fg, relief=tk.FLAT, cursor="hand2", width=3, bd=0,
                               activebackground=self.theme.BG_TAB_ACTIVE, activeforeground=self.theme.FG_WHITE)
                btn.grid(row=row_idx, column=col_idx, padx=1, pady=1, sticky="ew")
                cal_btn_map[ds] = btn
                
                btn.config(command=lambda ds=ds: on_cal_click(ds))
                
                col_idx += 1
                if col_idx > 6:
                    col_idx = 0
                    row_idx += 1
        
        def on_cal_click(ds):
            result[0] = ds
            update_cal_highlight(ds)
            # 同步快捷按钮
            for j, b in enumerate(quick_btn_refs):
                _, qs, _ = quick_dates[j]
                if qs == ds:
                    b.config(bg=self.theme.BG_TAB_ACTIVE, fg=self.theme.FG_WHITE)
                else:
                    b.config(bg=self.theme.BG_TAB, fg=self.theme.FG_MAIN)
        
        def update_cal_highlight(selected_ds):
            """只更新颜色，不重建日历"""
            for ds, btn in cal_btn_map.items():
                try:
                    d = date.fromisoformat(ds)
                except:
                    continue
                is_today = (d == today)
                is_selected = (ds == selected_ds)
                
                if is_selected:
                    btn.config(bg=self.theme.BG_TAB_ACTIVE, fg=self.theme.FG_WHITE)
                elif is_today:
                    btn.config(bg=self.theme.BTN_DELAY, fg=self.theme.FG_WHITE)
                else:
                    btn.config(bg=self.theme.BG_TAB, fg=self.theme.FG_MAIN)
        
        def prev_month():
            view_month[0] -= 1
            if view_month[0] < 1:
                view_month[0] = 12
                view_year[0] -= 1
            draw_calendar()
        
        def next_month():
            view_month[0] += 1
            if view_month[0] > 12:
                view_month[0] = 1
                view_year[0] += 1
            draw_calendar()
        
        prev_btn.config(command=prev_month)
        next_btn.config(command=next_month)
        
        draw_calendar()
        
        # === 底部按钮 ===
        btn_frame = tk.Frame(dialog, bg=self.theme.BG_MAIN)
        btn_frame.pack(pady=10)
        
        def on_cancel():
            dialog.destroy()
        
        def on_confirm():
            if result[0]:
                self._switch_date(result[0])
            dialog.destroy()
        
        def on_today():
            result[0] = today.isoformat()
            self._switch_date(today.isoformat())
            dialog.destroy()
        
        self._make_cute_btn(btn_frame, "❌ 取消", self.theme.BTN_EXIT, hover_color=self.theme.BTN_EXIT_HOVER,
                           command=on_cancel, font_size=9, padx=12, pady=4).pack(side=tk.LEFT, padx=5)
        self._make_cute_btn(btn_frame, "📍 回到今天", self.theme.BTN_DELAY, hover_color=self.theme.BTN_DELAY_HOVER,
                           command=on_today, font_size=9, padx=12, pady=4).pack(side=tk.LEFT, padx=5)
        self._make_cute_btn(btn_frame, "✅ 确定~", self.theme.BTN_ADD, hover_color=self.theme.BTN_ADD_HOVER,
                           command=on_confirm, font_size=9, padx=12, pady=4).pack(side=tk.RIGHT, padx=5)
        
        dialog.grab_set()
        dialog.wait_window()
    
    def _change_week(self):
        """弹出周选择器"""
        result = [None]
        
        dialog = self._make_cute_dialog("📅 选择周", 400)
        
        tk.Label(dialog, text="📅", font=("Segoe UI Emoji", 32), bg=self.theme.BG_MAIN).pack(pady=(10, 2))
        tk.Label(dialog, text="选择查看哪一周~", font=(self.theme.FONT_MAIN, 12, "bold"), 
                fg=self.theme.FG_MAIN, bg=self.theme.BG_MAIN).pack(pady=(0, 8))
        
        # === 快捷周选择 ===
        quick_card = tk.Frame(dialog, bg=self.theme.BG_CARD, padx=15, pady=10)
        quick_card.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(quick_card, text="⚡ 快捷选择", font=(self.theme.FONT_MAIN, 9, "bold"), 
                fg=self.theme.FG_MAIN, bg=self.theme.BG_CARD).pack(anchor="w", pady=(0, 5))
        
        today = date.today()
        this_monday = self._get_monday(today)
        
        quick_weeks = [
            ("📍 本周", this_monday, True),
            ("上周", this_monday - timedelta(days=7), False),
            ("下周", this_monday + timedelta(days=7), False),
        ]
        
        quick_row = tk.Frame(quick_card, bg=self.theme.BG_CARD)
        quick_row.pack(fill=tk.X)
        
        quick_btn_refs = []
        for idx, (label, monday, is_default) in enumerate(quick_weeks):
            bg = self.theme.BG_TAB_ACTIVE if is_default else self.theme.BG_TAB
            fg = self.theme.FG_WHITE if is_default else self.theme.FG_MAIN
            sunday = monday + timedelta(days=6)
            full_label = f"{label}\n{monday.strftime('%m/%d')}~{sunday.strftime('%m/%d')}"
            btn = tk.Button(quick_row, text=full_label, font=(self.theme.FONT_MAIN, 8),
                           bg=bg, fg=fg, relief=tk.FLAT, cursor="hand2", padx=8, pady=4, bd=0)
            btn.pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
            quick_btn_refs.append(btn)
            
            def on_quick_click(m=monday, i=idx):
                result[0] = m
                for j, b in enumerate(quick_btn_refs):
                    b.config(bg=self.theme.BG_TAB_ACTIVE if j == i else self.theme.BG_TAB,
                             fg=self.theme.FG_WHITE if j == i else self.theme.FG_MAIN)
                view_year[0] = m.year
                view_month[0] = m.month
                update_month_label()
                draw_month_cal()
            
            btn.config(command=on_quick_click)
        
        # === 月份日历选择周 ===
        month_card = tk.Frame(dialog, bg=self.theme.BG_CARD, padx=15, pady=10)
        month_card.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(month_card, text="📆 按月份选择", font=(self.theme.FONT_MAIN, 9, "bold"), 
                fg=self.theme.FG_MAIN, bg=self.theme.BG_CARD).pack(anchor="w", pady=(0, 5))
        
        nav_row = tk.Frame(month_card, bg=self.theme.BG_CARD)
        nav_row.pack(fill=tk.X, pady=2)
        
        view_year = [this_monday.year]
        view_month = [this_monday.month]
        
        month_label_var = tk.StringVar()
        
        def update_month_label():
            month_label_var.set(f"{view_year[0]}年{view_month[0]:02d}月")
        
        update_month_label()
        
        prev_btn = self._make_cute_btn(nav_row, "◀", self.theme.BG_TAB, fg_color=self.theme.FG_MAIN,
                                       font_size=8, padx=6, pady=1)
        prev_btn.pack(side=tk.LEFT)
        
        tk.Label(nav_row, textvariable=month_label_var, font=(self.theme.FONT_MAIN, 10, "bold"), 
                fg=self.theme.FG_MAIN, bg=self.theme.BG_CARD, width=10).pack(side=tk.LEFT, expand=True)
        
        next_btn = self._make_cute_btn(nav_row, "▶", self.theme.BG_TAB, fg_color=self.theme.FG_MAIN,
                                       font_size=8, padx=6, pady=1)
        next_btn.pack(side=tk.RIGHT)
        
        week_list_frame = tk.Frame(month_card, bg=self.theme.BG_CARD)
        week_list_frame.pack(fill=tk.X, pady=5)
        
        week_btn_refs = []
        week_row_refs = []  # 同时追踪 row_frame，以便清理

        def draw_month_cal():
            for b in week_btn_refs:
                b.destroy()
            week_btn_refs.clear()
            for r in week_row_refs:
                r.destroy()
            week_row_refs.clear()

            update_month_label()

            import calendar
            y, m = view_year[0], view_month[0]
            first_day = date(y, m, 1)
            days_in_month = calendar.monthrange(y, m)[1]

            current_monday = self._get_monday(first_day)
            if current_monday < first_day:
                current_monday = current_monday + timedelta(days=7)

            last_day = date(y, m, days_in_month)

            while current_monday <= last_day:
                sunday = current_monday + timedelta(days=6)
                display_start = max(current_monday, first_day)
                display_end = min(sunday, last_day)

                is_current = (current_monday == this_monday)
                is_selected = (result[0] is not None and current_monday == result[0])

                bg = self.theme.BG_TAB_ACTIVE if (is_selected or is_current) else self.theme.BG_TAB
                fg = self.theme.FG_WHITE if (is_selected or is_current) else self.theme.FG_MAIN

                label = f"{display_start.strftime('%m/%d')} ~ {display_end.strftime('%m/%d')}"

                row_frame = tk.Frame(week_list_frame, bg=self.theme.BG_CARD)
                row_frame.pack(fill=tk.X, pady=1)
                week_row_refs.append(row_frame)

                btn = tk.Button(row_frame, text=label, font=(self.theme.FONT_MAIN, 9),
                               bg=bg, fg=fg, relief=tk.FLAT, cursor="hand2", padx=10, pady=3, bd=0,
                               activebackground=self.theme.BG_TAB_ACTIVE, activeforeground=self.theme.FG_WHITE)
                btn.pack(fill=tk.X, expand=True)
                week_btn_refs.append(btn)

                btn.config(command=lambda m=current_monday: on_week_click(m))

                current_monday = current_monday + timedelta(days=7)
        
        def on_week_click(monday):
            result[0] = monday
            for j, (_, qm, _) in enumerate(quick_weeks):
                b = quick_btn_refs[j]
                if qm == monday:
                    b.config(bg=self.theme.BG_TAB_ACTIVE, fg=self.theme.FG_WHITE)
                else:
                    b.config(bg=self.theme.BG_TAB, fg=self.theme.FG_MAIN)
            draw_month_cal()
        
        def prev_month():
            view_month[0] -= 1
            if view_month[0] < 1:
                view_month[0] = 12
                view_year[0] -= 1
            draw_month_cal()
        
        def next_month():
            view_month[0] += 1
            if view_month[0] > 12:
                view_month[0] = 1
                view_year[0] += 1
            draw_month_cal()
        
        prev_btn.config(command=prev_month)
        next_btn.config(command=next_month)
        
        draw_month_cal()
        
        # === 底部按钮 ===
        btn_frame = tk.Frame(dialog, bg=self.theme.BG_MAIN)
        btn_frame.pack(pady=10)
        
        def on_cancel():
            dialog.destroy()
        
        def on_confirm():
            if result[0]:
                self._switch_week(result[0])
            dialog.destroy()
        
        def on_this_week():
            self._switch_week(this_monday)
            dialog.destroy()
        
        self._make_cute_btn(btn_frame, "❌ 取消", self.theme.BTN_EXIT, hover_color=self.theme.BTN_EXIT_HOVER,
                           command=on_cancel, font_size=9, padx=12, pady=4).pack(side=tk.LEFT, padx=5)
        self._make_cute_btn(btn_frame, "📍 本周", self.theme.BTN_DELAY, hover_color=self.theme.BTN_DELAY_HOVER,
                           command=on_this_week, font_size=9, padx=12, pady=4).pack(side=tk.LEFT, padx=5)
        self._make_cute_btn(btn_frame, "✅ 确定~", self.theme.BTN_ADD, hover_color=self.theme.BTN_ADD_HOVER,
                           command=on_confirm, font_size=9, padx=12, pady=4).pack(side=tk.RIGHT, padx=5)
        
        dialog.grab_set()
        dialog.wait_window()
    
    # ==================== UI 更新 ====================
    
    def update_input_ui_for_tab(self):
        current_tab = self.selected_tab.get()
        if current_tab == "🗑️ 回收站":
            if self.task_entry.winfo_ismapped():
                self.task_entry.pack_forget()
            if self.add_btn.winfo_ismapped():
                self.add_btn.pack_forget()
            if not self.clear_trash_btn.winfo_ismapped():
                self.clear_trash_btn.pack(side=tk.RIGHT)
        else:
            if not self.task_entry.winfo_ismapped():
                self.task_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=5)
            if not self.add_btn.winfo_ismapped():
                self.add_btn.pack(side=tk.RIGHT)
            if self.clear_trash_btn.winfo_ismapped():
                self.clear_trash_btn.pack_forget()
    
    def clear_trash(self):
        if not self.tasks.get("trash"):
            self._cute_messagebox("提示", "回收站已经是空的了~ 🌸", "info")
            return
        if self._cute_confirm("确认清空", f"确定要清空 {self.current_view_date} 的回收站吗？\n此操作不可恢复哦~ 💫"):
            self.tasks["trash"] = []
            self._save_tasks()
            self.update_display()
            self._cute_messagebox("成功", "回收站已清空~ ✨", "success")
    
    # ==================== 任务操作 ====================
    
    def add_task(self):
        task_text = self.task_entry.get().strip()
        if not task_text or task_text == self.task_entry_placeholder:
            return
        
        category = self.selected_tab.get()
        if category == "🗑️ 回收站":
            category = "🔄 进行中"
        
        key = self._get_key(category)
        
        remind_at = None
        if key == "upcoming":
            remind_at = self._ask_remind_time()
            if remind_at is None:
                return
        
        task = {
            "id": int(time.time() * 1000),
            "text": task_text,
            "timestamp": datetime.now().isoformat(),
            "date": self.current_view_date,
            "completed": False,
            "from_key": key,
            "remind_at": remind_at
        }
        
        self.tasks[key].append(task)
        self._save_tasks()
        self.task_entry.delete(0, tk.END)
        self.update_display()
    
    def _ask_remind_time(self, current_remind_at=None):
        """弹出可爱风格的日期时间选择器"""
        # 计算默认值
        if current_remind_at:
            try:
                default_dt = datetime.fromisoformat(current_remind_at)
            except:
                default_dt = datetime.now() + timedelta(hours=1)
        else:
            default_dt = datetime.now() + timedelta(hours=1)
        
        result = [None]  # 用列表存放结果，方便在闭包中修改
        
        dialog = self._make_cute_dialog("⏰ 设置提醒时间", 400)
        
        # 标题
        tk.Label(dialog, text="⏰", font=("Segoe UI Emoji", 32), bg=self.theme.BG_MAIN).pack(pady=(10, 2))
        tk.Label(dialog, text="选择提醒时间~", font=(self.theme.FONT_MAIN, 12, "bold"), 
                fg=self.theme.FG_MAIN, bg=self.theme.BG_MAIN).pack(pady=(0, 10))
        
        # === 日期选择区 ===
        date_card = tk.Frame(dialog, bg=self.theme.BG_CARD, padx=15, pady=10)
        date_card.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(date_card, text="📅 日期", font=(self.theme.FONT_MAIN, 10, "bold"), 
                fg=self.theme.FG_MAIN, bg=self.theme.BG_CARD).pack(anchor="w")
        
        date_row = tk.Frame(date_card, bg=self.theme.BG_CARD)
        date_row.pack(fill=tk.X, pady=5)
        
        # 生成未来7天的日期选项
        today = date.today()
        date_options = []
        date_values = []
        for d in range(0, 8):
            target_date = today + timedelta(days=d)
            weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
            weekday = weekday_names[target_date.weekday()]
            if d == 0:
                label = f"今天 {target_date.strftime('%m/%d')} {weekday}"
            elif d == 1:
                label = f"明天 {target_date.strftime('%m/%d')} {weekday}"
            elif d == 2:
                label = f"后天 {target_date.strftime('%m/%d')} {weekday}"
            else:
                label = f"{target_date.strftime('%m/%d')} {weekday}"
            date_options.append(label)
            date_values.append(target_date)
        
        # 找到默认日期对应的索引
        default_date_idx = 0
        for idx, dv in enumerate(date_values):
            if dv == default_dt.date():
                default_date_idx = idx
                break
        
        selected_date_idx = [default_date_idx]
        
        date_btn_frame = tk.Frame(date_row, bg=self.theme.BG_CARD)
        date_btn_frame.pack(fill=tk.X)
        
        date_btn_refs = []
        for idx, label in enumerate(date_options):
            is_selected = (idx == default_date_idx)
            bg = self.theme.BG_TAB_ACTIVE if is_selected else self.theme.BG_TAB
            fg = self.theme.FG_WHITE if is_selected else self.theme.FG_MAIN
            
            btn = tk.Button(date_btn_frame, text=label, font=(self.theme.FONT_MAIN, 8),
                           bg=bg, fg=fg, relief=tk.FLAT, cursor="hand2", padx=4, pady=3, bd=0)
            btn.grid(row=idx // 4, column=idx % 4, padx=2, pady=2, sticky="ew")
            date_btn_refs.append(btn)
            
            def on_date_click(i=idx):
                selected_date_idx[0] = i
                # 更新按钮样式
                for j, b in enumerate(date_btn_refs):
                    if j == i:
                        b.config(bg=self.theme.BG_TAB_ACTIVE, fg=self.theme.FG_WHITE)
                    else:
                        b.config(bg=self.theme.BG_TAB, fg=self.theme.FG_MAIN)
            
            btn.config(command=on_date_click)
        
        for c in range(4):
            date_btn_frame.columnconfigure(c, weight=1)
        
        # === 时间选择区 ===
        time_card = tk.Frame(dialog, bg=self.theme.BG_CARD, padx=15, pady=10)
        time_card.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(time_card, text="🕐 时间", font=(self.theme.FONT_MAIN, 10, "bold"), 
                fg=self.theme.FG_MAIN, bg=self.theme.BG_CARD).pack(anchor="w")
        
        time_row = tk.Frame(time_card, bg=self.theme.BG_CARD)
        time_row.pack(fill=tk.X, pady=5)
        
        # 小时选择
        tk.Label(time_row, text="时", font=(self.theme.FONT_MAIN, 9), fg=self.theme.FG_LIGHT, bg=self.theme.BG_CARD).pack(side=tk.LEFT, padx=(0, 2))
        
        hour_var = tk.StringVar(value=str(default_dt.hour).zfill(2))
        hour_spin = tk.Spinbox(time_row, from_=0, to=23, wrap=True, textvariable=hour_var, width=3,
                              font=(self.theme.FONT_MONO, 12, "bold"), bg=self.theme.BG_INPUT, fg=self.theme.FG_MAIN,
                              relief=tk.FLAT, buttonbackground=self.theme.BG_TAB, justify="center",
                              highlightthickness=1, highlightcolor=self.theme.BG_TAB_ACTIVE,
                              highlightbackground=self.theme.BG_TAB)
        hour_spin.pack(side=tk.LEFT, padx=2)
        hour_spin.config(format="%02.0f")
        
        tk.Label(time_row, text="：", font=(self.theme.FONT_MAIN, 14, "bold"), fg=self.theme.FG_MAIN, bg=self.theme.BG_CARD).pack(side=tk.LEFT, padx=4)
        
        # 分钟选择
        tk.Label(time_row, text="分", font=(self.theme.FONT_MAIN, 9), fg=self.theme.FG_LIGHT, bg=self.theme.BG_CARD).pack(side=tk.LEFT, padx=(0, 2))
        
        minute_var = tk.StringVar(value=str(default_dt.minute).zfill(2))
        minute_spin = tk.Spinbox(time_row, from_=0, to=59, increment=5, wrap=True, textvariable=minute_var, width=3,
                                font=(self.theme.FONT_MONO, 12, "bold"), bg=self.theme.BG_INPUT, fg=self.theme.FG_MAIN,
                                relief=tk.FLAT, buttonbackground=self.theme.BG_TAB, justify="center",
                                highlightthickness=1, highlightcolor=self.theme.BG_TAB_ACTIVE,
                                highlightbackground=self.theme.BG_TAB)
        minute_spin.pack(side=tk.LEFT, padx=2)
        minute_spin.config(format="%02.0f")
        
        # 快捷时间按钮
        quick_row = tk.Frame(time_card, bg=self.theme.BG_CARD)
        quick_row.pack(fill=tk.X, pady=(8, 0))
        
        tk.Label(quick_row, text="⚡ 快捷：", font=(self.theme.FONT_MAIN, 8), fg=self.theme.FG_LIGHT, bg=self.theme.BG_CARD).pack(side=tk.LEFT)
        
        quick_times = [("1小时后", 1), ("2小时后", 2), ("明天上午9点", 9, True), ("明天下午2点", 14, True)]
        
        def set_quick_time(hours=None, target_hour=None, is_tomorrow=False):
            if target_hour is not None:
                # 特定时间点
                if is_tomorrow:
                    selected_date_idx[0] = 1  # 明天
                hour_var.set(str(target_hour).zfill(2))
                minute_var.set("00")
                # 更新日期按钮样式
                for j, b in enumerate(date_btn_refs):
                    if j == selected_date_idx[0]:
                        b.config(bg=self.theme.BG_TAB_ACTIVE, fg=self.theme.FG_WHITE)
                    else:
                        b.config(bg=self.theme.BG_TAB, fg=self.theme.FG_MAIN)
            else:
                # N小时后
                future = datetime.now() + timedelta(hours=hours)
                # 找到对应日期
                for idx, dv in enumerate(date_values):
                    if dv == future.date():
                        selected_date_idx[0] = idx
                        break
                hour_var.set(str(future.hour).zfill(2))
                minute_var.set(str(future.minute).zfill(2))
                # 更新日期按钮样式
                for j, b in enumerate(date_btn_refs):
                    if j == selected_date_idx[0]:
                        b.config(bg=self.theme.BG_TAB_ACTIVE, fg=self.theme.FG_WHITE)
                    else:
                        b.config(bg=self.theme.BG_TAB, fg=self.theme.FG_MAIN)
        
        for qt in quick_times:
            if len(qt) == 2:
                text, hours = qt
                self._make_cute_btn(quick_row, text, self.theme.BG_TAB, fg_color=self.theme.FG_MAIN,
                                   command=lambda h=hours: set_quick_time(hours=h), font_size=7, padx=5, pady=1).pack(side=tk.LEFT, padx=2)
            else:
                text, hour, _ = qt
                self._make_cute_btn(quick_row, text, self.theme.BG_TAB, fg_color=self.theme.FG_MAIN,
                                   command=lambda h=hour: set_quick_time(target_hour=h, is_tomorrow=True), font_size=7, padx=5, pady=1).pack(side=tk.LEFT, padx=2)
        
        # === 预览区 ===
        preview_var = tk.StringVar()
        preview_label = tk.Label(dialog, textvariable=preview_var, font=(self.theme.FONT_MAIN, 9), 
                                fg=self.theme.FG_DATE, bg=self.theme.BG_MAIN)
        preview_label.pack(pady=5)
        
        def update_preview(*args):
            try:
                d_idx = selected_date_idx[0]
                h = int(hour_var.get())
                m = int(minute_var.get())
                if 0 <= h <= 23 and 0 <= m <= 59 and 0 <= d_idx < len(date_values):
                    sel_date = date_values[d_idx]
                    preview_var.set(f"📋 将在 {sel_date.strftime('%Y年%m月%d日')} {h:02d}:{m:02d} 提醒你~")
            except:
                preview_var.set("")
        
        hour_var.trace_add("write", update_preview)
        minute_var.trace_add("write", update_preview)
        update_preview()
        
        # === 底部按钮 ===
        btn_frame = tk.Frame(dialog, bg=self.theme.BG_MAIN)
        btn_frame.pack(pady=10)
        
        def on_confirm():
            try:
                d_idx = selected_date_idx[0]
                h = int(hour_var.get())
                m = int(minute_var.get())
                if not (0 <= h <= 23 and 0 <= m <= 59):
                    self._cute_messagebox("错误", "时间范围不正确哦~ 💫", "error")
                    return
                sel_date = date_values[d_idx]
                selected_dt = datetime(sel_date.year, sel_date.month, sel_date.day, h, m)
                if selected_dt < datetime.now():
                    self._cute_messagebox("错误", "提醒时间不能早于当前时间哦~ ⏰", "error")
                    return
                result[0] = selected_dt.isoformat()
                dialog.destroy()
            except:
                self._cute_messagebox("错误", "请选择有效的时间~ 💫", "error")
        
        def on_cancel():
            dialog.destroy()
        
        self._make_cute_btn(btn_frame, "❌ 取消", self.theme.BTN_EXIT, hover_color=self.theme.BTN_EXIT_HOVER,
                           command=on_cancel, font_size=10, padx=15, pady=5).pack(side=tk.LEFT, padx=10)
        self._make_cute_btn(btn_frame, "✅ 确定~", self.theme.BTN_ADD, hover_color=self.theme.BTN_ADD_HOVER,
                           command=on_confirm, font_size=10, padx=15, pady=5).pack(side=tk.RIGHT, padx=10)
        
        dialog.grab_set()
        dialog.wait_window()
        return result[0]
    
    def _parse_remind_time(self, time_str):
        try:
            return datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        except ValueError:
            pass
        try:
            t = datetime.strptime(time_str, "%H:%M")
            return t.replace(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)
        except ValueError:
            return None
    
    def _get_key(self, name):
        m = {"✅ 已完成": "completed", "🔄 进行中": "in_progress", "📅 即将做": "upcoming", "🗑️ 回收站": "trash"}
        return m.get(name, "in_progress")
    
    def _find_task_index(self, key, task_id):
        for i, t in enumerate(self.tasks.get(key, [])):
            if t.get("id") == task_id:
                return i
        return -1
    
    def update_display(self):
        self.task_container.update_idletasks()
        for widget in self.task_container.winfo_children():
            widget.destroy()
            
        if self.view_mode == "week":
            self._update_week_display()
            return
            
        key = self._get_key(self.selected_tab.get())
        tasks = self.tasks.get(key, [])
        
        if key == "upcoming":
            tasks = sorted(tasks, key=lambda x: x.get("remind_at", "9999"))
        
        if not tasks:
            # 空状态提示
            empty_icons = {"completed": "🎉", "in_progress": "💪", "upcoming": "📅", "trash": "🗑️"}
            empty_texts = {"completed": "还没有完成的任务哦~", "in_progress": "当前没有进行中的任务~", 
                          "upcoming": "没有待办任务~", "trash": "回收站是空的~"}
            tk.Label(self.task_container, text=empty_icons.get(key, "🌸"), font=("Segoe UI Emoji", 32), 
                    bg=self.theme.BG_MAIN).pack(pady=(30, 5))
            tk.Label(self.task_container, text=empty_texts.get(key, "暂无任务~"), font=(self.theme.FONT_MAIN, 10), 
                    fg=self.theme.FG_LIGHT, bg=self.theme.BG_MAIN).pack()
            return
        
        for i, task in enumerate(tasks):
            # 任务卡片
            row_bg = self.theme.BG_TASK_ROW if i % 2 == 0 else self.theme.BG_TASK_ROW_ALT
            row = tk.Frame(self.task_container, bg=row_bg, pady=6, padx=12)
            row.pack(fill=tk.X, padx=6, pady=2)
            
            # 悬停效果
            def on_enter(event, r=row, bg=row_bg):
                r.config(bg=self.theme.BG_TASK_HOVER)
                for child in r.winfo_children():
                    try:
                        child.config(bg=self.theme.BG_TASK_HOVER)
                    except:
                        pass
            def on_leave(event, r=row, bg=row_bg):
                r.config(bg=bg)
                for child in r.winfo_children():
                    try:
                        child.config(bg=bg)
                    except:
                        pass
            row.bind("<Enter>", on_enter)
            row.bind("<Leave>", on_leave)
            
            task_id = task.get("id", 0)
            
            # 1. 勾选按钮
            check_frame = tk.Frame(row, width=26, height=26, bg=row_bg)
            check_frame.pack(side=tk.LEFT, padx=(0, 6))
            check_frame.pack_propagate(False)
            
            if key == "completed":
                canvas = tk.Canvas(check_frame, width=26, height=26, bg=self.theme.CHECK_BG, highlightthickness=0, cursor="hand2")
                canvas.pack()
                canvas.create_line(5, 13, 10, 19, fill="white", width=2, capstyle=tk.ROUND)
                canvas.create_line(10, 19, 21, 7, fill="white", width=2, capstyle=tk.ROUND)
                canvas.bind("<Button-1>", lambda e, tid=task_id: self.unmark_complete(tid))
            elif key == "trash":
                canvas = tk.Canvas(check_frame, width=26, height=26, bg=row_bg, highlightthickness=0, cursor="hand2")
                canvas.pack()
                canvas.create_text(13, 13, text="↩️", font=("Segoe UI Emoji", 10))
                canvas.bind("<Button-1>", lambda e, tid=task_id: self.restore_from_trash(tid))
            else:
                canvas = tk.Canvas(check_frame, width=26, height=26, bg=row_bg, highlightthickness=0, cursor="hand2")
                canvas.pack()
                canvas.create_oval(4, 4, 22, 22, outline=self.theme.CHECK_OUTLINE, width=2)
                if key == "upcoming":
                    canvas.bind("<Button-1>", lambda e, tid=task_id: self.ask_start_task(tid))
                else:
                    canvas.bind("<Button-1>", lambda e, tid=task_id, k=key: self.mark_complete(tid, k))
            
            # 1.5 闹钟图标
            if task.get("remind_at"):
                try:
                    rt = datetime.fromisoformat(task["remind_at"])
                    if key == "upcoming":
                        time_str = rt.strftime("%m-%d %H:%M")
                        alarm_text = f"⏰{time_str}"
                    else:
                        alarm_text = "⏰"
                    
                    alarm_lbl = tk.Label(row, text=alarm_text, font=(self.theme.FONT_MAIN, 8), 
                                        fg=self.theme.FG_ALARM, bg=row_bg, cursor="hand2")
                    alarm_lbl.pack(side=tk.LEFT, padx=(0, 4))
                    alarm_lbl.bind("<Button-1>", lambda e, tid=task_id, k=key: self.reschedule_task(tid, k))
                    alarm_lbl.bind("<Enter>", lambda e, l=alarm_lbl: l.config(font=(self.theme.FONT_MAIN, 8, "bold")))
                    alarm_lbl.bind("<Leave>", lambda e, l=alarm_lbl: l.config(font=(self.theme.FONT_MAIN, 8)))
                except:
                    pass
            
            # 2. 删除按钮（先 pack 右侧，确保不被挤掉）
            del_btn = tk.Label(row, text="✕", font=("Arial", 10), bg=row_bg, fg=self.theme.FG_DELETE, cursor="hand2")
            del_btn.pack(side=tk.RIGHT, padx=(8, 0))
            del_btn.bind("<Button-1>", lambda e, tid=task_id, k=key: self.move_to_trash(tid, k))
            del_btn.bind("<Enter>", lambda e, l=del_btn: l.config(fg="#FF0000", font=("Arial", 11, "bold")))
            del_btn.bind("<Leave>", lambda e, l=del_btn: l.config(fg=self.theme.FG_DELETE, font=("Arial", 10)))
            
            # 3. 任务文本 (Label 显示换行，单击切换 Entry 可选中复制，失焦切回 Label)
            task_text = task['text']
            text_frame = tk.Frame(row, bg=row_bg)
            text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))
            
            # Label 模式：正常显示，支持换行
            task_label = tk.Label(text_frame, text=task_text, font=(self.theme.FONT_MAIN, 9), 
                                 fg=self.theme.FG_MAIN, bg=row_bg, anchor="w", justify="left", 
                                 wraplength=180, cursor="hand2")
            task_label.pack(fill=tk.X, expand=True)
            
            # Entry 模式：隐藏，单击时切换出来，支持选中高亮复制
            task_entry = tk.Entry(text_frame, font=(self.theme.FONT_MAIN, 9), 
                                 fg=self.theme.FG_MAIN, bg=row_bg, relief=tk.FLAT,
                                 readonlybackground=row_bg, selectbackground=self.theme.BG_TAB_ACTIVE,
                                 selectforeground=self.theme.FG_WHITE, highlightthickness=0, bd=0)
            task_entry.insert(0, task_text)
            task_entry.config(state="readonly")
            
            def switch_to_entry(event, l=task_label, e=task_entry, f=text_frame, bg=row_bg):
                """单击切换到 Entry 模式，可选中复制"""
                l.pack_forget()
                e.pack(fill=tk.X, expand=True)
                e.config(state="normal")
                e.focus_set()
                e.select_range(0, tk.END)
                e.config(state="readonly")
            
            def switch_to_label(event, l=task_label, e=task_entry, f=text_frame, bg=row_bg):
                """失焦切回 Label 模式，显示换行"""
                e.pack_forget()
                e.config(state="normal")
                e.select_range(0, tk.END)
                e.config(state="readonly")
                l.pack(fill=tk.X, expand=True)
            
            task_label.bind("<Button-1>", switch_to_entry)
            task_entry.bind("<FocusOut>", switch_to_label)
            task_entry.bind("<Escape>", switch_to_label)
            
            # 悬停时同步背景色
            task_label.bind("<Enter>", lambda e, l=task_label, r=row, bg=row_bg: (
                l.config(bg=self.theme.BG_TASK_HOVER), r.config(bg=self.theme.BG_TASK_HOVER)))
            task_label.bind("<Leave>", lambda e, l=task_label, r=row, bg=row_bg: (
                l.config(bg=bg), r.config(bg=bg)))
            task_entry.bind("<Enter>", lambda e, r=row: r.config(bg=self.theme.BG_TASK_HOVER))
            task_entry.bind("<Leave>", lambda e, r=row, bg=row_bg: r.config(bg=bg))
            
            # 右键复制菜单
            def show_copy_menu(event, text=task_text):
                menu = tk.Menu(task_label, tearoff=0, bg=self.theme.BG_CARD, fg=self.theme.FG_MAIN,
                              activebackground=self.theme.BG_TAB_ACTIVE, activeforeground=self.theme.FG_WHITE)
                menu.add_command(label="📋 复制内容", command=lambda: (self.root.clipboard_clear(), self.root.clipboard_append(text)))
                menu.post(event.x_root, event.y_root)
            task_label.bind("<Button-3>", show_copy_menu)
            task_entry.bind("<Button-3>", show_copy_menu)
        
        self.task_container.event_generate("<Configure>")
    
    def mark_complete(self, task_id, from_key):
        idx = self._find_task_index(from_key, task_id)
        if idx == -1: return
        task = self.tasks[from_key].pop(idx)
        task["completed"] = True
        task["from_key"] = from_key
        self.tasks["completed"].append(task)
        self._save_tasks()
        self.update_display()
    
    def ask_start_task(self, task_id):
        idx = self._find_task_index("upcoming", task_id)
        if idx == -1: return
        
        task = self.tasks["upcoming"][idx]
        
        dialog = self._make_cute_dialog("⏰ 开始任务", 420, 260)
        
        tk.Label(dialog, text="🤔", font=("Segoe UI Emoji", 32), bg=self.theme.BG_MAIN).pack(pady=(15, 5))
        tk.Label(dialog, text="是否立即开始这个任务呢？", font=(self.theme.FONT_MAIN, 12, "bold"), 
                fg=self.theme.FG_MAIN, bg=self.theme.BG_MAIN).pack()
        
        content_card = tk.Frame(dialog, bg=self.theme.BG_CARD, padx=15, pady=8)
        content_card.pack(fill=tk.X, padx=30, pady=10)
        tk.Label(content_card, text=f"📝 {task['text']}", font=(self.theme.FONT_MAIN, 10), 
                fg=self.theme.FG_MAIN, bg=self.theme.BG_CARD, wraplength=320).pack()
        
        btn_frame = tk.Frame(dialog, bg=self.theme.BG_MAIN)
        btn_frame.pack(pady=10)
        
        def on_yes():
            task = self.tasks["upcoming"].pop(idx)
            task["from_key"] = "in_progress"
            self.tasks["in_progress"].append(task)
            self._save_tasks()
            self.update_display()
            dialog.destroy()
        
        def on_no():
            dialog.destroy()
        
        self._make_cute_btn(btn_frame, "❌ 再等等", self.theme.BTN_EXIT, hover_color=self.theme.BTN_EXIT_HOVER, 
                           command=on_no, font_size=10, padx=15, pady=5).pack(side=tk.LEFT, padx=10)
        self._make_cute_btn(btn_frame, "✅ 开始吧~", self.theme.BTN_START, hover_color=self.theme.BTN_START_HOVER, 
                           command=on_yes, font_size=10, padx=15, pady=5).pack(side=tk.RIGHT, padx=10)
    
    def reschedule_task(self, task_id, from_key):
        idx = self._find_task_index(from_key, task_id)
        if idx == -1: return
        
        task = self.tasks[from_key][idx]
        current_remind_at = task.get("remind_at")
        new_time_str = self._ask_remind_time(current_remind_at)
        if not new_time_str:
            return
        
        try:
            new_time = datetime.fromisoformat(new_time_str)
        except:
            return
            
        now = datetime.now()
        
        if new_time > now and from_key != "upcoming":
            task = self.tasks[from_key].pop(idx)
            task["remind_at"] = new_time_str
            task["from_key"] = "upcoming"
            self.tasks["upcoming"].append(task)
            self._cute_messagebox("已推迟", f"任务已回到【即将做】~\n提醒时间：{new_time.strftime('%Y-%m-%d %H:%M')} 🕐", "info")
        else:
            task["remind_at"] = new_time_str
            status_msg = "未来" if new_time > now else "过去"
            self._cute_messagebox("已更新", f"提醒时间已更新为{status_msg}时间：\n{new_time.strftime('%Y-%m-%d %H:%M')} ✨", "success")
        
        self._save_tasks()
        self.update_display()
    
    def unmark_complete(self, task_id):
        idx = self._find_task_index("completed", task_id)
        if idx == -1: return
        task = self.tasks["completed"].pop(idx)
        task["completed"] = False
        from_key = task.get("from_key", "in_progress")
        if from_key not in self.tasks:
            from_key = "in_progress"
        self.tasks[from_key].append(task)
        self._save_tasks()
        self.update_display()
    
    def move_to_trash(self, task_id, from_key):
        idx = self._find_task_index(from_key, task_id)
        if idx == -1: return
        if from_key == "trash":
            if self._cute_confirm("确认删除", "确定要永久删除此任务吗？\n此操作不可恢复哦~ 💫"):
                self.tasks["trash"].pop(idx)
        else:
            task = self.tasks[from_key].pop(idx)
            task["deleted_from"] = from_key
            self.tasks["trash"].append(task)
        self._save_tasks()
        self.update_display()
    
    def restore_from_trash(self, task_id):
        idx = self._find_task_index("trash", task_id)
        if idx == -1: return
        task = self.tasks["trash"].pop(idx)
        task["completed"] = False
        restore_key = task.get("deleted_from", "in_progress")
        if restore_key == "completed":
            restore_key = "in_progress"
        if restore_key not in self.tasks:
            restore_key = "in_progress"
        self.tasks[restore_key].append(task)
        self._save_tasks()
        self.update_display()
    
    def _update_week_display(self):
        """按周视图显示"""
        weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        
        try:
            monday = date.fromisoformat(self.week_start_date)
        except:
            monday = self._get_monday(date.today())
        
        week_days = self._get_week_range(monday)
        today = date.today()
        has_any_task = False
        
        for i, d in enumerate(week_days):
            ds = d.isoformat()
            day_tasks = self.week_tasks_cache.get(ds, {"completed": [], "in_progress": [], "upcoming": [], "trash": []})
            completed = day_tasks.get("completed", [])
            in_progress = day_tasks.get("in_progress", [])
            upcoming = day_tasks.get("upcoming", [])
            
            all_tasks = completed + in_progress + upcoming
            if not all_tasks:
                continue
            has_any_task = True
            
            is_today = (d == today)
            is_weekend = (d.weekday() >= 5)
            day_bg = self.theme.BG_TAB_ACTIVE if is_today else (self.theme.BG_TASK_HOVER if is_weekend else self.theme.BG_CARD)
            day_fg = self.theme.FG_WHITE if is_today else self.theme.FG_MAIN
            
            day_header = tk.Frame(self.task_container, bg=day_bg, pady=4, padx=10)
            day_header.pack(fill=tk.X, padx=6, pady=(8, 2))
            
            day_label_text = f"📅 {d.strftime('%m/%d')} {weekday_names[i]}"
            if is_today:
                day_label_text += " 📍"
            day_count = f"✅{len(completed)} 🔄{len(in_progress)} 📅{len(upcoming)}"
            
            tk.Label(day_header, text=day_label_text, font=(self.theme.FONT_MAIN, 10, "bold"),
                    fg=day_fg, bg=day_bg).pack(side=tk.LEFT)
            tk.Label(day_header, text=day_count, font=(self.theme.FONT_MONO, 9),
                    fg=day_fg, bg=day_bg).pack(side=tk.RIGHT)
            
            for task in completed:
                row = tk.Frame(self.task_container, bg=self.theme.BG_TASK_ROW, pady=3, padx=16)
                row.pack(fill=tk.X, padx=6)
                tk.Label(row, text="✅", font=("Segoe UI Emoji", 9), bg=self.theme.BG_TASK_ROW).pack(side=tk.LEFT)
                tk.Label(row, text=task.get("text", ""), font=(self.theme.FONT_MAIN, 9),
                        fg=self.theme.FG_LIGHT, bg=self.theme.BG_TASK_ROW, anchor="w", wraplength=280).pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            for task in in_progress:
                row = tk.Frame(self.task_container, bg=self.theme.BG_TASK_ROW_ALT, pady=3, padx=16)
                row.pack(fill=tk.X, padx=6)
                tk.Label(row, text="🔄", font=("Segoe UI Emoji", 9), bg=self.theme.BG_TASK_ROW_ALT).pack(side=tk.LEFT)
                tk.Label(row, text=task.get("text", ""), font=(self.theme.FONT_MAIN, 9),
                        fg=self.theme.FG_MAIN, bg=self.theme.BG_TASK_ROW_ALT, anchor="w", wraplength=280).pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            for task in upcoming:
                row = tk.Frame(self.task_container, bg=self.theme.BG_TASK_ROW, pady=3, padx=16)
                row.pack(fill=tk.X, padx=6)
                tk.Label(row, text="📅", font=("Segoe UI Emoji", 9), bg=self.theme.BG_TASK_ROW).pack(side=tk.LEFT)
                tk.Label(row, text=task.get("text", ""), font=(self.theme.FONT_MAIN, 9),
                        fg=self.theme.FG_LIGHT, bg=self.theme.BG_TASK_ROW, anchor="w", wraplength=280).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        if not has_any_task:
            # 根据当前选中的tab显示不同的空状态图标，与天视图保持一致
            key = self._get_key(self.selected_tab.get())
            empty_icons = {"completed": "🎉", "in_progress": "💪", "upcoming": "📅", "trash": "🗑️"}
            empty_texts = {"completed": "本周还没有完成的任务哦~", "in_progress": "本周没有进行中的任务~",
                          "upcoming": "本周没有待办任务~", "trash": "本周回收站是空的~"}
            tk.Label(self.task_container, text=empty_icons.get(key, "💪"), font=("Segoe UI Emoji", 32),
                    bg=self.theme.BG_MAIN).pack(pady=(30, 5))
            tk.Label(self.task_container, text=empty_texts.get(key, "本周暂无任务记录~"), font=(self.theme.FONT_MAIN, 10),
                    fg=self.theme.FG_LIGHT, bg=self.theme.BG_MAIN).pack()
        
        self.task_container.event_generate("<Configure>")
    
    def generate_weekly_report(self):
        """生成周报弹窗"""
        if self.view_mode == "week":
            try:
                monday = date.fromisoformat(self.week_start_date)
            except:
                monday = self._get_monday(date.today())
        else:
            monday = self._get_monday(date.fromisoformat(self.current_view_date))
        
        week_days = self._get_week_range(monday)
        sunday = week_days[-1]
        
        dialog = self._make_cute_dialog("📋 周报", 520, 520)
        
        title_text = f"📋 周报 ({monday.strftime('%m/%d')} ~ {sunday.strftime('%m/%d')})"
        tk.Label(dialog, text=title_text, font=(self.theme.FONT_MAIN, 14, "bold"),
                fg=self.theme.FG_MAIN, bg=self.theme.BG_MAIN).pack(pady=(10, 5))
        
        nav_frame = tk.Frame(dialog, bg=self.theme.BG_MAIN)
        nav_frame.pack(fill=tk.X, padx=20, pady=5)
        
        week_label_var = tk.StringVar(value=f"{monday.strftime('%Y年%m月%d日')} ~ {sunday.strftime('%m月%d日')}")
        
        def prev_week():
            nonlocal monday, sunday, week_days
            monday = monday - timedelta(days=7)
            sunday = monday + timedelta(days=6)
            week_days = self._get_week_range(monday)
            week_label_var.set(f"{monday.strftime('%Y年%m月%d日')} ~ {sunday.strftime('%m月%d日')}")
            refresh_report()
        
        def next_week():
            nonlocal monday, sunday, week_days
            monday = monday + timedelta(days=7)
            sunday = monday + timedelta(days=6)
            week_days = self._get_week_range(monday)
            week_label_var.set(f"{monday.strftime('%Y年%m月%d日')} ~ {sunday.strftime('%m月%d日')}")
            refresh_report()
        
        self._make_cute_btn(nav_frame, "◀ 上一周", self.theme.BG_TAB, fg_color=self.theme.FG_MAIN,
                           command=prev_week, font_size=8, padx=8, pady=2).pack(side=tk.LEFT)
        tk.Label(nav_frame, textvariable=week_label_var, font=(self.theme.FONT_MAIN, 10, "bold"),
                fg=self.theme.FG_DATE, bg=self.theme.BG_MAIN).pack(side=tk.LEFT, expand=True)
        self._make_cute_btn(nav_frame, "下一周 ▶", self.theme.BG_TAB, fg_color=self.theme.FG_MAIN,
                           command=next_week, font_size=8, padx=8, pady=2).pack(side=tk.RIGHT)
        
        report_frame = tk.Frame(dialog, bg=self.theme.BG_MAIN)
        report_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        report_canvas = tk.Canvas(report_frame, bg=self.theme.BG_MAIN, highlightthickness=0)
        report_scrollbar = tk.Scrollbar(report_frame, orient="vertical", command=report_canvas.yview)
        report_content_frame = tk.Frame(report_canvas, bg=self.theme.BG_MAIN)
        
        report_content_frame.bind("<Configure>", lambda e: report_canvas.configure(scrollregion=report_canvas.bbox("all")))
        report_canvas_window = report_canvas.create_window((0, 0), window=report_content_frame, anchor="nw")
        report_canvas.configure(yscrollcommand=report_scrollbar.set)
        
        def _on_report_canvas_configure(event):
            report_canvas.itemconfig(report_canvas_window, width=event.width)
        report_canvas.bind("<Configure>", _on_report_canvas_configure)
        
        report_canvas.pack(side="left", fill="both", expand=True)
        report_scrollbar.pack(side="right", fill="y")
        
        def _on_report_mousewheel(event):
            report_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        def _bind_report_mousewheel(event):
            report_canvas.bind_all("<MouseWheel>", _on_report_mousewheel)
        def _unbind_report_mousewheel(event):
            report_canvas.unbind_all("<MouseWheel>")
        report_canvas.bind("<Enter>", _bind_report_mousewheel)
        report_canvas.bind("<Leave>", _unbind_report_mousewheel)
        report_scrollbar.bind("<Enter>", _bind_report_mousewheel)
        report_scrollbar.bind("<Leave>", _unbind_report_mousewheel)
        
        weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        
        def refresh_report():
            for w in report_content_frame.winfo_children():
                w.destroy()
            
            total_completed = 0
            total_in_progress = 0
            total_upcoming = 0
            
            for i, d in enumerate(week_days):
                ds = d.isoformat()
                day_tasks = self._load_tasks(ds)
                completed = day_tasks.get("completed", [])
                in_progress = day_tasks.get("in_progress", [])
                upcoming = day_tasks.get("upcoming", [])
                
                total_completed += len(completed)
                total_in_progress += len(in_progress)
                total_upcoming += len(upcoming)
                
                if not (completed or in_progress or upcoming):
                    continue
                
                day_card = tk.Frame(report_content_frame, bg=self.theme.BG_CARD, padx=10, pady=6)
                day_card.pack(fill=tk.X, pady=3)
                
                is_today = (d == date.today())
                day_title = f"📅 {d.strftime('%m/%d')} {weekday_names[i]}"
                if is_today:
                    day_title += " 📍"
                
                tk.Label(day_card, text=day_title, font=(self.theme.FONT_MAIN, 10, "bold"),
                        fg=self.theme.FG_DATE if is_today else self.theme.FG_MAIN, bg=self.theme.BG_CARD).pack(anchor="w")
                
                for task in completed:
                    tk.Label(day_card, text=f"  ✅ {task.get('text', '')}", font=(self.theme.FONT_MAIN, 9),
                            fg=self.theme.FG_LIGHT, bg=self.theme.BG_CARD, anchor="w", wraplength=440).pack(anchor="w")
                for task in in_progress:
                    tk.Label(day_card, text=f"  🔄 {task.get('text', '')}", font=(self.theme.FONT_MAIN, 9),
                            fg=self.theme.FG_MAIN, bg=self.theme.BG_CARD, anchor="w", wraplength=440).pack(anchor="w")
                for task in upcoming:
                    tk.Label(day_card, text=f"  📅 {task.get('text', '')}", font=(self.theme.FONT_MAIN, 9),
                            fg=self.theme.FG_LIGHT, bg=self.theme.BG_CARD, anchor="w", wraplength=440).pack(anchor="w")
            
            if total_completed + total_in_progress + total_upcoming == 0:
                tk.Label(report_content_frame, text="📭 本周暂无任务记录~", font=(self.theme.FONT_MAIN, 11),
                        fg=self.theme.FG_LIGHT, bg=self.theme.BG_MAIN).pack(pady=30)
            else:
                summary_card = tk.Frame(report_content_frame, bg=self.theme.BG_HEADER, padx=10, pady=6)
                summary_card.pack(fill=tk.X, pady=(10, 3))
                summary_text = f"📊 本周统计：✅ 完成 {total_completed} 项 | 🔄 进行中 {total_in_progress} 项 | 📅 计划中 {total_upcoming} 项"
                tk.Label(summary_card, text=summary_text, font=(self.theme.FONT_MAIN, 10, "bold"),
                        fg=self.theme.FG_WHITE, bg=self.theme.BG_HEADER).pack()

                # === 周总结：按任务名去重，取最后状态 ===
                task_summary = {}  # {任务名: {"status": key, "last_date": date}}
                status_order = {"completed": 3, "in_progress": 2, "upcoming": 1}
                status_emoji = {"completed": "✅", "in_progress": "🔄", "upcoming": "📅"}
                status_name = {"completed": "已完成", "in_progress": "进行中", "upcoming": "计划中"}

                for i, d in enumerate(week_days):
                    ds = d.isoformat()
                    day_tasks = self._load_tasks(ds)
                    for status_key in ["completed", "in_progress", "upcoming"]:
                        for task in day_tasks.get(status_key, []):
                            name = task.get("text", "").strip()
                            if not name:
                                continue
                            if name not in task_summary or status_order.get(status_key, 0) > status_order.get(task_summary[name]["status"], 0):
                                task_summary[name] = {"status": status_key, "last_date": d}

                if task_summary:
                    week_summary_card = tk.Frame(report_content_frame, bg=self.theme.BG_CARD, padx=10, pady=8)
                    week_summary_card.pack(fill=tk.X, pady=(8, 3))

                    tk.Label(week_summary_card, text="📝 周总结（按任务汇总）", font=(self.theme.FONT_MAIN, 10, "bold"),
                            fg=self.theme.FG_DATE, bg=self.theme.BG_CARD).pack(anchor="w", pady=(0, 5))

                    for name, info in sorted(task_summary.items(), key=lambda x: (-status_order.get(x[1]["status"], 0), x[0])):
                        s = info["status"]
                        emoji = status_emoji.get(s, "📌")
                        sname = status_name.get(s, "未知")
                        last_d = info["last_date"].strftime("%m/%d")
                        task_label = tk.Label(week_summary_card,
                            text=f"  {emoji} {name}  [{sname} · {last_d}]",
                            font=(self.theme.FONT_MAIN, 9),
                            fg=self.theme.FG_MAIN if s == "in_progress" else self.theme.FG_LIGHT,
                            bg=self.theme.BG_CARD, anchor="w", wraplength=440)
                        task_label.pack(anchor="w", pady=1)
        
        refresh_report()
        
        btn_frame = tk.Frame(dialog, bg=self.theme.BG_MAIN)
        btn_frame.pack(pady=10)
        
        def export_report():
            report_dir = self.settings.get("report_dir", "") or str(Path(__file__).parent / "workLog")
            Path(report_dir).mkdir(parents=True, exist_ok=True)
            
            report_text = f"工作周报 ({monday.strftime('%Y/%m/%d')} ~ {sunday.strftime('%Y/%m/%d')})" + "\n"
            report_text += "=" * 50 + "\n\n"
            
            total_c, total_p, total_u = 0, 0, 0
            for i, d in enumerate(week_days):
                ds = d.isoformat()
                day_tasks = self._load_tasks(ds)
                completed = day_tasks.get("completed", [])
                in_progress = day_tasks.get("in_progress", [])
                upcoming = day_tasks.get("upcoming", [])
                total_c += len(completed)
                total_p += len(in_progress)
                total_u += len(upcoming)
                
                if not (completed or in_progress or upcoming):
                    continue
                
                report_text += f"\n📅 {d.strftime('%m/%d')} {weekday_names[i]}:\n"
                for t in completed:
                    report_text += f"  ✅ {t['text']}\n"
                for t in in_progress:
                    report_text += f"  🔄 {t['text']}\n"
                for t in upcoming:
                    report_text += f"  📅 {t['text']}\n"
            
            report_text += "\n" + "=" * 50 + "\n"
            report_text += f"📊 统计：✅{total_c} 🔄{total_p} 📅{total_u}\n"
            
            filename = f"周报_{monday.strftime('%Y%m%d')}_{sunday.strftime('%Y%m%d')}.txt"
            filepath = os.path.join(report_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_text)
            self._cute_messagebox("导出成功", f"周报已保存到：\n{filepath} ✨", "success")
        
        def copy_report():
            """复制周报全部内容到剪贴板"""
            report_text = f"📋 周报 ({monday.strftime('%Y/%m/%d')} ~ {sunday.strftime('%Y/%m/%d')})" + "\n"
            report_text += "=" * 50 + "\n\n"
            
            for i, d in enumerate(week_days):
                ds = d.isoformat()
                day_tasks = self._load_tasks(ds)
                completed = day_tasks.get("completed", [])
                in_progress = day_tasks.get("in_progress", [])
                upcoming = day_tasks.get("upcoming", [])
                if not (completed or in_progress or upcoming):
                    continue
                report_text += f"\n📅 {d.strftime('%m/%d')} {weekday_names[i]}:\n"
                for t in completed:
                    report_text += f"  ✅ {t['text']}\n"
                for t in in_progress:
                    report_text += f"  🔄 {t['text']}\n"
                for t in upcoming:
                    report_text += f"  📅 {t['text']}\n"
            
            task_summary = {}
            status_order = {"completed": 3, "in_progress": 2, "upcoming": 1}
            status_emoji = {"completed": "✅", "in_progress": "🔄", "upcoming": "📅"}
            status_name = {"completed": "已完成", "in_progress": "进行中", "upcoming": "计划中"}
            for i, d in enumerate(week_days):
                ds = d.isoformat()
                day_tasks = self._load_tasks(ds)
                for sk in ["completed", "in_progress", "upcoming"]:
                    for task in day_tasks.get(sk, []):
                        name = task.get("text", "").strip()
                        if not name:
                            continue
                        if name not in task_summary or status_order.get(sk, 0) > status_order.get(task_summary[name]["status"], 0):
                            task_summary[name] = {"status": sk, "last_date": d}
            
            if task_summary:
                report_text += "\n" + "=" * 50 + "\n"
                report_text += "📝 周总结（按任务汇总）:\n"
                for name, info in sorted(task_summary.items(), key=lambda x: (-status_order.get(x[1]["status"], 0), x[0])):
                    s = info["status"]
                    emoji = status_emoji.get(s, "📌")
                    sname = status_name.get(s, "未知")
                    last_d = info["last_date"].strftime("%m/%d")
                    report_text += f"  {emoji} {name}  [{sname} · {last_d}]\n"
            
            self.root.clipboard_clear()
            self.root.clipboard_append(report_text)
            self._cute_messagebox("已复制", "周报内容已复制到剪贴板~ 📋", "success")
        
        self._make_cute_btn(btn_frame, "💾 导出周报", self.theme.BTN_START, hover_color=self.theme.BTN_START_HOVER,
                           command=export_report, font_size=9, padx=12, pady=4).pack(side=tk.LEFT, padx=5)
        self._make_cute_btn(btn_frame, "📋 复制全部", self.theme.BTN_SUMMARY, hover_color=self.theme.BTN_SUMMARY_HOVER,
                           command=copy_report, font_size=9, padx=12, pady=4).pack(side=tk.LEFT, padx=5)
        self._make_cute_btn(btn_frame, "关闭~", self.theme.BTN_ADD, hover_color=self.theme.BTN_ADD_HOVER,
                           command=dialog.destroy, font_size=9, padx=12, pady=4).pack(side=tk.RIGHT, padx=5)
        
        dialog.grab_set()
    def generate_summary(self):
        view_date = self.current_view_date
        summary = f"📊 工作总结 ({view_date})\n\n"
        completed = [t for t in self.tasks.get("completed", [])]
        in_progress = [t for t in self.tasks.get("in_progress", [])]
        upcoming = [t for t in self.tasks.get("upcoming", [])]
        
        summary += f"✅ 已完成 ({len(completed)}项):\n"
        for t in completed: summary += f"  • {t['text']}\n"
        summary += f"\n🔄 进行中 ({len(in_progress)}项):\n"
        for t in in_progress: summary += f"  • {t['text']}\n"
        summary += f"\n📅 计划中 ({len(upcoming)}项):\n"
        for t in upcoming: summary += f"  • {t['text']}\n"
        
        dialog = self._make_cute_dialog("📊 工作总结", 500, 420)
        
        tk.Label(dialog, text="📊 工作总结", font=(self.theme.FONT_MAIN, 14, "bold"), 
                fg=self.theme.FG_MAIN, bg=self.theme.BG_MAIN).pack(pady=(10, 5))
        tk.Label(dialog, text=view_date, font=(self.theme.FONT_MONO, 9), 
                fg=self.theme.FG_DATE, bg=self.theme.BG_MAIN).pack()
        
        text_area = tk.Text(dialog, font=(self.theme.FONT_MAIN, 10), fg=self.theme.FG_MAIN, bg=self.theme.BG_CARD,
                           relief=tk.FLAT, wrap=tk.WORD, padx=15, pady=10,
                           selectbackground=self.theme.BG_TAB_ACTIVE, selectforeground=self.theme.FG_WHITE)
        text_area.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        text_area.insert(tk.END, summary)
        text_area.config(state=tk.DISABLED)
        
        self._make_cute_btn(dialog, "关闭~", self.theme.BTN_ADD, hover_color=self.theme.BTN_ADD_HOVER, 
                           command=dialog.destroy, font_size=10, padx=30, pady=5).pack(pady=10)
    
    def quit_app(self):
        self._save_tasks()
        self._stop_event.set()
        # 修复：退出时更新 last_sync_date 为今天，避免下次启动时重复同步
        self.settings["last_sync_date"] = date.today().isoformat()
        self._save_settings()
        if self._cute_confirm("退出", "确定要关闭智能助手吗？\n下次见~ 👋"):
            self.root.destroy()
            sys.exit(0)


def main():
    root = tk.Tk()
    app = SmartDesktopAssistant(root)
    root.mainloop()

if __name__ == "__main__":
    main()
