from django.urls import path
from .views import ProfileView ,RequestResetOTPView, VerifyOTPView, ResetPasswordView

   

urlpatterns = [
    path('', ProfileView.as_view(), name='profile'),
    path("password-reset/request/", RequestResetOTPView.as_view()),
    path("password-reset/verify/", VerifyOTPView.as_view()),
    path("password-reset/confirm/", ResetPasswordView.as_view()),
]
