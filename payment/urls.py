from django.urls import path
from .views import PaymentView

urlpatterns = [
    path('payment-post/', PaymentView.as_view(), name='subscription-reports'),
    path('payment-get/', PaymentView.as_view(), name='subscription-reports'),
    
]
