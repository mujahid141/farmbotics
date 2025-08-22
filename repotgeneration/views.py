from django.shortcuts import render
from soilanalysis.models import SoilPrediction
from pestanddisease.models import LeafDiseasePrediction
from weatherprediction.models import ChatbotInteraction
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from collections import defaultdict
# Create your views here.


from django.db.models import Avg
from django.http import JsonResponse

class SoilPredictionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):  # ← FIXED: added *args, **kwargs
        averages = SoilPrediction.objects.filter(user = request.user).aggregate(
            avg_phosphorus=Avg('phosphorus'),
            avg_ph=Avg('ph'),
            avg_organic_matter=Avg('organic_matter'),
            avg_electrical_conductivity=Avg('electrical_conductivity')
        )
        return JsonResponse(averages)

             
class LeafDiseasePredectionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Filter only the current user's predictions
        all_analysis = LeafDiseasePrediction.objects.filter(user=request.user)

        # Count each disease type
        disease_counts = defaultdict(int)
        for entry in all_analysis:
            disease = entry.predicted_class
            disease_counts[disease] += 1

        # Convert to regular dict for JSON serialization
        result = dict(disease_counts)

        return JsonResponse({'pest_data': result})


class ChatbotInteractionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        bot_interaction = ChatbotInteraction.objects.filter(user=request.user)

        # Example: count of each disease per user
        all_interaction = []

        for entry in bot_interaction:
            # email =  entry.user.email or  '' # or adjust if field is named differently
            question = entry.question
            matched_question = entry.matched_question
            answer = entry.answer
            ent={
                'question': question,
                'matched_question': matched_question,
                'answer': answer,
                # 'email': email
            }
            all_interaction.append(ent)
            

        # Convert defaultdict to normal dict for JSON serialization
        result = all_interaction

        return JsonResponse({'Bot_Interaction ': result})