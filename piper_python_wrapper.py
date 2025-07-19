import wave
import logging
import time
from typing import Union

from piper import PiperVoice, SynthesisConfig
from pathlib import Path


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PiperPythonWrapper:
    """
     A Python wrapper for the Piper text-to-speech engine.
    
    This class provides an interface to load voice models and 
    synthesize speech from text using the Piper TTS system.
    
    Example:
        >>> wrapper = PiperPythonWrapper()
        >>> wrapper.load_voice("models/judge_voice.onnx")
        >>> wrapper.synthesize_wav_from_string("Hello from the courtroom", "output.wav")
    """

    def __init__(self):

        """Initialize the wrapper with default settings."""

        self.voice: PiperVoice = None
        self.model_path = None
        self.use_cuda: bool = False
        self.syn_config: SynthesisConfig = None


    def load_voice(self, model_path: Union[str, Path] = "models/default.onnx", config_path: Union[str, Path] = None):

        """
        Load a Piper voice model from disk.
        
        Args:
            model_path: Path to the .onnx voice model file
            config_path: Optional path to model config file (auto-detected if None)
            
        Raises:
            Exception: If the voice model fails to load
            
        Example:
            >>> wrapper.load_voice("models/judge_voice.onnx")
        """

        start_time = time.time()

        logger.info(f"Loading voice {model_path} ...")

        try:
            voice = PiperVoice.load(
                model_path=model_path,
                config_path=config_path,
                use_cuda=self.use_cuda
            )

            self.voice = voice
            self.model_path = str(model_path)

            load_time = time.time() - start_time
            logger.info(f"Voice loaded in {load_time:.2f}s: {model_path}")

        except Exception as e:
            logger.error(f"Failed to load voice model: {e}")
            raise

    def set_syn_config(self, syn_config: SynthesisConfig):

        """
        Set synthesis configuration for speech generation.
        
        Args:
            syn_config: Configuration object controlling speech parameters

        syn_config format:
            speaker_id:         Index of speaker to use (multi-speaker voices only).
            length_scale:       Phoneme length scale (< 1 is faster, > 1 is slower).
            noise_scale:        Amount of generator noise to add.
            noise_w_scale:      Amount of phoneme width noise to add.
            normalize_audio:    nable/disable scaling audio samples to fit full range.
            volume:             Multiplier for audio samples (< 1 is quieter, > 1 is louder).
            
        Example:
            >>> config = SynthesisConfig(volume=1.2, length_scale=2.0)
            >>> wrapper.set_syn_config(config)
        """
        
        self.syn_config = syn_config
    
    def set_use_cuda(self, use_cuda: bool):

        """
        Enable or disable CUDA GPU acceleration.
        
        Args:
            use_cuda: True to use GPU, False for CPU-only
            
        Note:
            Must be called before load_voice() to take effect.
        """

        self.use_cuda = use_cuda

    def get_use_cuda(self):

        """
        Check if CUDA GPU acceleration allowed.
        
        """

        return self.use_cuda

    def synthesize_wav_from_string(self, text: str, output_path: Union[str, Path] = "static/audio/output.wav"):

        """
        Convert text to speech and save as WAV file.
        
        Args:
            text: The text to convert to speech
            output_path: Where to save the generated audio file
            
        Raises:
            Exception: If synthesis fails or no voice is loaded
            
        Example:
            >>> wrapper.synthesize_wav_from_string("Hello world", "greeting.wav")
        """

        if self.voice is None:
            raise ValueError("No voice loaded. Call load_voice() first.")

        try:
            logger.info(f"Synthesizing text: '{text[:50]}...'")
            start_time = time.time()

                       
            with wave.open(str(output_path), "wb") as wav_file:
                self.voice.synthesize_wav(
                    text, 
                    wav_file, 
                    syn_config=self.syn_config
                )

            synthesis_time = time.time() - start_time
            logger.info(f"Synthesis completed in {synthesis_time:.2f}s: {output_path}")

        except Exception as e:
            logger.error(f"Failed to synthesize voice: {e}")
            raise

    def is_voice_loaded(self) -> bool:
        """
        Check if a voice model is currently loaded.
        
        Returns:
            True if a voice is loaded, False otherwise
        """
        return self.voice is not None