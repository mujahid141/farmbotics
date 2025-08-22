from django.urls import path
from .views import FarmReportAPIView

urlpatterns = [
    path('farm-reports/', FarmReportAPIView.as_view(), name='farm-reports'),
]
