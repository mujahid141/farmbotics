from django.urls import path
from .views import  ProfileDetailView , CustomPasswordResetView

urlpatterns = [
    path('profile/', ProfileDetailView.as_view(), name='profile-detail'),
    path('auth/password/reset/', CustomPasswordResetView.as_view(), name='password_reset')
]
