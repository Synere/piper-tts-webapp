class PiperTTSWrapper {
    constructor() {
        this.speaking = false;
        this.generating = false;
        this.paused = false;
        this.audio = document.getElementById('piper-audio');
        this.audio_rate = 1;
        this.currentUtterance = null;
        this.modelLoaded = false;
        this.initializeModel();
        
        // Setup audio event end listener
        this.audio.addEventListener('ended', () => {
            this.speaking = false;
            this.paused = false;
            if (this.currentUtterance && this.currentUtterance.onend) {
                this.currentUtterance.onend();
            }
        });
        
    }
    
    async initializeModel() {
        try {
            // Load default.onnx model automatically
            const response = await fetch('/api/load_model', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    model_path: 'models/en-us_ritche-200judicial-vs0.1-medium.onnx',
                    use_cuda: true
                })
            });
            const result = await response.json();
            this.modelLoaded = result.success;
            if (!result.success) {
                console.error('Failed to load PiperTTS model:', result.error);
            }
        } catch (error) {
            console.error('Error initializing PiperTTS:', error);
        }
    }
    
    async speak(utterance, play_audio) {
        if (!this.modelLoaded) {
            console.error('PiperTTS model not loaded');
            if (utterance.onerror) utterance.onerror(new Error('Model not loaded'));
            return;
        }
        
        this.cancel();
        
        try {
            this.currentUtterance = utterance;
            this.generating = true;
            
            // Generate speech via API
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({text: utterance.text, play: play_audio})
            });
            
            const result = await response.json();
            
            this.generating = false;
            
            if (result.success && play_audio) {
                this.speaking = true;
                this.audio.src = result.audio_url;
                this.audio.playbackRate = this.audio_rate;
                this.audio.play();
            } else {
                this.speaking = false;
                if (utterance.onerror) utterance.onerror(new Error(result.error));
            }
        } catch (error) {
            this.speaking = false;
            if (utterance.onerror) utterance.onerror(error);
        }
    }
    
    pause() {
        if (this.speaking && !this.paused) {
            this.paused = true;
            this.audio.pause();
        }
    }
    
    resume() {
        if (this.speaking && this.paused) {
            this.paused = false;
            this.audio.play();
        }
    }
    
    cancel() {
        this.speaking = false;
        this.paused = false;
        this.audio.pause();
        this.audio.src = '';
        this.currentUtterance = null;
    }

    setPlaybackRate(rate) {
      this.audio.playbackRate = rate;
      this.audio_rate = rate;
  }
}