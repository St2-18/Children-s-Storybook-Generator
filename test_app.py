# """
# Quick test script to verify the Streamlit app works correctly.
# """

# import subprocess
# import sys
# import time
# import webbrowser
# from pathlib import Path

# def test_imports():
#     """Test that all required modules can be imported"""
#     print("🔍 Testing imports...")
    
#     try:
#         import streamlit as st
#         print("✅ Streamlit imported successfully")
#     except ImportError as e:
#         print(f"❌ Streamlit import failed: {e}")
#         return False
    
#     try:
#         from utils.story_generator import StoryGenerator
#         from utils.image_generator import ImageGenerator
#         from utils.pdf_builder import PDFBuilder
#         from utils.tts_engine import TTSEngine
#         from utils.character_manager import CharacterManager
#         print("✅ All utility modules imported successfully")
#     except ImportError as e:
#         print(f"❌ Utility module import failed: {e}")
#         return False
    
#     return True

# def test_basic_functionality():
#     """Test basic functionality without running Streamlit"""
#     print("\n🧪 Testing basic functionality...")
    
#     try:
#         from utils.story_generator import StoryGenerator
#         from utils.image_generator import ImageGenerator
#         from utils.character_manager import CharacterManager
        
#         # Test story generation
#         generator = StoryGenerator()
#         story = generator.generate_story("A test story about a brave little mouse", style="cartoon")
        
#         if story and 'title' in story and 'pages' in story:
#             print("✅ Story generation works")
#         else:
#             print("❌ Story generation failed")
#             return False
        
#         # Test image generation
#         img_gen = ImageGenerator()
#         test_image = img_gen.generate_image(
#             "A test image of a mouse", "Placeholder Mode", "cartoon", "1024x1024", page_num=1
#         )
        
#         if test_image and Path(test_image).exists():
#             print("✅ Image generation works")
#         else:
#             print("❌ Image generation failed")
#             return False
        
#         # Test character management
#         char_manager = CharacterManager()
#         test_char = {"name": "Test Mouse", "description": "A small brown mouse with big ears"}
#         template = char_manager.create_character_template(test_char)
        
#         if template and 'name' in template:
#             print("✅ Character management works")
#         else:
#             print("❌ Character management failed")
#             return False
        
#         return True
        
#     except Exception as e:
#         print(f"❌ Basic functionality test failed: {e}")
#         return False

# def run_streamlit_app():
#     """Run the Streamlit app"""
#     print("\n🚀 Starting Streamlit app...")
#     print("The app will open in your browser at http://localhost:8501")
#     print("Press Ctrl+C to stop the app")
    
#     try:
#         # Start Streamlit
#         process = subprocess.Popen([
#             sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
#             "--server.headless", "false",
#             "--server.port", "8501"
#         ])
        
#         # Wait a moment for the app to start
#         time.sleep(3)
        
#         # Open browser
#         webbrowser.open("http://localhost:8501")
        
#         # Wait for user to stop
#         try:
#             process.wait()
#         except KeyboardInterrupt:
#             print("\n🛑 Stopping Streamlit app...")
#             process.terminate()
#             process.wait()
#             print("✅ App stopped successfully")
        
#         return True
        
#     except Exception as e:
#         print(f"❌ Failed to start Streamlit app: {e}")
#         return False

# def main():
#     """Main test function"""
#     print("🧪 Children's Storybook Generator - Test Suite")
#     print("=" * 50)
    
#     # Test imports
#     if not test_imports():
#         print("\n❌ Import tests failed. Please install missing dependencies:")
#         print("pip install -r requirements.txt")
#         return
    
#     # Test basic functionality
#     if not test_basic_functionality():
#         print("\n❌ Basic functionality tests failed.")
#         return
    
#     print("\n✅ All tests passed! The app is ready to use.")
    
#     # Ask user if they want to run the app
#     response = input("\n🚀 Would you like to start the Streamlit app? (y/n): ").lower().strip()
    
#     if response in ['y', 'yes']:
#         run_streamlit_app()
#     else:
#         print("\n📝 To run the app manually, use:")
#         print("streamlit run streamlit_app.py")

# if __name__ == "__main__":
#     main()
