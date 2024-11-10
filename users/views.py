from dj_rest_auth.registration.views import RegisterView
from rest_framework.permissions import AllowAny
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions
from .models import Profile
from dj_rest_auth.views import LoginView
from rest_framework.exceptions import NotFound
from .serializers import ProfileSerializer
# Ensure this is imported correctly

# views.py
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _

class CustomPasswordResetView(APIView):
    """
    Custom password reset view to handle password reset logic and customize emails.
    """
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        if not email:
            return Response({"error": _("Email is required")}, status=status.HTTP_400_BAD_REQUEST)
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": _("User with this email does not exist")}, status=status.HTTP_404_NOT_FOUND)

        # Generate uid and token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Compose plain text email content
        subject = "Password Reset Request"
        reset_url = f"https://127.0.0.1:8000/api/auth/password/reset/confirm/{uid}/{token}/"
        message = (
            f"Hello {user.username},\n\n"
            "You requested a password reset. Click the link below to reset your password:\n\n"
            f"{reset_url}\n\n"
            "Alternatively, you can copy and paste the following details into the app:\n\n"
            f"UID (Base64): {uid}\n"
            f"Token: {token}\n\n"
            f"Username:{user.username}..........in case You forgot username\n\n"
            "If you didn’t request this, please ignore this email.\n\n"
            "Best regards,\n"
            "Your Website Team"
        )
        
        # Send the email
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

        return Response({"success": _("Password reset email sent.")}, status=status.HTTP_200_OK)


class Register(RegisterView):
    # Override the permission classes to allow any user
    permission_classes = [AllowAny]

    # Optionally, you can override other methods if needed
    def create(self, request, *args, **kwargs):
        # Custom logic before registration if needed
        return super().create(request, *args, **kwargs)



@method_decorator(csrf_exempt, name='dispatch')
class CsrfExemptLoginView(LoginView):
    pass







class ProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]  # Ensure only authenticated users can access it

    def get_object(self):
        user_id = self.request.user.id
        try:
            return Profile.objects.get(user_id=user_id)
        except Profile.DoesNotExist:
            raise NotFound("Profile not found for the authenticated user.")



