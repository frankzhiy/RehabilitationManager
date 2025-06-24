import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from .views import stream_deepseek_response

# 定义一个辅助 async_generator，用于包装同步生成器
async def async_generator(sync_gen):
    for item in sync_gen:
        yield item
        await asyncio.sleep(0)

class DiagnosisLLMConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_input = data.get('text', '')
        if not user_input:
            await self.send(json.dumps({'error': '请输入文本内容'}))
            return

        try:
            # 使用 async_generator 包装同步生成器 stream_deepseek_response
            async for chunk in async_generator(stream_deepseek_response(user_input)):
                await self.send(json.dumps({'content': chunk}))
        except Exception as e:
            await self.send(json.dumps({'error': str(e)}))