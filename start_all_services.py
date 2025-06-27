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
import glob
from threading import Thread

def rotate_logs(log_file, max_files=5):
    """日志轮转，保持最多 max_files 个日志文件"""
    if os.path.exists(log_file):
        # 获取所有相关日志文件
        base_name = log_file.rsplit('.', 1)[0]
        ext = log_file.rsplit('.', 1)[1] if '.' in log_file else 'log'
        pattern = f"{base_name}.*.{ext}"
        existing_logs = glob.glob(pattern)
        existing_logs.sort(key=os.path.getctime, reverse=True)
        
        # 删除多余的日志文件
        if len(existing_logs) >= max_files - 1:
            for old_log in existing_logs[max_files-2:]:
                try:
                    os.remove(old_log)
                except OSError:
                    pass
        
        # 重命名当前日志文件
        timestamp = int(time.time())
        backup_name = f"{base_name}.{timestamp}.{ext}"
        try:
            os.rename(log_file, backup_name)
        except OSError:
            pass

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

def start_service(name, command, log_file=None, env_vars=None):
    """启动服务进程"""
    print(f"启动 {name}...")
    try:
        # 日志轮转
        if log_file:
            rotate_logs(log_file)
        
        # 设置环境变量
        env = os.environ.copy()
        if env_vars:
            env.update(env_vars)
        
        if log_file:
            with open(log_file, 'w') as f:
                if isinstance(command, list):
                    process = subprocess.Popen(command, stdout=f, stderr=f, env=env)
                else:
                    process = subprocess.Popen(command, shell=True, stdout=f, stderr=f, env=env)
        else:
            if isinstance(command, list):
                process = subprocess.Popen(command, env=env)
            else:
                process = subprocess.Popen(command, shell=True, env=env)
        
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
        # 设置本地环境的 Celery 环境变量
        celery_env = {
            'CELERY_BROKER_URL': 'redis://localhost:6379/0',
            'CELERY_RESULT_BACKEND': 'redis://localhost:6379/0'
        }
        
        # 启动 Celery Worker
        worker_process = start_service(
            "Celery Worker",
            "celery -A RehabilitationManager worker --loglevel=info",
            "logs/celery_worker.log",
            celery_env
        )
        if worker_process:
            processes.append(("Celery Worker", worker_process))
        
        time.sleep(3)  # 等待 Worker 启动
        
        # 启动 Celery Beat
        beat_process = start_service(
            "Celery Beat",
            "celery -A RehabilitationManager beat --loglevel=info",
            "logs/celery_beat.log",
            celery_env
        )
        if beat_process:
            processes.append(("Celery Beat", beat_process))
        
        time.sleep(3)  # 等待 Beat 启动
        
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
        
        # 等待用户中断，减少进程检查频率
        try:
            check_count = 0
            while True:
                time.sleep(5)  # 每5秒检查一次
                check_count += 1
                
                # 每30秒详细检查一次进程状态
                if check_count % 6 == 0:
                    active_processes = []
                    for name, process in processes:
                        if process.poll() is None:
                            active_processes.append((name, process))
                        else:
                            print(f"警告: {name} 进程已终止 (退出码: {process.returncode})")
                    processes = active_processes
                    
                    if not processes:
                        print("所有服务进程都已终止")
                        break
                        
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
