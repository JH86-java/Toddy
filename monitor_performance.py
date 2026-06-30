#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Toddy 性能监控工具
==================
实时监控程序的CPU和内存占用情况
"""

import psutil
import os
import time
import sys
from datetime import datetime

def find_toddy_process():
    """查找Toddy进程"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if 'smart_assistant.py' in cmdline or 'toddy' in cmdline.lower():
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def monitor_performance(duration_minutes=5, interval_seconds=2):
    """监控性能指标"""
    
    print("=" * 60)
    print("🔍 Toddy 性能监控")
    print("=" * 60)
    print(f"监控时长: {duration_minutes} 分钟")
    print(f"采样间隔: {interval_seconds} 秒")
    print()
    
    # 查找进程
    process = find_toddy_process()
    if not process:
        print("❌ 未找到运行中的Toddy进程")
        print("请先启动 smart_assistant.py")
        return
    
    print(f"✅ 找到进程: PID={process.pid}")
    print()
    
    # 开始监控
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    
    cpu_samples = []
    memory_samples = []
    
    print("时间戳              | CPU(%)  | 内存(MB) | 线程数")
    print("-" * 60)
    
    try:
        while time.time() < end_time:
            try:
                # 获取性能指标
                cpu_percent = process.cpu_percent(interval=1)
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                num_threads = process.num_threads()
                
                # 记录样本
                cpu_samples.append(cpu_percent)
                memory_samples.append(memory_mb)
                
                # 显示当前状态
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"{timestamp} | {cpu_percent:6.2f}  | {memory_mb:7.2f}  | {num_threads}")
                
                # 等待下一次采样
                time.sleep(interval_seconds - 1)  # 减去cpu_percent的等待时间
                
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                print(f"\n⚠️  进程已结束或无法访问: {e}")
                break
    
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断监控")
    
    # 输出统计信息
    print()
    print("=" * 60)
    print("📊 性能统计摘要")
    print("=" * 60)
    
    if cpu_samples:
        avg_cpu = sum(cpu_samples) / len(cpu_samples)
        max_cpu = max(cpu_samples)
        min_cpu = min(cpu_samples)
        
        print(f"CPU占用:")
        print(f"  平均值: {avg_cpu:.2f}%")
        print(f"  最大值: {max_cpu:.2f}%")
        print(f"  最小值: {min_cpu:.2f}%")
        print()
        
        # 评估
        if avg_cpu < 2:
            print("  ✅ CPU占用优秀 (< 2%)")
        elif avg_cpu < 5:
            print("  ⚠️  CPU占用良好 (2-5%)")
        elif avg_cpu < 10:
            print("  ⚠️  CPU占用偏高 (5-10%)")
        else:
            print("  ❌ CPU占用过高 (> 10%)")
    
    if memory_samples:
        avg_memory = sum(memory_samples) / len(memory_samples)
        max_memory = max(memory_samples)
        min_memory = min(memory_samples)
        
        print(f"\n内存占用:")
        print(f"  平均值: {avg_memory:.2f} MB")
        print(f"  最大值: {max_memory:.2f} MB")
        print(f"  最小值: {min_memory:.2f} MB")
        print()
        
        # 检查内存泄漏
        if len(memory_samples) > 10:
            first_quarter = memory_samples[:len(memory_samples)//4]
            last_quarter = memory_samples[-len(memory_samples)//4:]
            
            avg_first = sum(first_quarter) / len(first_quarter)
            avg_last = sum(last_quarter) / len(last_quarter)
            
            growth_rate = ((avg_last - avg_first) / avg_first * 100) if avg_first > 0 else 0
            
            print(f"  内存增长率: {growth_rate:.2f}%")
            if growth_rate < 5:
                print("  ✅ 内存稳定，无明显泄漏")
            elif growth_rate < 15:
                print("  ⚠️  内存有轻微增长")
            else:
                print("  ❌ 可能存在内存泄漏")
    
    print()
    print("=" * 60)
    print("💡 建议:")
    if cpu_samples and sum(cpu_samples) / len(cpu_samples) > 5:
        print("  - CPU占用较高，建议检查是否有频繁的UI更新")
    if memory_samples and len(memory_samples) > 10:
        first_q = memory_samples[:len(memory_samples)//4]
        last_q = memory_samples[-len(memory_samples)//4:]
        if (sum(last_q)/len(last_q) - sum(first_q)/len(first_q)) > 20:
            print("  - 内存持续增长，可能存在资源泄漏")
    print("  - 如果性能良好，可以长时间运行观察稳定性")
    print("=" * 60)

if __name__ == "__main__":
    # 检查依赖
    try:
        import psutil
    except ImportError:
        print("❌ 缺少依赖: psutil")
        print("请安装: pip install psutil")
        sys.exit(1)
    
    # 解析命令行参数
    duration = 5
    interval = 2
    
    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
        except ValueError:
            pass
    
    if len(sys.argv) > 2:
        try:
            interval = int(sys.argv[2])
        except ValueError:
            pass
    
    monitor_performance(duration, interval)
