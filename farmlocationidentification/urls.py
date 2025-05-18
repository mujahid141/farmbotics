from django.urls import path
from . import views
urlpatterns = [
    path('save-region/', views.SaveFarmRegion.as_view(), name='save-farm-region'),
    path('get-region/', views.GetFarmRegion.as_view(), name='get-farm-region'),
]