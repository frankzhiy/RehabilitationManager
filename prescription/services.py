from .models import MotionList,MotionAudio


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
                # if limb in [0, 1, 2, 3] and entry.name in ["神经肌肉电刺激"]:
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
        "duration": entry.duration,
        "object": entry.object,
        "applicability": entry.applicability,
        "purpose": entry.purpose,
        "details": entry.details,
        "is_recommended": False
    }




# services.py

from .models import MotionAudio

def get_audio_url(name: str, category: str = None) -> str:
    """
    从数据库里获取匹配 name 和可选category 的音频URL。
    """
    if category:
        audio_obj = MotionAudio.objects.filter(name=name, category=category).first()
    else:
        audio_obj = MotionAudio.objects.filter(name=name).first()
    return audio_obj.oss_url if audio_obj else ""
def build_audio_url_sequence(motion_sequence):
    """
    根据 motion_sequence 构建一个“音频与静音”混合的列表，供后端合并时使用。
    除了 "第","组","1","2"...,"12" 这些不加静音，其余音频后面都插入一个短静音。
    """
    audio_url_sequence = []

    # 定义那些【不插入静音】的关键短语
    SKIP_SILENCE_NAMES = {"第", "组"} | {str(i) for i in range(1, 13)}
    # 例如: {"第","组","1","2","3",...,"12"}

    # 定义一个辅助函数：将音频加进列表，并在其后插入静音（除非音频在跳过列表内）
    def add_audio_and_maybe_silence(name: str):
        """将对应 name 的音频url加入列表，并视情况插入短静音。"""
        if not name:
            return
        url = get_audio_url(name)
        if not url:
            return
        # 先放 (type="audio", url)
        audio_url_sequence.append(("audio", url))

        # 若 name 不在 SKIP_SILENCE_NAMES，就额外加一个短静音
        if name not in SKIP_SILENCE_NAMES:
            audio_url_sequence.append(("silence", 1000))  # 300毫秒静音，可自行调整

    # 1. "准备一下"
    add_audio_and_maybe_silence("准备一下")

    # 2. 5下嘟声 (每次都是1秒)
    beep_url = get_audio_url("嘟")
    for _ in range(5):
        if beep_url:
            audio_url_sequence.append(("audio", beep_url))
    # 嘟声播完后，如果你想再加个短暂停，可以：
    audio_url_sequence.append(("silence", 300))  # 播完嘟再稍停一会儿

    # 3. "开始运动"
    add_audio_and_maybe_silence("开始运动")

    total_actions = len(motion_sequence)
    for index, motion_item in enumerate(motion_sequence, start=1):
        # 判断第一个、中间、最后一个动作
        if index == 1:
            # 第一个动作
            add_audio_and_maybe_silence("第一个动作")
        elif index == total_actions:
            # 最后一个动作
            add_audio_and_maybe_silence("最后一个动作")
        else:
            # 中间动作
            add_audio_and_maybe_silence("下一个动作")

        # 播“准备一下”
        add_audio_and_maybe_silence("准备一下")

        # 播动作名称
        action_name = motion_item.get("name", "")
        add_audio_and_maybe_silence(action_name)

        # 播组数 & 嘟声
        daily_count = motion_item.get("daily_training_count", 1)
        reps_per_set = motion_item.get("reps_per_set", 1)
        for d in range(daily_count):
            add_audio_and_maybe_silence("第")
            add_audio_and_maybe_silence(str(d + 1))
            add_audio_and_maybe_silence("组")

            beep_count = 2 * reps_per_set
            for _ in range(beep_count):
                if beep_url:
                    audio_url_sequence.append(("audio", beep_url))
            # 这里播完了这“一组”的动作嘟声，可以再加间隔也行（看需求）
            audio_url_sequence.append(("silence", 300))

    # 最后播“完成练习”
    add_audio_and_maybe_silence("完成练习")

    return audio_url_sequence

# def build_audio_url_sequence(motion_sequence):
#     audio_url_sequence = []
#
#     # 1. 播放 "准备一下"
#     prepare_audio = get_audio_url("准备一下")
#     if prepare_audio:
#         audio_url_sequence.append(prepare_audio)
#
#     # 2. 播放5个 "嘟" 作为等待时长 (可按需求调整)
#     beep_audio = get_audio_url("嘟")
#     for _ in range(5):
#         audio_url_sequence.append(beep_audio)
#
#     # 3. "开始运动"
#     start_audio = get_audio_url("开始运动")
#     if start_audio:
#         audio_url_sequence.append(start_audio)
#
#     # 4. 依次处理每个动作
#     total_actions = len(motion_sequence)
#     for index, motion_item in enumerate(motion_sequence, start=1):
#         # 4.1 判断是第一个动作、最后一个动作，还是中间动作
#         if index == 1:
#             # 如果是第一个动作
#             first_action_audio = get_audio_url("第一个动作")
#             if first_action_audio:
#                 audio_url_sequence.append(first_action_audio)
#         elif index == total_actions:
#             # 如果是最后一个动作
#             last_action_audio = get_audio_url("最后一个动作")
#             if last_action_audio:
#                 audio_url_sequence.append(last_action_audio)
#         else:
#             # 中间动作
#             next_action_audio = get_audio_url("下一个动作")
#             if next_action_audio:
#                 audio_url_sequence.append(next_action_audio)
#
#         # 4.2 “准备一下”
#         prep_audio = get_audio_url("准备一下")
#         if prep_audio:
#             audio_url_sequence.append(prep_audio)
#
#         # 4.3 动作名称
#         action_name = motion_item.get("name", "")
#         action_audio = get_audio_url(action_name)
#         if action_audio:
#             audio_url_sequence.append(action_audio)
#
#         # 4.4 播放组数和嘟声
#         daily_count = motion_item.get("daily_training_count", 1)
#         reps_per_set = motion_item.get("reps_per_set", 1)
#         for d in range(daily_count):
#             de_audio = get_audio_url("第")
#             if de_audio:
#                 audio_url_sequence.append(de_audio)
#
#             number_audio = get_audio_url(str(d+1))
#             if number_audio:
#                 audio_url_sequence.append(number_audio)
#
#             group_audio = get_audio_url("组")
#             if group_audio:
#                 audio_url_sequence.append(group_audio)
#
#             # 2 秒 * reps_per_set 个“嘟”
#             beep_count = 2 * reps_per_set
#             for _ in range(beep_count):
#                 audio_url_sequence.append(beep_audio)
#
#     # 5. 所有动作结束后，播放“完成练习”
#     finish_audio = get_audio_url("完成练习")
#     if finish_audio:
#         audio_url_sequence.append(finish_audio)
#
#     return audio_url_sequence
