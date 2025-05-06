from contextlib import nullcontext
from enum import unique
from django.db import models
from rest_framework import serializers


# Create your models here.
class Menu(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="菜单名称")
    url = models.CharField(max_length=255, unique=True, verbose_name="菜单URL")
    icon = models.CharField(max_length=255, null=True, verbose_name="菜单图标")
    parent_id = models.IntegerField(null=True, verbose_name="父菜单ID")
    order = models.IntegerField(null=True, verbose_name="菜单排序")
    path = models.CharField(max_length=255, null=True, verbose_name="菜单路径")
    component = models.CharField(max_length=255, null=True, verbose_name="菜单组件")
    menu_type = models.CharField(max_length=255, null=True, verbose_name="菜单类型")
    permission = models.CharField(max_length=255, null=True, verbose_name="权限标识")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    role = models.CharField(max_length=255, null=True, verbose_name="角色")

    def __lt__(self, other):
        return self.order < other.order

    def __str__(self):
        return self.name

    class Meta:
        db_table = "menu"


class MenuSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    def get_children(self, obj):
        if hasattr(obj, "children"):
            serializerMenuList: list[MenuSerializer] = list()
            for menu in obj.children:
                serializerMenuList.append(MenuSerializer2(menu).data)
            return serializerMenuList

    class Meta:
        model = Menu
        fields = "__all__"


class MenuSerializer2(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = "__all__"
