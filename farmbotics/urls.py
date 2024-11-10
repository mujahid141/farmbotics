"""
URL configuration for farmbotics project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from soilanalysis import views
from dj_rest_auth.views import LoginView
from dj_rest_auth.registration.views import RegisterView
from rest_framework.authtoken import views as auth_views
from dj_rest_auth.views import PasswordResetView, PasswordResetConfirmView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    #soil analysis
    path('api/users/', include('users.urls')),
    path('api/soil_analysis/', include('soilanalysis.urls')),
    #path('api/pest_detection/', include('pestanddisease.urls')),
    
    # Auth and registration URLs
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    
    # Token URL (for generating tokens after login)
    path('api/auth/token/', auth_views.obtain_auth_token, name='token'),
     # AllAuth URLs for email verification
    path('accounts/', include('allauth.urls')), 
    
    # Social auth
    path('api/social/', include('allauth.socialaccount.urls')),

    # Password Reset 
    path('api/auth/password/reset/', PasswordResetView.as_view(), name='password_reset'),
    path('api/auth/password/reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
   
]
