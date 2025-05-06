from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path
from .views import (
    LoginView,
    SearchView,
    CheckView,
    SaveView,
    ActionView,
    ActiveView,
    PasswordView,
    RefreshTokenView,
    UserListView,
)

urlpatterns = [
    path("login", LoginView.as_view(), name="login"),
    path("refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("search", SearchView.as_view(), name="search"),  # 用户信息分页查询
    path("check", CheckView.as_view(), name="check"),
    path("save", SaveView.as_view(), name="save"),
    path("action", ActionView.as_view(), name="action"),
    path("active", ActiveView.as_view(), name="active"),
    path("resetPassword", PasswordView.as_view(), name="resetPassword"),
    path("refreshToken", RefreshTokenView.as_view(), name="refresh_token"),
    path("list", UserListView.as_view(), name="list"),
]
