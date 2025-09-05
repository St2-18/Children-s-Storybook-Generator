"""
Character consistency manager for maintaining character appearance across story pages.
"""

import re
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class CharacterManager:
    """Handles character consistency across story pages"""
    
    def __init__(self):
        self.character_templates = {}
    
    def create_image_prompt(self, base_prompt: str, characters: List[Dict], style: str) -> str:
        """
        Create a character-consistent image prompt
        
        Args:
            base_prompt: Original image prompt
            characters: List of character descriptions
            style: Image style (cartoon, watercolor, etc.)
            
        Returns:
            Enhanced prompt with character consistency
        """
        try:
            # Start with the base prompt
            enhanced_prompt = base_prompt
            
            # Add character consistency for each character
            for character in characters:
                character_name = character.get('name', '')
                character_desc = character.get('description', '')
                
                if character_name and character_desc:
                    # Create character consistency clause
                    consistency_clause = f"featuring {character_name}, {character_desc}"
                    
                    # Add to prompt if not already present
                    if character_name.lower() not in enhanced_prompt.lower():
                        enhanced_prompt = f"{enhanced_prompt}, {consistency_clause}"
            
            # Add style consistency
            style_clause = self._get_style_consistency(style)
            if style_clause and style_clause not in enhanced_prompt:
                enhanced_prompt = f"{enhanced_prompt}, {style_clause}"
            
            # Add quality and consistency keywords
            quality_keywords = [
                "consistent character design",
                "same character appearance",
                "detailed illustration",
                "children's book illustration"
            ]
            
            for keyword in quality_keywords:
                if keyword not in enhanced_prompt.lower():
                    enhanced_prompt = f"{enhanced_prompt}, {keyword}"
            
            return enhanced_prompt
            
        except Exception as e:
            logger.error(f"Character prompt enhancement failed: {e}")
            return base_prompt
    
    def _get_style_consistency(self, style: str) -> str:
        """Get style-specific consistency keywords"""
        style_keywords = {
            'cartoon': "cartoon style, bright colors, simple shapes, child-friendly",
            'watercolor': "watercolor painting style, soft brushstrokes, gentle colors, artistic",
            'flat': "flat design style, clean lines, minimal shading, modern illustration",
            'painterly': "painterly style, artistic brushwork, rich colors, traditional art",
            'realistic': "realistic illustration style, detailed, lifelike, photographic quality"
        }
        
        return style_keywords.get(style.lower(), "illustration style")
    
    def extract_character_elements(self, character_desc: str) -> Dict[str, str]:
        """
        Extract key visual elements from character description
        
        Args:
            character_desc: Character description text
            
        Returns:
            Dictionary of extracted elements
        """
        elements = {
            'colors': [],
            'clothing': [],
            'accessories': [],
            'physical_features': [],
            'personality_traits': []
        }
        
        try:
            desc_lower = character_desc.lower()
            
            # Extract colors
            color_keywords = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'brown', 'black', 'white', 'gray', 'grey']
            for color in color_keywords:
                if color in desc_lower:
                    elements['colors'].append(color)
            
            # Extract clothing items
            clothing_keywords = ['scarf', 'hat', 'shirt', 'dress', 'collar', 'bow tie', 'jacket', 'sweater']
            for item in clothing_keywords:
                if item in desc_lower:
                    elements['clothing'].append(item)
            
            # Extract accessories
            accessory_keywords = ['glasses', 'jewelry', 'bag', 'backpack', 'crown', 'wings', 'horn']
            for item in accessory_keywords:
                if item in desc_lower:
                    elements['accessories'].append(item)
            
            # Extract physical features
            feature_keywords = ['eyes', 'tail', 'ears', 'mane', 'fur', 'wings', 'horns', 'smile', 'nose']
            for feature in feature_keywords:
                if feature in desc_lower:
                    elements['physical_features'].append(feature)
            
            # Extract personality traits
            personality_keywords = ['curious', 'shy', 'brave', 'kind', 'playful', 'wise', 'gentle', 'friendly']
            for trait in personality_keywords:
                if trait in desc_lower:
                    elements['personality_traits'].append(trait)
            
        except Exception as e:
            logger.error(f"Character element extraction failed: {e}")
        
        return elements
    
    def create_character_template(self, character: Dict) -> Dict:
        """
        Create a reusable character template
        
        Args:
            character: Character dictionary with name and description
            
        Returns:
            Character template for consistency
        """
        try:
            name = character.get('name', '')
            description = character.get('description', '')
            
            if not name or not description:
                return {}
            
            # Extract elements
            elements = self.extract_character_elements(description)
            
            # Create template
            template = {
                'name': name,
                'description': description,
                'elements': elements,
                'key_phrases': self._extract_key_phrases(description),
                'visual_consistency': self._create_visual_consistency_phrase(description)
            }
            
            # Store template
            self.character_templates[name] = template
            
            return template
            
        except Exception as e:
            logger.error(f"Character template creation failed: {e}")
            return {}
    
    def _extract_key_phrases(self, description: str) -> List[str]:
        """Extract key descriptive phrases from character description"""
        try:
            # Split into phrases and clean
            phrases = re.split(r'[,;.]', description)
            key_phrases = []
            
            for phrase in phrases:
                phrase = phrase.strip()
                if len(phrase) > 5 and len(phrase) < 50:  # Reasonable length
                    key_phrases.append(phrase)
            
            return key_phrases[:5]  # Limit to 5 key phrases
            
        except Exception as e:
            logger.error(f"Key phrase extraction failed: {e}")
            return []
    
    def _create_visual_consistency_phrase(self, description: str) -> str:
        """Create a phrase that ensures visual consistency"""
        try:
            # Extract the most important visual elements
            desc_lower = description.lower()
            
            # Find color + object combinations
            color_objects = []
            colors = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'brown', 'black', 'white']
            objects = ['scarf', 'hat', 'collar', 'bow tie', 'eyes', 'tail', 'mane', 'fur']
            
            for color in colors:
                for obj in objects:
                    if color in desc_lower and obj in desc_lower:
                        color_objects.append(f"{color} {obj}")
            
            if color_objects:
                return f"with {', '.join(color_objects[:2])}"  # Top 2 combinations
            else:
                # Fallback to first few words
                words = description.split()[:6]
                return ' '.join(words)
                
        except Exception as e:
            logger.error(f"Visual consistency phrase creation failed: {e}")
            return description[:50]  # Fallback to first 50 characters
    
    def get_character_consistency_prompt(self, character_name: str) -> str:
        """Get consistency prompt for a specific character"""
        if character_name in self.character_templates:
            template = self.character_templates[character_name]
            return template.get('visual_consistency', '')
        return ''
    
    def validate_character_consistency(self, story_data: Dict) -> List[str]:
        """
        Validate character consistency across story pages
        
        Args:
            story_data: Complete story data
            
        Returns:
            List of consistency issues found
        """
        issues = []
        
        try:
            characters = story_data.get('characters', [])
            pages = story_data.get('pages', [])
            
            if not characters or not pages:
                return issues
            
            # Check if character names appear consistently
            character_names = [char['name'] for char in characters]
            
            for page in pages:
                page_text = page.get('text', '').lower()
                image_prompt = page.get('image_prompt', '').lower()
                
                # Check if main characters are mentioned
                for char_name in character_names:
                    if char_name.lower() not in page_text and char_name.lower() not in image_prompt:
                        issues.append(f"Character '{char_name}' not mentioned in page {page['page']}")
            
            # Check image prompt consistency
            for page in pages:
                image_prompt = page.get('image_prompt', '')
                for char in characters:
                    char_name = char['name']
                    if char_name.lower() in image_prompt.lower():
                        # Check if character description is included
                        char_desc = char.get('description', '')
                        if char_desc and char_desc.lower() not in image_prompt.lower():
                            issues.append(f"Character '{char_name}' description missing from page {page['page']} image prompt")
            
        except Exception as e:
            logger.error(f"Character consistency validation failed: {e}")
            issues.append("Error validating character consistency")
        
        return issues
    
    def enhance_story_consistency(self, story_data: Dict) -> Dict:
        """
        Enhance story data for better character consistency
        
        Args:
            story_data: Original story data
            
        Returns:
            Enhanced story data with improved consistency
        """
        try:
            enhanced_story = story_data.copy()
            
            # Create character templates
            for character in enhanced_story.get('characters', []):
                self.create_character_template(character)
            
            # Enhance image prompts for consistency
            for page in enhanced_story.get('pages', []):
                original_prompt = page.get('image_prompt', '')
                enhanced_prompt = self.create_image_prompt(
                    original_prompt,
                    enhanced_story.get('characters', []),
                    'cartoon'  # Default style
                )
                page['image_prompt'] = enhanced_prompt
            
            return enhanced_story
            
        except Exception as e:
            logger.error(f"Story consistency enhancement failed: {e}")
            return story_data
