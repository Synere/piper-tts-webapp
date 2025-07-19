// Global variables
let currentAudioUrl = null;
let currentFilename = null;

// DOM elements
// Voice model loading and generation
const modelSelect = document.getElementById('modelSelect');
const loadModelBtn = document.getElementById('loadModelBtn');
const generateBtn = document.getElementById('generateBtn');
const cudaCheckbox = document.getElementById('useCuda')

// Textbox
const textInput = document.getElementById('textInput');
const charCount = document.getElementById('charCount');

// Audio player
const audioSection = document.getElementById('audioSection');
const audioPlayer = document.getElementById('audioPlayer');
const audioInfo = document.getElementById('audioInfo');
const playBtn = document.getElementById('playBtn');
const pauseBtn = document.getElementById('pauseBtn');
const downloadBtn = document.getElementById('downloadBtn');


// Status
const generateStatus = document.getElementById('generateStatus');
const modelStatus = document.getElementById('modelStatus');

/**
 * Display status messages in UI elements
 * @param {HTMLElement} element - DOM element to display status in
 * @param {string} message - Status message text (can include HTML)
 * @param {string} type - Status type ('success', 'error', 'info')
 */
function showStatus(element, message, type) {
    element.innerHTML = `<div class="status ${type}">${message}</div>`;
    element.classList.remove('hidden');
}

/**
 * Handle model selection changes
 * Enables/disables the load model button based on selection
 */
modelSelect.addEventListener('change', function() {
    // If no model selected, value is blank
    loadModelBtn.disabled = !this.value;
});

/**
 * Handle load model button click
 * Loads the selected voice model via API call
 * Updates UI with loading state and results
 */
loadModelBtn.addEventListener('click', async function() {
    const modelPath = modelSelect.value;
    const useCuda = cudaCheckbox.checked;
    
    if (!modelPath) return;
    
    this.disabled = true;
    this.textContent = '⏳ Loading...';
    
    try {
        const response = await fetch('/api/load_model', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                model_path: modelPath,
                use_cuda: useCuda
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showStatus(modelStatus, `✅ Model loaded <br> Model path: ${result.model_path} <br> Cuda enabled: ${result.cuda_enabled}`, 'success');
            generateBtn.disabled = false;
        } else {
            showStatus(modelStatus, `❌ ${result.error}`, 'error');
        }
    } catch (error) {
        showStatus(modelStatus, `❌ Error: ${error.message}`, 'error');
    } finally {
        this.disabled = false;
        this.textContent = 'Load Selected Model';
    }
});

/**
 * Handle text input changes
 * Updates the character counter display
 */
textInput.addEventListener('input', function() {
    charCount.textContent = this.value.length;
});

/**
 * Handle generate speech button click
 * Validates input text and sends API request to generate speech
 * Updates UI with generation progress and results
 */
generateBtn.addEventListener('click', async function() {
    const text = textInput.value.trim();
    
    if (!text) {
        showStatus(generateStatus, '❌ Please enter some text', 'error');
        return;
    }
    
    this.disabled = true;
    this.textContent = '🔄 Generating...';
    showStatus(generateStatus, '⏳ Generating speech...', 'info');
    
    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text: text})
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Global variable setting for download
            currentAudioUrl = result.audio_url;
            currentFilename = result.filename;

            // Show audio section
            audioSection.classList.remove('hidden');
            audioPlayer.src = result.audio_url;
            
            // Update audio info
            const sizeKB = Math.round(result.file_size / 1024);
            audioInfo.textContent = `File: ${result.filename} (${sizeKB} KB)`;
            
            showStatus(generateStatus, '✅ Speech generated!', 'success');
        } else {
            showStatus(generateStatus, `❌ ${result.error}`, 'error');
        }
    } catch (error) {
        showStatus(generateStatus, `❌ Error: ${error.message}`, 'error');
    } finally {
        this.disabled = false;
        this.textContent = '🔊 Generate Speech';
    }
});


/**
 * Handle play button click
 * Starts audio playback
 */
playBtn.addEventListener('click', () => {
    audioPlayer.play();
});

/**
 * Handle pause button click
 * Pauses audio playback
 */
pauseBtn.addEventListener('click', () => {
    audioPlayer.pause();
});

/**
 * Handle download button click
 * Downloads the currently generated audio file
 */
downloadBtn.addEventListener('click', function() {
    if (currentAudioUrl) {
        const a = document.createElement('a');
        a.href = currentAudioUrl;
        a.download = currentFilename || 'speech.wav';
        a.click();
    }
});


/**
 * Initialize webpage on DOM content loaded
 * Sets up initial state and checks for existing voice model
 */
document.addEventListener('DOMContentLoaded', function() {
    // Character count
    charCount.textContent = textInput.value.length;
    
    // Check if voice is already loaded
    fetch('/api/status')
        .then(response => response.json())
        .then(status => {
            if (status.voice_loaded) {
                showStatus(modelStatus, `✅ Voice model already loaded <br> Model path: ${status.model_path} <br> Cuda enabled: ${status.cuda_enabled}`, 'success');
                generateBtn.disabled = false;
            }
        })
        .catch(error => console.error('Status check failed:', error));
});