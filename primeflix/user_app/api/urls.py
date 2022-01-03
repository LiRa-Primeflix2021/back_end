from django.urls import path, include

from rest_framework.authtoken.views import obtain_auth_token
from user_app.api.views import registration_view, logout_view, ChangePasswordAndEmail
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView



urlpatterns = [
    path('login/', obtain_auth_token, name='login'),
    path('register/', registration_view, name='register'),
    path('logout/', logout_view, name='logout'),
    
    path('token/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    path('change-password-email/',ChangePasswordAndEmail.as_view(), name='change-pwd-email' ),

    path('fb-login/', include('social_django.urls', namespace='social')),
    
    # url ('https://www.facebook.com/v12.0/dialog/oauth?', name='test'),
    ]
