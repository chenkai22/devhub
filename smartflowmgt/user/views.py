from django.shortcuts import render
from django.views import View
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from .models import UserSerializer, User
from menu.models import Menu, MenuSerializer
import json
from django.core.paginator import Paginator


class RefreshTokenView(View):
    def post(self, request):
        refresh_token = json.loads(request.body).get("refresh", "")
        if refresh_token:
            try:
                refresh = RefreshToken(refresh_token)
                access_token = str(refresh.access_token)
                return JsonResponse(
                    {"code": 200, "token": access_token, "msg": "刷新成功"}
                )
            except Exception as e:
                print(str(e))
                return JsonResponse({"code": 400, "msg": "刷新失败"})


# Create your views here.
class LoginView(View):
    def get_menu_list(self, role):
        menu_list = Menu.objects.filter(role__contains=role).order_by(
            "-parent_id", "order"
        )
        return menu_list

    def buildTreeMenu(self, menus):
        tree = []
        for menu in menus:
            print(menu.parent_id)
            if menu.parent_id is None:
                tree.append(menu)
            else:
                for node in tree:
                    if node.id == menu.parent_id:
                        if not hasattr(node, "children"):
                            node.children = list()
                        node.children.append(menu)
        return tree

    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")
        except json.JSONDecodeError:
            return JsonResponse({"code": 400, "msg": "无效的JSON格式"})
        user = authenticate(username=username, password=password)
        print(user, password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            menus = self.get_menu_list(user.role)
            print("1", menus)
            menus = self.buildTreeMenu(menus)
            print("2", menus)
            menus = MenuSerializer(menus, many=True).data
            print("3", menus)

            login(request, user)
            return JsonResponse(
                {
                    "code": 200,
                    "token": access_token,
                    "refresh_token": str(refresh),
                    "user": UserSerializer(user).data,
                    "menuList": menus,
                    "msg": "登录成功",
                }
            )
        else:
            return JsonResponse({"code": 400, "msg": "登录失败"})


class SearchView(View):

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        pageNum = data["pageNum"]  # 当前页
        pageSize = data["pageSize"]  # 每页大小
        query = data["query"]  # 查询参数
        user_objs = User.objects.filter(username__icontains=query)
        user_objs = UserSerializer(instance=user_objs, many=True).data
        print("1111", user_objs)
        userListPage = Paginator(user_objs, pageSize).page(pageNum)
        obj_users = userListPage.object_list
        print("2222", obj_users)
        total = User.objects.filter(username__icontains=query).count()
        return JsonResponse({"code": 200, "userList": obj_users, "total": total})


class UserListView(View):

    def get(self, request):
        user_objs = User.objects.all()
        user_objs = UserSerializer(instance=user_objs, many=True).data
        return JsonResponse(
            {"code": 200, "data": UserSerializer(user_objs, many=True).data}
        )


class SaveView(View):

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        print(data)
        if data["id"] == -1:  # 添加
            User.objects.create_user(
                username=data["username"],
                is_superuser=False,
                email=data["email"],
                role="client",
                password="123456",
            )
        else:  # 修改
            user_obj = User.objects.get(id=data["id"])
            user_obj.username = data["username"]
            user_obj.email = data["email"]
            user_obj.is_active = data["is_active"]
            user_obj.save()
        return JsonResponse({"code": 200})


class ActionView(View):

    def get(self, request):
        """
        根据id获取用户信息
        :param request:
        :return:
        """
        id = request.GET.get("id")
        user_object = User.objects.get(id=id)
        return JsonResponse({"code": 200, "user": UserSerializer(user_object).data})

    def delete(self, request):
        """
        删除操作
        :param request:
        :return:
        """
        idList = request.GET.get("ids", []).split(",")
        User.objects.filter(id__in=idList).delete()
        return JsonResponse({"code": 200})


class CheckView(View):

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        username = data["username"]
        print("username=", username)
        if User.objects.filter(username=username).exists():
            return JsonResponse({"code": 500})
        else:
            return JsonResponse({"code": 200})


class ActiveView(View):
    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        id = data["id"]
        is_active = data["is_active"]
        user_object = User.objects.get(id=id)
        user_object.is_active = is_active
        user_object.save()
        return JsonResponse({"code": 200})


class PasswordView(View):

    def get(self, request):
        id = request.GET.get("id")
        user_object = User.objects.get(id=id)
        user_object.set_password("123456")
        user_object.save()
        return JsonResponse({"code": 200})
