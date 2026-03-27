import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.services.prediction_service import PredictionService
from app.utils.helpers import validate_image_upload, logger

api_bp = Blueprint('api', __name__, url_prefix='')

@api_bp.route('/predict', methods=['POST'])
def predict():
    """
    Main endpoint for receiving an image, running prediction via service layer,
    and returning a rich, detailed JSON response.
    """
    # 1. Validation Logic
    file, error_msg, status_code = validate_image_upload(request)
    if error_msg:
        return jsonify({"success": False, "error": error_msg}), status_code

    # 2. Save secure temporary image file
    original_filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
    
    try:
        file.save(upload_path)
        logger.info(f"File saved cleanly to {upload_path}")
        
        # 3. Trigger Service Layer
        predictor = current_app.config.get('PREDICTOR_INSTANCE')
        if not predictor:
            logger.error("Predictor Instance loosely bound or not injected.")
            return jsonify({"success": False, "error": "ML Service unavailable."}), 503

        prediction_data = predictor.predict(upload_path)
        
        # Attach preview image URL to prediction payload to build history later
        if prediction_data.get('success'):
            prediction_data['image_url'] = f"/static/upload/{unique_filename}"
            
        return jsonify(prediction_data), 200

    except Exception as e:
        logger.exception("Prediction Route Failure")
        return jsonify({"success": False, "error": "Internal Server Error."}), 500
    
    finally:
        # NOTE: If we want to clean up storage aggressively, uncomment the line below.
        # But for 'History Dashboard' feature, we keep them in 'static/upload'.
        # if os.path.exists(upload_path): os.remove(upload_path)
        pass
