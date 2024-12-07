# service.py
from .models import PatientADLWarn, PatientCATWarn, PatientmMRCWarn, PatientCCQWarn
from django.utils import timezone


def process_adl_data(record):
    """
    处理 ADL 数据，当 score 小于 75 时，保存到 PatientADLWarn，并设置 Barthel指数。

    :param record: 已保存的 PatientADL 实例。
    """
    try:
        score = int(record.score)
    except (ValueError, TypeError):
        score = 0

    if score < 75:
        # 根据 score 的范围设置 Barthel指数
        if 50 <= score <= 70:
            barthel_index = "中度功能缺失"
        elif 25 <= score <= 45:
            barthel_index = "严重功能缺失"
        elif 0 <= score <= 20:
            barthel_index = "极严重功能缺失"
        else:
            barthel_index = "完全自理"

        # 保存到 PatientADLWarn 表
        warn_record = PatientADLWarn(
            hygiene=record.hygiene,
            stool=record.stool,
            urinating=record.urinating,
            bathing=record.bathing,
            dressing=record.dressing,
            feeding=record.feeding,
            stairs=record.stairs,
            toileting=record.toileting,
            transferring=record.transferring,
            walking=record.walking,
            score=record.score,
            doctor=record.doctor,
            id_card=record.id_card,
            name=record.name,
            phone=record.phone,
            uploadTime=record.uploadTime,
            isbydoctor=record.isbydoctor,
            is_active=True,
            barthel_index=barthel_index
        )
        warn_record.save()
def process_cat_data(record):
    """
    处理 CAT 数据，当 score 大于 20 时，保存到 PatientCATWarn，并设置 CAT指数。

    :param record: 已保存的 PatientCAT 实例。
    """
    try:
        score = int(record.score)
    except (ValueError, TypeError):
        score = 0

    if score > 20:
        # 根据 score 的范围设置 CAT指数
        if 20 < score <= 30:
            cat_index = "严重"
        elif score > 30:
            cat_index = "非常严重"
        else:
            cat_index = "未知"

        # 保存到 PatientCATWarn 表
        warn_record = PatientCATWarn(
            chestTightness=record.chestTightness,
            confidenceLeavingHome=record.confidenceLeavingHome,
            cough=record.cough,
            energyLevels=record.energyLevels,
            homeActivities=record.homeActivities,
            phlegm=record.phlegm,
            shortnessOfBreath=record.shortnessOfBreath,
            sleepQuality=record.sleepQuality,
            score=record.score,
            doctor=record.doctor,
            id_card=record.id_card,
            name=record.name,
            phone=record.phone,
            uploadTime=record.uploadTime,
            isbydoctor=record.isbydoctor,
            is_active=True,
            cat_index=cat_index
        )
        warn_record.save()


def process_mmrc_data(record):
    """
    处理 mMRC 数据，当 score >= 2 时，保存到 PatientmMRCWarn，并设置 mMRC指数。

    :param record: 已保存的 PatientmMRC 实例。
    """
    try:
        score = int(record.score)
    except (ValueError, TypeError):
        score = 0

    if score >= 2:
        mmrc_index = "症状多"
        # 保存到 PatientmMRCWarn 表
        warn_record = PatientmMRCWarn(
            degreeOfBreathing=record.degreeOfBreathing,
            score=record.score,
            doctor=record.doctor,
            id_card=record.id_card,
            name=record.name,
            phone=record.phone,
            uploadTime=record.uploadTime,
            isbydoctor=record.isbydoctor,
            is_active=True,
            mmrc_index=mmrc_index
        )
        warn_record.save()


def process_ccq_data(record):
    """
    处理 CCQ 数据，当 score ≥ 25 时，保存到 PatientCCQWarn，并设置 CCQ指数。

    :param record: 已保存的 PatientCCQ 实例。
    """
    try:
        score = int(record.score)
    except (ValueError, TypeError):
        score = 0

    # 根据 score 的值设置 CCQ指数
    if score >= 25:
        ccq_index = "高风险"
        # 保存到 PatientCCQWarn 表
        warn_record = PatientCCQWarn(
            breathing=record.breathing,
            chestTightness=record.chestTightness,
            dailyActivities=record.dailyActivities,
            mentalHealth=record.mentalHealth,
            morningSymptoms=record.morningSymptoms,
            phlegm=record.phlegm,
            score=record.score,
            doctor=record.doctor,
            id_card=record.id_card,
            name=record.name,
            phone=record.phone,
            uploadTime=record.uploadTime,
            isbydoctor=record.isbydoctor,
            is_active=True,
            ccq_index=ccq_index
        )
        warn_record.save()