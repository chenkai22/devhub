from django.urls import path
from .views import (
    SearchView,
    SaveView,
    ActionView,
    ESTicketSearch,
    TicketSuggest,
    TicketExportView,
    TicketStatusView,
    TicketKanbanView,
    WarningSettingsView,
    TicketReportView,
    UserRankingView,
)

urlpatterns = [
    path("search", SearchView.as_view(), name="search"),  # 用户信息分页查询
    path("save", SaveView.as_view(), name="save"),
    path("action", ActionView.as_view(), name="action"),
    path("es-search", ESTicketSearch.as_view(), name="es-search"),
    path("suggest", TicketSuggest.as_view(), name="suggest"),
    path("export", TicketExportView.as_view(), name="ticket-export"),
    path("<int:pk>/status", TicketStatusView.as_view(), name="ticket-status"),
    path("kanban", TicketKanbanView.as_view(), name="ticket-kanban"),
    path("settings", WarningSettingsView.as_view(), name="warning-settings"),
    path("report", TicketReportView.as_view(), name="ticket-report"),
    path("ranking", UserRankingView.as_view(), name="user-ranking"),
]
