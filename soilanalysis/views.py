import base64
import numpy as np
import cv2
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import pickle

# Load models (assuming they're stored in your Django project directory)
Pmodel = pickle.load(open('soilanalysis/Pclassifier.pkl', 'rb'))
pHmodel = pickle.load(open('soilanalysis/pHclassifier.pkl', 'rb'))
OMmodel = pickle.load(open('soilanalysis/OMclassifier.pkl', 'rb'))
ECmodel = pickle.load(open('soilanalysis/ECclassifier.pkl', 'rb'))

class HomeView(APIView):
    def get(self, request):
        return Response(["Serving service to mobile application with API to respond to image with analysis"])


class PredictView(APIView):
    def post(self, request):
        input_image = request.data.get('inputImage')
        if input_image:
            try:
                # Decode the base64 image and convert it to a NumPy array
                nparr = np.frombuffer(base64.b64decode(input_image), np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                # Check if the image is loaded successfully
                if image is None:
                    return Response({"error": "Invalid image"}, status=status.HTTP_400_BAD_REQUEST)

                # Extract color channels
                blue_channel = image[:, :, 0]
                green_channel = image[:, :, 1]
                red_channel = image[:, :, 2]
                temp = (np.median(green_channel) + np.median(blue_channel) + np.median(red_channel)) / 3
                temp = np.nanmean(temp)

                # Model predictions
                Presult = float(Pmodel.predict([[temp]]))
                pHresult = float(pHmodel.predict([[temp]]))
                OMresult = float(OMmodel.predict([[temp]]))
                ECresult = float(ECmodel.predict([[temp]]))

                # Create the result dictionary
                result = {'P': Presult, 'pH': pHresult, 'OM': OMresult, 'EC': ECresult}
                return Response(result, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        return Response(["API is running to handle Android application requests"])