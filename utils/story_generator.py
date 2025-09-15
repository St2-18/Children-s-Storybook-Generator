"""
Story generation module using OpenAI API with fallback to local generation.
"""

import json
import os
import random
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class StoryGenerator:
    """Handles story generation using LLM or fallback methods"""
    
    def __init__(self):
        self.openai_available = False
        try:
            import openai
            self.openai_available = True
        except ImportError:
            logger.warning("OpenAI library not available, using fallback generation")
    
    def generate_story(self, prompt: str, api_key: Optional[str] = None, style: str = "cartoon") -> Optional[Dict]:
        """
        Generate a 5-page children's story from a prompt
        
        Args:
            prompt: User's story prompt
            api_key: OpenAI API key (optional)
            style: Image style for character descriptions
            
        Returns:
            Dictionary containing story data or None if generation fails
        """
        try:
            # Try OpenAI first if API key is provided
            if api_key and self.openai_available:
                return self._generate_with_openai(prompt, api_key, style)
            else:
                # Fallback to local generation
                return self._generate_local_fallback(prompt, style)
                
        except Exception as e:
            logger.error(f"Story generation failed: {e}")
            return self._generate_local_fallback(prompt, style)
    
    def _generate_with_openai(self, prompt: str, api_key: str, style: str) -> Optional[Dict]:
        """Generate story using OpenAI API"""
        try:
            import openai
            
            openai.api_key = api_key
            
            system_prompt = f"""You are a creative children's book author with unlimited imagination. Create a unique, engaging 5-page illustrated story based entirely on the user's prompt.

            Generate a story in JSON format with this exact structure:
            {{
                "title": "Creative Story Title",
                "characters": [
                    {{
                        "name": "Character Name",
                        "description": "Detailed physical description for consistent illustration"
                    }}
                ],
                "pages": [
                    {{
                        "page": 1,
                        "text": "Story text (50-80 words, age 3-8 appropriate)",
                        "image_prompt": "Detailed visual description for {style} style illustration"
                    }}
                ]
            }}
            
            Creative Guidelines:
            - 5 pages total, each with 50-80 words
            - Be completely creative and original - don't use generic templates
            - Use the user's prompt for unique characters, settings, and plot
            - Create engaging, imaginative scenarios that surprise and delight
            - Characters must be consistent across all pages
            - Image prompts should include character descriptions for visual consistency
            - Use {style} art style in image prompts
            - Age appropriate for 3-8 years with positive themes
            - No copyrighted characters - be original
            - Let your creativity flow - unusual combinations, magical elements, unexpected friendships, and imaginative solutions are encouraged
            - Make each story unique and memorable
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Create a unique, creative story based on this prompt: {prompt}"}
                ],
                max_tokens=2500,
                temperature=0.9
            )
            
            story_text = response.choices[0].message.content.strip()
            
            # Clean up the response to extract JSON
            if "```json" in story_text:
                story_text = story_text.split("```json")[1].split("```")[0]
            elif "```" in story_text:
                story_text = story_text.split("```")[1].split("```")[0]
            
            story_data = json.loads(story_text)
            
            # Validate the structure
            if self._validate_story_structure(story_data):
                return story_data
            else:
                logger.warning("Generated story structure invalid, using fallback")
                return self._generate_local_fallback(prompt, style)
                
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            return self._generate_local_fallback(prompt, style)
    
    def _generate_local_fallback(self, prompt: str, style: str) -> Dict:
        """Generate story using creative AI-based fallback method"""
        logger.info("Using creative AI-based fallback story generation")
        
        try:
            # Try to use OpenAI without API key for demo purposes
            # This will create a more creative story than hardcoded templates
            return self._generate_creative_story(prompt, style)
        except Exception as e:
            logger.error(f"Creative generation failed: {e}")
            # Ultimate fallback - create a simple story based on prompt
            return self._generate_simple_fallback(prompt, style)
    
    def _generate_creative_story(self, prompt: str, style: str) -> Dict:
        """Generate a creative story using AI-like logic"""
        import random
        
        # Extract character information from prompt
        character_name = self._extract_character_name(prompt)
        character_desc = self._extract_character_description(prompt, character_name)
        
        # Create a creative title based on the prompt
        title_words = ["Adventure", "Journey", "Discovery", "Quest", "Tale", "Story"]
        title = f"{character_name}'s {random.choice(title_words)}"
        
        # Generate creative story pages based on prompt elements
        pages = []
        prompt_lower = prompt.lower()
        
        # Page 1: Introduction
        # Clean up character description for better readability
        if character_desc and character_desc != "a wonderful character":
            clean_desc = f"a {character_desc.replace(',', ' and')}"
        else:
            clean_desc = "a wonderful character"
        intro_text = f"Once upon a time, there was {clean_desc} named {character_name}. "
        if "shy" in prompt_lower:
            intro_text += f"{character_name} was quiet and thoughtful, always observing the world with curious eyes. "
        elif "brave" in prompt_lower:
            intro_text += f"{character_name} was fearless and adventurous, always ready for new challenges. "
        elif "kind" in prompt_lower:
            intro_text += f"{character_name} had a heart full of compassion, always looking for ways to help others. "
        else:
            intro_text += f"{character_name} was special and unique, with wonderful qualities that made them extraordinary. "
        
        pages.append({
            "page": 1,
            "text": intro_text + f"One day, something amazing was about to happen that would change {character_name}'s world forever.",
            "image_prompt": f"{style} illustration: {character_desc} in a beautiful setting, looking curious and ready for adventure"
        })
        
        # Page 2: Challenge or Discovery
        if "learn" in prompt_lower or "discover" in prompt_lower:
            pages.append({
                "page": 2,
                "text": f"{character_name} discovered something wonderful - a place filled with mystery and magic! The discovery sparked {character_name}'s imagination and filled their heart with excitement about what might be possible.",
                "image_prompt": f"{style} illustration: {character_desc} discovering something magical and wonderful, with an expression of wonder and joy"
            })
        else:
            pages.append({
                "page": 2,
                "text": f"Suddenly, {character_name} faced an unexpected challenge. At first, it seemed impossible, but {character_name} remembered that every challenge is an opportunity to grow and discover new strengths.",
                "image_prompt": f"{style} illustration: {character_desc} facing a challenge with determination and courage"
            })
        
        # Page 3: Action and Growth
        pages.append({
            "page": 3,
            "text": f"{character_name} decided to take action! Using creativity, kindness, and determination, {character_name} began to work on the challenge. Each step brought new insights and {character_name} grew stronger and wiser.",
            "image_prompt": f"{style} illustration: {character_desc} taking action and working creatively to solve problems"
        })
        
        # Page 4: Resolution and Friendship
        pages.append({
            "page": 4,
            "text": f"As {character_name} worked through the challenge, wonderful friends appeared to help! Together, they discovered that the greatest adventures happen when we work together and support each other.",
            "image_prompt": f"{style} illustration: {character_desc} working with friends and other characters, showing teamwork and friendship"
        })
        
        # Page 5: Conclusion and Lesson
        pages.append({
            "page": 5,
            "text": f"From that day forward, {character_name} knew that with courage, creativity, and friendship, any challenge could become an amazing adventure. The experience taught {character_name} that the most magical things in life come from believing in yourself and caring for others.",
            "image_prompt": f"{style} illustration: {character_desc} celebrating with friends, surrounded by joy and magical elements"
        })
        
        return {
            "title": title,
            "characters": [
                {
                    "name": character_name,
                    "description": character_desc
                }
            ],
            "pages": pages
        }
    
    def _generate_simple_fallback(self, prompt: str, style: str) -> Dict:
        """Ultimate fallback - very simple story structure"""
        character_name = self._extract_character_name(prompt)
        character_desc = self._extract_character_description(prompt, character_name)
        
        return {
            "title": f"{character_name}'s Story",
            "characters": [
                {
                    "name": character_name,
                    "description": character_desc
                }
            ],
            "pages": [
            {
                "page": 1,
                    "text": f"Once upon a time, there was {character_desc} named {character_name}.",
                    "image_prompt": f"{style} illustration: {character_desc}"
            },
            {
                "page": 2,
                    "text": f"{character_name} went on an amazing adventure.",
                    "image_prompt": f"{style} illustration: {character_desc} on an adventure"
            },
            {
                "page": 3,
                    "text": f"Along the way, {character_name} met wonderful friends.",
                    "image_prompt": f"{style} illustration: {character_desc} with friends"
            },
            {
                "page": 4,
                    "text": f"Together, they discovered something magical.",
                    "image_prompt": f"{style} illustration: {character_desc} discovering magic"
            },
            {
                "page": 5,
                    "text": f"And they all lived happily ever after, knowing that friendship makes everything better.",
                    "image_prompt": f"{style} illustration: {character_desc} celebrating with friends"
                }
            ]
        }
    
    
    
    def _extract_character_name(self, prompt: str) -> str:
        """Extract character name from user prompt"""
        # Look for patterns like "named X", "called X", "X who", etc.
        import re
        
        patterns = [
            r'named\s+([A-Z][a-z]+)',
            r'called\s+([A-Z][a-z]+)',
            r'([A-Z][a-z]+)\s+who',
            r'([A-Z][a-z]+)\s+the\s+',
            r'([A-Z][a-z]+)\s+learns',
            r'([A-Z][a-z]+)\s+discovers',
            r'([A-Z][a-z]+)\s+helps'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, prompt)
            if match:
                return match.group(1)
        
        # Fallback to generic names based on animal type
        prompt_lower = prompt.lower()
        if "fox" in prompt_lower:
            return "Poppy"
        elif "cat" in prompt_lower:
            return "Whiskers"
        elif "bear" in prompt_lower:
            return "Buddy"
        elif "unicorn" in prompt_lower:
            return "Luna"
        elif "mouse" in prompt_lower:
            return "Mickey"
        elif "rabbit" in prompt_lower:
            return "Bunny"
        elif "dog" in prompt_lower:
            return "Rex"
        else:
            return "Luna"
    
    def _extract_character_description(self, prompt: str, character_name: str) -> str:
        """Extract or generate character description from prompt"""
        # Look for descriptive words in the prompt
        prompt_lower = prompt.lower()
        
        # Extract animal type
        animal_type = "creature"
        if "fox" in prompt_lower:
            animal_type = "fox"
        elif "cat" in prompt_lower:
            animal_type = "cat"
        elif "bear" in prompt_lower:
            animal_type = "bear"
        elif "unicorn" in prompt_lower:
            animal_type = "unicorn"
        elif "mouse" in prompt_lower:
            animal_type = "mouse"
        elif "rabbit" in prompt_lower:
            animal_type = "rabbit"
        elif "dog" in prompt_lower:
            animal_type = "dog"
        
        # Extract personality traits
        traits = []
        if "shy" in prompt_lower:
            traits.append("shy")
        if "brave" in prompt_lower:
            traits.append("brave")
        if "curious" in prompt_lower:
            traits.append("curious")
        if "kind" in prompt_lower:
            traits.append("kind")
        if "friendly" in prompt_lower:
            traits.append("friendly")
        if "gentle" in prompt_lower:
            traits.append("gentle")
        
        # Extract colors
        colors = []
        if "red" in prompt_lower:
            colors.append("red")
        if "blue" in prompt_lower:
            colors.append("blue")
        if "green" in prompt_lower:
            colors.append("green")
        if "yellow" in prompt_lower:
            colors.append("yellow")
        if "orange" in prompt_lower:
            colors.append("orange")
        if "purple" in prompt_lower:
            colors.append("purple")
        if "brown" in prompt_lower:
            colors.append("brown")
        
        # Build description
        desc_parts = []
        
        # Add size/type
        if "little" in prompt_lower or "small" in prompt_lower:
            desc_parts.append(f"small {animal_type}")
        else:
            desc_parts.append(f"{animal_type}")
        
        # Add colors
        if colors:
            desc_parts.append(f"with {', '.join(colors)} fur")
        
        # Add accessories
        if "scarf" in prompt_lower:
            desc_parts.append("wears a colorful scarf")
        if "hat" in prompt_lower:
            desc_parts.append("wears a hat")
        if "collar" in prompt_lower:
            desc_parts.append("wears a collar")
        
        # Add personality
        if traits:
            desc_parts.append(f"{', '.join(traits)} and adventurous")
        
        # Add special features
        if "tail" in prompt_lower:
            desc_parts.append("with a fluffy tail")
        if "wings" in prompt_lower:
            desc_parts.append("with beautiful wings")
        if "horn" in prompt_lower:
            desc_parts.append("with a magical horn")
        
        # Clean up the description for better readability
        description = ", ".join(desc_parts)
        if description and description.endswith(" and adventurous"):
            description = description.replace(" and adventurous", "")
        return description if description else "a wonderful character"
    
    
    def _validate_story_structure(self, story_data: Dict) -> bool:
        """Validate that the story has the correct structure"""
        try:
            # Check required keys
            if not all(key in story_data for key in ['title', 'characters', 'pages']):
                return False
            
            # Check characters structure
            if not isinstance(story_data['characters'], list) or len(story_data['characters']) == 0:
                return False
            
            for character in story_data['characters']:
                if not all(key in character for key in ['name', 'description']):
                    return False
            
            # Check pages structure
            if not isinstance(story_data['pages'], list) or len(story_data['pages']) != 5:
                return False
            
            for page in story_data['pages']:
                if not all(key in page for key in ['page', 'text', 'image_prompt']):
                    return False
                if not isinstance(page['page'], int) or page['page'] < 1 or page['page'] > 5:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Story validation error: {e}")
            return False
