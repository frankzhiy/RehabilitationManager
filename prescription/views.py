from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator

from registration.models import PatientPrescription
from django.views.decorators.csrf import csrf_exempt
import json
import io
import requests
from datetime import datetime, timedelta
from pydub import AudioSegment
from .models import MotionPrescription, MotionList, ExerciseRecord
from .services import get_recommendations,build_audio_url_sequence
from django.views import View
from django.utils import timezone
import logging
from .tasks import generate_audio_sequence_task
import base64
from celery.result import AsyncResult

logger = logging.getLogger(__name__)
@csrf_exempt
def create_or_update_prescription(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        # 获取医生和患者的标识信息
        doctor = data.get('doctor')
        id_card = data.get('id_card')
        name = data.get('name')
        phone = data.get('phone')

        if not all([doctor, id_card, name, phone]):
            return JsonResponse({'error': '缺少必填字段'}, status=400)

        # 获取或创建记录
        prescription, created = PatientPrescription.objects.get_or_create(
            doctor=doctor,
            id_card=id_card,
            name=name,
            phone=phone
        )

        # 更新非空字段
        updated_fields = {}
        for field in ['swallowStatusPrescription', 'MepAndMipPrescription', 'limbStatus', 'PEFPrescription',
                      'TCEPrescription', 'MwtAndStepPrescription']:
            if field in data and data[field]:
                updated_fields[field] = data[field]

        # 更新并保存上传时间
        if updated_fields:
            for field, value in updated_fields.items():
                setattr(prescription, field, value)
            prescription.uploadtime = datetime.now()
            prescription.save()
            return JsonResponse({'message': '处方以添加' if not created else '处方记录创建失败'}, status=200)

        return JsonResponse({'error': '没有更新的字段'}, status=400)

    return JsonResponse({'error': '无效的请求方法'}, status=405)


@csrf_exempt
def get_prescription(request):
    if request.method == 'GET':
        doctor = request.GET.get('doctor')


        if not doctor:
            return JsonResponse({'status': 'error', 'message': '必须提供完整的医生信息才可获取患者列表'})

        try:
            prescription = PatientPrescription.objects.filter(doctor=doctor, is_verified=True)

            if not prescription:
                return JsonResponse({'status': 'success', 'message': '未找到患者处方记录'})

            # 将记录转换为字典
            data = list(prescription.values(
                'doctor', 'id_card', 'name', 'phone', 'swallowStatusPrescription','sex',
                'MepAndMipPrescription', 'limbStatusPrescription', 'PEFPrescription',
                'TCEPrescription', 'MwtAndStepPrescription', 'uploadtime', 'isActive', 'is_verified'
            ))
            return JsonResponse({'status': 'success', 'data': data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': '无效请求方法'})


@csrf_exempt
def recommend_assessments(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from request
            assessments = json.loads(request.body)
            # Get recommendations based on the assessments
            recommendations = get_recommendations(assessments)
            return JsonResponse({'status': 'success', 'recommendations': recommendations})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
def save_motion_prescription(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            id_card = data.get('id_card')
            phone = data.get('phone')
            doctor = data.get('doctor')

            # Deactivate existing prescriptions with the same name, id_card, phone, doctor
            MotionPrescription.objects.filter(
                name=name, id_card=id_card, phone=phone, doctor=doctor, is_active=True
            ).update(is_active=False)

            # Save new prescription
            prescription = MotionPrescription(
                name=name,
                id_card=id_card,
                phone=phone,
                doctor=doctor,
                limbPrescription=data.get('limbPrescription', []),
                pefPrescription=data.get('pefPrescription', []),
                respiratoryPrescription=data.get('respiratoryPrescription', []),
                swallowPrescription=data.get('swallowPrescription', []),
                tcePrescription=data.get('tcePrescription', []),
                upload_time=data.get('upload_time'),
                is_active=True
            )
            prescription.save()

            # Update corresponding PatientPrescription
            patient_prescription = PatientPrescription.objects.filter(
                name=name, id_card=id_card, phone=phone, doctor=doctor
            ).first()

            if patient_prescription:
                patient_prescription.limbStatusPrescription = data.get('limbPrescription', [])
                patient_prescription.PEFPrescription = data.get('pefPrescription', [])
                patient_prescription.MepAndMipPrescription = data.get('respiratoryPrescription', [])
                patient_prescription.swallowStatusPrescription = data.get('swallowPrescription', [])
                patient_prescription.TCEPrescription = data.get('tcePrescription', [])
                patient_prescription.save()
            else:
                return JsonResponse({'error': 'PatientPrescription not found'}, status=404)

            return JsonResponse({'message': 'Prescription saved and updated successfully.'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@csrf_exempt
def get_motion_prescriptions(request):
    if request.method == 'GET':
        name = request.GET.get('name')
        id_card = request.GET.get('id_card')
        phone = request.GET.get('phone')
        doctor = request.GET.get('doctor')

        if not all([name, id_card, phone, doctor]):
            return JsonResponse({'error': '缺少必填字段'}, status=400)

        prescriptions = MotionPrescription.objects.filter(
            name=name, id_card=id_card, phone=phone, doctor=doctor
        ).order_by('-upload_time')

        if not prescriptions.exists():
            return JsonResponse({'error': '未找到符合条件的处方记录'}, status=404)

        latest_prescription = prescriptions.first()
        other_prescriptions = prescriptions[1:]

        latest_data = {
            'name': latest_prescription.name,
            'id_card': latest_prescription.id_card,
            'phone': latest_prescription.phone,
            'doctor': latest_prescription.doctor,
            'limbPrescription': latest_prescription.limbPrescription,
            'pefPrescription': latest_prescription.pefPrescription,
            'respiratoryPrescription': latest_prescription.respiratoryPrescription,
            'swallowPrescription': latest_prescription.swallowPrescription,
            'tcePrescription': latest_prescription.tcePrescription,
            'upload_time': latest_prescription.upload_time,
            'is_active': latest_prescription.is_active,
        }

        other_data = list(other_prescriptions.values(
            'name', 'id_card', 'phone', 'doctor', 'limbPrescription', 'pefPrescription',
            'respiratoryPrescription', 'swallowPrescription', 'tcePrescription', 'upload_time', 'is_active'
        ))

        return JsonResponse({
            'latest_prescription': latest_data,
            'other_prescriptions': other_data
        })

    return JsonResponse({'error': '无效的请求方法'}, status=405)


def get_motion_prescriptions_with_urls(request):
    if request.method == 'GET':
        name = request.GET.get('name')
        id_card = request.GET.get('id_card')
        phone = request.GET.get('phone')
        doctor = request.GET.get('doctor')

        if not all([name, id_card, phone, doctor]):
            return JsonResponse({'error': '缺少必填字段'}, status=400)

        prescriptions = MotionPrescription.objects.filter(
            name=name, id_card=id_card, phone=phone, doctor=doctor
        ).order_by('-upload_time')

        if not prescriptions.exists():
            return JsonResponse({'error': '未找到符合条件的处方记录'}, status=404)

        latest_prescription = prescriptions.first()
        other_prescriptions = prescriptions[1:]

        def add_urls_to_prescription(prescription):
            for field in ['tcePrescription', 'swallowPrescription', 'respiratoryPrescription', 'pefPrescription', 'limbPrescription']:
                if field in prescription:
                    for item in prescription[field]:
                        motion = MotionList.objects.filter(name=item['name']).first()
                        if motion:
                            item['url'] = motion.urls
                            item['purpose'] = motion.purpose
                            item['details'] = motion.details

            return prescription

        latest_data = {
            'name': latest_prescription.name,
            'id_card': latest_prescription.id_card,
            'phone': latest_prescription.phone,
            'doctor': latest_prescription.doctor,
            'limbPrescription': latest_prescription.limbPrescription,
            'pefPrescription': latest_prescription.pefPrescription,
            'respiratoryPrescription': latest_prescription.respiratoryPrescription,
            'swallowPrescription': latest_prescription.swallowPrescription,
            'tcePrescription': latest_prescription.tcePrescription,
            'upload_time': latest_prescription.upload_time,
            'is_active': latest_prescription.is_active,
        }

        other_data = list(other_prescriptions.values(
            'name', 'id_card', 'phone', 'doctor', 'limbPrescription', 'pefPrescription',
            'respiratoryPrescription', 'swallowPrescription', 'tcePrescription', 'upload_time', 'is_active'
        ))

        urls_data = add_urls_to_prescription({
            'limbPrescription': latest_prescription.limbPrescription,
            'pefPrescription': latest_prescription.pefPrescription,
            'respiratoryPrescription': latest_prescription.respiratoryPrescription,
            'swallowPrescription': latest_prescription.swallowPrescription,
            'tcePrescription': latest_prescription.tcePrescription,
        })

        # 提取duration为null的元素
        def extract_null_duration_elements(prescription):
            null_duration_elements = []
            for field in ['limbPrescription', 'pefPrescription', 'respiratoryPrescription', 'swallowPrescription', 'tcePrescription']:
                if field in prescription:
                    for item in prescription[field]:
                        if item.get('duration') is None:
                            null_duration_elements.append(item)
            return null_duration_elements

        null_duration_elements = extract_null_duration_elements(latest_data)

        # 组合成一个序列
        sequence = []
        for element in null_duration_elements:
            motion = MotionList.objects.filter(name=element['name']).first()
            if motion:
                sequence.append({
                    'name': motion.name,
                    'weekly_training_count': motion.weekly_training_count,
                    'daily_training_count': motion.daily_training_count,
                    'reps_per_set': motion.reps_per_set,
                    'sets_per_session': motion.sets_per_session
                })

        return JsonResponse({
            'latest_prescription': latest_data,
            'other_prescriptions': other_data,
            'urls_data': urls_data,
            'motion_sequence': sequence
        })

    return JsonResponse({'error': '无效的请求方法'}, status=405)

def count_repetitive(rep_item):
    count = 0
    if isinstance(rep_item, list):
        for it in rep_item:
            if isinstance(it, dict):
                count += 1
            elif isinstance(it, list):
                count += len(it)
    return count
@csrf_exempt
def get_exercise_record(request):
    if request.method == 'POST':
        try:
            # 解析请求数据
            data = json.loads(request.body)
            id_card = data.get("id_card")
            name = data.get("name")
            phone = data.get("phone")
            doctor = data.get("doctor")
            current_time_str = data.get("current_time")

            if not all([id_card, name, phone, doctor, current_time_str]):
                return JsonResponse({"error": "缺少必填字段"}, status=400)

            try:
                current_time = datetime.strptime(current_time_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return JsonResponse({"error": "Invalid date format"}, status=400)

            # 获取该id_card、name、phone、doctor的所有记录
            records = ExerciseRecord.objects.filter(
                id_card=id_card, name=name, phone=phone, doctor=doctor
            ).order_by("-submission_time")

            if not records.exists():
                return JsonResponse({"message": "不存在"}, status=404)

            # 七天内运动的天数：记录条数（如果一天多条，也作为多次记录）
            seven_days_ago = timezone.now() - timedelta(days=7)
            count_within_seven_days = records.filter(submission_time__gte=seven_days_ago).count()

            # 统计当天的记录（以请求中的current_time为当天依据）
            start_of_day = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            day_records = records.filter(submission_time__range=(start_of_day, end_of_day))

            # 初始化当天运动统计数据
            today_motion_count = 0  # 今天运动的次数（组数）
            today_total_duration_minutes = 0  # 今天时长运动的分钟（continuousAction中duration之和）
            today_repetition_count = 0  # 今天次数运动的个数（repetitiveAction中字典个数）

            for record in day_records:
                # training_content为一个列表，每个元素为字符串格式的JSON数据
                if isinstance(record.training_content, list):
                    for group in record.training_content:
                        try:
                            group_data = json.loads(group)
                        except json.JSONDecodeError:
                            continue
                        today_motion_count += 1
                        # 累加continuousAction中duration之和
                        for action in group_data.get("continuousAction", []):
                            duration_str = action.get("duration", "0")
                            try:
                                today_total_duration_minutes += int(duration_str)
                            except ValueError:
                                continue
                        # 累加repetitiveAction中所有字典的个数
                        rep_item = group_data.get("repetitiveAction", [])
                        today_repetition_count += count_repetitive(rep_item)
                else:
                    try:
                        content = json.loads(record.training_content)
                        today_motion_count += 1
                        for action in content.get("continuousAction", []):
                            duration_str = action.get("duration", "0")
                            try:
                                today_total_duration_minutes += int(duration_str)
                            except ValueError:
                                continue
                        rep_item = content.get("repetitiveAction", [])
                        today_repetition_count += count_repetitive(rep_item)
                    except Exception:
                        continue

            return JsonResponse({
                "count_within_seven_days": count_within_seven_days,
                "today_motion_count": today_motion_count,
                "today_total_duration_minutes": today_total_duration_minutes,
                "today_repetition_count": today_repetition_count
            })

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def save_exercise_record(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            id_card = data.get('id_card')
            name = data.get('name')
            phone = data.get('phone')
            doctor = data.get('doctor')
            training_content = data.get('training_content')
            submission_time = timezone.now()

            if not all([id_card, name, phone, doctor, training_content]):
                return JsonResponse({'error': '缺少必填字段'}, status=400)

            # Check if there is an existing record for the same day
            start_of_day = submission_time.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            existing_record = ExerciseRecord.objects.filter(
                id_card=id_card, name=name, phone=phone, doctor=doctor,
                submission_time__range=(start_of_day, end_of_day)
            ).first()

            if existing_record:
                # Update the existing record
                existing_content = existing_record.training_content
                if isinstance(existing_content, list):
                    existing_content.append(training_content)
                else:
                    existing_content = [existing_content, training_content]
                existing_record.training_content = existing_content
                existing_record.submission_time = submission_time
                existing_record.save()
            else:
                # Create a new record
                ExerciseRecord.objects.create(
                    id_card=id_card,
                    name=name,
                    phone=phone,
                    doctor=doctor,
                    training_content=[training_content],  # Store as a list
                    submission_time=submission_time
                )

            return JsonResponse({'message': '记录保存成功'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def generate_audio_sequence(request):
    if request.method == 'POST':
        try:
            # 1. 解析body
            body = request.body.decode('utf-8')
            data = json.loads(body)
            motion_sequence = data.get('motion_sequence', [])
            
            logger.info(f"收到音频生成请求，动作序列长度: {len(motion_sequence)}")

            if not motion_sequence:
                return JsonResponse({"error": "No motion_sequence data provided."}, status=400)

            # 2. 启动异步任务
            from prescription.tasks import generate_audio_sequence_task
            
            logger.info("准备提交音频生成任务到 Celery")
            task = generate_audio_sequence_task.delay(motion_sequence)
            logger.info(f"任务已提交，ID: {task.id}")
            
            return JsonResponse({
                "task_id": task.id,
                "status": "PENDING",
                "message": "音频生成任务已启动，请使用task_id查询进度"
            })

        except Exception as e:
            logger.error(f"提交音频生成任务失败: {str(e)}", exc_info=True)
            return JsonResponse({"error": str(e)}, status=500)

    else:
        return JsonResponse({"error": "Only POST method is allowed."}, status=405)

@csrf_exempt
def get_audio_task_status(request):
    """查询音频生成任务状态"""
    if request.method == 'GET':
        task_id = request.GET.get('task_id')
        if not task_id:
            return JsonResponse({"error": "task_id is required"}, status=400)
        
        logger.info(f"查询任务状态: {task_id}")
        
        try:
            from celery.result import AsyncResult
            from celery import current_app
            
            # 获取任务结果
            result = AsyncResult(task_id)
            logger.debug(f"任务 {task_id} 当前状态: {result.state}")
            
            # 检查 worker 状态
            inspect = current_app.control.inspect()
            
            try:
                # 获取所有 worker 的状态
                stats = inspect.stats() or {}
                active_tasks = inspect.active() or {}
                reserved_tasks = inspect.reserved() or {}
                
                worker_count = len(stats)
                total_active = sum(len(tasks) for tasks in active_tasks.values())
                total_reserved = sum(len(tasks) for tasks in reserved_tasks.values())
                
                logger.info(f"Worker 状态: {worker_count} 个worker, {total_active} 个活跃任务, {total_reserved} 个等待任务")
                
            except Exception as inspect_error:
                logger.warning(f"无法获取 worker 状态: {str(inspect_error)}")
                worker_count = 0
            
            if result.state == 'PENDING':
                if worker_count == 0:
                    status_msg = "没有可用的 Celery worker，请启动 worker"
                    response = {
                        'task_id': task_id,
                        'state': result.state,
                        'status': status_msg,
                        'worker_info': f"发现 {worker_count} 个 worker"
                    }
                else:
                    # 检查任务是否在队列中
                    task_found = False
                    for worker_tasks in list(active_tasks.values()) + list(reserved_tasks.values()):
                        if any(task.get('id') == task_id for task in worker_tasks):
                            task_found = True
                            break
                    
                    if task_found:
                        status_msg = "任务在队列中等待处理"
                    else:
                        status_msg = "任务可能已丢失或尚未到达 worker"
                    
                    response = {
                        'task_id': task_id,
                        'state': result.state,
                        'status': status_msg,
                        'worker_info': f"发现 {worker_count} 个 worker"
                    }
            elif result.state == 'PROGRESS':
                info = result.info or {}
                response = {
                    'task_id': task_id,
                    'state': result.state,
                    'status': info.get('status', '进行中...'),
                    'progress': info.get('progress', 0)
                }
            elif result.state == 'SUCCESS':
                response = {
                    'task_id': task_id,
                    'state': result.state,
                    'status': '任务完成',
                    'result': result.result or {}
                }
            else:  # FAILURE, REVOKED, 等其他状态
                response = {
                    'task_id': task_id,
                    'state': result.state,
                    'status': '任务失败',
                    'error': str(result.info) if result.info else '未知错误'
                }
                
            return JsonResponse(response)
                
        except Exception as e:
            logger.error(f"获取任务状态时发生异常: {str(e)}", exc_info=True)
            return JsonResponse({
                "error": "服务器内部错误",
                "details": str(e)
            }, status=500)
    
    return JsonResponse({"error": "只允许GET方法。"}, status=405)

@csrf_exempt 
def download_audio_result(request):
    """下载音频生成结果"""
    if request.method == 'GET':
        task_id = request.GET.get('task_id')
        if not task_id:
            return JsonResponse({"error": "task_id is required"}, status=400)
            
        try:
            result = AsyncResult(task_id)
            
            if result.state != 'SUCCESS':
                return JsonResponse({"error": "Task not completed or failed"}, status=400)
            
            result_data = result.result
            audio_data = result_data.get('audio_data')
            filename = result_data.get('filename', 'final_audio.mp3')
            
            if not audio_data:
                return JsonResponse({"error": "No audio data found"}, status=404)
            
            # 解码base64数据
            audio_bytes = base64.b64decode(audio_data)
            
            response = HttpResponse(audio_bytes, content_type="audio/mpeg")
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Only GET method is allowed."}, status=405)


