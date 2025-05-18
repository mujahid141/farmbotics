from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Profile
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



