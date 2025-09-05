"""
Demo script to test the Children's Storybook Generator without API keys.
This script demonstrates the placeholder/demo mode functionality.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from utils.story_generator import StoryGenerator
from utils.image_generator import ImageGenerator
from utils.pdf_builder import PDFBuilder
from utils.tts_engine import TTSEngine
from utils.character_manager import CharacterManager

def test_story_generation():
    """Test story generation in demo mode"""
    print("🧪 Testing Story Generation...")
    
    generator = StoryGenerator()
    
    # Test with a sample prompt
    prompt = "A shy fox named Poppy who learns to share sunshine with the forest — gentle, whimsical, watercolor style."
    
    story_data = generator.generate_story(prompt, api_key=None, style="watercolor")
    
    if story_data:
        print("✅ Story generation successful!")
        print(f"Title: {story_data['title']}")
        print(f"Characters: {len(story_data['characters'])}")
        print(f"Pages: {len(story_data['pages'])}")
        
        # Show first page
        first_page = story_data['pages'][0]
        print(f"\nFirst page text: {first_page['text'][:100]}...")
        print(f"First page image prompt: {first_page['image_prompt'][:100]}...")
        
        return story_data
    else:
        print("❌ Story generation failed!")
        return None

def test_image_generation(story_data):
    """Test image generation in placeholder mode"""
    print("\n🎨 Testing Image Generation...")
    
    generator = ImageGenerator()
    images = {}
    
    for page in story_data['pages']:
        page_num = page['page']
        print(f"Generating image for page {page_num}...")
        
        image_path = generator.generate_image(
            prompt=page['image_prompt'],
            provider="Placeholder Mode",
            style="watercolor",
            size="1024x1024",
            page_num=page_num
        )
        
        if image_path and Path(image_path).exists():
            images[str(page_num)] = image_path
            print(f"✅ Image generated: {image_path}")
        else:
            print(f"❌ Image generation failed for page {page_num}")
    
    return images

def test_character_consistency(story_data):
    """Test character consistency features"""
    print("\n👥 Testing Character Consistency...")
    
    manager = CharacterManager()
    
    # Create character templates
    for character in story_data['characters']:
        template = manager.create_character_template(character)
        if template:
            print(f"✅ Character template created for {character['name']}")
        else:
            print(f"❌ Character template creation failed for {character['name']}")
    
    # Test consistency validation
    issues = manager.validate_character_consistency(story_data)
    if issues:
        print(f"⚠️  Found {len(issues)} consistency issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ Character consistency validation passed!")
    
    return True

def test_tts_generation(story_data):
    """Test TTS generation in local mode"""
    print("\n🔊 Testing Text-to-Speech...")
    
    engine = TTSEngine()
    
    # Test with first page
    first_page = story_data['pages'][0]
    text = first_page['text']
    
    print("Generating audio for first page...")
    audio_path = engine.generate_audio(
        text=text,
        provider="pyttsx3 (Local)",
        page_num=1
    )
    
    if audio_path and Path(audio_path).exists():
        print(f"✅ Audio generated: {audio_path}")
        return True
    else:
        print("❌ Audio generation failed!")
        return False

def test_pdf_creation(story_data, images):
    """Test PDF creation"""
    print("\n📄 Testing PDF Creation...")
    
    builder = PDFBuilder()
    
    pdf_path = builder.create_pdf(
        story_data=story_data,
        images=images,
        output_filename="demo_storybook.pdf"
    )
    
    if pdf_path and Path(pdf_path).exists():
        print(f"✅ PDF created: {pdf_path}")
        return True
    else:
        print("❌ PDF creation failed!")
        return False

def main():
    """Run all demo tests"""
    print("🚀 Children's Storybook Generator - Demo Mode Test")
    print("=" * 60)
    
    # Test story generation
    story_data = test_story_generation()
    if not story_data:
        print("❌ Demo failed at story generation step")
        return
    
    # Test character consistency
    test_character_consistency(story_data)
    
    # Test image generation
    images = test_image_generation(story_data)
    
    # Test TTS generation
    test_tts_generation(story_data)
    
    # Test PDF creation
    if images:
        test_pdf_creation(story_data, images)
    else:
        print("⚠️  Skipping PDF test - no images generated")
    
    print("\n" + "=" * 60)
    print("🎉 Demo completed! Check the generated files:")
    print("  - Story images: Check temp directory")
    print("  - Audio files: Check temp directory") 
    print("  - PDF file: Check temp directory")
    print("\nTo run the full Streamlit app:")
    print("  streamlit run streamlit_app.py")

if __name__ == "__main__":
    main()
