
from rest_framework.permissions import BasePermission

class IsOwnerOnlyCanViewUsers(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_owner
class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_owner