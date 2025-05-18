# import base64
# import requests
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import csrf_exempt


# @method_decorator(csrf_exempt, name='dispatch')
# class PredictSoilAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         try:
#             # Get base64 image
#             base64_img = request.data.get('inputImage')
#             if not base64_img:
#                 return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

#             # Flask API endpoint (ensure Flask server is running)
#             url = "http://127.0.0.1:5000/predict"

#             # Send POST request to Flask
#             response = requests.post(url, data={'inputImage': base64_img})

#             if response.status_code == 200:
#                 return Response(response.json(), status=status.HTTP_200_OK)
#             else:
#                 return Response(
#                     {'error': 'Flask server error', 'details': response.text},
#                     status=response.status_code
#                 )

#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def get(self, request):
#         return Response({"message": "API is up and running."})
import base64
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from .models import SoilPrediction
import uuid

@method_decorator(csrf_exempt, name='dispatch')
class PredictSoilAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Get base64 image
            base64_img = request.data.get('inputImage')
            if not base64_img:
                return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

            # Decode base64 and save image
            # try:
            #     format, imgstr = base64_img.split(';base64,')  # Separate metadata from the image data
            #     ext = format.split('/')[-1]  # Get image extension (e.g., png, jpeg)
            #     img_filename = f"{uuid.uuid4()}.{ext}"  # Create a unique filename using uuid
            #     img_file = ContentFile(base64.b64decode(imgstr), name=img_filename)
            # except Exception as e:
            #     return Response({'error': 'Invalid base64 image format'}, status=status.HTTP_400_BAD_REQUEST)

            # Flask API endpoint (ensure Flask server is running)
            url = "http://127.0.0.1:5000/predict"
            
            # Send POST request to Flask with base64 image data
            response = requests.post(url, data={'inputImage': base64_img})

            if response.status_code == 200:
                # Extract the prediction results
                result = response.json()
                phosphorus = result.get('P', 0.0)
                ph = result.get('pH', 0.0)
                organic_matter = result.get('OM', 0.0)
                ec = result.get('EC', 0.0)

                # Save to SoilPrediction model
                soil_prediction = SoilPrediction.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    image=base64_img,  # Save image
                    phosphorus=phosphorus,
                    ph=ph,
                    organic_matter=organic_matter,
                    electrical_conductivity=ec
                )

                return Response(response.json(), status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'Flask server error', 'details': response.text},
                    status=response.status_code
                )

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        return Response({"message": "API is up and running."})
