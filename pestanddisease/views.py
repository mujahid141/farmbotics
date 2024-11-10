
# import numpy as np
# import base64
# from io import BytesIO
# from PIL import Image
# import tensorflow as tf
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework.decorators import api_view
# from rest_framework import status
# from django.conf import settings

# # Load the model once when the server starts
# MODEL = tf.keras.models.load_model("../saved_models/1")
# CLASS_NAMES = ["Early Blight", "Late Blight", "Healthy"]

# def read_file_as_image(data) -> np.ndarray:
#     image = np.array(Image.open(BytesIO(data)))
#     return image

# @api_view(['GET'])
# def ping(request):
#     return Response({"message": "Hello, I am alive"})

# class PredictView(APIView):
#     def post(self, request, *args, **kwargs):
#         if 'file' not in request.data:
#             return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             # Decode the base64 image
#             image_data = request.data['file']
#             image_bytes = base64.b64decode(image_data)
#             image = read_file_as_image(image_bytes)
#             img_batch = np.expand_dims(image, 0)
        
#             # Make the prediction
#             predictions = MODEL.predict(img_batch)
#             predicted_class = CLASS_NAMES[np.argmax(predictions[0])]
#             confidence = np.max(predictions[0])

#             return Response({
#                 'class': predicted_class,
#                 'confidence': float(confidence)
#             })
        
#         except Exception as e:
#             return Response({'error': 'Invalid image data', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
