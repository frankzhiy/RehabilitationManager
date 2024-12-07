# from django.utils.deprecation import MiddlewareMixin
# from logsystem.models import LogEntry
#
# class LoggingMiddleware(MiddlewareMixin):
#     def process_request(self, request):
#         LogEntry.objects.create(
#             level='DEBUG',
#             message=f"Request to {request.path}",
#             path=request.path,
#             method=request.method,
#             ip_address=request.META.get('REMOTE_ADDR'),
#         )
#
#     def process_exception(self, request, exception):
#         LogEntry.objects.create(
#             level='ERROR',
#             message=f"Exception at {request.path}: {str(exception)}",
#             path=request.path,
#             method=request.method,
#             ip_address=request.META.get('REMOTE_ADDR'),
#         )
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from logsystem.models import LogEntry
import json

class LoggingMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # 检查是否为 JsonResponse
        if isinstance(response, JsonResponse):
            try:
                # 解析 JsonResponse 的内容
                response_data = json.loads(response.content)
                log_message = response_data.get('message', 'No message provided')  # 获取 message 字段
            except Exception as e:
                log_message = f"Failed to parse JsonResponse: {str(e)}"
        else:
            log_message = "Response is not a JsonResponse"

        # 写入日志
        LogEntry.objects.create(
            level='INFO',
            message=log_message,
            path=request.path,
            method=request.method,
            ip_address=request.META.get('REMOTE_ADDR'),
        )

        return response

    def process_exception(self, request, exception):
        # 捕获异常并记录日志
        LogEntry.objects.create(
            level='ERROR',
            message=str(exception),
            path=request.path,
            method=request.method,
            ip_address=request.META.get('REMOTE_ADDR'),
        )
        return None
