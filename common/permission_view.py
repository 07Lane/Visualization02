from rest_framework.views import APIView


# 自定义一个PermissionView继承自APIView，在保留原本功能的情况下进行功能拓展
# 这里的权限判断关系是或的关系

class PermissionView(APIView):
    def check_permissions(self, request):
        no_permission_objects = []  # 定义一个无法通过权限的列表
        for permission in self.get_permissions():
            if permission.has_permission(request, self):
                return
            else:
                no_permission_objects.append(permission)  # 将无权限的加入列表
        else:
            self.permission_denied(
                request,
                # 这里仅仅展示第一个错误信息，后面的不展示
                message=getattr(no_permission_objects[0], 'message', None),
                code=getattr(no_permission_objects[0], 'code', None)
            )
