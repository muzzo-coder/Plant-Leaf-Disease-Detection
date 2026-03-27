import os
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from app.utils.helpers import logger

class PredictionService:
    _instance = None
    
    def __new__(cls, model_path, kb_path):
        if cls._instance is None:
            cls._instance = super(PredictionService, cls).__new__(cls)
            cls._instance.model_path = model_path
            cls._instance.kb_path = kb_path
            cls._instance.model = None
            cls._instance.knowledge_base = {}
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Loads the TensorFlow model and Knowledge Base JSON statically."""
        try:
            logger.info("Loading ML Model...")
            self.model = tf.keras.models.load_model(self.model_path)
            logger.info("ML Model Loaded Successfully.")
        except Exception as e:
            logger.error(f"Failed to load ML Model: {e}")
            raise

        try:
            logger.info("Loading Knowledge Base...")
            with open(self.kb_path, 'r') as f:
                self.knowledge_base = json.load(f)
            logger.info("Knowledge Base Loaded Successfully.")
        except Exception as e:
            logger.error(f"Failed to load Knowledge Base JSON: {e}")
            raise

    def predict(self, file_path):
        """Pre-processes image, runs inference, and composes rich response."""
        try:
            logger.info(f"Processing image at {file_path}")
            
            # 1. Preprocessing
            img = load_img(file_path, target_size=(128, 128))
            img_array = img_to_array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            
            # 2. Inference
            predictions = self.model.predict(img_array)
            predicted_class = int(np.argmax(predictions, axis=1)[0])
            confidence = float(np.max(predictions))
            
            # 3. Confidence Threshold Logic
            if confidence < 0.45:
                logger.info(f"Low confidence ({confidence:.2f}) rejection.")
                return {
                    "success": True,
                    "is_plant": False,
                    "message": "Unable to confidently detect disease. Please upload a clearer, closer image of the plant leaf.",
                    "confidence": confidence
                }

            # 4. Lookup Knowledge Base
            class_str = str(predicted_class)
            disease_info = self.knowledge_base.get(class_str, {})
            
            if not disease_info:
                logger.error(f"Class {class_str} missing from Knowledge Base.")
                return {"success": False, "error": "Internal Knowledge Base mapping error."}

            # 5. Build Comprehensive Output
            return {
                "success": True,
                "is_plant": True,
                "confidence": confidence,
                "result": disease_info
            }

        except Exception as e:
            logger.exception("Error during prediction process")
            return {"success": False, "error": "Failed during AI analysis."}
