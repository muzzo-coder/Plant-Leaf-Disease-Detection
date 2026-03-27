import os
import logging
from werkzeug.utils import secure_filename

# Configure explicit logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('AgritechAI')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    """Check if uploaded file has a permitted extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image_upload(request):
    """
    Validates the incoming HTTP request for image uploads.
    Returns (error_message, status_code) on failure, or (file_object, None) on success.
    """
    if 'image' not in request.files and 'file' not in request.files:
        logger.warning("Upload failed: No image part in request")
        return None, "No image found in request", 400
        
    file = request.files.get('image') or request.files.get('file')

    if file.filename == '':
        logger.warning("Upload failed: Empty filename")
        return None, "No selected file", 400

    if not allowed_file(file.filename):
        logger.warning(f"Upload failed: Invalid extension for {file.filename}")
        return None, "Invalid file format. Only JPG, JPEG, and PNG are allowed.", 400

    return file, None, 200
