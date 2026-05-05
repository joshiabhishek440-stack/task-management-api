from rest_framework.permissions import BasePermission


class IsManagerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        try:
            return request.user.profile.role in ['admin', 'manager']
        except:
            return False


class IsOwnerOrManagerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            role = request.user.profile.role
            if role in ['admin', 'manager']:
                return True
            return obj.created_by == request.user or obj.assigned_to == request.user
        except:
            return False