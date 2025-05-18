import base64
import io
import numpy as np
import tensorflow as tf
import cv2
from PIL import Image
from django.views import View
from django.http import JsonResponse
import os
from tensorflow.keras.preprocessing import image as keras_image
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.files.base import ContentFile
from .models import LeafDiseasePrediction

# === ✅ Load model once at module level ===
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, 'tomato_leaf_disease_model.h5')
model = tf.keras.models.load_model(model_path)

disease_info = {
    "American Bollworm on Cotton": {
        "description": "The American bollworm (Helicoverpa armigera) is a significant pest that attacks cotton bolls and flower buds, leading to substantial yield losses.",
        "care": "Implement crop rotation and maintain field sanitation to disrupt the pest's life cycle.",
        "treatment": "Utilize biological control agents like Bacillus thuringiensis (Bt) and apply neem oil-based insecticides.",
        "recommended_pesticides_or_fungicides": ["Spinosad", "Indoxacarb"]
    },
    "Army Worm": {
        "description": "Armyworms are caterpillar pests that consume foliage, causing severe defoliation in various crops.",
        "care": "Promote natural predators such as birds and parasitic wasps to naturally control populations.",
        "treatment": "Apply biological insecticides like Bacillus thuringiensis (Bt) during early larval stages.",
        "recommended_pesticides_or_fungicides": ["Emamectin benzoate", "Lambda-cyhalothrin"]
    },
    "Bacterial Blight in Rice": {
        "description": "A disease caused by Xanthomonas oryzae, leading to wilting seedlings, yellowing leaves, and reduced grain yield.",
        "care": "Plant resistant rice varieties and avoid high nitrogen fertilization.",
        "treatment": "Apply copper-based bactericides at the onset of symptoms.",
        "recommended_pesticides_or_fungicides": ["Copper hydroxide", "Streptomycin sulfate"]
    },
    "Brownspot": {
        "description": "Fungal disease caused by Cochliobolus miyabeanus, resulting in brown lesions on rice leaves and grains.",
        "care": "Ensure proper field drainage and balanced fertilization to reduce disease incidence.",
        "treatment": "Use fungicides when initial symptoms are observed.",
        "recommended_pesticides_or_fungicides": ["Mancozeb", "Tricyclazole"]
    },
    "Common Rust": {
        "description": "A fungal disease affecting maize, characterized by reddish-brown pustules on leaves.",
        "care": "Plant resistant hybrids and avoid overhead irrigation to minimize leaf wetness.",
        "treatment": "Apply fungicides if the disease appears early in the season.",
        "recommended_pesticides_or_fungicides": ["Propiconazole", "Azoxystrobin"]
    },
    "Cotton Aphid": {
        "description": "Small sap-sucking insects that cause leaf curling and can transmit viral diseases in cotton.",
        "care": "Encourage natural enemies like lady beetles and lacewings.",
        "treatment": "Use insecticidal soaps or oils for minor infestations; apply selective insecticides for severe cases.",
        "recommended_pesticides_or_fungicides": ["Imidacloprid", "Thiamethoxam"]
    },
    "Flag Smut": {
        "description": "A fungal disease affecting wheat, causing black streaks on leaves and stunted growth.",
        "care": "Use certified disease-free seeds and practice crop rotation.",
        "treatment": "Seed treatment with appropriate fungicides before planting.",
        "recommended_pesticides_or_fungicides": ["Carboxin", "Thiram"]
    },
    "Gray Leaf Spot": {
        "description": "Fungal disease in maize leading to grayish lesions on leaves, reducing photosynthetic area.",
        "care": "Plant resistant varieties and manage crop residues to reduce inoculum.",
        "treatment": "Apply foliar fungicides at the first sign of disease.",
        "recommended_pesticides_or_fungicides": ["Pyraclostrobin", "Tebuconazole"]
    },
    "Healthy Maize": {
        "description": "Maize plants exhibiting no signs of disease or pest infestation.",
        "care": "Maintain proper field hygiene and monitor regularly for early detection of issues.",
        "treatment": "Not applicable.",
        "recommended_pesticides_or_fungicides": []
    },
    "Healthy Wheat": {
        "description": "Wheat crops growing vigorously without any disease symptoms or pest damage.",
        "care": "Implement integrated pest management practices and ensure balanced fertilization.",
        "treatment": "Not applicable.",
        "recommended_pesticides_or_fungicides": []
    },
    "Healthy Cotton": {
        "description": "Cotton plants free from pests and diseases, showing optimal growth.",
        "care": "Regular field scouting and maintaining soil health.",
        "treatment": "Not applicable.",
        "recommended_pesticides_or_fungicides": []
    },
    "Leaf Curl": {
        "description": "Viral disease in cotton causing upward or downward curling of leaves, stunted growth, and reduced yield.",
        "care": "Plant resistant varieties and control whitefly populations, which transmit the virus.",
        "treatment": "Manage vector populations using appropriate insecticides.",
        "recommended_pesticides_or_fungicides": ["Acetamiprid", "Buprofezin"]
    },
    "Leaf Smut": {
        "description": "Fungal disease causing black powdery lesions on rice leaves, leading to tissue death.",
        "care": "Use resistant varieties and avoid excessive nitrogen application.",
        "treatment": "Fungicidal sprays at the early stages of infection.",
        "recommended_pesticides_or_fungicides": ["Propiconazole", "Mancozeb"]
    },
    "Mosaic Sugarcane": {
        "description": "Viral disease leading to mosaic patterns of light and dark green on sugarcane leaves.",
        "care": "Plant virus-free seed cane and control aphid vectors.",
        "treatment": "Rogueing of infected plants to prevent spread.",
        "recommended_pesticides_or_fungicides": []
    },
    "RedRot Sugarcane": {
        "description": "Fungal disease causing reddening of the internal stalk tissues, leading to plant death.",
        "care": "Use resistant varieties and practice crop rotation.",
        "treatment": "Remove and destroy infected canes; apply fungicides if necessary.",
        "recommended_pesticides_or_fungicides": ["Carbendazim", "Mancozeb"]
    },
    "RedRust Sugarcane": {
        "description": "Fungal disease characterized by reddish-brown pustules on sugarcane leaves.",
        "care": "Ensure proper spacing and air circulation to reduce humidity.",
        "treatment": "Apply appropriate fungicides when symptoms are first noticed.",
        "recommended_pesticides_or_fungicides": ["Propiconazole", "Tebuconazole"]
    },
    "Rice Blast": {
        "description": "A severe fungal disease in rice causing spindle-shaped lesions on leaves and panicle blast.",
        "care": "Plant resistant varieties and avoid excessive nitrogen fertilization.",
        "treatment": "Apply fungicides at the booting stage.",
        "recommended_pesticides_or_fungicides": ["Tricyclazole", "Isoprothiolane"]
    },
     "Sugarcane Healthy": {
        "description": "Sugarcane crops exhibiting no visible signs of pest or disease, indicating robust growth and optimal health.",
        "care": "Maintain regular field monitoring, balanced nutrient application, and clean irrigation practices.",
        "treatment": "Not applicable.",
        "recommended_pesticides_or_fungicides": []
    },
    "Tungro": {
        "description": "A viral disease in rice transmitted by green leafhoppers, causing stunted growth and yellow-orange leaf discoloration.",
        "care": "Use resistant varieties and manage vector populations.",
        "treatment": "Remove infected plants and apply insecticides targeting vectors.",
        "recommended_pesticides_or_fungicides": ["Imidacloprid", "Thiamethoxam"]
    },
    "Wheat Brown Leaf Rust": {
        "description": "A fungal disease causing orange-brown pustules on wheat leaves, affecting photosynthesis and yield.",
        "care": "Grow resistant cultivars and manage plant density.",
        "treatment": "Apply fungicides during early infection.",
        "recommended_pesticides_or_fungicides": ["Propiconazole", "Tebuconazole"]
    },
    "Wheat Stem Fly": {
        "description": "Pest causing dead hearts in wheat by boring into the stem base.",
        "care": "Early sowing and field sanitation reduce infestation.",
        "treatment": "Spray appropriate insecticides at the early crop stage.",
        "recommended_pesticides_or_fungicides": ["Chlorpyrifos", "Quinalphos"]
    },
    "Wheat Aphid": {
        "description": "Aphids suck sap from wheat leaves and spikes, leading to yellowing and reduced grain quality.",
        "care": "Encourage natural predators like ladybugs and hoverflies.",
        "treatment": "Spray insecticides if aphid population exceeds threshold.",
        "recommended_pesticides_or_fungicides": ["Dimethoate", "Imidacloprid"]
    },
    "Wheat Black Rust": {
        "description": "Also known as stem rust, it forms black pustules on wheat stems and leaves.",
        "care": "Use rust-resistant wheat varieties and monitor regularly.",
        "treatment": "Timely application of fungicides prevents spread.",
        "recommended_pesticides_or_fungicides": ["Propiconazole", "Triadimefon"]
    },
    "Wheat Leaf Blight": {
        "description": "Fungal disease causing tan-colored lesions with yellow halos on wheat leaves.",
        "care": "Avoid excessive irrigation and apply balanced fertilizers.",
        "treatment": "Apply fungicides during early symptoms.",
        "recommended_pesticides_or_fungicides": ["Carbendazim", "Zineb"]
    },
    "Wheat Mite": {
        "description": "Tiny mites damage wheat leaves by sucking sap, causing discoloration and stunted growth.",
        "care": "Keep fields weed-free and dust-free as mites thrive in dusty environments.",
        "treatment": "Use miticides during early infestation.",
        "recommended_pesticides_or_fungicides": ["Propargite", "Dicofol"]
    },
    "Wheat Powdery Mildew": {
        "description": "Fungal disease with white powdery spots on wheat leaves and stems.",
        "care": "Ensure proper spacing and air flow between plants.",
        "treatment": "Spray fungicides at first signs of infection.",
        "recommended_pesticides_or_fungicides": ["Sulfur", "Triadimefon"]
    },
    "Wheat Scab": {
        "description": "Also called Fusarium head blight, it causes bleaching and shriveled wheat kernels.",
        "care": "Avoid continuous wheat cropping and rotate with non-host crops.",
        "treatment": "Spray fungicides during heading stage.",
        "recommended_pesticides_or_fungicides": ["Metconazole", "Prothioconazole"]
    },
    "Wheat Yellow Rust": {
        "description": "Caused by Puccinia striiformis, this disease causes yellow pustules in stripes along leaves.",
        "care": "Plant resistant cultivars and avoid early sowing.",
        "treatment": "Timely application of fungicides curbs spread.",
        "recommended_pesticides_or_fungicides": ["Propiconazole", "Tebuconazole"]
    },
    "Wilt": {
        "description": "Fungal or bacterial infection causing sudden wilting and yellowing of crops like cotton or tomato.",
        "care": "Use disease-free planting material and rotate crops.",
        "treatment": "Apply bio-fungicides or soil drenches.",
        "recommended_pesticides_or_fungicides": ["Carbendazim", "Trichoderma harzianum"]
    },
    "Yellow Rust Sugarcane": {
        "description": "Yellow rust in sugarcane leads to yellow stripes and reduces photosynthetic capacity.",
        "care": "Plant resistant sugarcane varieties and manage field humidity.",
        "treatment": "Use fungicides when symptoms appear.",
        "recommended_pesticides_or_fungicides": ["Propiconazole", "Azoxystrobin"]
    },
    "Bacterial Blight in Cotton": {
        "description": "Caused by Xanthomonas citri, this blight results in angular leaf spots and blackened bolls.",
        "care": "Use certified seeds and avoid overhead irrigation.",
        "treatment": "Spray bactericides as preventive measure.",
        "recommended_pesticides_or_fungicides": ["Copper oxychloride", "Streptomycin"]
    },
    "Cotton Mealy Bug": {
        "description": "Mealybugs are sap-sucking pests covered in white wax, leading to stunted cotton growth.",
        "care": "Encourage biological control agents like beetles.",
        "treatment": "Use systemic insecticides.",
        "recommended_pesticides_or_fungicides": ["Buprofezin", "Imidacloprid"]
    },
    "Cotton Whitefly": {
        "description": "Whiteflies feed on sap and excrete honeydew, which encourages sooty mold.",
        "care": "Use yellow sticky traps and maintain field hygiene.",
        "treatment": "Spray selective insecticides that are soft on natural enemies.",
        "recommended_pesticides_or_fungicides": ["Acetamiprid", "Thiamethoxam"]
    },
    "Maize Ear Rot": {
        "description": "Fungal infection that affects maize ears, leading to discolored and moldy kernels.",
        "care": "Harvest maize at proper moisture levels and dry immediately.",
        "treatment": "Fungicide seed treatment and early harvest.",
        "recommended_pesticides_or_fungicides": ["Azoxystrobin", "Fludioxonil"]
    },
    "Maize Fall Armyworm": {
        "description": "Highly destructive caterpillar pest that bores into maize whorls.",
        "care": "Monitor crops regularly and use pheromone traps.",
        "treatment": "Spray biological and chemical insecticides when larvae are young.",
        "recommended_pesticides_or_fungicides": ["Spinetoram", "Emamectin benzoate"]
    },
    "Maize Stem Borer": {
        "description": "Larvae bore into maize stems and disrupt nutrient flow.",
        "care": "Early planting and field sanitation are effective.",
        "treatment": "Use insecticide granules at the base of plants.",
        "recommended_pesticides_or_fungicides": ["Carbofuran", "Fipronil"]
    },
    "Red Cotton Bug": {
        "description": "Pest causing lint discoloration and seed damage in cotton.",
        "care": "Avoid late sowing and remove infested bolls.",
        "treatment": "Apply contact insecticides during flowering.",
        "recommended_pesticides_or_fungicides": ["Cypermethrin", "Deltamethrin"]
    },
    "Thrips on Cotton": {
        "description": "Tiny pests that cause silvering of cotton leaves and retard growth.",
        "care": "Avoid water stress and use reflective mulches.",
        "treatment": "Apply systemic insecticides during early infestation.",
        "recommended_pesticides_or_fungicides": ["Spinosad", "Imidacloprid"]
    }
}

 

