from dj_rest_auth.registration.views import RegisterView
from rest_framework.permissions import AllowAny
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions
from .models import Profile
from .serializers import ProfileSerializer
from dj_rest_auth.views import LoginView

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




class ProfileListCreateView(generics.ListCreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # Set the user to the authenticated user


class ProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter profiles to those owned by the authenticated user
        return Profile.objects.filter(user=self.request.user)

    