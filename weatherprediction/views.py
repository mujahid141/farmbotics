from rest_framework.views import APIView
from rest_framework.response import Response
import pandas as pd
from rest_framework.permissions import AllowAny , IsAuthenticated
import os
from .models import ChatbotInteraction, WeatherData  # Import the models
from .serializers import WeatherDataSerializer  # Import the serializer
import google.generativeai as genai
from decouple import config
from django.conf import settings
import joblib
import numpy as np
from rest_framework import status
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
import logging
import re
import os
import json
import re
import logging
from django.conf import settings
from django_ratelimit.decorators import ratelimit
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils.decorators import method_decorator
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
logger = logging.getLogger(__name__)

# Configure Gemini globally
GEMINI_API_KEY = config("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.error("GEMINI_API_KEY not found in configuration. Please check your .env file.")





class GetAnswerAPIView(APIView):
    """
    Professional Chatbot API for SMB Digital Zone with RAG.
    Uses document-based knowledge for accurate responses about company services, founders, etc.
    """

    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.knowledge_base = self._load_knowledge_base()
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.document_embeddings = self._build_embeddings()

    def _load_knowledge_base(self):
        json_path = os.path.join(settings.BASE_DIR, 'knowledge_base.json')
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Knowledge base not found at {json_path}")
            return []

    def _build_embeddings(self):
        if not self.knowledge_base:
            return np.array([])
        texts = [item['text'] for item in self.knowledge_base]
        return self.embedder.encode(texts, show_progress_bar=False)

    def retrieve_relevant_chunks(self, query, top_k=3):
        if not self.document_embeddings.size:
            return []
        query_emb = self.embedder.encode([query])
        similarities = cosine_similarity(query_emb, self.document_embeddings)[0]
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        return [
            self.knowledge_base[i] for i in top_indices
            if similarities[i] > 0.6
        ]

    @method_decorator(ratelimit(key='ip', rate='100/m', method='POST'))
    def post(self, request):
        try:
            user_question = request.data.get("question", "").strip()
            user_question = self._sanitize_input(user_question)

            if not user_question:
                return Response(
                    {"status": "error", "message": "Please provide a valid question.", "data": {}},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            max_length = getattr(settings, 'CHATBOT_MAX_QUESTION_LENGTH', 500)
            if len(user_question) > max_length:
                return Response(
                    {"status": "error", "message": f"Question exceeds maximum length of {max_length} characters.", "data": {}},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not GEMINI_API_KEY:
                return Response(
                    {"status": "error", "message": "Chatbot service is temporarily unavailable.", "data": {}},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

            try:
                model = genai.GenerativeModel(
                    model_name=getattr(settings, 'GEMINI_MODEL_NAME', 'gemini-1.5-flash')
                )
            except Exception as e:
                logger.error(f"Failed to initialize Gemini model: {str(e)}")
                return Response(
                    {"status": "error", "message": "Internal server error.", "data": {}},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            relevant_chunks = self.retrieve_relevant_chunks(user_question)
            system_prompt = self._build_system_prompt(user_question, relevant_chunks)

            try:
                response = model.generate_content(system_prompt)
                answer = response.text.strip() if response and response.text else (
                    "Sorry, I couldn't generate a response. Please try again."
                )
            except Exception as e:
                logger.error(f"Gemini API error: {str(e)}")
                return Response(
                    {"status": "error", "message": "Failed to generate response.", "data": {}},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            logger.info(f"Chatbot query: {user_question[:50]}... Response length: {len(answer)}")
            return Response(
                {"status": "success", "message": "Response generated successfully.", "data": {"answer": answer}},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response(
                {"status": "error", "message": "An unexpected error occurred.", "data": {}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _sanitize_input(self, input_text):
        sanitized = re.sub(r'[<>;{}]', '', input_text)
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        return sanitized

    def _build_system_prompt(self, user_question, relevant_chunks):
        company_info = {
            "name": "SMB Digital Zone",
            "location": "Dubai, UAE",
            "website": "https://smbdigitalzone.com/",
            "about_url": "https://smbdigitalzone.com/about-us/",
            "services_url": "https://smbdigitalzone.com/services/",
            "description": (
                "SMB Digital Zone is a founder-led digital agency specializing in emotionally intelligent branding, "
                "strategic content creation, SEO, AI Solutions, E-commerce, software and web development, and product innovation."
            )
        }

        context = ""
        if relevant_chunks:
            context = "\n".join([
                f"- {chunk['text']} (Source: {chunk['metadata']['section']})"
                for chunk in relevant_chunks
            ])
            context = f"\n**Retrieved Company Knowledge:**\n{context}\n"

        system_prompt = f"""
        You are a professional AI assistant for {company_info['name']}, a digital agency based in {company_info['location']}.
        Your role is to provide accurate, concise, and professional answers about {company_info['name']}’s services, founders, company information, and contact details, using the provided knowledge base.

        **Company Information:**
        - Name: {company_info['name']}
        - Location: {company_info['location']}
        - Website: {company_info['website']}
        - Founders: Refer to {company_info['about_url']}
        - Services: Refer to {company_info['services_url']}
        - Description: {company_info['description']}

        {context}

        **Guidelines:**
        - Base your response strictly on the provided company information and retrieved knowledge.
        - Use bullet points, headings, and clear formatting for lists (e.g., services).
        - Be polite, professional, and concise (under 300 words).
        - If the question is unrelated, respond: "I can only provide information about {company_info['name']} and its services. Please ask a related question."
        - Cite the source section from the knowledge base when applicable (e.g., 'Based on our services section').

        **User Question:**
        {user_question}

        **Response:**
        """
        return system_prompt
# class GetAnswerAPIView(APIView):
#     """
#     Professional Chatbot API for SMB Digital Zone.
#     Integrates Gemini AI to provide accurate information about company services, founders, and contact details.
#     """

#     permission_classes = [AllowAny]

#     # Rate limiting: 100 requests per minute per IP
#     @method_decorator(ratelimit(key='ip', rate='100/m', method='POST'))
#     def post(self, request):
#         """
#         Handle POST requests to answer user questions about SMB Digital Zone using Gemini AI.
#         """
#         try:
#             # Extract and sanitize user input
#             user_question = request.data.get("question", "").strip()
#             user_question = self._sanitize_input(user_question)

#             # Validate input
#             if not user_question:
#                 return Response(
#                     {
#                         "status": "error",
#                         "message": "Please provide a valid question.",
#                         "data": {}
#                     },
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#             # Enforce maximum question length
#             max_length = getattr(settings, 'CHATBOT_MAX_QUESTION_LENGTH', 500)
#             if len(user_question) > max_length:
#                 return Response(
#                     {
#                         "status": "error",
#                         "message": f"Question exceeds maximum length of {max_length} characters.",
#                         "data": {}
#                     },
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#             # Check if Gemini is configured
#             if not GEMINI_API_KEY:
#                 return Response(
#                     {
#                         "status": "error",
#                         "message": "Chatbot service is temporarily unavailable. Please try again later.",
#                         "data": {}
#                     },
#                     status=status.HTTP_503_SERVICE_UNAVAILABLE,
#                 )

#             # Initialize Gemini Model with configuration
#             try:
#                 model = genai.GenerativeModel(
#                     model_name=getattr(settings, 'GEMINI_MODEL_NAME', 'gemini-1.5-flash')
#                 )
#             except Exception as e:
#                 logger.error(f"Failed to initialize Gemini model: {str(e)}", exc_info=True)
#                 return Response(
#                     {
#                         "status": "error",
#                         "message": "Internal server error. Please try again later.",
#                         "data": {}
#                     },
#                     status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 )

#             # Construct system prompt with company context
#             system_prompt = self._build_system_prompt(user_question)

#             # Generate answer
#             try:
#                 response = model.generate_content(system_prompt)
#                 answer = response.text.strip() if response and response.text else (
#                     "Sorry, I couldn't generate a response at the moment. Please try again."
#                 )
#             except Exception as e:
#                 logger.error(f"Gemini API response error: {str(e)}", exc_info=True)
#                 return Response(
#                     {
#                         "status": "error",
#                         "message": "Failed to generate response. Please try again later.",
#                         "data": {}
#                     },
#                     status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 )

#             # Log successful query
#             logger.info(f"Chatbot query processed: {user_question[:50]}... Response length: {len(answer)}")

#             # Format successful response
#             return Response(
#                 {
#                     "status": "success",
#                     "message": "Response generated successfully.",
#                     "data": {"answer": answer}
#                 },
#                 status=status.HTTP_200_OK
#             )

#         except Exception as e:
#             logger.error(f"Unexpected error in GetAnswerAPIView: {str(e)}", exc_info=True)
#             return Response(
#                 {
#                     "status": "error",
#                     "message": "An unexpected error occurred. Please try again later.",
#                     "data": {}
#                 },
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

#     def _sanitize_input(self, input_text):
#         """
#         Sanitize user input to prevent injection attacks and clean up text.
#         """
#         # Remove potentially dangerous characters and excessive whitespace
#         sanitized = re.sub(r'[<>;{}]', '', input_text)
#         sanitized = re.sub(r'\s+', ' ', sanitized).strip()
#         return sanitized

#     def _build_system_prompt(self, user_question):
#         """
#         Construct a detailed system prompt for Gemini AI with company context.
#         """
#         company_info = {
#             "name": "SMB Digital Zone",
#             "location": "Dubai, UAE",
#             "website": "https://smbdigitalzone.com/",
#             "about_url": "https://smbdigitalzone.com/about-us/",
#             "services_url": "https://smbdigitalzone.com/services/",
#             "description": (
#                 "SMB Digital Zone is a leading digital solutions company based in Dubai, "
#                 "specializing in web development, digital marketing, and business automation."
#             )
#         }

#         system_prompt = f"""
#         You are a professional AI assistant for {company_info['name']}, a digital solutions company based in {company_info['location']}.
#         Your role is to provide accurate, concise, and professional answers about {company_info['name']}’s services, founders, company information, and contact details.

#         **Company Information:**
#         - Name: {company_info['name']}
#         - Location: {company_info['location']}
#         - Website: {company_info['website']}
#         - Founders: Refer to {company_info['about_url']}
#         - Services: Refer to {company_info['services_url']}
#         - Description: {company_info['description']}

#         **Guidelines:**
#         - Respond only to questions related to {company_info['name']}.
#         - Use bullet points, headings, and clear formatting for lists (e.g., services).
#         - Be polite, professional, and concise.
#         - If the question is unrelated to {company_info['name']}, respond with:
#           "I can only provide information about {company_info['name']} and its services. Please ask a related question."

#         **User Question:**
#         {user_question}
#         """
#         return system_prompt


# class GetAnswerAPIView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         user_question = request.data.get('question', '').strip()

#         # Check if question is agriculture-related using simple keyword filter
#         agriculture_keywords = ["crop", "soil", "farm", "farming", "agriculture", "plant", 
#                                 "fertilizer", "irrigation", "weather", "pesticide", "seed", "yield"]

#         if not any(word in user_question.lower() for word in agriculture_keywords):
#             answer = "I can only answer agriculture-related questions. Please ask something about farming or crops."
#             status_code = status.HTTP_400_BAD_REQUEST
#             matched_question = None
#         else:
#             try:
#                 # Ask Gemini
#                 model = genai.GenerativeModel("gemini-1.5-flash")
#                 response = model.generate_content(f"Answer only agriculture-related: {user_question}")

#                 answer = response.text if response.text else "Sorry, I couldn't generate a proper answer."
#                 status_code = status.HTTP_200_OK
#                 matched_question = user_question
#             except Exception as e:
#                 answer = f"Error contacting Gemini API: {str(e)}"
#                 status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
#                 matched_question = None

#         # Save interaction
#         ChatbotInteraction.objects.create(
#             user=request.user if request.user else None,
#             question=user_question,
#             matched_question=matched_question,
#             answer=answer
#         )

#         return Response({'answer': answer}, status=status_code)

class WeatherDataAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        weather_data = WeatherData.objects.filter(request.user) if request.user.is_authenticated else WeatherData.objects.all()
        if not weather_data:
            return Response({"detail": "No weather data found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = WeatherDataSerializer(weather_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = WeatherDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    


# Load trained model
MODEL_PATH = os.path.join(settings.BASE_DIR, "weatherprediction/ml_models", "crop-recommendation.joblib")

# Load trained model
model = joblib.load(MODEL_PATH)

class CropRecommendationAPIView(APIView):
    def post(self, request):
        try:
            data = request.data

            # Extract features in the correct order
            features = np.array([[
                data.get("N", 0),
                data.get("P", 0),
                data.get("K", 0),
                data.get("temperature", 25),
                data.get("humidity", 60),
                data.get("ph", 6.5),
                data.get("rainfall", 100)
            ]])

            prediction = model.predict(features)[0]

            return Response({"recommended_crop": prediction}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
