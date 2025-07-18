import unittest
import os
from pathlib import Path

from piper_python_wrapper import PiperPythonWrapper

class TestPiperWrapper(unittest.TestCase):

    def test_voice_loading_and_synthesis(self):
        wrapper = PiperPythonWrapper()
        wrapper.load_voice("models/default.onnx")
        
        output_path = Path("audio/test_output.wav")
        wrapper.synthesize_wav_from_string("Hello from the courtroom", output_path)
        
        self.assertTrue(output_path.exists(), "WAV file was not created")

        # Clean up
        output_path.unlink()

if __name__ == "__main__":
    unittest.main()