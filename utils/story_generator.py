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
            
            system_prompt = f"""You are a children's book author creating a 5-page illustrated story. 
            Generate a story in JSON format with this exact structure:
            {{
                "title": "Story Title",
                "characters": [
                    {{
                        "name": "Character Name",
                        "description": "Detailed physical description for consistent illustration"
                    }}
                ],
                "pages": [
                    {{
                        "page": 1,
                        "text": "Story text (40-80 words, age 3-8 appropriate)",
                        "image_prompt": "Detailed visual description for {style} style illustration"
                    }}
                ]
            }}
            
            Requirements:
            - 5 pages total
            - Each page text should be 50-60 words
            - Characters must be consistent across all pages
            - Image prompts should include character descriptions for visual consistency
            - Use {style} art style
            - Age appropriate for 3-8 years
            - Positive, educational themes
            - No copyrighted characters
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Create a story about: {prompt}"}
                ],
                max_tokens=2000,
                temperature=0.7
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
        """Generate story using local fallback method based on user prompt"""
        logger.info("Using local fallback story generation based on user prompt")
        
        # Extract key elements from user prompt
        prompt_lower = prompt.lower()
        
        # Extract character name from prompt if mentioned
        character_name = self._extract_character_name(prompt)
        character_desc = self._extract_character_description(prompt, character_name)
        
        # Determine story theme from prompt
        theme = self._extract_theme_from_prompt(prompt_lower)
        
        # Generate story based on theme
        if "sharing" in theme:
            story_pages = self._generate_sharing_story(character_name, character_desc, style)
        elif "adventure" in theme:
            story_pages = self._generate_adventure_story(character_name, character_desc, style)
        elif "kindness" in theme:
            story_pages = self._generate_kindness_story(character_name, character_desc, style)
        elif "creativity" in theme or "dance" in prompt_lower or "music" in prompt_lower:
            story_pages = self._generate_creativity_story(character_name, character_desc, style)
        elif "learning" in theme:
            story_pages = self._generate_learning_story(character_name, character_desc, style)
        else:
            story_pages = self._generate_magic_story(character_name, character_desc, style)
        
        return {
            "title": f"{character_name}'s Amazing Adventure",
            "characters": [
                {
                    "name": character_name,
                    "description": character_desc
                }
            ],
            "pages": story_pages
        }
    
    def _generate_sharing_story(self, character_name: str, character_desc: str, style: str) -> List[Dict]:
        """Generate a sharing-themed story"""
        return [
            {
                "page": 1,
                "text": f"Once upon a time, there was a shy little fox named {character_name}. {character_name} loved to play alone in the garden, tending to beautiful flowers and watching them bloom. But something was missing - the garden felt lonely and quiet, and {character_name} wished for friends to share the beauty with.",
                "image_prompt": f"{style} illustration: {character_desc} sitting alone in a colorful garden with flowers, looking thoughtful and a bit sad"
            },
            {
                "page": 2,
                "text": f"One sunny morning, {character_name} noticed the other forest animals playing together in the meadow. They laughed and shared stories, but {character_name} was too shy to join them. 'Maybe I can share something special with them,' {character_name} thought, looking at the beautiful garden.",
                "image_prompt": f"{style} illustration: {character_desc} watching other forest animals (rabbits, squirrels, birds) playing together in the distance, looking wistful"
            },
            {
                "page": 3,
                "text": f"{character_name} had a wonderful idea! The fox decided to share the most beautiful flowers from the garden with everyone. Carefully, {character_name} picked the prettiest blooms and arranged them in small bouquets for each friend, making sure each one was perfect.",
                "image_prompt": f"{style} illustration: {character_desc} carefully picking colorful flowers and arranging them into small bouquets, with a determined and happy expression"
            },
            {
                "page": 4,
                "text": f"With a deep breath, {character_name} approached the other animals carrying the flower bouquets. 'Would you like some flowers?' {character_name} asked shyly. The animals' eyes lit up with joy! They loved the beautiful gifts and immediately invited {character_name} to join their games.",
                "image_prompt": f"{style} illustration: {character_desc} offering flower bouquets to happy forest animals, all smiling and welcoming the fox into their group"
            },
            {
                "page": 5,
                "text": f"From that day on, {character_name} was never lonely again. The garden became a special place where all the forest friends gathered to share stories, laughter, and the beauty of nature. {character_name} learned that sharing brings the greatest joy of all, and friendship is the most precious gift!",
                "image_prompt": f"{style} illustration: {character_desc} and all the forest animals happily playing together in the garden, surrounded by beautiful flowers, with sunshine and rainbows overhead"
            }
        ]
    
    def _generate_adventure_story(self, character_name: str, character_desc: str, style: str) -> List[Dict]:
        """Generate an adventure-themed story"""
        return [
            {
                "page": 1,
                "text": f"Meet {character_name}, a curious cat who loved to explore! Every day, {character_name} would venture into the mysterious forest behind the house, looking for new discoveries and exciting adventures.",
                "image_prompt": f"{style} illustration: {character_desc} standing at the edge of a magical forest, with sparkling eyes full of curiosity and wonder"
            },
            {
                "page": 2,
                "text": f"One morning, {character_name} found a mysterious glowing path that hadn't been there before. 'I wonder where this leads!' {character_name} thought excitedly. The path seemed to sparkle with magic and promise.",
                "image_prompt": f"{style} illustration: {character_desc} discovering a glowing, magical path winding through the forest, with sparkling lights and mysterious atmosphere"
            },
            {
                "page": 3,
                "text": f"Following the path, {character_name} discovered a hidden clearing filled with talking animals! There was a wise old owl, a friendly rabbit, and a cheerful squirrel. They were having a grand party!",
                "image_prompt": f"{style} illustration: {character_desc} entering a magical clearing where various forest animals are gathered in a circle, all looking friendly and welcoming"
            },
            {
                "page": 4,
                "text": f"'Welcome to our secret gathering!' said the wise owl. 'We've been waiting for a brave explorer like you!' {character_name} was amazed and delighted to be part of this special group of friends.",
                "image_prompt": f"{style} illustration: {character_desc} meeting a wise old owl and other forest animals in the magical clearing, with expressions of surprise and joy"
            },
            {
                "page": 5,
                "text": f"From that day forward, {character_name} became the official explorer of the forest! The cat would discover new magical places and share them with all the animal friends. Every adventure was more wonderful than the last!",
                "image_prompt": f"{style} illustration: {character_desc} leading a parade of forest animals on a new adventure, with magical sparkles and a bright, happy atmosphere"
            }
        ]
    
    def _generate_kindness_story(self, character_name: str, character_desc: str, style: str) -> List[Dict]:
        """Generate a kindness-themed story"""
        return [
            {
                "page": 1,
                "text": f"{character_name} was the kindest bear in the whole forest. Every morning, {character_name} would wake up with a big smile and think, 'How can I help someone today?' The bear's heart was full of love and care.",
                "image_prompt": f"{style} illustration: {character_desc} waking up with a big smile in a cozy forest home, with sunshine streaming through the window"
            },
            {
                "page": 2,
                "text": f"One day, {character_name} heard crying coming from the old oak tree. A little bird had fallen from its nest and couldn't fly back up. 'Don't worry, little friend,' {character_name} said gently. 'I'll help you!'",
                "image_prompt": f"{style} illustration: {character_desc} carefully approaching a small, scared bird on the ground near a big oak tree, with a gentle and caring expression"
            },
            {
                "page": 3,
                "text": f"Carefully, {character_name} lifted the little bird and climbed up the tree. The bird's family was so happy to see their little one safe! 'Thank you, kind bear!' they chirped gratefully.",
                "image_prompt": f"{style} illustration: {character_desc} carefully climbing the oak tree while holding the little bird, with the bird family watching from the nest above"
            },
            {
                "page": 4,
                "text": f"Word of {character_name}'s kindness spread throughout the forest. Soon, all the animals knew they could count on the bear for help. {character_name} became known as the 'Helper Bear' and loved every moment of it!",
                "image_prompt": f"{style} illustration: {character_desc} surrounded by grateful forest animals, all smiling and thanking the bear, with a warm and happy atmosphere"
            },
            {
                "page": 5,
                "text": f"From that day on, {character_name} continued to help anyone in need. The forest became a place where everyone looked out for each other, inspired by the bear's example. Kindness truly makes the world a better place!",
                "image_prompt": f"{style} illustration: {character_desc} helping various forest animals with different tasks, creating a beautiful scene of community and kindness"
            }
        ]
    
    def _generate_magic_story(self, character_name: str, character_desc: str, style: str) -> List[Dict]:
        """Generate a magic-themed story"""
        return [
            {
                "page": 1,
                "text": f"In a magical meadow, there lived a special unicorn named {character_name}. {character_name} had the most beautiful rainbow mane and could make flowers bloom with just a touch of the horn!",
                "image_prompt": f"{style} illustration: {character_desc} in a magical meadow with rainbow flowers blooming around, with sparkles and magical atmosphere"
            },
            {
                "page": 2,
                "text": f"One day, {character_name} discovered that the meadow was losing its magic! The flowers were wilting, and the colors were fading. 'I must find a way to restore the magic!' {character_name} thought determinedly.",
                "image_prompt": f"{style} illustration: {character_desc} looking concerned at wilting flowers in the meadow, with a determined expression and magical sparkles around"
            },
            {
                "page": 3,
                "text": f"{character_name} decided to share the magic with others. The unicorn visited every corner of the meadow, touching each flower with the magical horn and spreading joy wherever {character_name} went.",
                "image_prompt": f"{style} illustration: {character_desc} moving through the meadow, touching flowers with the horn, with magical sparkles and blooming flowers following the unicorn's path"
            },
            {
                "page": 4,
                "text": f"As {character_name} shared the magic, something wonderful happened! The meadow began to glow brighter than ever before. All the creatures came to see the beautiful transformation and thanked the unicorn.",
                "image_prompt": f"{style} illustration: {character_desc} surrounded by glowing, blooming flowers and happy forest creatures, with a brilliant magical aura and rainbow colors"
            },
            {
                "page": 5,
                "text": f"From that day forward, {character_name} learned that the greatest magic comes from sharing and caring for others. The meadow became the most magical place in the whole forest, filled with love and wonder!",
                "image_prompt": f"{style} illustration: {character_desc} in the center of a brilliantly magical meadow, surrounded by happy creatures and blooming flowers, with rainbows and sparkles everywhere"
            }
        ]
    
    def _generate_creativity_story(self, character_name: str, character_desc: str, style: str) -> List[Dict]:
        """Generate a creativity-themed story"""
        return [
            {
                "page": 1,
                "text": f"Meet {character_name}, a small and brave creature who loved to dance and make music! Every day, {character_name} would tap their tiny feet and hum beautiful melodies, but the other animals didn't understand the joy of rhythm and movement.",
                "image_prompt": f"{style} illustration: {character_desc} dancing alone in a forest clearing, with musical notes floating around and a happy expression"
            },
            {
                "page": 2,
                "text": f"One day, {character_name} noticed that the forest seemed quiet and sad. The birds weren't singing, and even the wind seemed to whisper instead of dance. 'I know what this place needs,' {character_name} thought with determination.",
                "image_prompt": f"{style} illustration: {character_desc} looking around a quiet forest, with sad animals in the background and musical instruments scattered around"
            },
            {
                "page": 3,
                "text": f"{character_name} began to dance with all their heart, twirling and spinning in the meadow. The rhythm was so infectious that soon the birds started to chirp along, and the leaves began to rustle in time with the music.",
                "image_prompt": f"{style} illustration: {character_desc} dancing energetically in a meadow, with birds singing along and leaves dancing in the wind"
            },
            {
                "page": 4,
                "text": f"Before long, all the forest animals joined in! Rabbits hopped to the beat, squirrels swayed on branches, and even the wise old owl bobbed his head. {character_name} had taught everyone that music and dance bring joy to any heart.",
                "image_prompt": f"{style} illustration: {character_name} leading all the forest animals in a joyful dance, with musical notes and happy expressions everywhere"
            },
            {
                "page": 5,
                "text": f"From that day forward, the forest was filled with music and laughter. {character_name} became the forest's dance teacher, and every creature learned that when you move to the rhythm of your heart, you can spread happiness everywhere you go!",
                "image_prompt": f"{style} illustration: {character_name} teaching a group of happy forest animals to dance, with musical instruments and rainbow colors in the background"
            }
        ]
    
    def _generate_learning_story(self, character_name: str, character_desc: str, style: str) -> List[Dict]:
        """Generate a learning-themed story"""
        return [
            {
                "page": 1,
                "text": f"Once upon a time, there was a curious little creature named {character_name} who loved to learn new things. Every day, {character_name} would ask questions about everything around them, from why the sky is blue to how flowers grow so tall.",
                "image_prompt": f"{style} illustration: {character_desc} sitting with books and looking up at the sky with a curious expression, surrounded by question marks"
            },
            {
                "page": 2,
                "text": f"One morning, {character_name} discovered a mysterious old library hidden in the hollow of an ancient tree. Inside were books about all the wonders of the world, and {character_name} knew this was the perfect place to learn!",
                "image_prompt": f"{style} illustration: {character_name} discovering a magical library inside a tree, with glowing books and a sense of wonder"
            },
            {
                "page": 3,
                "text": f"Day after day, {character_name} read and studied, learning about stars, oceans, mountains, and all the amazing things in nature. But the most important lesson was yet to come - learning is best when shared with friends!",
                "image_prompt": f"{style} illustration: {character_name} reading books in the magical library, with stars and nature elements floating around"
            },
            {
                "page": 4,
                "text": f"Soon, {character_name} began to teach other animals what they had learned. The birds learned about migration, the fish learned about ocean currents, and everyone discovered that knowledge grows stronger when it's shared!",
                "image_prompt": f"{style} illustration: {character_name} teaching a group of forest animals, with educational elements and happy expressions"
            },
            {
                "page": 5,
                "text": f"From that day forward, the forest became a place of learning and discovery. {character_name} showed everyone that curiosity and sharing knowledge makes the world a more wonderful place for everyone to live and grow!",
                "image_prompt": f"{style} illustration: {character_name} surrounded by happy animals in a learning environment, with books, stars, and nature elements"
            }
        ]
    
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
        
        return ", ".join(desc_parts)
    
    def _extract_theme_from_prompt(self, prompt_lower: str) -> str:
        """Extract story theme from user prompt"""
        if "dance" in prompt_lower or "music" in prompt_lower or "rhythm" in prompt_lower:
            return "creativity and joy"
        elif "learn" in prompt_lower or "teach" in prompt_lower or "learns" in prompt_lower:
            return "learning and growth"
        elif "share" in prompt_lower or "sharing" in prompt_lower:
            return "sharing and friendship"
        elif "adventure" in prompt_lower or "explore" in prompt_lower or "discover" in prompt_lower:
            return "adventure and discovery"
        elif "help" in prompt_lower or "kind" in prompt_lower or "care" in prompt_lower:
            return "kindness and helping"
        elif "magic" in prompt_lower or "magical" in prompt_lower or "wonder" in prompt_lower:
            return "magic and wonder"
        else:
            return "adventure and discovery"
    
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
