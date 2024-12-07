# service.py

from .models import PatientDiscomfortRecordWarn


def process_discomfort_record(record):
    """
    当指定的字段中有一项或多项为 True 时，将记录保存到 PatientDiscomfortRecordWarn。
    并将为 True 的字段转换为中文描述，保存到 alert_type 字段中。

    :param record: 已保存的 PatientDiscomfortRecord 实例。
    """
    # 指定需要检查的字段列表及其对应的中文描述
    fields_to_check = {
        'breathingWorsened': '呼吸困难加重',
        'coughWorsened': '咳嗽加重',
        'fever': '发热',
        'sputumIncreased': '痰量增加',
        'fastHeartbeat': '心跳过快',
        'sleepPatternChange': '睡眠模式改变',
        'swollenLegs': '腿部肿胀'
    }

    # 初始化一个标志，表示是否需要保存到 Warn 表
    should_warn = False
    alert_descriptions = []

    # 检查每个字段的值
    for field_name, description in fields_to_check.items():
        field_value = getattr(record, field_name, False)
        if field_value:
            should_warn = True
            alert_descriptions.append(description)

    if should_warn:
        # 将中文描述列表合并成一个字符串，使用逗号分隔
        alert_type_str = '，'.join(alert_descriptions)

        # 保存到 PatientDiscomfortRecordWarn 表
        warn_record = PatientDiscomfortRecordWarn(
            id_card=record.id_card,
            phone=record.phone,
            doctor=record.doctor,
            name=record.name,
            comfort=record.comfort,
            appetiteLoss=record.appetiteLoss,
            breathing=record.breathing,
            breathingWorsened=record.breathingWorsened,
            cough=record.cough,
            coughWorsened=record.coughWorsened,
            fastHeartbeat=record.fastHeartbeat,
            fatigue=record.fatigue,
            fever=record.fever,
            sleepPatternChange=record.sleepPatternChange,
            sputum=record.sputum,
            sputumIncreased=record.sputumIncreased,
            swollenLegs=record.swollenLegs,
            weightLoss=record.weightLoss,
            datetime=record.datetime,
            is_active=True,
            alert_type=alert_type_str  # 设置预警类型
        )
        warn_record.save()
