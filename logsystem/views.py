from django.http import JsonResponse
from django.core.paginator import Paginator
from logsystem.models import LogEntry

def get_logs(request):
    """
    返回日志列表，支持分页和筛选。
    """
    level = request.GET.get('level')  # 筛选日志级别
    page = request.GET.get('page', 1)  # 分页页码
    page_size = request.GET.get('page_size', 10)  # 每页条数

    logs = LogEntry.objects.all()

    if level:
        logs = logs.filter(level=level)

    paginator = Paginator(logs, page_size)
    try:
        page_obj = paginator.page(page)
    except Exception:
        return JsonResponse({'error': 'Invalid page number'}, status=400)

    data = [
        {
            'id': log.id,
            'level': log.level,
            'message': log.message,
            'module': log.module,
            'path': log.path,
            'user': log.user,
            'ip_address': log.ip_address,
            'created_at': log.created_at,
        }
        for log in page_obj.object_list
    ]

    return JsonResponse({
        'logs': data,
        'page': page_obj.number,
        'total_pages': paginator.num_pages,
        'total_logs': paginator.count,
    })
