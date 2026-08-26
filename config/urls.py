"""
URL configuration for Araf's Assistant project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Frontend Views (Single Page App & Auth Pages)
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login_page'),
    path('register/', TemplateView.as_view(template_name='register.html'), name='register_page'),

    # REST APIs
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/chat/', include('chatbot.urls')),
]
