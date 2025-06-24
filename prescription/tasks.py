from celery import shared_task
import json
import io
import requests
from pydub import AudioSegment
from .services import build_audio_url_sequence
import logging
import time
import os
import traceback

logger = logging.getLogger(__name__)

@shared_task
def test_celery_task():
    """简单测试任务，用于验证 Celery 工作正常"""
    import time
    logger.info("测试任务开始执行")
    time.sleep(2)  # 模拟工作
    logger.info("测试任务完成")
    return {"status": "success", "message": "测试任务完成", "timestamp": time.time()}

@shared_task(bind=True)
def generate_audio_sequence_task(self, motion_sequence):
    """
    异步处理音频合并任务
    """
    logger.info(f"开始执行音频生成任务 {self.request.id}")
    logger.info(f"Worker 进程 PID: {os.getpid()}")
    logger.info(f"接收到 {len(motion_sequence)} 个动作序列项")
    
    try:
        # 立即更新状态，确认任务被接收
        self.update_state(
            state='PROGRESS', 
            meta={'status': 'Worker 已接收任务，开始处理', 'progress': 1}
        )
        
        # 检查输入
        if not motion_sequence:
            logger.error("传入的 motion_sequence 为空")
            return {"status": "error", "message": "No motion_sequence data provided."}

        # 更新任务状态
        self.update_state(
            state='PROGRESS', 
            meta={'status': '开始处理音频序列', 'progress': 0}
        )
        
        # 通过 services.py 的函数，获取 (type, value) 的列表
        audio_sequence = build_audio_url_sequence(motion_sequence)
        if not audio_sequence:
            logger.error("build_audio_url_sequence 返回空结果")
            return {"status": "error", "message": "Empty audio sequence generated"}

        logger.info(f"已生成音频序列，共 {len(audio_sequence)} 项")
        self.update_state(
            state='PROGRESS', 
            meta={'status': '开始下载和合并音频文件', 'progress': 10}
        )
        
        final_audio = None
        total_items = len(audio_sequence)
        processed_items = 0

        # 逐个处理
        for idx, (item_type, item_value) in enumerate(audio_sequence):
            try:
                progress = int(10 + (idx / total_items) * 80)
                self.update_state(
                    state='PROGRESS', 
                    meta={
                        'status': f'处理音频项 {idx+1}/{total_items}',
                        'progress': progress
                    }
                )
                
                logger.debug(f"处理音频项 {idx+1}/{total_items}: {item_type}")
                
                if item_type == "audio":
                    # item_value 是字符串URL
                    logger.debug(f"下载音频: {item_value}")
                    
                    try:
                        resp = requests.get(item_value, timeout=30)
                        resp.raise_for_status()  # 检查请求是否成功
                        
                        # 假设是 mp3
                        segment = AudioSegment.from_file(io.BytesIO(resp.content), format="mp3")
                        logger.debug(f"成功加载音频，长度: {len(segment)}ms")
                        
                    except Exception as e:
                        logger.error(f"下载或解析音频失败: {str(e)}")
                        continue

                elif item_type == "silence":
                    # item_value 是毫秒数
                    logger.debug(f"生成静音: {item_value}ms")
                    segment = AudioSegment.silent(duration=item_value)

                else:
                    # 其它类型不做处理
                    logger.warning(f"未知音频项类型: {item_type}")
                    continue

                # 拼接
                if final_audio is None:
                    final_audio = segment
                else:
                    final_audio += segment
                    
                processed_items += 1
                
            except Exception as e:
                logger.error(f"处理音频项时出错: {str(e)}")
                continue

        if final_audio is None:
            logger.error("没有可合并的有效音频段")
            return {"status": "error", "message": "No valid segments to merge."}

        self.update_state(
            state='PROGRESS', 
            meta={'status': '正在导出最终音频文件', 'progress': 90}
        )
        
        # 导出到内存
        logger.info("导出最终音频文件")
        output_buffer = io.BytesIO()
        final_audio.export(output_buffer, format="mp3")
        output_buffer.seek(0)
        
        # 将音频数据转换为base64字符串以便存储和传输
        import base64
        audio_data = base64.b64encode(output_buffer.read()).decode('utf-8')
        
        logger.info(f"任务 {self.request.id} 完成，生成的音频大小: {len(audio_data)} bytes")
        return {
            'status': 'SUCCESS',
            'audio_data': audio_data,
            'filename': 'final_audio.mp3'
        }

    except Exception as e:
        logger.error(f"生成音频序列任务出错: {str(e)}", exc_info=True)
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'traceback': traceback.format_exc()}
        )
        raise
