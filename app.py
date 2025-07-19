import logging


from pathlib import Path
from piper import SynthesisConfig
from flask import Flask, render_template, request
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

    """
    Helper function
    
    Get list of available .onnx model files in the models directory
    """

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


# Webpage routes
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



# API routes
@app.route('/api/status')
def api_status():
    """

    Get application status
    
    """

    return {
        "voice_loaded": tts_wrapper.is_voice_loaded() if tts_wrapper else False,
        "model_path": tts_wrapper.model_path,
        "models_available": len(get_model_files()),
        "cuda_enabled": tts_wrapper.get_use_cuda()  # Add actual CUDA detection
    }

@app.route('/api/models')
def api_get_models():
    """

    Get list of available model files, unused
    Since model list isn't expected to be changed too much, no need to dynamically populate it in js
    
    """
    return get_model_files()

@app.route('/api/load_model', methods=['POST'])
def api_load_model():
    """Load a voice model, accepts JSON"""
    try:
        data = request.get_json()
        # JSON as dict
        model_path = data.get('model_path')
        use_cuda = data.get('use_cuda', False)

        
        
        if not model_path:
            return {"success": False, "error": "No model path provided"}
        
        model_path = Path(model_path)
        
        if not model_path.exists():
            return {"success": False, "error": "Model file not found"}
        
        # Set CUDA preference
        tts_wrapper.set_use_cuda(use_cuda)
        
        # Load the model
        tts_wrapper.load_voice(model_path)
        
        return {
            "success": True, 
            "model_path": str(model_path),
            "cuda_enabled": use_cuda
        }
        
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return {"success": False, "error": str(e)}

@app.route('/api/synthesis_config', methods=['POST'])
def api_set_synthesis_config():
    """TODO Set synthesis configuration"""
    try:
        
        data = request.get_json()
        
        syn_config = SynthesisConfig()
        
        tts_wrapper.set_syn_config(syn_config)
        
        return {
            "success": True,
            "message": "Synthesis configuration updated"
        }
        
    except Exception as e:
        logger.error(f"Error setting synthesis config: {e}")
        return {"success": False, "error": str(e)}

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