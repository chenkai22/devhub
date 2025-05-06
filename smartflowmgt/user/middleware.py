from os import path
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.settings import api_settings
from django.http import HttpResponse
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError, PyJWTError


class JwtAuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        white_list = ["/user/login", "/user/refresh", "/user/refreshToken"]
        path = request.path
        if (path not in white_list) and (not path.startswith("/media")):
            print("要进行token验证")
            token = request.META.get("HTTP_AUTHORIZATION")
            try:
                # 替换旧的解码方式
                decoded_token = jwt.decode(
                    token,
                    api_settings.SIGNING_KEY,  # 使用签名密钥
                    algorithms=[api_settings.ALGORITHM],  # 指定算法
                    audience=api_settings.AUDIENCE,
                    issuer=api_settings.ISSUER,
                )
                # 可以将解码后的token存储到request对象中
                request.user_token = decoded_token
            except ExpiredSignatureError:
                print("token过期")
                return HttpResponse("token过期")
            except InvalidTokenError:
                print("token无效")
                return HttpResponse("token无效")
            except PyJWTError:
                print("token格式错误")
                return HttpResponse("token格式错误")
        else:
            print("不需要进行token验证")
