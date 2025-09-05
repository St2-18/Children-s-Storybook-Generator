"""
Test script to verify custom prompt handling
"""

from utils.story_generator import StoryGenerator

def test_custom_prompt():
    """Test story generation with custom prompt"""
    print("🧪 Testing Custom Prompt Handling...")
    
    generator = StoryGenerator()
    
    # Test with a custom prompt
    custom_prompt = "A brave little mouse named Max who learns to dance and helps other animals find their rhythm"
    
    print(f"Input prompt: {custom_prompt}")
    print("-" * 60)
    
    story_data = generator.generate_story(custom_prompt, api_key=None, style="cartoon")
    
    if story_data:
        print("✅ Story generation successful!")
        print(f"Title: {story_data['title']}")
        print(f"Characters: {len(story_data['characters'])}")
        
        # Show character details
        for char in story_data['characters']:
            print(f"Character: {char['name']}")
            print(f"Description: {char['description']}")
        
        print(f"\nPages: {len(story_data['pages'])}")
        
        # Show first page with word count
        first_page = story_data['pages'][0]
        word_count = len(first_page['text'].split())
        print(f"\nFirst page text ({word_count} words):")
        print(first_page['text'])
        print(f"\nFirst page image prompt:")
        print(first_page['image_prompt'])
        
        return True
    else:
        print("❌ Story generation failed!")
        return False

if __name__ == "__main__":
    test_custom_prompt()
