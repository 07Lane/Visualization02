from rest_framework.permissions import BasePermission


# 执行所有权限类的has_permission方法，返回True通过、返回False表示不通过。
# -> 执行所有的权限类
# 默认情况下，保证所有的权限类中的has_permission方法都返回True（通过所有的权限判定之后才能通过）
# 自定义：满足任意一个权限即可通过：
# （自定义权限通过方法在要用到的view的类中定义；或者在common类中定义一个自己的view类将他作为一个API接口后面要用到的时候进行调用和继承这个view）
# def check_permissions(self, request):
#         no_permission_objects = []  # 定义一个无法通过权限的列表
#         for permission in self.get_permissions():
#             if permission.has_permission(request, self):
#                    return
#             else:
#                    no_permission_objects.append(permission) # 将无权限的加入列表
#         else:
#                 self.permission_denied(
#                     request,
#                     # 这里仅仅展示第一个错误信息，后面的不展示
#                     message=getattr(no_permission_objects[0], 'message', None),
#                     code=getattr(no_permission_objects[0], 'code', None)
#                 )

# 关系是且的权限认证

class UserPermission(BasePermission):
    # permission组件中自定义错误返回的内容
    message = {"status": False, "message": "无权访问1"}

    def has_permission(self, request, view):
        # 获取请求中的数据，进行权限校验
        # 在上一步的认证中已经将user放入了request中
        if request.user.role == 1:  # 如果是用户
            return True
        return False


class ManagerPermission(BasePermission):
    # permission组件中自定义错误返回的内容
    message = {"status": False, "message": "无权访问2"}

    def has_permission(self, request, view):
        # 获取请求中的数据，进行权限校验
        if request.user.role == 2:  # 如果是管理员
            return True
        return False
