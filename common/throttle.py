from django.core.cache import cache as default_cache
from rest_framework import exceptions, status
from rest_framework.throttling import SimpleRateThrottle


class ThrottledException(exceptions.APIException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_code = 'throttled'


# 限流->对于某些操作进行频率限制
# 如果设置多个限流组件，只要有一个不满足就会限制
class MyRateThrottle(SimpleRateThrottle):
    cache = default_cache  # 访问记录存放在django的缓存中（需设置缓存）
    scope = "user"  # 构造缓存中的key
    cache_format = 'throttle_%(scope)s_%(ident)s'

    # 设置访问频率，例如：1分钟允许访问5次
    # 其他：'s', 'sec', 'm', 'min', 'h', 'hour', 'd', 'day'
    THROTTLE_RATES = {"user": "5/m"}

    def get_cache_key(self, request, view):
        if request.user: # 如果用户已经登录可以获取到他的ID作为主键
            ident = request.user.pk  # 用户ID
        else:
            ident = self.get_ident(request)  # 获取请求用户IP（匿名用户：没有ID）（去request中找请求头）
        # throttle_u # throttle_user_11.11.11.11ser_2
        return self.cache_format % {'scope': self.scope, 'ident': ident}

    def throttle_failure(self):
        wait = self.wait()
        detail = {
            "code": 1005,
            "data": "访问频率限制",
            'detail': "需等待{}s才能访问".format(int(wait))
        }
        raise ThrottledException(detail)
