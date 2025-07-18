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
    tts_app = PiperPythonWrapper()
    
    
    logger.info("TTS Web Application initialized")


# Flask Routes
@app.route('/')
def index():
    """Main page"""
    
    return "<p>Hello, World!</p>"


if __name__ == 'main':
    initialize()
    print(f"Starting web server on http://localhost:8000")

    app.run(host='0.0.0.0', port=8000, debug=True)