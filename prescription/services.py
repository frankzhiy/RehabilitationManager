from .models import MotionList

def get_recommendations(assessments):
    recommendations = []

    # Swallow 条件判断
    swallow = assessments.get('swallow', '')
    if swallow:
        swallow_entries = MotionList.objects.filter(category="吞咽")
        for entry in swallow_entries:
            entry_data = _get_entry_data(entry)
            if swallow == "正常":
                entry_data["is_recommended"] = False
            elif swallow == "可疑" and entry.name in ["进食指导", "进食姿势", "吞咽代偿姿势"]:
                entry_data["is_recommended"] = True
            elif swallow == "异常":
                entry_data["is_recommended"] = True
            recommendations.append(entry_data)
    else:
        recommendations.append({"message": "未获取吞咽数据，无法推荐"})

    # Respiratory 条件判断
    respiratory = assessments.get('respiratory', '')
    if respiratory:
        try:
            mip, mep = map(float, respiratory.split(','))
            respiratory_entries = MotionList.objects.filter(category="呼吸肌")
            for entry in respiratory_entries:
                entry_data = _get_entry_data(entry)
                if mip < -4 and mep < 7.5 and entry.name in ["呼吸训练器", "加压腹式呼吸法", "体外膈肌反搏呼吸", "暗示呼吸法", "辅助呼吸肌放松"]:
                    entry_data["is_recommended"] = True
                elif mip < -4 and mep > 20 and entry.name in ["呼吸训练器", "加压腹式呼吸法", "体外膈肌反搏呼吸", "暗示呼吸法", "辅助呼吸肌放松"]:
                    entry_data["is_recommended"] = True
                elif mip > -7 and mep < 7.5 and entry.name in ["吹蜡烛法", "缩唇呼吸", "呼吸训练器", "暗示呼吸法"]:
                    entry_data["is_recommended"] = True
                elif mip > -7 and mep > 20 and entry.name in ["耸肩运动", "辅助呼吸肌放松", "暗示呼吸法", "加压腹式呼吸法"]:
                    entry_data["is_recommended"] = True
                recommendations.append(entry_data)
        except ValueError:
            recommendations.append({"message": "未获取有效的呼吸肌数据，无法推荐"})

    # Limb 条件判断
    limb = assessments.get('limb', '')
    if limb:
        try:
            limb = int(limb)
            limb_entries = MotionList.objects.filter(category="四肢肌")
            for entry in limb_entries:
                entry_data = _get_entry_data(entry)
                if limb in [0, 1, 2, 3] and entry.name in ["神经肌肉电刺激", "助力训练"]:
                    entry_data["is_recommended"] = True
                elif limb in [4, 5] and entry.name in ["弹力带拉伸", "弹力带蹬腿"]:
                    entry_data["is_recommended"] = True
                recommendations.append(entry_data)
        except ValueError:
            recommendations.append({"message": "未获取有效的四肢肌数据，无法推荐"})

    # PEF 条件判断
    pef = assessments.get('pef', '')
    if pef:
        try:
            pef = float(pef)
            pef_entries = MotionList.objects.filter(category="排痰")
            for entry in pef_entries:
                entry_data = _get_entry_data(entry)
                if pef >= 250 and entry.name == "ACBT":
                    entry_data["is_recommended"] = True
                elif pef < 250 and entry.name == "体位引流":
                    entry_data["is_recommended"] = True
                recommendations.append(entry_data)
        except ValueError:
            recommendations.append({"message": "未获取有效的排痰数据，无法推荐"})

    # TCE 条件判断
    tce = assessments.get('tce', '')
    if tce:
        try:
            tce = float(tce)
            tce_entries = MotionList.objects.filter(category="胸廓")
            for entry in tce_entries:
                entry_data = _get_entry_data(entry)
                if tce < 2.5 and entry.name in ["肋骨松动", "胸廓扩张", "体位管理"]:
                    entry_data["is_recommended"] = True
                recommendations.append(entry_data)
        except ValueError:
            recommendations.append({"message": "未获取有效的胸廓数据，无法推荐"})

    return recommendations

def _get_entry_data(entry):
    return {
        "action_id": entry.action_id,
        "name": entry.name,
        "category": entry.category,
        "weekly_training_count": entry.weekly_training_count,
        "daily_training_count": entry.daily_training_count,
        "sets_per_session": entry.sets_per_session,
        "reps_per_set": entry.reps_per_set,
        "training_method": entry.training_method,
        "intensity": entry.intensity,
        "is_recommended": False
    }
