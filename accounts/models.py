from django.contrib.auth.models import User
from django.db import models


class UserInfo(models.Model):
    """
    用户表
    """
    role = models.IntegerField(verbose_name="角色", choices=((1, "用户"),(2, "管理员")), default=1)
    username = models.CharField(verbose_name="用户名", max_length=32, db_index=True)
    password = models.CharField(verbose_name="密码", max_length=64)
    token = models.CharField(verbose_name="TOKEN", max_length=64, null=True, blank=True, db_index=True)
    status = models.IntegerField(verbose_name="状态", choices=((0, "不活跃"), (1, "活跃")), default=0)


class ChatMessage(models.Model):
    """
    聊天表
    """
    username = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class UploadedFile(models.Model):
    """
    文件上传表
    """
    username = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)