from django.urls import path


from .views import SoilPredictionView, LeafDiseasePredectionView, ChatbotInteractionView


urlpatterns = [
    path('soil-report/', SoilPredictionView.as_view(), name='soil_prediction'),
    path('leaf-disease-report/', LeafDiseasePredectionView.as_view(), name='leaf_disease_prediction'),
    path('chatbot-interaction/', ChatbotInteractionView.as_view(), name='chatbot_interaction'),
]
