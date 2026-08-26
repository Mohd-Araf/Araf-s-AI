from django.urls import path
from .views import RegisterAPIView, LoginAPIView, LogoutAPIView, CurrentUserAPIView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='auth_register'),
    path('login/', LoginAPIView.as_view(), name='auth_login'),
    path('logout/', LogoutAPIView.as_view(), name='auth_logout'),
    path('me/', CurrentUserAPIView.as_view(), name='auth_me'),
]
