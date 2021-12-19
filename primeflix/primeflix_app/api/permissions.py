from rest_framework import permissions

class IsAdminOrReadyOnly(permissions.IsAdminUser):
    
    def has_permission(self, request, view):
        # admin_permission = bool(request.user and request.user.is_staff)
        # return request.method == "GET" or admin_permission

        if (request.method in permissions.SAFE_METHODS):
            return True
        else:
            return bool(request.user and request.user.is_staff)
            

    

class IsReviewUserOrReadOnly(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if (request.method in permissions.SAFE_METHODS):
            return True
        else:
            # return obj.review_user == request.user or request.user.is_staff
            return obj.review_user == request.user or request.user.is_staff
        
        
        
class IsOrderUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if (request.method in permissions.SAFE_METHODS):
            return True
        else:
            # return obj.review_user == request.user or request.user.is_staff
            return obj.order_user == request.user and request.user.is_staff
    # def has_object_permission(self, request, view, obj):

    #     if (request.method in permissions.SAFE_METHODS):

    #         if obj.order_user == request.user:
    #             return True
    #     else:
    #         return False
        
        
        
        # if (request.method in permissions.SAFE_METHODS):
        #     return True
        # else:
        #     # return obj.review_user == request.user or request.user.is_staff
        #     return obj.order_user == request.user