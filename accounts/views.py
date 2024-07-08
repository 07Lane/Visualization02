import uuid

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi

from Visualization02.settings import API_KEY, BASE_URL
from .models import ChatMessage
from rest_framework import serializers, exceptions
from rest_framework.versioning import QueryParameterVersioning  # 配置api接口的版本（version），用于GET参数传递，通过request.version取到
from rest_framework.views import APIView
from rest_framework.response import Response
from openai import OpenAI

from accounts import models
from common.auth import ParamAuthentication, HeaderAuthentication
from common.permission import UserPermission, ManagerPermission
from common import permission_view  # 自定义的权限拓展视图（如果继承了APIView权限判断就是且的关系，如果继承了自定义的view就是或的关系）
from common.throttle import MyRateThrottle


# 注册------------------------------------------------------------------------
# 注册的序列化器
class RegisterSerializers(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = models.UserInfo
        fields = ['id', 'username', 'password', 'confirm_password']
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True}
        }

    def validate_password(self, value):
        return value

    def validate_confirm_password(self, value):
        password = self.initial_data.get("password")
        if password != value:
            raise exceptions.ValidationError("密码不一致")
        return value


class RegisterView(APIView):
    # Swagger 配置
    swagger_schema_fields = {
        'manual_parameters': [
            openapi.Parameter('username', openapi.IN_FORM, description="用户名", type=openapi.TYPE_STRING),
            openapi.Parameter('password', openapi.IN_FORM, description="密码", type=openapi.TYPE_STRING),
            openapi.Parameter('confirm_password', openapi.IN_FORM, description="确认密码", type=openapi.TYPE_STRING),
        ],
        'responses': {
            200: openapi.Response('成功', None),
            400: openapi.Response('错误请求', None),
        }
    }

    def post(self, request):
        # 1.提交数据{"username":"xxx","password":"xxx","confirm_password":"xxx"}
        # 2.数据校验 + 数据保存
        ser = RegisterSerializers(data=request.data)
        if ser.is_valid():
            ser.validated_data.pop('confirm_password')  # 将之前在数据库中的confirm_password出栈，因为这个字段是自己局部定义的，数据库中没有
            ser.save()  # 校验成功，将数据保存到数据库
            return Response({"code": 1000, "success": "注册成功", "data": ser.data})
        else:
            return Response({"code": 1001, "error": "注册失败", "detail": ser.errors})


# 登录------------------------------------------------------------------------

# 登录序列化器
class LoginSerializers(serializers.ModelSerializer):
    class Meta:
        model = models.UserInfo
        fields = ['username', 'password']


class LoginView(APIView):
    # 登录界面，不需要认证
    throttle_classes = [MyRateThrottle, ]  # 限流

    # Swagger 配置
    swagger_schema_fields = {
        'manual_parameters': [
            openapi.Parameter('username', openapi.IN_FORM, description="用户名", type=openapi.TYPE_STRING),
            openapi.Parameter('password', openapi.IN_FORM, description="密码", type=openapi.TYPE_STRING),
        ],
        'responses': {
            200: openapi.Response('成功', None),
            400: openapi.Response('错误请求', None),
            401: openapi.Response('未授权', None),
        }
    }

    def post(self, request):
        # 1.接收用户POST提交的用户名和密码
        # 2.序列化器校验
        ser = LoginSerializers(data=request.data)
        if not ser.is_valid():
            return Response({"code": 1002, "error": "校验失败", "detail": ser.errors})
        # request.query_params 用来接收URL传递的参数
        # user = request.data.get("username")  # 通过request.data拿到JSON、表单...之类格式的数据
        # pwd = request.data.get("password")
        #
        # # 3.数据库校验
        # user_object = models.UserInfo.objects.filter(username=user, password=pwd).first()

        # 3.数据库校验
        instance = models.UserInfo.objects.filter(**ser.validated_data).first()
        if not instance:
            return Response({"code": 1003, "error": "用户名或密码错误"})

        # 4.校验正确后设置token
        # 暂时用uuid设置token（项目中一般用jwt令牌或者session或者cookie）
        token = str(uuid.uuid4())
        instance.token = token
        instance.status = 1  # 登录成功后将状态变为活跃态
        instance.save()

        return Response({"code": 1004, "success": "登录成功", "token": token})


# 登出------------------------------------------------------------------------
class LogoutView(APIView):
    # 经过认证之后才能进行登出操作
    authentication_classes = [ParamAuthentication, HeaderAuthentication]

    # Swagger 配置
    swagger_schema_fields = {
        'responses': {
            200: openapi.Response('成功', None),
            401: openapi.Response('未授权', None),
        }
    }

    def post(self, request):
        # 获取当前认证的用户对象
        user, token = request.user, request.auth
        if user and token:
            # 清除用户的token和状态
            user.token = None
            user.status = 0
            user.save()
            return Response({"code": 1005, "success": "登出成功"})
        else:
            return Response({"code": 2001, "msg": "未找到用户或认证信息无效"})


# 销户------------------------------------------------------------------------
class DeleteView(APIView):
    # 经过认证之后才能进行销户操作
    authentication_classes = [ParamAuthentication, HeaderAuthentication]

    # Swagger 配置
    swagger_schema_fields = {
        'responses': {
            200: openapi.Response('成功', None),
            401: openapi.Response('未授权', None),
        }
    }

    def delete(self, request):
        # 获取当前认证的用户对象
        user = request.user
        if user:
            # 删除用户数据
            user.delete()
            return Response({"code": 1006, "success": "销户成功"})
        else:
            return Response({"code": 2001, "msg": "未找到用户或认证信息无效"}, status=401)


# ChatBot--------------------------------------------------------------------

# # 初始化 OpenAI 客戶端
# client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
#
#
# # 测试聊天功能
# @login_required
# @method_decorator(csrf_exempt)
# def chat_interface(request):
#     return render(request, 'chat.html')
#
#
# class ChatView(LoginRequiredMixin, APIView):
#     # @method_decorator(csrf_exempt)
#     # def dispatch(self, request, *args, **kwargs):
#     #     return super().dispatch(request, *args, **kwargs)
#
#     def post(self, request):
#         user_message = request.data.get('message', '')
#         if user_message:
#             response = client.chat.completions.create(
#                 model="gpt-3.5",
#                 messages=[{"role": "user", "content": user_message}],
#                 max_tokens=3000
#             )
#             response_text = response.choices[0].message['content']
#
#             chat_message = ChatMessage(
#                 user=request.user,
#                 message=user_message,
#                 response=response_text
#             )
#             chat_message.save()
#
#             return Response({'message': user_message, 'response': response_text}, status=200)
#         return Response({'error': '没有可以提供的数据'}, status=400)
#
#     def get(self, request):
#         return Response({'error': '错误的请求方式，请用POST来请求'}, status=400)
