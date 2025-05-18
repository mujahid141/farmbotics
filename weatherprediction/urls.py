from django.urls import path
from . import views

urlpatterns = [
    path('get_answer/', views.GetAnswerAPIView.as_view(), name='get_answer'),
    # Add other routes here
]