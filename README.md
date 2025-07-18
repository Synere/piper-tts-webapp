# Judicial TTS System

A text-to-speech web application designed for judicial professionals, built using PiperTTS

## Overview

This system enables judges and court personnel to generate high-quality, personalized text-to-speech audio using their own voice models.

### Core Components

1. **PiperPythonWrapper**: Python wrapper for PiperTTS functionality
2. **Flask Web Application**: REST API and web interface

### Technology Stack

- **Backend**: Python, Flask
- **TTS Engine**: PiperTTS
- **Frontend**: HTML, CSS, JavaScript

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/piper-tts-judicial-webapp.git
   cd piper-tts-judicial-webapp
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the web interface**
   - Open your browser and go to `http://localhost:8000`

### Web Interface

- **Text Input**: Enter text to be converted to speech
- **Voice Selection**: Choose from available trained voices
- **Audio Controls**: Play, pause, download generated audio
- **Settings**: Adjust speech speed, volume, and other parameters

## Deployment

### Standalone Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --name JudicialTTS app.py

# Find executable in dist/ folder
```