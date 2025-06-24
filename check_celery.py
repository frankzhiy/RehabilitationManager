import os
import django
import sys

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RehabilitationManager.settings')
django.setup()

from celery import current_app
from prescription.tasks import test_celery_task

def check_celery_status():
    """检查 Celery 工作状态"""
    print("=== Celery 状态检查 ===")
    
    try:
        # 1. 检查 broker 连接
        print("1. 检查 broker 连接...")
        inspect = current_app.control.inspect()
        stats = inspect.stats()
        if stats:
            print(f"   ✓ 发现 {len(stats)} 个活跃的 worker:")
            for worker_name in stats.keys():
                print(f"     - {worker_name}")
        else:
            print("   ✗ 没有发现活跃的 worker")
            return False
        
        # 2. 检查活跃任务
        print("2. 检查活跃任务...")
        active = inspect.active()
        if active:
            total_active = sum(len(tasks) for tasks in active.values())
            print(f"   当前有 {total_active} 个活跃任务")
        else:
            print("   当前没有活跃任务")
        
        # 3. 提交测试任务
        print("3. 提交测试任务...")
        task = test_celery_task.delay()
        print(f"   测试任务已提交，ID: {task.id}")
        
        # 4. 等待任务完成
        print("4. 等待任务完成...")
        try:
            result = task.get(timeout=10)
            print(f"   ✓ 任务完成，结果: {result}")
            return True
        except Exception as e:
            print(f"   ✗ 任务执行失败: {str(e)}")
            return False
            
    except Exception as e:
        print(f"检查过程中出错: {str(e)}")
        return False

if __name__ == "__main__":
    success = check_celery_status()
    if not success:
        print("\n=== 问题诊断建议 ===")
        print("1. 确保 Redis 服务正在运行:")
        print("   redis-cli ping")
        print("2. 启动 Celery worker:")
        print("   celery -A RehabilitationManager worker --loglevel=info")
        print("3. 检查 Django 设置中的 CELERY_BROKER_URL")
        sys.exit(1)
    else:
        print("\n✓ Celery 工作正常!")
