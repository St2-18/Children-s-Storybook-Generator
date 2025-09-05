# Children's Storybook Generator 📚

A complete Python Streamlit application that generates beautiful illustrated children's stories with consistent characters, text-to-speech narration, and PDF export capabilities.

## Features ✨

- **AI-Powered Story Generation**: Create 5-page children's stories using OpenAI GPT or local fallback
- **Multiple Image Providers**: Support for OpenAI DALL-E, Stable Diffusion, and placeholder mode
- **Multiple Image Providers**: Support for OpenAI DALL-E, Stable Diffusion, Hugging Face Inference API, and placeholder mode
- **Character Consistency**: Maintain consistent character appearance across all pages
- **Text-to-Speech**: Local (pyttsx3) and cloud (Google TTS, ElevenLabs) narration options
- **PDF Export**: Generate printable storybook PDFs with images and text
- **Responsive UI**: Clean, child-friendly interface with progress indicators
- **Fallback Mode**: Works without API keys using placeholder images and local generation

## Quick Start 🚀

### Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
streamlit run streamlit_app.py
```

### Demo Mode (No API Keys Required)

The app works out-of-the-box in demo mode! Just run:

```bash
streamlit run streamlit_app.py
```

or

```bash
python -m streamlit run streamlit_app.py
```

Enter a story prompt like: "A shy fox named Poppy who learns to share sunshine with the forest — gentle, whimsical, watercolor style."

## Environment Variables 🔑

For full functionality, set these environment variables:

```bash
# OpenAI API (for story generation and DALL-E images)
export OPENAI_API_KEY="your-openai-api-key"

# Stability AI (for Stable Diffusion images)
export STABILITY_API_KEY="your-stability-api-key"

# Hugging Face (optional alternative provider)
export HF_TOKEN="your-hf-token"  # optional; some public models may work without a token
export HF_MODEL_NAME="stabilityai/stable-diffusion-2-1"

# ElevenLabs (for premium TTS)
export ELEVENLABS_API_KEY="your-elevenlabs-api-key"
```

## Usage Guide 📖

### 1. Story Input

- Enter your story prompt in the sidebar
- Choose image style (cartoon, watercolor, flat, painterly, realistic)
- Select image size and provider

### 2. API Configuration

- Add your API keys in the sidebar
- Choose your preferred image and TTS providers
- The app will automatically fallback to local options if keys are missing

### 3. Story Generation

- Click "Generate Story" to create your 5-page story
- Watch the progress as images and audio are generated
- View each page with text, images, and audio controls

### 4. Export Options

- Download the complete storybook as PDF
- Play or download individual page audio
- All files are automatically saved to your system

## Example Story Structure 📝

The app generates stories in this JSON format:

```json
{
  "title": "Poppy and the Shared Sunshine",
  "characters": [
    {
      "name": "Poppy",
      "description": "small red fox with a white-tipped tail, wears a blue scarf, curious eyes, loves gardening"
    }
  ],
  "pages": [
    {
      "page": 1,
      "text": "Once upon a time, there was a shy little fox named Poppy...",
      "image_prompt": "watercolor scene: Poppy the small red fox with white-tipped tail and blue scarf sitting alone in a colorful garden..."
    }
  ]
}
```

## Sample Prompts 💡

Try these example prompts:

- "A brave little cloud who helps flowers grow"
- "A curious cat who discovers a magical forest"
- "A kind bear who helps lost animals find their way home"
- "A magical unicorn who spreads joy through the meadow"
- "A friendly dragon who learns to share his treasure"

## Technical Details 🔧

### Architecture

- **Main App**: `streamlit_app.py` - Streamlit interface and orchestration
- **Story Generation**: `utils/story_generator.py` - OpenAI integration with local fallback
- **Image Generation**: `utils/image_generator.py` - Multiple providers with PIL fallback
- **PDF Creation**: `utils/pdf_builder.py` - ReportLab, FPDF, and img2pdf support
- **Text-to-Speech**: `utils/tts_engine.py` - Local and cloud TTS options
- **Character Management**: `utils/character_manager.py` - Consistency across pages

### Dependencies

- **Streamlit**: Web interface
- **OpenAI**: Story and image generation
- **Pillow**: Image processing and placeholder generation
- **ReportLab/FPDF**: PDF creation
- **pyttsx3/gTTS**: Text-to-speech
- **Requests**: API communication

### Fallback System

The app includes comprehensive fallback options:

- **Story Generation**: Local template-based generation if OpenAI unavailable
- **Image Generation**: Programmatic placeholder images using PIL
- **TTS**: Local pyttsx3 if cloud services unavailable
- **PDF**: Multiple PDF libraries with graceful degradation

## Testing 🧪

### Quick Test

```bash
# Run in demo mode (no API keys needed)
streamlit run streamlit_app.py

# Test with a simple prompt
"A friendly robot who learns to dance"
```

### Full Test

1. Set up API keys
2. Generate a complete story
3. Verify PDF download works
4. Test audio playback
5. Check character consistency across pages

## Troubleshooting 🔍

### Common Issues

**"No module named 'openai'"**

```bash
pip install openai>=1.3.0
```

**"Image generation failed"**

- Check API keys in sidebar
- Try placeholder mode
- Verify internet connection

**"PDF creation failed"**

- Install ReportLab: `pip install reportlab`
- Try FPDF: `pip install fpdf2`

**"Audio not playing"**

- Install pygame: `pip install pygame`
- Check browser audio permissions
- Try different TTS provider

### Debug Mode

Set logging level to see detailed error messages:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

<!-- ## License 📄

This project is open source and available under the MIT License. -->

## Support 💬

For issues and questions:

1. Check the troubleshooting section
2. Review the logs for error messages
3. Test in demo mode first
4. Create an issue with detailed information

---

**Happy Storytelling!** 📚✨

Create magical stories that will delight children and spark their imagination. The app works great for parents, teachers, and anyone who loves children's literature.

## Author

- Harshit Sharma
