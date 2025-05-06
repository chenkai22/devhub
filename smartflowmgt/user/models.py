from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.contrib.postgres.fields import ArrayField
from rest_framework import serializers


class Department(models.Model):  # 新增部门模型
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class User(AbstractUser):
    ROLE_CHOICES = (
        ("client", "客户"),
        ("agent", "客服"),
        ("admin", "管理员"),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="client")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    skills = ArrayField(models.CharField(max_length=20), default=list)

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_set",  # 添加反向关系名称
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_set",  # 添加反向关系名称
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    class Meta:
        db_table = "user_user"


class UserSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(format="%Y:%m:%d %H:%M:%S", read_only=True)
    last_login = serializers.DateTimeField(format="%Y:%m:%d %H:%M:%S", read_only=True)

    class Meta:
        model = User
        fields = "__all__"
