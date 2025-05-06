from celery import shared_task
from .models import Ticket, SystemConfig
from django.utils import timezone
from user.models import User
import math


@shared_task
def check_ticket_deadlines():
    # 获取预警配置
    config = {
        key: int(SystemConfig.objects.get(key=key).value)
        for key in ["xHours", "yHours", "zHours"]
    }

    now = timezone.now()

    # 查询需要监控的工单（待处理和处理中状态）
    tickets = Ticket.objects.filter(status__in=["handle", "handling"]).select_related(
        "handler"
    )

    for ticket in tickets:
        # 计算剩余时间（小时）
        remaining = (ticket.deadline - now).total_seconds() / 3600

        # 判断预警阶段
        stage = None
        if remaining <= config["xHours"] and remaining > config["yHours"]:
            stage = "warning"
        elif remaining <= config["yHours"] and remaining > 0:
            stage = "urgent"
        elif remaining <= 0:
            stage = "timeout"

        # 发送通知
        if stage:
            message = format_message(stage, ticket, remaining)
            send_notification.delay(ticket.handler.id, message)


def format_message(stage, ticket, remaining):
    templates = {
        "warning": f"工单[{ticket.ticket_code}]剩余时间不足{abs(math.floor(remaining))}小时，请及时处理！",
        "urgent": f"工单[{ticket.ticket_code}]即将超时（剩余{abs(math.floor(remaining))}小时），请立即处理！",
        "timeout": f"工单[{ticket.ticket_code}]已超时{abs(math.floor(remaining))}小时，请尽快处理！",
    }
    return templates[stage]


@shared_task
def send_notification(user_id, message):
    # 实际发送通知的逻辑（示例实现）
    user = User.objects.get(id=user_id)
    print(f"发送通知给 {user.username}: {message}")  # 替换为实际通知方式
