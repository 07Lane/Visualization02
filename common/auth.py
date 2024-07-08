from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from accounts.models import UserInfo


# 执行每个认证类中的authenticate方法;
# ->认证成功或失败，不会在执行后续的认证类
# ->返回None，执行后续的认证类。

class ParamAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.query_params.get('token')
        if not token:
            return None  # 如果没有token，则返回None，表示未认证
        try:
            user_object = UserInfo.objects.get(token=token)
        except UserInfo.DoesNotExist:
            raise AuthenticationFailed({"code": 2000, "msg": "认证失败!"})
        return user_object, token

    def authenticate_header(self, request):
        return 'API'


class HeaderAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if not token:
            return None
        try:
            user_object = UserInfo.objects.get(token=token)
        except UserInfo.DoesNotExist:
            raise AuthenticationFailed({"code": 2000, "msg": "认证失败!"})
        return user_object, token

    def authenticate_header(self, request):
        return 'API'


class NotAuthentication(BaseAuthentication):
    def authenticate(self, request):
        raise AuthenticationFailed({"code": 2000, "msg": "认证失败!"})

    def authenticate_header(self, request):
        return 'API'
