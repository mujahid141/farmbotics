"""
URL configuration for farmbotics project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from soilanalysis import views
from pestanddisease import views as pest_views
from weatherprediction import views as weather_views
from dj_rest_auth.registration.views import VerifyEmailView
from users.views import CustomConfirmEmailView

from repotgeneration.views import SoilPredictionView
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ✅ Override BEFORE including the default registration URLs
    path(
        'api/auth/registration/account-confirm-email/<str:key>/',
        CustomConfirmEmailView.as_view(),
        name='account_confirm_email'
    ),
    
    path('api/auth/', include('dj_rest_auth.urls')),  
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),  
    path('api/social/', include('allauth.socialaccount.urls')), 
   

    path('api/soilanalysis/', views.PredictSoilAPIView.as_view(), name="first"), 
    path('api/community/', include('community.urls')),
    path('api/pestanddisease/', pest_views.PredictLeafDiseaseView.as_view(), name="pest-disease"),       
    path('api/bot/', include('weatherprediction.urls')),  
    path('api/profile/', include('users.urls')),
    path('api/farm/', include('farmlocationidentification.urls')),
    
    
    #APIs for report generation
    path('api/report/', include('repotgeneration.urls')),
    path('api/payment/', include('payment.urls')),
    
]
    

