from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from logsystem.models import LogEntry
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime, timedelta

# 获取自定义日志记录器
logger = logging.getLogger('custom_logger')
error_logger = logging.getLogger('error_logger')

# 配置日志轮转（如果还没有配置）
def setup_rotating_logger():
    # 使用环境变量配置日志路径，Docker环境下更灵活
    log_dir = os.environ.get('LOG_DIR', '/app/logs')
    
    try:
        os.makedirs(log_dir, exist_ok=True)
        
        # 检查目录写权限
        test_file = os.path.join(log_dir, '.write_test')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        
    except (OSError, PermissionError) as e:
        # 如果无法写入指定目录，回退到临时目录
        print(f"Cannot write to {log_dir}, falling back to /tmp/logs: {e}")
        log_dir = '/tmp/logs'
        os.makedirs(log_dir, exist_ok=True)
    
    # 为custom_logger设置轮转
    if not logger.handlers:
        try:
            handler = RotatingFileHandler(
                os.path.join(log_dir, 'app.log'),
                maxBytes=10*1024*1024,  # 10MB
                backupCount=4  # 保持4个备份 + 1个当前 = 5个文件
            )
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        except Exception as e:
            print(f"Failed to setup app logger: {e}")
    
    # 为error_logger设置轮转
    if not error_logger.handlers:
        try:
            error_handler = RotatingFileHandler(
                os.path.join(log_dir, 'error.log'),
                maxBytes=10*1024*1024,  # 10MB
                backupCount=4  # 保持4个备份 + 1个当前 = 5个文件
            )
            error_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            error_handler.setFormatter(error_formatter)
            error_logger.addHandler(error_handler)
            error_logger.setLevel(logging.ERROR)
        except Exception as e:
            print(f"Failed to setup error logger: {e}")

class LoggingMiddleware(MiddlewareMixin):
    
    def __init__(self, get_response):
        super().__init__(get_response)
        setup_rotating_logger()
        self.last_db_log_time = {}  # 缓存最近数据库日志时间
    
    # 定义需要记录的重要路径
    IMPORTANT_PATHS = [
        '/login/', '/registration/', '/assessment/', '/prescription/',
        '/patient/', '/medication/', '/followup/', '/questionnaire/'
    ]
    
    # 定义忽略的静态资源路径
    IGNORE_PATHS = [
        '/static/', '/favicon.ico', '/admin/jsi18n/', '/media/'
    ]
    
    def should_log_request(self, request):
        """判断是否需要记录该请求"""
        path = request.path.lower()
        
        # 忽略静态资源
        if any(ignore_path in path for ignore_path in self.IGNORE_PATHS):
            return False
            
        # 只记录重要路径或错误响应
        return any(important_path in path for important_path in self.IMPORTANT_PATHS)
    
    def should_log_to_db(self, request, response):
        """判断是否需要写入数据库（减少数据库写入频率）"""
        path_key = f"{request.method}:{request.path}"
        now = datetime.now()
        
        # 错误请求总是记录
        if response.status_code >= 400:
            return True
            
        # 重要路径的成功请求，限制频率（每分钟最多一次相同路径）
        if any(path in request.path for path in self.IMPORTANT_PATHS):
            last_time = self.last_db_log_time.get(path_key)
            if not last_time or (now - last_time).seconds > 60:
                self.last_db_log_time[path_key] = now
                return True
                
        return False
    
    def process_response(self, request, response):
        # 只记录重要请求或错误响应
        if not self.should_log_request(request) and response.status_code < 400:
            return response
            
        try:
            if isinstance(response, JsonResponse):
                try:
                    response_data = json.loads(response.content)
                    log_message = response_data.get('message', f'Status: {response.status_code}')
                except Exception:
                    log_message = f'JSON Response - Status: {response.status_code}'
            else:
                log_message = f'Response - Status: {response.status_code}'

            # 根据响应状态码选择日志级别
            level = 'ERROR' if response.status_code >= 400 else 'INFO'
            
            # 有选择性地写入数据库日志
            if self.should_log_to_db(request, response):
                LogEntry.objects.create(
                    level=level,
                    message=log_message,
                    path=request.path,
                    method=request.method,
                    ip_address=self.get_client_ip(request),
                )
            
            # 写入文件日志（使用轮转）
            if response.status_code >= 400:
                error_logger.error(f"{request.method} {request.path} - {log_message} - IP: {self.get_client_ip(request)}")
            else:
                logger.info(f"{request.method} {request.path} - {log_message}")
                
        except Exception as e:
            error_logger.error(f"Logging middleware error: {str(e)}")

        return response

    def process_exception(self, request, exception):
        error_message = f"Exception: {str(exception)}"
        
        try:
            # 写入数据库日志
            LogEntry.objects.create(
                level='ERROR',
                message=error_message,
                path=request.path,
                method=request.method,
                ip_address=self.get_client_ip(request),
            )
        except Exception:
            pass  # 避免日志记录本身引发异常
        
        # 写入文件日志
        error_logger.error(f"{request.method} {request.path} - {error_message} - IP: {self.get_client_ip(request)}")
        
        return None
    
    def get_client_ip(self, request):
        """获取客户端真实IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
