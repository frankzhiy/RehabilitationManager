from django.db import models

class MotionList(models.Model):
    # 定义数据表的字段
    action_id = models.AutoField(primary_key=True, verbose_name="动作ID")  # 自增ID
    name = models.CharField(max_length=100, verbose_name="动作名称")
    category = models.CharField(max_length=50, verbose_name="动作分类")
    is_recommended = models.BooleanField(default=False, verbose_name="是否推荐")
    weekly_training_count = models.IntegerField(default=7, verbose_name="每周训练次数")
    daily_training_count = models.IntegerField(default=2, verbose_name="每日训练次数")
    sets_per_session = models.IntegerField(default=5, verbose_name="每次训练组数")
    reps_per_set = models.IntegerField(default=6, verbose_name="每组训练个数")
    training_method = models.CharField(max_length=50, default="时长", verbose_name="单一动作训练方式")
    intensity = models.CharField(max_length=50, blank=True, null=True, verbose_name="动作强度")

    def __str__(self):
        return f"{self.name} - {self.category}"

    class Meta:
        verbose_name = "运动列表"
        verbose_name_plural = "运动列表"

class MotionPrescription(models.Model):
    doctor = models.CharField(max_length=100, verbose_name="医生")
    id_card = models.CharField(max_length=18, verbose_name="身份证号")
    limbPrescription = models.JSONField(default=list, verbose_name="四肢处方")
    name = models.CharField(max_length=100, verbose_name="姓名")
    pefPrescription = models.JSONField(default=list, verbose_name="PEF处方")
    phone = models.CharField(max_length=20, verbose_name="电话")
    respiratoryPrescription = models.JSONField(default=list, verbose_name="呼吸处方")
    swallowPrescription = models.JSONField(default=list, verbose_name="吞咽处方")
    tcePrescription = models.JSONField(default=list, verbose_name="TCE处方")
    upload_time = models.DateTimeField(verbose_name="上传时间")
    is_active = models.BooleanField(default=True, verbose_name="是否激活")


    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "处方详情"
        verbose_name_plural = "处方详情"