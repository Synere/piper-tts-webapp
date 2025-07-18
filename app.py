import logging

from pathlib import Path
from flask import Flask, render_template
from piper_python_wrapper import PiperPythonWrapper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = Flask(__name__)

tts_wrapper = None

def initialize():
    """Initialize the TTS application"""
    global tts_wrapper

    logger.info("Initializing TTS Web Application...")
    tts_wrapper = PiperPythonWrapper()
    
    
    logger.info("TTS Web Application initialized")


def get_model_files():
    """Get list of available .onnx model files in the models directory"""
    models_dir = Path("models")
    if not models_dir.exists():
        return []
    
    model_files = []
    for onnx_file in models_dir.glob("*.onnx"):
        # Check if corresponding .json config file exists
        json_file = onnx_file.with_suffix(".onnx.json")
        model_files.append({
            "filename": onnx_file.name,
            "path": str(onnx_file),
            "has_config": json_file.exists(),
            "size_mb": round(onnx_file.stat().st_size / (1024 * 1024), 1)
        })
    
    return sorted(model_files, key=lambda x: x["filename"])


# Flask Routes
@app.route('/')
def index():
    """Main page"""
    if not tts_wrapper:
        return "Application not initialized", 500
    
    # Get available model files
    model_files = get_model_files()
    
    return render_template('index.html',
                           model_files=model_files,
                           voice_loaded=tts_wrapper.is_voice_loaded())



# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html',
                         error_title="Page Not Found",
                         error_message="The page you're looking for doesn't exist."), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html',
                         error_title="Server Error",
                         error_message="An internal server error occurred."), 500


if __name__ == "__main__":
    initialize()
    print(f"Starting web server on http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)