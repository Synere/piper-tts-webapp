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

// Status
const generateStatus = document.getElementById('generateStatus');
const modelStatus = document.getElementById('modelStatus');

// Utility function, change status panes
function showStatus(element, message, type) {
    element.innerHTML = `<div class="status ${type}">${message}</div>`;
    element.classList.remove('hidden');
}

// Model selection handling
modelSelect.addEventListener('change', function() {
    // If no model selected, value is blank
    loadModelBtn.disabled = !this.value;
});

// Load model button
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


// Initialize webpage
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