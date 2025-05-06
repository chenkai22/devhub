from django.shortcuts import render, get_object_or_404
from django.views import View
from django.contrib.auth import authenticate, login
from django.http import JsonResponse, HttpResponse
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from .models import Ticket, TicketSerializer, SystemConfig
import json
from django.core.paginator import Paginator
from files.models import Attachment
from datetime import datetime
from django.db import transaction, models
from user.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from elasticsearch_dsl import Q
from .documents import TicketDocument
import pandas as pd
from io import BytesIO
from django.db.models import Case, Value, When
from django.utils import timezone
from django_redis import get_redis_connection
from celery.schedules import crontab
from .tasks import check_ticket_deadlines


class SearchView(View):

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        pageNum = data["pageNum"]  # 当前页
        pageSize = data["pageSize"]  # 每页大小
        query = data["query"]  # 查询参数
        ticket_objs = Ticket.objects.filter(title__icontains=query)
        ticket_objs = TicketSerializer(instance=ticket_objs, many=True).data

        ticketListPage = Paginator(ticket_objs, pageSize).page(pageNum)
        obj_tickets = ticketListPage.object_list

        total = Ticket.objects.filter(title__icontains=query).count()
        return JsonResponse({"code": 200, "ticketList": obj_tickets, "total": total})


class SaveView(View):

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        print(data)
        if data["id"] == -1:  # 添加
            today_str = datetime.now().strftime("%Y%m%d")
            with transaction.atomic():
                # 查找当日最新工单号
                last_ticket = (
                    Ticket.objects.filter(ticket_code__startswith=today_str)
                    .select_for_update()
                    .order_by("-ticket_code")
                    .first()
                )

                if last_ticket:
                    sequence = int(last_ticket.ticket_code[-4:]) + 1
                else:
                    sequence = 1

                ticket_code = f"{today_str}{sequence:04d}"
            ticket = Ticket(
                title=data["title"],
                desc=data["desc"],
                find_user=request.user,
                handler=User.objects.get(id=data["handler"]),
                deadline=datetime.strptime(data["deadline"], "%Y-%m-%dT%H:%M:%S"),
                ticket_code=ticket_code,
            )
            ticket.save()
            print("附件信息为", data)
            if "attachments" in data:
                attachments = Attachment.objects.filter(
                    id__in=[i["file_id"] for i in data["attachments"]]
                )
                ticket.attachments.set(attachments)
        else:  # 修改
            ticket_obj = Ticket.objects.get(id=data["id"])
            ticket_obj.title = data["title"]
            ticket_obj.desc = data["desc"]
            ticket_obj.handler = User.objects.get(id=data["handler"])
            ticket_obj.deadline = datetime.strptime(
                data["deadline"], "%Y-%m-%dT%H:%M:%S"
            )
            ticket_obj.save()
        return JsonResponse({"code": 200})


class ActionView(View):

    def get(self, request):
        """
        根据id获取工单信息
        :param request:
        :return:
        """
        id = request.GET.get("id")
        ticket_object = Ticket.objects.get(id=id)
        return JsonResponse(
            {"code": 200, "ticket": TicketSerializer(ticket_object).data}
        )


class ESTicketSearch(APIView):
    def post(self, request):
        query = request.data.get("query", "")
        page = int(request.data.get("page", 1))
        size = int(request.data.get("size", 10))

        search = TicketDocument.search()

        # 构建查询条件
        q = Q(
            "multi_match",
            query=query,
            fields=["title^3", "desc", "ticket_code", "status_display"],
        )

        response = search.query(q)[(page - 1) * size : page * size].execute()

        formatted_hits = []
        for hit in response:
            hit_data = hit.to_dict()
            # 格式化截止时间
            hit_data["deadline"] = (
                hit.deadline.strftime("%Y-%m-%d %H:%M") if hit.deadline else ""
            )
            # 获取附件详情
            hit_data["attachments"] = [
                a.id for a in Attachment.objects.filter(id__in=(hit.attachments or []))
            ]
            formatted_hits.append(hit_data)

        return Response(
            {
                "hits": {
                    "hits": formatted_hits,
                    "total": {"value": response.hits.total.value},
                }
            }
        )


class TicketSuggest(APIView):
    def post(self, request):
        text = request.data.get("text", "")
        field = request.data.get("field", "title")

        search = TicketDocument.search()

        # 建议查询
        suggest_name = "ticket_suggestions"
        search = search.suggest(
            suggest_name,
            text,
            completion={"field": "suggest", "size": 5},  # 使用根节点的 suggest 字段
        )

        suggestions = []
        for option in search.execute().suggest[suggest_name][0]["options"]:
            suggestions.append({"text": option.text, "count": 1})  # 使用固定值

        suggest_response = search.execute()
        return Response(
            {
                "suggestions": [
                    {"text": option.text, "count": 1}  # 使用固定值
                    for option in suggest_response.suggest[suggest_name][0]["options"]
                ]
            }
        )


