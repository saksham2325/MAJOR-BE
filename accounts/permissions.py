from rest_framework import permissions


class ObjectAdmin(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        print(request.user)
        print(obj.admin)
        return request.user==obj.admin
    
    
class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.id==obj.id


class ListPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return False
