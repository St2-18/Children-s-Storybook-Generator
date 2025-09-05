"""
Text-to-Speech engine with support for multiple providers and local fallback.
"""

import os
import tempfile
import requests
import base64
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class TTSEngine:
    """Handles text-to-speech generation using various providers"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "storybook_audio"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Check for available TTS libraries
        self.pyttsx3_available = False
        self.gtts_available = False
        self.requests_available = False
        
        try:
            import pyttsx3
            self.pyttsx3_available = True
        except ImportError:
            logger.warning("pyttsx3 not available")
        
        try:
            from gtts import gTTS
            self.gtts_available = True
        except ImportError:
            logger.warning("gTTS not available")
        
        try:
            import requests
            self.requests_available = True
        except ImportError:
            logger.warning("requests not available")
    
    def generate_audio(self, text: str, provider: str, api_key: Optional[str] = None, 
                      page_num: int = 1) -> Optional[str]:
        """
        Generate audio from text using the specified provider
        
        Args:
            text: Text to convert to speech
            provider: TTS provider to use
            api_key: API key for cloud providers
            page_num: Page number for filename
            
        Returns:
            Path to generated audio file or None if generation fails
        """
        try:
            # Clean text for TTS
            clean_text = self._clean_text_for_tts(text)
            
            # Generate filename
            filename = f"page_{page_num}_audio.mp3"
            output_path = self.temp_dir / filename
            
            # Try the specified provider
            if provider == "pyttsx3 (Local)" and self.pyttsx3_available:
                success = self._generate_pyttsx3_audio(clean_text, output_path)
            elif provider == "Google TTS" and self.gtts_available:
                success = self._generate_gtts_audio(clean_text, output_path)
            elif provider == "ElevenLabs" and api_key and self.requests_available:
                success = self._generate_elevenlabs_audio(clean_text, api_key, output_path)
            else:
                # Fallback to available provider
                if self.pyttsx3_available:
                    success = self._generate_pyttsx3_audio(clean_text, output_path)
                elif self.gtts_available:
                    success = self._generate_gtts_audio(clean_text, output_path)
                else:
                    logger.error("No TTS provider available")
                    return None
            
            if success and output_path.exists():
                return str(output_path)
            else:
                logger.error(f"Audio generation failed for page {page_num}")
                return None
                
        except Exception as e:
            logger.error(f"TTS generation error: {e}")
            return None
    
    def _clean_text_for_tts(self, text: str) -> str:
        """Clean text for better TTS output"""
        # Remove page numbers and formatting
        clean_text = text.replace("Page 1", "").replace("Page 2", "").replace("Page 3", "").replace("Page 4", "").replace("Page 5", "")
        clean_text = clean_text.replace("Page 1:", "").replace("Page 2:", "").replace("Page 3:", "").replace("Page 4:", "").replace("Page 5:", "")
        
        # Remove extra whitespace
        clean_text = " ".join(clean_text.split())
        
        # Add pauses for better flow
        clean_text = clean_text.replace(".", ". ")
        clean_text = clean_text.replace("!", "! ")
        clean_text = clean_text.replace("?", "? ")
        
        return clean_text.strip()
    
    def _generate_pyttsx3_audio(self, text: str, output_path: Path) -> bool:
        """Generate audio using pyttsx3 (local)"""
        try:
            import pyttsx3
            import pygame
            
            # Initialize TTS engine
            engine = pyttsx3.init()
            
            # Set properties for better quality
            voices = engine.getProperty('voices')
            if voices:
                # Try to find a female voice (usually better for children's stories)
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
            
            # Set speech rate and volume
            engine.setProperty('rate', 150)  # Speed of speech
            engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
            
            # Save to file
            engine.save_to_file(text, str(output_path))
            engine.runAndWait()
            
            return output_path.exists()
            
        except Exception as e:
            logger.error(f"pyttsx3 audio generation failed: {e}")
            return False
    
    def _generate_gtts_audio(self, text: str, output_path: Path) -> bool:
        """Generate audio using Google Text-to-Speech"""
        try:
            from gtts import gTTS
            
            # Create TTS object
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Save to file
            tts.save(str(output_path))
            
            return output_path.exists()
            
        except Exception as e:
            logger.error(f"gTTS audio generation failed: {e}")
            return False
    
    def _generate_elevenlabs_audio(self, text: str, api_key: str, output_path: Path) -> bool:
        """Generate audio using ElevenLabs API"""
        try:
            if not self.requests_available:
                return False
            
            url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                logger.error(f"ElevenLabs API error: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"ElevenLabs audio generation failed: {e}")
            return False
    
    def get_available_voices(self) -> list:
        """Get list of available voices for local TTS"""
        voices = []
        
        if self.pyttsx3_available:
            try:
                import pyttsx3
                engine = pyttsx3.init()
                voices = engine.getProperty('voices')
                return [{"id": voice.id, "name": voice.name} for voice in voices]
            except Exception as e:
                logger.error(f"Error getting voices: {e}")
        
        return voices
    
    def test_tts(self, provider: str, api_key: Optional[str] = None) -> bool:
        """Test TTS functionality"""
        try:
            test_text = "Hello, this is a test of the text to speech system."
            test_path = self.temp_dir / "test_audio.mp3"
            
            success = self.generate_audio(test_text, provider, api_key, 999)
            
            if success:
                # Clean up test file
                test_file = self.temp_dir / "page_999_audio.mp3"
                if test_file.exists():
                    test_file.unlink()
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"TTS test failed: {e}")
            return False
