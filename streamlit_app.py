"""
Children's Storybook Generator
A Streamlit app that creates illustrated 5-page children's stories with consistent characters.
"""

import streamlit as st
import json
import os
import tempfile
import base64
from pathlib import Path
import time
from typing import Dict, List, Optional, Tuple
import logging

# Import our custom modules
from utils.story_generator import StoryGenerator
from utils.image_generator import ImageGenerator
# PDF builder import with safe fallback for Streamlit Cloud
try:
    from utils.pdf_builder import PDFBuilder
except Exception as _pdf_import_err:
    import logging as _logging
    _logging.getLogger(__name__).error(f"Falling back to minimal PDF builder: {_pdf_import_err}")
    from pathlib import Path as _Path
    import tempfile as _tempfile
    from typing import Dict as _Dict
    try:
        from PIL import Image as _PILImage, ImageDraw as _PILDraw, ImageFont as _PILFont
    except Exception as _e:
        _PILImage = None

    class PDFBuilder:  # Minimal PIL-only fallback
        def __init__(self):
            self.temp_dir = _Path(_tempfile.gettempdir()) / "storybook_pdfs"
            self.temp_dir.mkdir(exist_ok=True)

        def create_pdf(self, story_data: _Dict, images: _Dict, output_filename: str = "storybook.pdf") -> str | None:
            if _PILImage is None:
                return None
            try:
                page_w, page_h = 1240, 1754
                margin = 80
                image_area_h = 900

                def _get_img(page_num: int):
                    path = images.get(page_num) or images.get(str(page_num))
                    if path and _Path(path).exists():
                        try:
                            im = _PILImage.open(path).convert('RGB')
                            im.thumbnail((page_w - 2*margin, image_area_h - margin))
                            return im
                        except Exception:
                            return None
                    return None

                try:
                    title_font = _PILFont.truetype("DejaVuSans-Bold.ttf", 48)
                    body_font = _PILFont.truetype("DejaVuSans.ttf", 28)
                    small_font = _PILFont.truetype("DejaVuSans.ttf", 22)
                except Exception:
                    title_font = _PILFont.load_default()
                    body_font = _PILFont.load_default()
                    small_font = _PILFont.load_default()

                pages = []
                # Title page
                timg = _PILImage.new('RGB', (page_w, page_h), 'white')
                d = _PILDraw.Draw(timg)
                title = story_data.get('title', 'Storybook')
                tw = d.textlength(title, font=title_font)
                d.text(((page_w - tw)//2, page_h//3), title, fill='darkblue', font=title_font)
                d.text((margin, page_h//3 + 120), "A Children's Story", fill='gray', font=body_font)
                pages.append(timg)

                for p in story_data.get('pages', []):
                    canvas = _PILImage.new('RGB', (page_w, page_h), 'white')
                    draw = _PILDraw.Draw(canvas)
                    pnum = p.get('page', 1)
                    im = _get_img(pnum)
                    if im:
                        x = (page_w - im.width)//2
                        y = margin
                        canvas.paste(im, (x, y))
                    text_top = (margin + image_area_h) if im else margin
                    draw.text((margin, text_top), f"Page {pnum}", fill='black', font=small_font)
                    # simple wrap
                    text = p.get('text', '')
                    words, line, y = text.split(), [], text_top + 50
                    for w in words:
                        test = (' '.join(line+[w])).strip()
                        if draw.textlength(test, font=body_font) <= (page_w - 2*margin):
                            line.append(w)
                        else:
                            draw.text((margin, y), ' '.join(line), fill='black', font=body_font)
                            y += 44
                            line = [w]
                    if line:
                        draw.text((margin, y), ' '.join(line), fill='black', font=body_font)
                    pages.append(canvas)

                out = self.temp_dir / output_filename
                if pages:
                    pages[0].save(str(out), save_all=True, append_images=pages[1:], format='PDF')
                return str(out) if out.exists() else None
            except Exception:
                return None
from utils.tts_engine import TTSEngine
from utils.character_manager import CharacterManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Children's Storybook Generator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .story-page {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        background-color: #f9f9f9;
    }
    .character-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        background-color: #fff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .main-title {
        font-size: 2.5em;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 30px;
    }
    .page-title {
        font-size: 1.5em;
        color: #34495e;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

class StorybookApp:
    def __init__(self):
        self.story_generator = StoryGenerator()
        self.image_generator = ImageGenerator()
        self.pdf_builder = PDFBuilder()
        self.tts_engine = TTSEngine()
        self.character_manager = CharacterManager()
        
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'story_data' not in st.session_state:
            st.session_state.story_data = None
        if 'generated_images' not in st.session_state:
            st.session_state.generated_images = {}
        if 'generated_audio' not in st.session_state:
            st.session_state.generated_audio = {}
        if 'pdf_path' not in st.session_state:
            st.session_state.pdf_path = None
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'login_attempts' not in st.session_state:
            st.session_state.login_attempts = 0

    def _check_credentials(self, username: str, password: str) -> bool:
        """Validate credentials against fixed or env-provided values."""
        valid_user = os.environ.get('APP_LOGIN_USER', 'test_user')
        valid_pass = os.environ.get('APP_LOGIN_PASSWORD', 'test_pass')
        return username == valid_user and password == valid_pass

    def render_login(self) -> bool:
        """Render a simple login screen. Returns True when authenticated."""
        st.title("🔐 Login")
        st.write("Please sign in to use the Storybook Generator.")

        with st.form(key="login_form", clear_on_submit=False):
            username = st.text_input("User ID", value="", placeholder="test_user")
            password = st.text_input("Password", value="", type="password", placeholder="test_pass")
            submitted = st.form_submit_button("Log in")

            if submitted:
                if self._check_credentials(username.strip(), password):
                    st.session_state.authenticated = True
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.session_state.login_attempts += 1
                    st.error("Invalid credentials. Hint: User ID is 'test_user'.")

        st.caption("Tip: You can set APP_LOGIN_USER and APP_LOGIN_PASSWORD environment variables to change credentials.")
        return False

    def render_sidebar(self) -> Dict:
        """Render the sidebar with input controls"""
        st.sidebar.title("📚 Story Settings")
        
        # Main story prompt
        story_prompt = st.sidebar.text_area(
            "Story Prompt",
            value="A shy fox named Poppy who learns to share sunshine with the forest — gentle, whimsical, watercolor style.",
            height=100,
            help="Describe your story idea, characters, and style"
        )
        
        st.sidebar.markdown("---")
        
        # Image generation settings
        st.sidebar.subheader("🎨 Image Settings")
        
        image_provider = st.sidebar.selectbox(
            "Image Provider",
            ["OpenAI DALL-E", "Stable Diffusion", "Placeholder Mode"],
            help="Choose image generation method"
        )
        
        image_style = st.sidebar.selectbox(
            "Image Style",
            ["cartoon", "watercolor", "flat", "painterly", "realistic"],
            help="Visual style for the illustrations"
        )
        
        image_size = st.sidebar.selectbox(
            "Image Size",
            ["1024x1024", "1200x1600", "1024x1536"],
            help="Dimensions for generated images"
        )
        
        # API Keys section (optional)
        st.sidebar.subheader("🔑 API Keys (Optional)")
        st.sidebar.markdown("*Leave empty to use demo mode with placeholder images*")
        
        openai_key = st.sidebar.text_input(
            "OpenAI API Key",
            type="password",
            help="For story generation and DALL-E images (optional)"
        )
        
        stability_key = st.sidebar.text_input(
            "Stability AI Key",
            type="password",
            help="For Stable Diffusion images (optional)"
        )
        
        # TTS Settings
        st.sidebar.subheader("🔊 Audio Settings")
        
        enable_tts = st.sidebar.checkbox("Enable Text-to-Speech", value=False)
        
        tts_provider = st.sidebar.selectbox(
            "TTS Provider",
            ["pyttsx3 (Local)", "Google TTS", "ElevenLabs"],
            disabled=not enable_tts
        )
        
        tts_key = st.sidebar.text_input(
            "TTS API Key",
            type="password",
            help="Required for cloud TTS providers",
            disabled=not enable_tts or tts_provider == "pyttsx3 (Local)"
        )
        
        return {
            'story_prompt': story_prompt,
            'image_provider': image_provider,
            'image_style': image_style,
            'image_size': image_size,
            'openai_key': openai_key,
            'stability_key': stability_key,
            'enable_tts': enable_tts,
            'tts_provider': tts_provider,
            'tts_key': tts_key
        }

    def generate_story(self, settings: Dict) -> Optional[Dict]:
        """Generate the story using LLM"""
        with st.spinner("Generating your story..."):
            try:
                story_data = self.story_generator.generate_story(
                    prompt=settings['story_prompt'],
                    api_key=settings['openai_key'],
                    style=settings['image_style']
                )
                
                if story_data:
                    st.session_state.story_data = story_data
                    st.success("Story generated successfully!")
                    return story_data
                else:
                    st.error("Failed to generate story. Please try again.")
                    return None
                    
            except Exception as e:
                st.error(f"Error generating story: {str(e)}")
                logger.error(f"Story generation error: {e}")
                return None

    def generate_images(self, story_data: Dict, settings: Dict) -> Dict[str, str]:
        """Generate images for all story pages"""
        generated_images = {}
        
        with st.spinner("Creating illustrations..."):
            progress_bar = st.progress(0)
            
            for i, page in enumerate(story_data['pages']):
                try:
                    # Update progress
                    progress_bar.progress((i + 1) / len(story_data['pages']))
                    
                    # Generate character-consistent image prompt
                    image_prompt = self.character_manager.create_image_prompt(
                        page['image_prompt'],
                        story_data['characters'],
                        settings['image_style']
                    )
                    
                    # Generate image
                    image_path = self.image_generator.generate_image(
                        prompt=image_prompt,
                        provider=settings['image_provider'],
                        style=settings['image_style'],
                        size=settings['image_size'],
                        openai_key=settings['openai_key'],
                        stability_key=settings['stability_key'],
                        page_num=page['page']
                    )
                    
                    if image_path:
                        generated_images[page['page']] = image_path
                        st.success(f"Generated image for page {page['page']}")
                    else:
                        st.warning(f"Failed to generate image for page {page['page']}")
                        
                except Exception as e:
                    st.error(f"Error generating image for page {page['page']}: {str(e)}")
                    logger.error(f"Image generation error for page {page['page']}: {e}")
            
            progress_bar.empty()
            st.session_state.generated_images = generated_images
            return generated_images

    def generate_audio(self, story_data: Dict, settings: Dict) -> Dict[str, str]:
        """Generate audio for story pages"""
        if not settings['enable_tts']:
            return {}
            
        generated_audio = {}
        
        with st.spinner("Generating audio narration..."):
            progress_bar = st.progress(0)
            
            for i, page in enumerate(story_data['pages']):
                try:
                    progress_bar.progress((i + 1) / len(story_data['pages']))
                    
                    audio_path = self.tts_engine.generate_audio(
                        text=page['text'],
                        provider=settings['tts_provider'],
                        api_key=settings['tts_key'],
                        page_num=page['page']
                    )
                    
                    if audio_path:
                        generated_audio[page['page']] = audio_path
                        st.success(f"Generated audio for page {page['page']}")
                    else:
                        st.warning(f"Failed to generate audio for page {page['page']}")
                        
                except Exception as e:
                    st.error(f"Error generating audio for page {page['page']}: {str(e)}")
                    logger.error(f"Audio generation error for page {page['page']}: {e}")
            
            progress_bar.empty()
            st.session_state.generated_audio = generated_audio
            return generated_audio

    def create_pdf(self, story_data: Dict, images: Dict[str, str]) -> Optional[str]:
        """Create PDF from story and images"""
        with st.spinner("Creating PDF..."):
            try:
                pdf_path = self.pdf_builder.create_pdf(
                    story_data=story_data,
                    images=images,
                    output_filename="children_storybook.pdf"
                )
                
                if pdf_path:
                    st.session_state.pdf_path = pdf_path
                    st.success("PDF created successfully!")
                    return pdf_path
                else:
                    st.error("Failed to create PDF")
                    return None
                    
            except Exception as e:
                st.error(f"Error creating PDF: {str(e)}")
                logger.error(f"PDF creation error: {e}")
                return None

    def render_story_display(self, story_data: Dict, images: Dict[str, str], audio: Dict[str, str]):
        """Render the main story display"""
        st.markdown(f'<h1 class="main-title">{story_data["title"]}</h1>', unsafe_allow_html=True)
        
        # Character cards
        if story_data.get('characters'):
            st.subheader("👥 Characters")
            cols = st.columns(min(len(story_data['characters']), 3))
            
            for i, character in enumerate(story_data['characters']):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="character-card">
                        <h4>{character['name']}</h4>
                        <p>{character['description']}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Story pages
        st.subheader("📖 Story Pages")
        
        for page in story_data['pages']:
            with st.container():
                st.markdown(f'<div class="story-page">', unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown(f'<h3 class="page-title">Page {page["page"]}</h3>', unsafe_allow_html=True)
                    st.write(page['text'])
                    
                    # Audio controls
                    if page['page'] in audio:
                        col_play, col_download = st.columns([1, 1])
                        with col_play:
                            if st.button(f"🔊 Play", key=f"play_{page['page']}"):
                                st.audio(audio[page['page']], format="audio/mp3")
                        with col_download:
                            with open(audio[page['page']], "rb") as f:
                                audio_bytes = f.read()
                            st.download_button(
                                label="📥 Download Audio",
                                data=audio_bytes,
                                file_name=f"page_{page['page']}_audio.mp3",
                                key=f"download_audio_{page['page']}"
                            )
                
                with col2:
                    if page['page'] in images:
                        st.image(images[page['page']], use_column_width=True)
                    else:
                        st.info("Image not generated yet")
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("---")

    def run(self):
        """Main application loop"""
        self.initialize_session_state()
        
        # Require login
        if not st.session_state.authenticated:
            self.render_login()
            return
        
        # Render sidebar and get settings
        settings = self.render_sidebar()
        
        # Sidebar logout
        with st.sidebar:
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.rerun()
        
        # Main content area
        st.title("📚 Children's Storybook Generator")
        st.markdown("Create beautiful illustrated stories for children with consistent characters and narration!")
        
        # Generate story button
        if st.button("✨ Generate Story", type="primary"):
            story_data = self.generate_story(settings)
            
            if story_data:
                # Generate images
                if not settings['openai_key'] and not settings['stability_key']:
                    # Force placeholder mode if no API keys
                    settings['image_provider'] = "Placeholder Mode"
                images = self.generate_images(story_data, settings)
                
                # Generate audio if enabled
                audio = {}
                if settings['enable_tts']:
                    audio = self.generate_audio(story_data, settings)
                
                # Create PDF
                pdf_path = self.create_pdf(story_data, images)
        
        # Display generated story
        if st.session_state.story_data:
            story_data = st.session_state.story_data
            images = st.session_state.generated_images
            audio = st.session_state.generated_audio
            
            # PDF download button
            if st.session_state.pdf_path:
                with open(st.session_state.pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                st.download_button(
                    label="📥 Download Complete Storybook PDF",
                    data=pdf_bytes,
                    file_name="children_storybook.pdf",
                    mime="application/pdf",
                    type="primary"
                )
            
            # Render story display
            self.render_story_display(story_data, images, audio)

def main():
    """Main entry point"""
    app = StorybookApp()
    app.run()

if __name__ == "__main__":
    main()