# === ✅ Class labels ===
class_labels = [
    "American Bollworm on Cotton", "Army Worm", "Bacterial Blight in Rice", "Brownspot",
    "Common Rust", "Cotton Aphid", "Flag Smut", "Gray Leaf Spot", "Healthy Maize", "Healthy Wheat",
    "Healthy Cotton", "Leaf Curl", "Leaf Smut", "Mosaic Sugarcane", "RedRot Sugarcane",
    "RedRust Sugarcane", "Rice Blast", "Sugarcane Healthy", "Tungro", "Wheat Brown Leaf Rust",
    "Wheat Stem Fly", "Wheat Aphid", "Wheat Black Rust", "Wheat Leaf Blight", "Wheat Mite",
    "Wheat Powdery Mildew", "Wheat Scab", "Wheat Yellow Rust", "Wilt", "Yellow Rust Sugarcane",
    "Bacterial Blight in Cotton", "Cotton Mealy Bug", "Cotton Whitefly", "Maize Ear Rot",
    "Maize Fall Armyworm", "Maize Atem Borer", "Red Cotton Bug", "Thrips on Cotton"
]


# === ✅ Contrast Enhancement Function ===
def contrast_stretching(img_array):
    img = img_array.astype(np.uint8)
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    hsv[:, :, 2] = cv2.equalizeHist(hsv[:, :, 2])
    enhanced_img = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    return enhanced_img.astype(np.float32) / 255.0

