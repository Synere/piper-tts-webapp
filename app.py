import logging
import time

from pathlib import Path
from flask import Flask, render_template, request, url_for, send_file
from piper_python_wrapper import PiperPythonWrapper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = Flask(__name__)

tts_wrapper = None

def initialize():
    """Initialize the TTS application.
    
    Sets up the global tts_wrapper instance with PiperPythonWrapper
    for text-to-speech functionality. Must be called before using
    any TTS features.
    
    Raises:
        Exception: If initialization fails
    """

    global tts_wrapper

    logger.info("Initializing TTS Web Application...")
    tts_wrapper = PiperPythonWrapper()
    
    
    logger.info("TTS Web Application initialized")


def get_model_files():
    """Get list of available .onnx model files in the models directory.
    
    Scans the 'models' directory for .onnx files and returns information
    about each model including whether it has a corresponding config file.
    
    Returns:
        list: List of dictionaries containing model information:
            - filename (str): The model filename
            - path (str): Full path to the model file
            - has_config (bool): Whether corresponding .json config exists
            - size_mb (float): File size in megabytes
    
    Note:
        Returns empty list if models directory doesn't exist.
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
    """Render the main web interface page.
    
    Displays the TTS web interface with available models and current
    voice loading status.
    
    Returns:
        str: Rendered HTML template or error message with 500 status
        
    Raises:
        500: If application is not initialized
    """
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
    """Get current application status.
    
    Returns information about the TTS system state including
    whether a voice model is loaded and system capabilities.
    
    Returns:
        dict: JSON object containing:
            - voice_loaded (bool): Whether a voice model is loaded
            - model_path (str): Path to currently loaded model
            - models_available (int): Number of available models
            - cuda_enabled (bool): Whether CUDA is enabled
    """
    if tts_wrapper is None:
        return {
            "voice_loaded": False,
            "model_path": '',
            "models_available": 0,
            "cuda_enabled": False  # Add actual CUDA detection
        }
    return {
        "voice_loaded": tts_wrapper.is_voice_loaded() if tts_wrapper else False,
        "model_path": tts_wrapper.model_path,
        "models_available": len(get_model_files()),
        "cuda_enabled": tts_wrapper.get_use_cuda()  # Add actual CUDA detection
    }

@app.route('/api/models')
def api_get_models():
    """Get list of available model files.
    
    Returns the same information as get_model_files() but as a JSON API endpoint.
    Currently unused as the model list is populated server-side in the template.
    
    Returns:
        list: JSON array of model file information
    
    Note:
        This endpoint exists for potential future dynamic model loading
        but is not currently used by the frontend.
    """
    return get_model_files()

@app.route('/api/load_model', methods=['POST'])
def api_load_model():
    """Load a voice model for speech synthesis.
    
    Accepts JSON request with model path and CUDA preference,
    loads the specified model into the TTS wrapper.
    
    Expected JSON payload:
        {
            "model_path": str,  # Path to the .onnx model file
            "use_cuda": bool   # Whether to use CUDA acceleration (optional)
        }
    
    Returns:
        dict: JSON response containing:
            - success (bool): Whether the operation succeeded
            - model_path (str): Path to loaded model (on success)
            - cuda_enabled (bool): CUDA status (on success)
            - error (str): Error message (on failure)
    
    Raises:
        400: If no model path provided or file not found
        500: If model loading fails
    """
    if tts_wrapper is None:
        return {
            "success": False, 
            "error": "tts wrapper not initialized"
        }

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
    
@app.route('/api/generate', methods=['POST'])
def api_generate():
    """Generate speech audio from input text.
    
    Synthesizes speech from the provided text using the currently
    loaded voice model and saves it as a WAV file.
    
    Expected JSON payload:
        {
            "text": str  # Text to convert to speech
        }
    
    Returns:
        dict: JSON response containing:
            - success (bool): Whether generation succeeded
            - audio_url (str): URL to access the generated audio (on success)
            - filename (str): Generated audio filename (on success)
            - file_size (int): Audio file size in bytes (on success)
            - error (str): Error message (on failure)
    
    Raises:
        400: If no voice model is loaded or text is empty
        500: If speech generation fails
    
    Note:
        Generated files are saved to static/audio/ with timestamp-based names.
    """
    if tts_wrapper is None:
        return {
            "success": False,
            "error": "tts wrapper not initialized"
        }
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not tts_wrapper.is_voice_loaded():
            return {"success": False, "error": "No voice model loaded"}
        
        # Generate unique filename
        timestamp = int(time.time())
        filename = f"tts_output_{timestamp}.wav"
        output_path = Path("static/audio") / filename
        
        # Generate speech
        tts_wrapper.synthesize_wav_from_string(text, output_path)
        
        # Get audio file info
        file_size = output_path.stat().st_size
        
        logger.info(url_for('serve_audio', filename=filename))

        return {
            "success": True,
            "audio_url": url_for('serve_audio', filename=filename),
            "filename": filename,
            "file_size": file_size
        }
        
    except Exception as e:
        logger.error(f"Error generating speech: {e}")
        return {"success": False, "error": str(e)}
    
# Audio serving
@app.route('/audio/<filename>')
def serve_audio(filename):
    """Serve generated audio files.
    
    Provides access to WAV audio files generated by the TTS system.
    Files are served from the static/audio directory.
    
    Args:
        filename (str): Name of the audio file to serve
    
    Returns:
        Response: WAV audio file with appropriate MIME type
        
    Raises:
        404: If the requested audio file doesn't exist
    
    Security Note:
        Only serves files from the static/audio directory to prevent
        directory traversal attacks.
    """
    file_path = Path("static/audio") / filename
    
    if not file_path.exists():
        return "Audio file not found", 404
    
    
    return send_file(file_path, mimetype='audio/wav')



# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors.
    
    Args:
        error: The error object from Flask
        
    Returns:
        tuple: Rendered error template and 404 status code
    """
    return render_template('error.html',
                         error_title="Page Not Found",
                         error_message="The page you're looking for doesn't exist."), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server errors.
    
    Args:
        error: The error object from Flask
        
    Returns:
        tuple: Rendered error template and 500 status code
    """
    return render_template('error.html',
                         error_title="Server Error",
                         error_message="An internal server error occurred."), 500


if __name__ == "__main__":
    initialize()
    print(f"Starting web server on http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)