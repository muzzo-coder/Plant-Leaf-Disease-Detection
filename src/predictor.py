import os
import numpy as np
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.models import load_model

# Plant Disease Knowledge Base for richer UI/UX Returns
DISEASE_INFO = {
    0: {
        "name": "Bacteria Spot",
        "severity": "High",
        "treatment": "Use copper-based bactericides. Remove infected leaves and avoid overhead watering.",
        "organic_treatment": "Apply neem oil or a baking soda spray. Ensure good air circulation.",
        "prevention": "Crop rotation, use disease-free seeds, avoid working with plants when wet."
    },
    1: {
        "name": "Early Blight",
        "severity": "Medium",
        "treatment": "Apply fungicides like chlorothalonil or mancozeb as soon as symptoms appear.",
        "organic_treatment": "Use copper spray or biological control agents like Bacillus subtilis.",
        "prevention": "Stake plants, allow spacing, avoid watering foliage."
    },
    2: {
        "name": "Healthy and Fresh",
        "severity": "None",
        "treatment": "No treatment needed. Maintain optimal watering and nutrition.",
        "organic_treatment": "N/A",
        "prevention": "Continue good agricultural practices and regular monitoring."
    },
    3: {
        "name": "Late Blight",
        "severity": "High",
        "treatment": "Apply preventative fungicides (e.g., chlorothalonil, copper). Destroy severely infected plants.",
        "organic_treatment": "Apply fixed copper fungicides. Remove and destroy infected plant parts immediately.",
        "prevention": "Plant resistant varieties, destroy cull potatoes and nightshade weeds."
    },
    4: {
        "name": "Leaf Mold",
        "severity": "Medium",
        "treatment": "Use fungicides with chlorothalonil or mancozeb. Improve greenhouse ventilation.",
        "organic_treatment": "Increase air circulation, reduce humidity. Apply potassium bicarbonate.",
        "prevention": "Avoid wetting foliage, prune for better airflow, control humidity."
    },
    5: {
        "name": "Septoria Leaf Spot",
        "severity": "Medium",
        "treatment": "Apply chlorothalonil, mancozeb, or copper-based fungicides. Remove infected lower leaves.",
        "organic_treatment": "Spray with fixed copper or neem oil. Mulch to prevent soil splash.",
        "prevention": "Crop rotation, remove plant debris post-harvest, use mulch."
    },
    6: {
        "name": "Target Spot",
        "severity": "High",
        "treatment": "Apply broad-spectrum fungicides. Ensure adequate airflow and reduce leaf wetness.",
        "organic_treatment": "Use copper fungicides. Improve canopy airflow.",
        "prevention": "Provide adequate spacing, manage watering times to allow quick drying."
    },
    7: {
        "name": "Yellow Leaf Curl Virus",
        "severity": "High",
        "treatment": "No cure for infected plants. Control whitefly populations using insecticidal soap or neonicotinoids.",
        "organic_treatment": "Use reflective mulches, yellow sticky traps, and neem oil for whiteflies.",
        "prevention": "Use virus-resistant varieties, clear weeds hosting whiteflies."
    },
    8: {
        "name": "Mosaic Virus",
        "severity": "High",
        "treatment": "No cure. Remove and destroy infected plants immediately. Disinfect tools.",
        "organic_treatment": "N/A - Viral infection cannot be treated organically or chemically.",
        "prevention": "Wash hands with soap before handling plants, disinfect tools, do not use tobacco near plants."
    },
    9: {
        "name": "Two Spotted Spider Mite",
        "severity": "High",
        "treatment": "Use miticides like abamectin or bifenazate. Spray undersides of leaves thoroughly.",
        "organic_treatment": "Use horticultural oils, insecticidal soaps, or introduce predatory mites.",
        "prevention": "Avoid drought stress, dampen pathways to raise humidity."
    }
}

class DiseasePredictor:
    def __init__(self, model_path):
        """
        Initializes the model efficiently so it doesn't reload on every request.
        """
        self.model_path = model_path
        self.model = None
        self._load_model()
    
    def _load_model(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found at {self.model_path}")
        print(f"Loading ML Model from {self.model_path}...")
        self.model = load_model(self.model_path)
        print("Model Loaded Successfully.")

    def predict(self, image_path):
        """
        Takes an image path, performs preprocessing, and returns a detailed prediction JSON.
        """
        try:
            # 1. Load and Preprocess
            img = load_img(image_path, target_size=(128, 128))
            img_array = img_to_array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0) # 3D to 4D

            # 2. Predict
            predictions = self.model.predict(img_array)
            predicted_class = int(np.argmax(predictions, axis=1)[0])
            confidence = float(np.max(predictions))
            
            # 3. Retrieve Knowledge Base Info
            info = DISEASE_INFO.get(predicted_class, {})
            
            # Reject low confidence predictions (Threshold logic)
            if confidence < 0.45:
                # If confidence is exceptionally low, the image might not be a leaf at all
                return {
                    "success": True,
                    "is_plant": False,
                    "message": "Confidence is too low. Please upload a clear image of a plant leaf.",
                    "confidence": confidence
                }

            return {
                "success": True,
                "is_plant": True,
                "disease": info.get("name", "Unknown Disease"),
                "confidence": confidence,
                "severity": info.get("severity", "Unknown"),
                "treatment": info.get("treatment", "Consult a specialist."),
                "organic_treatment": info.get("organic_treatment", "Consult a specialist."),
                "prevention": info.get("prevention", "Maintain hygiene.")
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

# Instantiate a Singleton pattern for the loaded model in the app
# The actual file is usually in the root path "model.h5"
MODEL_PATH = os.path.join(os.getcwd(), 'model.h5')
# We do lazy loading to avoid issues during module import if file is missing,
# but for a production server, it should be loaded globally on worker start.
predictor_instance = None

def get_predictor():
    global predictor_instance
    if predictor_instance is None:
        try:
            predictor_instance = DiseasePredictor(MODEL_PATH)
        except Exception as e:
            print(f"Error loading model: {e}")
            return None
    return predictor_instance