# === ✅ Class-Based View ===
@method_decorator(csrf_exempt, name='dispatch')
class PredictLeafDiseaseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))
            img_base64 = data.get('image')

            if not img_base64:
                return JsonResponse({'error': 'Image data not provided'}, status=400)

            # Decode base64 image
            img_data = base64.b64decode(img_base64.split(',')[-1])
            img = Image.open(io.BytesIO(img_data)).convert("RGB")
            img = img.resize((224, 224))
            img_array = keras_image.img_to_array(img)

            # Preprocess image
            img_array = contrast_stretching(img_array)
            img_array = np.expand_dims(img_array, axis=0)

            # Prediction
            predictions = model.predict(img_array)
            predicted_class_idx = np.argmax(predictions, axis=1)[0]
            confidence = float(np.max(predictions))
            predicted_label = class_labels[predicted_class_idx]

            # Get extra info
            info = disease_info.get(predicted_label, {
                "description": "No description available.",
                "care": "No care information available.",
                "treatment": "No treatment available.",
                "recommended_pesticides_or_fungicides": []
            })
            image_file = ContentFile(img_data, name=f"{request.user.id}_leaf_{predicted_label}.jpg")

            # Save prediction to database (only if user is authenticated)
            
            if request.user.is_authenticated:
                LeafDiseasePrediction.objects.create(
                    user=request.user,
                    image=image_file,
                    predicted_class=predicted_label,
                    confidence=confidence,
                    description=info["description"],
                    care=info["care"],
                    treatment=info["treatment"],
                    recommended_pesticides_or_fungicides=info["recommended_pesticides_or_fungicides"]
                )
            
            

            return JsonResponse({
                'predicted_class': predicted_label,
                'confidence': round(confidence * 100, 2),
                'description': info["description"],
                'care': info["care"],
                'treatment': info["treatment"],
                'recommended_pesticides_or_fungicides': info["recommended_pesticides_or_fungicides"]
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def get(self, request, *args, **kwargs):
        return JsonResponse({'message': 'Only POST method is allowed'}, status=405)