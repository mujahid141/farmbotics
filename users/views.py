from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Profile,CustomUser as User
from .serializers import ProfileSerializer
from allauth.account.views import ConfirmEmailView
from django.http import JsonResponse, HttpResponseRedirect
from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC
from django.shortcuts import redirect

class CustomConfirmEmailView(ConfirmEmailView):
    def get(self, request, *args, **kwargs):
        # Try to fetch the confirmation object
        self.object = self.get_object()
        self.object.confirm(request)

        # Option A: Return JSON response
        return JsonResponse({'detail': 'Email confirmed successfully!'})

        # Option B: Redirect to your frontend instead
        # return render(request, 'account/email_confirm.html', {
                # 'email': self.object.email_address.email
            # })

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Profile
from .serializers import ProfileSerializer

import random
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(user):
    otp = generate_otp()
    user.otp = otp
    user.otp_created_at = timezone.now()
    user.save()

    subject = "Password Reset Request – One-Time Password (OTP)"
    message = f"""
Hello {user.username},

We received a request to reset your password on your account registered with this email address.

Please use the following One-Time Password (OTP) to reset your password:

🔐 OTP: {otp}

This OTP is valid for 10 minutes. Do not share this code with anyone for security reasons.

If you did not request a password reset, you can safely ignore this email.

Regards,  
Support Team  
YourAppName
"""

    send_mail(
        subject=subject,
        message=message,
        from_email="noreply@yourdomain.com",
        recipient_list=[user.email],
    )

class RequestResetOTPView(APIView):
    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
            send_otp_email(user)
            return Response({"message": "OTP sent to your email."})
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)

class VerifyOTPView(APIView):
    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        print(email,otp)
        try:
            user = User.objects.get(email=email)
            print(user.otp, otp)
            if user.otp != otp:
                return Response({"error": "Invalid OTP"}, status=400)

            if timezone.now() - user.otp_created_at > timedelta(minutes=10):
                return Response({"error": "OTP expired"}, status=400)

            return Response({"message": "OTP verified"})
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        new_password = request.data.get("new_password")

        try:
            user = User.objects.get(email=email)

            if user.otp != otp:
                return Response({"error": "Invalid OTP"}, status=400)

            if timezone.now() - user.otp_created_at > timedelta(minutes=10):
                return Response({"error": "OTP expired"}, status=400)

            user.set_password(new_password)
            user.otp = None  # Invalidate OTP
            user.otp_created_at = None
            user.save()
            return Response({"message": "Password reset successful"})
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Retrieve or create the user's profile
        profile, created = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        # Retrieve or create the user's profile
        profile, created = Profile.objects.get_or_create(user=request.user)
        # Update profile with partial data (to only update what is provided)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



