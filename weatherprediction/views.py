from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.permissions import IsAuthenticated
import difflib
import os
from .models import ChatbotInteraction  # Import the model

# Load CSV data
file_path = os.path.join(os.path.dirname(__file__), 'farmbotics_chatbot_qa.csv')
df = pd.read_csv(file_path)
questions = df["question"].tolist()
answers = df["answer"].tolist()

class GetAnswerAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_question = request.data.get('question', '')

        closest_match = difflib.get_close_matches(user_question, questions, n=1, cutoff=0.5)

        if closest_match:
            matched_question = closest_match[0]
            answer = answers[questions.index(matched_question)]
            status_code = status.HTTP_200_OK
        else:
            matched_question = None
            answer = "Sorry, I don't have an answer to that."
            status_code = status.HTTP_404_NOT_FOUND

        # Save interaction
        ChatbotInteraction.objects.create(
            user=request.user if request.user else None,
            question=user_question,
            matched_question=matched_question,
            answer=answer
        )

        return Response({'answer': answer}, status=status_code)