class TicketExportView(APIView):
    def post(self, request):
        # 获取请求参数
        ids = request.data.get("ids", [])
        export_all = request.data.get("export_all", False)
        search_query = request.data.get("query", "")

        # 构建基础查询
        if export_all:
            # 获取全部搜索结果（需要与列表接口相同的查询条件）
            queryset = Ticket.objects.all()
            if search_query:
                queryset = queryset.filter(
                    Q(ticket_code__icontains=search_query)
                    | Q(title__icontains=search_query)
                    | Q(desc__icontains=search_query)
                )
        else:
            # 根据ID列表查询
            queryset = Ticket.objects.filter(id__in=ids)

        # 转换为DataFrame
        data = queryset.values("ticket_code", "title", "status", "deadline")
        df = pd.DataFrame(list(data))
        status_choices = dict(Ticket.STATUS_CHOICES)
        df["status_display"] = df["status"].map(status_choices)

        # 重命名列
        df = df[["ticket_code", "title", "status_display", "deadline"]]
        df.rename(
            columns={
                "ticket_code": "工单号",
                "title": "主题",
                "status_display": "状态",
                "deadline": "截止时间",
            },
            inplace=True,
        )

        # 生成Excel文件
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False)

        # 创建HTTP响应
        response = HttpResponse(
            output.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        filename = f"tickets_export_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        response["Content-Disposition"] = f"attachment; filename*=utf-8''{filename}"
        response["Cache-Control"] = "no-store"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"

        return response


class TicketStatusView(APIView):
    def put(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)
        new_status = request.data.get("status")

        if new_status not in dict(Ticket.STATUS_CHOICES).keys():
            return Response({"error": "无效状态"}, status=400)

        ticket.status = new_status
        ticket.save()
        return Response({"code": 200, "message": "状态更新成功"})


class TicketKanbanView(APIView):
    def get(self, request):
        tickets = Ticket.objects.all().values(
            "id", "ticket_code", "title", "status", "deadline", "update_time"
        )

        # 使用Redis缓存剩余时间（示例）
        redis_client = get_redis_connection("default")
        for ticket in tickets:
            cache_key = f"ticket:{ticket['id']}:countdown"
            if not redis_client.exists(cache_key):
                deadline = ticket["deadline"]
                remaining = deadline - timezone.now()
                redis_client.setex(cache_key, 3600, remaining.total_seconds())

        return Response(list(tickets))


class WarningSettingsView(APIView):
    # 默认配置
    DEFAULT_SETTINGS = {"xHours": 72, "yHours": 24, "zHours": 2}

    def get(self, request):
        try:
            settings = {}
            for key in self.DEFAULT_SETTINGS.keys():
                # 获取配置项，不存在则使用默认值
                config, _ = SystemConfig.objects.get_or_create(
                    key=key, defaults={"value": str(self.DEFAULT_SETTINGS[key])}
                )
                settings[key] = int(config.value)
            return Response(settings)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def post(self, request):
        try:
            # 验证并保存配置
            for key, value in request.data.items():
                if key not in self.DEFAULT_SETTINGS:
                    continue
                # 更新或创建配置记录
                SystemConfig.objects.update_or_create(
                    key=key, defaults={"value": str(value)}
                )
            return Response({"code": 200, "message": "设置保存成功"})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @classmethod
    def get_celery_schedule(cls):
        return {
            "check-ticket-deadlines": {
                "task": "ticket.tasks.check_ticket_deadlines",
                "schedule": crontab(minute="*/15"),  # 每15分钟检查一次
                "options": {"queue": "notifications"},
            }
        }


class TicketReportView(APIView):
    def get(self, request):
        total = Ticket.objects.count()
        completed = Ticket.objects.filter(status="handled").count()
        return Response(
            {
                "pending": Ticket.objects.filter(status="handle").count(),
                "processing": Ticket.objects.filter(status="handling").count(),
                "completed": completed,
                "completionRate": round(
                    (completed / total * 100) if total > 0 else 0, 2
                ),
            }
        )


class UserRankingView(APIView):
    def get(self, request):
        users = User.objects.annotate(
            count=models.Count("handler_ticket"),
            totalTime=models.ExpressionWrapper(
                models.F("handler_ticket__deadline")
                - models.F("handler_ticket__create_time"),
                output_field=models.DurationField(),
            ),
        ).order_by("-count")

        return Response(
            [
                {
                    "id": u.id,
                    "username": u.username,
                    "count": u.count,
                    "totalTime": (
                        u.totalTime.total_seconds() / 3600 if u.totalTime else 0
                    ),
                }
                for u in users
            ]
        )
