#!/usr/bin/env python
"""
启动完整的开发环境服务
包括 Django WSGI/ASGI、Celery Worker 和 Celery Beat
"""
import os
import subprocess
import sys
import signal
import time
from threading import Thread

def check_redis():
    """检查 Redis 是否运行"""
    try:
        result = subprocess.run(['redis-cli', 'ping'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and 'PONG' in result.stdout:
            print("✓ Redis 正在运行")
            return True
        else:
            print("✗ Redis 未运行，请先启动 Redis")
            return False
    except Exception as e:
        print(f"✗ 无法检查 Redis 状态: {e}")
        return False

def start_service(name, command, log_file=None):
    """启动服务进程"""
    print(f"启动 {name}...")
    try:
        if log_file:
            with open(log_file, 'w') as f:
                if isinstance(command, list):
                    process = subprocess.Popen(command, stdout=f, stderr=f)
                else:
                    process = subprocess.Popen(command, shell=True, stdout=f, stderr=f)
        else:
            if isinstance(command, list):
                process = subprocess.Popen(command)
            else:
                process = subprocess.Popen(command, shell=True)
        
        print(f"✓ {name} 已启动 (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"✗ 启动 {name} 失败: {e}")
        return None

def main():
    """主函数"""
    print("=== 启动完整开发环境 ===")
    
    # 检查 Redis
    if not check_redis():
        print("请先启动 Redis 服务:")
        print("  macOS: brew services start redis")
        print("  或直接运行: redis-server")
        sys.exit(1)
    
    processes = []
    
    try:
        # 启动 Celery Worker
        worker_process = start_service(
            "Celery Worker",
            "celery -A RehabilitationManager worker --loglevel=info",
            "logs/celery_worker.log"
        )
        if worker_process:
            processes.append(("Celery Worker", worker_process))
        
        time.sleep(2)  # 等待 Worker 启动
        
        # 启动 Celery Beat
        beat_process = start_service(
            "Celery Beat",
            "celery -A RehabilitationManager beat --loglevel=info",
            "logs/celery_beat.log"
        )
        if beat_process:
            processes.append(("Celery Beat", beat_process))
        
        time.sleep(2)  # 等待 Beat 启动
        
        # 启动 WSGI 服务 (gunicorn) - 端口 8087
        wsgi_process = start_service(
            "WSGI Server (Gunicorn)",
            ["gunicorn", "RehabilitationManager.wsgi:application", "-b", "0.0.0.0:8087"],
            "logs/wsgi.log"
        )
        if wsgi_process:
            processes.append(("WSGI Server", wsgi_process))
        
        time.sleep(2)  # 等待 WSGI 启动
        
        # 启动 ASGI 服务 (daphne) - 端口 8088  
        asgi_process = start_service(
            "ASGI Server (Daphne)",
            ["daphne", "-b", "0.0.0.0", "-p", "8088", "RehabilitationManager.asgi:application"],
            "logs/asgi.log"
        )
        if asgi_process:
            processes.append(("ASGI Server", asgi_process))
        
        print("\n=== 所有服务已启动 ===")
        print("- WSGI Server: http://localhost:8087")
        print("- ASGI Server: http://localhost:8088") 
        print("- Celery Worker: 监听任务队列")
        print("- Celery Beat: 定时任务调度")
        print("\n按 Ctrl+C 停止所有服务")
        
        # 等待用户中断
        try:
            while True:
                time.sleep(1)
                # 检查进程是否还在运行
                for name, process in processes:
                    if process.poll() is not None:
                        print(f"警告: {name} 进程已终止")
        except KeyboardInterrupt:
            pass
    
    except Exception as e:
        print(f"启动过程中出错: {e}")
    
    finally:
        # 停止所有进程
        print("\n=== 停止所有服务 ===")
        for name, process in processes:
            try:
                print(f"停止 {name}...")
                process.terminate()
                process.wait(timeout=5)
                print(f"✓ {name} 已停止")
            except subprocess.TimeoutExpired:
                print(f"强制终止 {name}...")
                process.kill()
            except Exception as e:
                print(f"停止 {name} 时出错: {e}")

if __name__ == "__main__":
    # 创建日志目录
    os.makedirs("logs", exist_ok=True)
    main()
