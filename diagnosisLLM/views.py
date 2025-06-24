from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import logging
from openai import OpenAI

# Create your views here.

logger = logging.getLogger(__name__)

API_KEY = "your_deepseek_api_key"  # 请替换为您的 API 密钥

@csrf_exempt
@require_POST
def generate_text(request):
    """
    接收前端传递的文字内容，调用 deepseek r1 接口，并实时返回生成的内容
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        user_input = data.get('text', '')
        
        if not user_input:
            return JsonResponse({'error': '请提供文本内容'}, status=400)
        
        # 返回纯 JSON 格式的流式响应
        return StreamingHttpResponse(stream_deepseek_response(user_input), content_type='application/json')
    
    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        return JsonResponse({'error': f'处理请求时出错: {str(e)}'}, status=500)

def stream_deepseek_response(user_input):
    """
    使用官方客户端库流式传输 deepseek 响应给前端（返回纯 JSON 格式数据，不使用 SSE 格式）
    """
    try:
        # 初始化 OpenAI 客户端，使用 DeepSeek API 端点
        client = OpenAI(
            api_key="sk-3a9af6cc4e784b2680a84ca54c9c5f85",
            base_url="https://api.deepseek.com"
        )
        
        # 创建流式聊天完成请求
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": user_input}
            ],
            max_tokens=1024,
            temperature=0.7,
            stream=True
        )
        
        # 处理流式响应
        for chunk in response:
            if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content'):
                content = chunk.choices[0].delta.content
                if content:
                    # 直接返回纯 JSON 数据，并设置 ensure_ascii=False
                    yield json.dumps({'content': content}, ensure_ascii=False)
        
        # 完成标识
        yield json.dumps({'done': True}, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"连接到 API 时出错: {str(e)}")
        yield json.dumps({'error': f"连接到 API 时出错: {str(e)}"}, ensure_ascii=False)
