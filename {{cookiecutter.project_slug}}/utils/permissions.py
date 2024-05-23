from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrSuperuser(BasePermission):
    def has_permission(self, request, view):
        return request.user and (request.user.is_superuser or request.user.is_staff)


class IsAdminOrSuperuserOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and (request.user.is_superuser or request.user.is_staff)


class IsAdminOrSuperuserOrPostOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        return request.user and (request.user.is_superuser or request.user.is_staff)
