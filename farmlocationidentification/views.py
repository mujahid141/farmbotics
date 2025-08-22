from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import FarmReport
from .serializers import FarmReportSerializer

class FarmReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            report = FarmReport.objects.get(user=request.user)
            serializer = FarmReportSerializer(report)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except FarmReport.DoesNotExist:
            return Response({"detail": "No farm report found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        try:
            # Try to get existing farm report for the user
            report = FarmReport.objects.get(user=request.user)
            serializer = FarmReportSerializer(report, data=request.data, partial=True)
        except FarmReport.DoesNotExist:
            # If not exists, create new
            serializer = FarmReportSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
