import os
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from src.config import Config
from app.routes.api import api_bp
from app.services.prediction_service import PredictionService
from app.routes.api import api_bp
def create_app():
    """Application factory for modular architecture."""
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.config.from_object(Config)
    Config.init_app(app)

    # Initialize ML Predictor and attach to the app context
    models_dir = os.path.join(os.getcwd(), 'app', 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    model_path = os.path.join(os.getcwd(), 'model', 'model.h5')
    kb_path = os.path.join(models_dir, 'disease_kb.json')

    try:
        predictor = PredictionService(model_path, kb_path)
        app.config['PREDICTOR_INSTANCE'] = predictor
    except Exception as e:
        print(f"Warning: Failed to instantiate PredictionService. Ensure 'model.h5' exists. {e}")

    # Register Blueprints
    app.register_blueprint(api_bp)

    @app.route("/", methods=['GET'])
    def index():
        """Serve SPA UI Frontend"""
        return render_template('index.html')

    # Global Error Handlers
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({"success": False, "error": "File exceeds the 16MB limit."}), 413

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"success": False, "error": "Endpoint not found."}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"success": False, "error": "Internal Server Error."}), 500

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=app.config['DEBUG'], ssl_context='adhoc')

