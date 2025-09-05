"""
Image generation module with support for multiple providers and fallback options.
"""

import os
import tempfile
import requests
import base64
from pathlib import Path
from typing import Optional, Tuple
import logging
from PIL import Image, ImageDraw, ImageFont
import random

logger = logging.getLogger(__name__)

class ImageGenerator:
    """Handles image generation using various providers with fallback options"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "storybook_images"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Check for available providers
        self.openai_available = False
        self.requests_available = False
        
        try:
            import openai
            self.openai_available = True
        except ImportError:
            logger.warning("OpenAI library not available")
        
        try:
            import requests
            self.requests_available = True
        except ImportError:
            logger.warning("Requests library not available")
    
    def generate_image(self, prompt: str, provider: str, style: str, size: str, 
                      openai_key: Optional[str] = None, stability_key: Optional[str] = None,
                      page_num: int = 1, hf_token: Optional[str] = None,
                      hf_model: Optional[str] = None) -> Optional[str]:
        """
        Generate an image based on the prompt and provider
        
        Args:
            prompt: Image generation prompt
            provider: Image provider to use
            style: Visual style for the image
            size: Image dimensions
            openai_key: OpenAI API key
            stability_key: Stability AI API key
            page_num: Page number for filename
            
        Returns:
            Path to generated image or None if generation fails
        """
        try:
            # Parse size
            width, height = self._parse_size(size)
            
            # Generate filename
            filename = f"page_{page_num}_{style}_{width}x{height}.png"
            output_path = self.temp_dir / filename
            
            # Try the specified provider
            if provider == "OpenAI DALL-E" and openai_key:
                success = self._generate_openai_image(prompt, openai_key, width, height, output_path)
            elif provider == "Stable Diffusion" and stability_key:
                success = self._generate_stable_diffusion_image(prompt, stability_key, width, height, output_path)
            elif provider in ("Hugging Face", "HuggingFace"):
                success = self._generate_huggingface_image(prompt, width, height, output_path, hf_token, hf_model)
            elif provider == "Placeholder Mode":
                # Use placeholder mode
                success = self._generate_placeholder_image(prompt, style, width, height, output_path, page_num)
            else:
                # Fallback to placeholder
                success = self._generate_placeholder_image(prompt, style, width, height, output_path, page_num)
            
            if success and output_path.exists():
                return str(output_path)
            else:
                logger.error(f"Image generation failed for page {page_num}")
                return None
                
        except Exception as e:
            logger.error(f"Image generation error: {e}")
            return self._generate_placeholder_image(prompt, style, 1024, 1024, 
                                                 self.temp_dir / f"page_{page_num}_fallback.png", page_num)

    def _generate_huggingface_image(self, prompt: str, width: int, height: int, output_path: Path,
                                    hf_token: Optional[str], hf_model: Optional[str]) -> bool:
        """Generate image using Hugging Face Inference API.
        Defaults to stabilityai/stable-diffusion-2-1. Token optional; if missing and 401, fall back.
        """
        try:
            if not self.requests_available:
                return False
            model = hf_model or os.environ.get("HF_MODEL_NAME", "stabilityai/stable-diffusion-2-1")
            url = f"https://api-inference.huggingface.co/models/{model}"
            headers = {"Accept": "image/png"}
            if hf_token:
                headers["Authorization"] = f"Bearer {hf_token}"

            payload = {
                "inputs": prompt,
                "options": {"wait_for_model": True},
                # Some text-to-image pipelines look at width/height in parameters
                "parameters": {"width": width, "height": height}
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=120)
            if resp.status_code == 200 and resp.content:
                with open(output_path, 'wb') as f:
                    f.write(resp.content)
                return True
            else:
                logger.error(f"Hugging Face API error {resp.status_code}: {resp.text[:200]}")
                return False
        except Exception as e:
            logger.error(f"Hugging Face generation failed: {e}")
            return False
    
    def _parse_size(self, size_str: str) -> Tuple[int, int]:
        """Parse size string to width and height"""
        try:
            if "x" in size_str:
                width, height = map(int, size_str.split("x"))
                return width, height
            else:
                return 1024, 1024
        except:
            return 1024, 1024
    
    def _generate_openai_image(self, prompt: str, api_key: str, width: int, height: int, output_path: Path) -> bool:
        """Generate image using OpenAI DALL-E"""
        try:
            import openai
            
            openai.api_key = api_key
            
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size=f"{width}x{height}",
                response_format="url"
            )
            
            image_url = response['data'][0]['url']
            
            # Download the image
            if self.requests_available:
                response = requests.get(image_url)
                if response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"OpenAI image generation failed: {e}")
            return False
    
    def _generate_stable_diffusion_image(self, prompt: str, api_key: str, width: int, height: int, output_path: Path) -> bool:
        """Generate image using Stability AI API"""
        try:
            if not self.requests_available:
                return False
            
            url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            data = {
                "text_prompts": [{"text": prompt}],
                "cfg_scale": 7,
                "height": height,
                "width": width,
                "samples": 1,
                "steps": 20,
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                image_data = base64.b64decode(result["artifacts"][0]["base64"])
                
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                return True
            else:
                logger.error(f"Stability AI API error: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Stable Diffusion image generation failed: {e}")
            return False
    
    def _generate_placeholder_image(self, prompt: str, style: str, width: int, height: int, 
                                  output_path: Path, page_num: int) -> bool:
        """Generate a placeholder image using PIL"""
        try:
            # Create a new image with the specified dimensions
            image = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(image)
            
            # Try to load a font, fallback to default if not available
            try:
                font_large = ImageFont.truetype("arial.ttf", 48)
                font_medium = ImageFont.truetype("arial.ttf", 24)
                font_small = ImageFont.truetype("arial.ttf", 16)
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Generate colors based on style
            colors = self._get_style_colors(style)
            bg_color = colors['background']
            accent_color = colors['accent']
            text_color = colors['text']
            
            # Fill background
            image = Image.new('RGB', (width, height), color=bg_color)
            draw = ImageDraw.Draw(image)
            
            # Draw decorative elements
            self._draw_decorative_elements(draw, width, height, colors, style)
            
            # Draw page number
            page_text = f"Page {page_num}"
            text_bbox = draw.textbbox((0, 0), page_text, font=font_medium)
            text_width = text_bbox[2] - text_bbox[0]
            text_x = (width - text_width) // 2
            draw.text((text_x, 50), page_text, fill=text_color, font=font_medium)
            
            # Draw style indicator
            style_text = f"{style.title()} Style"
            text_bbox = draw.textbbox((0, 0), style_text, font=font_small)
            text_width = text_bbox[2] - text_bbox[0]
            text_x = (width - text_width) // 2
            draw.text((text_x, 100), style_text, fill=text_color, font=font_small)
            
            # Draw a simple illustration based on the prompt
            self._draw_simple_illustration(draw, prompt, width, height, colors, style)
            
            # Add prompt text (truncated)
            prompt_words = prompt.split()[:10]  # First 10 words
            prompt_text = " ".join(prompt_words) + "..."
            
            # Wrap text
            lines = self._wrap_text(prompt_text, font_small, width - 40)
            y_start = height - 150
            
            for i, line in enumerate(lines):
                text_bbox = draw.textbbox((0, 0), line, font=font_small)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = (width - text_width) // 2
                draw.text((text_x, y_start + i * 20), line, fill=text_color, font=font_small)
            
            # Save the image
            image.save(output_path, 'PNG')
            return True
            
        except Exception as e:
            logger.error(f"Placeholder image generation failed: {e}")
            return False
    
    def _get_style_colors(self, style: str) -> dict:
        """Get color palette based on style"""
        color_palettes = {
            'cartoon': {
                'background': (255, 255, 255),
                'accent': (255, 193, 7),
                'text': (33, 37, 41),
                'secondary': (108, 117, 125)
            },
            'watercolor': {
                'background': (248, 249, 250),
                'accent': (220, 53, 69),
                'text': (52, 58, 64),
                'secondary': (108, 117, 125)
            },
            'flat': {
                'background': (255, 255, 255),
                'accent': (0, 123, 255),
                'text': (33, 37, 41),
                'secondary': (108, 117, 125)
            },
            'painterly': {
                'background': (245, 245, 245),
                'accent': (40, 167, 69),
                'text': (33, 37, 41),
                'secondary': (108, 117, 125)
            },
            'realistic': {
                'background': (248, 249, 250),
                'accent': (102, 16, 242),
                'text': (33, 37, 41),
                'secondary': (108, 117, 125)
            }
        }
        
        return color_palettes.get(style, color_palettes['cartoon'])
    
    def _draw_decorative_elements(self, draw, width: int, height: int, colors: dict, style: str):
        """Draw decorative elements based on style"""
        if style == 'watercolor':
            # Draw soft, flowing shapes
            for i in range(5):
                x = random.randint(0, width)
                y = random.randint(0, height)
                size = random.randint(50, 150)
                draw.ellipse([x, y, x + size, y + size], fill=colors['accent'], outline=None)
        
        elif style == 'cartoon':
            # Draw simple geometric shapes
            for i in range(3):
                x = random.randint(0, width - 100)
                y = random.randint(0, height - 100)
                size = random.randint(30, 80)
                draw.rectangle([x, y, x + size, y + size], fill=colors['accent'], outline=colors['text'])
        
        elif style == 'flat':
            # Draw clean, flat shapes
            for i in range(4):
                x = random.randint(0, width - 60)
                y = random.randint(0, height - 60)
                size = 60
                draw.rectangle([x, y, x + size, y + size], fill=colors['accent'])
        
        else:
            # Default decorative elements
            for i in range(3):
                x = random.randint(0, width - 50)
                y = random.randint(0, height - 50)
                size = random.randint(20, 50)
                draw.ellipse([x, y, x + size, y + size], fill=colors['accent'])
    
    def _draw_simple_illustration(self, draw, prompt: str, width: int, height: int, colors: dict, style: str):
        """Draw a simple illustration based on the prompt"""
        center_x, center_y = width // 2, height // 2
        
        # Simple character detection
        prompt_lower = prompt.lower()
        
        if 'fox' in prompt_lower:
            self._draw_fox(draw, center_x, center_y, colors)
        elif 'cat' in prompt_lower:
            self._draw_cat(draw, center_x, center_y, colors)
        elif 'bear' in prompt_lower:
            self._draw_bear(draw, center_x, center_y, colors)
        elif 'unicorn' in prompt_lower:
            self._draw_unicorn(draw, center_x, center_y, colors)
        else:
            self._draw_generic_character(draw, center_x, center_y, colors)
    
    def _draw_fox(self, draw, x: int, y: int, colors: dict):
        """Draw a simple fox"""
        # Body
        draw.ellipse([x-30, y-20, x+30, y+20], fill=colors['accent'])
        # Head
        draw.ellipse([x-15, y-35, x+15, y-5], fill=colors['accent'])
        # Ears
        draw.polygon([(x-10, y-40), (x-5, y-50), (x, y-40)], fill=colors['accent'])
        draw.polygon([(x, y-40), (x+5, y-50), (x+10, y-40)], fill=colors['accent'])
        # Tail
        draw.ellipse([x+25, y-10, x+45, y+10], fill=colors['accent'])
    
    def _draw_cat(self, draw, x: int, y: int, colors: dict):
        """Draw a simple cat"""
        # Body
        draw.ellipse([x-25, y-15, x+25, y+15], fill=colors['accent'])
        # Head
        draw.ellipse([x-12, y-30, x+12, y-5], fill=colors['accent'])
        # Ears
        draw.polygon([(x-8, y-35), (x-3, y-45), (x+2, y-35)], fill=colors['accent'])
        draw.polygon([(x-2, y-35), (x+3, y-45), (x+8, y-35)], fill=colors['accent'])
        # Tail
        draw.ellipse([x+20, y-8, x+35, y+8], fill=colors['accent'])
    
    def _draw_bear(self, draw, x: int, y: int, colors: dict):
        """Draw a simple bear"""
        # Body
        draw.ellipse([x-35, y-20, x+35, y+20], fill=colors['accent'])
        # Head
        draw.ellipse([x-20, y-40, x+20, y-5], fill=colors['accent'])
        # Ears
        draw.ellipse([x-15, y-45, x-5, y-35], fill=colors['accent'])
        draw.ellipse([x+5, y-45, x+15, y-35], fill=colors['accent'])
    
    def _draw_unicorn(self, draw, x: int, y: int, colors: dict):
        """Draw a simple unicorn"""
        # Body
        draw.ellipse([x-30, y-20, x+30, y+20], fill=colors['accent'])
        # Head
        draw.ellipse([x-15, y-35, x+15, y-5], fill=colors['accent'])
        # Horn
        draw.polygon([(x-3, y-40), (x+3, y-40), (x, y-55)], fill=colors['text'])
        # Ears
        draw.polygon([(x-10, y-40), (x-5, y-50), (x, y-40)], fill=colors['accent'])
        draw.polygon([(x, y-40), (x+5, y-50), (x+10, y-40)], fill=colors['accent'])
    
    def _draw_generic_character(self, draw, x: int, y: int, colors: dict):
        """Draw a generic character"""
        # Simple circle character
        draw.ellipse([x-20, y-20, x+20, y+20], fill=colors['accent'])
        # Eyes
        draw.ellipse([x-8, y-8, x-4, y-4], fill=colors['text'])
        draw.ellipse([x+4, y-8, x+8, y-4], fill=colors['text'])
        # Smile
        draw.arc([x-10, y-5, x+10, y+5], 0, 180, fill=colors['text'], width=2)
    
    def _wrap_text(self, text: str, font, max_width: int) -> list:
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            # This is a simplified version - in practice you'd measure text width
            if len(test_line) * 8 <= max_width:  # Rough estimate
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines[:3]  # Limit to 3 lines
