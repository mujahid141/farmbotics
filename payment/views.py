from django.shortcuts import render
from .serializers import PaymentSerializer
from .models import Payment
from django.http import HttpResponse
from rest_framework import permissions, status 
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.views import APIView


class PaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payments = Payment.objects.all() #filter(user=request.user)
        serializer = PaymentSerializer(payments, many=True)
        return HttpResponse(serializer.data, content_type='application/json')

    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return HttpResponse(serializer.data, status=status.HTTP_201_CREATED, content_type='application/json')
        return HttpResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')