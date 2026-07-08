"""
Content Personalization Module for Agentic AI Learning Platform
Simplifies and adapts content based on student preferences and abilities
"""
import re
import logging

logger = logging.getLogger(__name__)


class ContentPersonalizer:
    """
    Content personalization engine for adapting learning materials
    """
    
    READING_LEVELS = {
        'easy': {
            'max_sentence_length': 15,
            'max_word_length': 8,
            'vocabulary_level': 'basic',
            'use_bullet_points': True,
        },
        'medium': {
            'max_sentence_length': 25,
            'max_word_length': 12,
            'vocabulary_level': 'intermediate',
            'use_bullet_points': True,
        },
        'advanced': {
            'max_sentence_length': 40,
            'max_word_length': 20,
            'vocabulary_level': 'advanced',
            'use_bullet_points': False,
        }
    }
    
    SIMPLE_WORDS = {
        'utilize': 'use',
        'implement': 'do',
        'facilitate': 'help',
        'approximately': 'about',
        'subsequently': 'then',
        'nevertheless': 'but',
        'furthermore': 'also',
        'consequently': 'so',
        'demonstrate': 'show',
        'comprehend': 'understand',
        'acquire': 'get',
        'sufficient': 'enough',
        'commence': 'start',
        'terminate': 'end',
        'endeavor': 'try',
        'ascertain': 'find out',
        'accomplish': 'do',
        'investigate': 'look into',
        'determine': 'find',
        'establish': 'set up',
    }
    
    def __init__(self):
        pass
    
    def get_content_for_level(self, lesson, difficulty):
        """
        Get appropriate content based on difficulty level
        
        Args:
            lesson: Lesson object
            difficulty: 'easy', 'medium', or 'advanced'
        
        Returns:
            str: Content appropriate for the difficulty level
        """
        if difficulty == 'easy':
            return lesson.content_easy
        elif difficulty == 'medium':
            return lesson.content_medium
        else:
            return lesson.content_advanced
    
    def simplify_text(self, text, level='easy'):
        """
        Simplify text for easier reading
        
        Args:
            text: Original text content
            level: Reading level to target
        
        Returns:
            str: Simplified text
        """
        if not text:
            return text
        
        simplified = text
        for complex_word, simple_word in self.SIMPLE_WORDS.items():
            pattern = re.compile(re.escape(complex_word), re.IGNORECASE)
            simplified = pattern.sub(simple_word, simplified)
        
        if level == 'easy':
            simplified = self._break_long_sentences(simplified)
        
        return simplified
    
    def _break_long_sentences(self, text, max_words=15):
        """Break long sentences into shorter ones"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        result = []
        
        for sentence in sentences:
            words = sentence.split()
            if len(words) <= max_words:
                result.append(sentence)
            else:
                parts = []
                current_part = []
                
                for word in words:
                    current_part.append(word)
                    if len(current_part) >= max_words // 2:
                        if word.endswith(',') or word in ['and', 'but', 'or', 'so', 'then']:
                            parts.append(' '.join(current_part))
                            current_part = []
                
                if current_part:
                    parts.append(' '.join(current_part))
                
                if parts:
                    result.extend([p.strip() + '.' if not p.endswith('.') else p for p in parts])
                else:
                    result.append(sentence)
        
        return ' '.join(result)
    
    def format_for_display(self, content, preferences):
        """
        Format content based on student preferences
        
        Args:
            content: Text content
            preferences: Dict with display preferences
        
        Returns:
            dict: Formatted content with metadata
        """
        formatted = {
            'text': content,
            'paragraphs': [],
            'key_points': [],
            'summary': '',
        }
        
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        formatted['paragraphs'] = paragraphs
        
        formatted['key_points'] = self._extract_key_points(content)
        
        formatted['summary'] = self._generate_summary(content)
        
        return formatted
    
    def _extract_key_points(self, content):
        """Extract key points from content"""
        key_points = []
        
        sentences = re.split(r'(?<=[.!?])\s+', content)
        
        important_markers = ['important', 'key', 'remember', 'note', 'main', 'essential']
        
        for sentence in sentences[:10]:
            sentence_lower = sentence.lower()
            if any(marker in sentence_lower for marker in important_markers):
                key_points.append(sentence.strip())
        
        if not key_points and sentences:
            key_points = [s.strip() for s in sentences[:3]]
        
        return key_points
    
    def _generate_summary(self, content, max_sentences=3):
        """Generate a brief summary of the content"""
        sentences = re.split(r'(?<=[.!?])\s+', content)
        
        if len(sentences) <= max_sentences:
            return content
        
        summary_sentences = sentences[:max_sentences]
        return ' '.join(summary_sentences)
    
    def convert_to_bullet_points(self, content):
        """
        Convert paragraph content to bullet points for easier reading
        
        Args:
            content: Text content
        
        Returns:
            list: List of bullet points
        """
        sentences = re.split(r'(?<=[.!?])\s+', content)
        
        bullet_points = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 10:
                sentence = sentence[0].upper() + sentence[1:] if sentence else sentence
                if not sentence.endswith('.'):
                    sentence += '.'
                bullet_points.append(sentence)
        
        return bullet_points
    
    def get_content_formats(self, content, lesson_id):
        """
        Get content in multiple formats
        
        Args:
            content: Original content
            lesson_id: ID of the lesson
        
        Returns:
            dict: Content in various formats
        """
        return {
            'text': content,
            'simplified': self.simplify_text(content, 'easy'),
            'bullet_points': self.convert_to_bullet_points(content),
            'key_points': self._extract_key_points(content),
            'summary': self._generate_summary(content),
            'audio_available': True,
            'sign_language_available': False,
        }
    
    def adjust_font_size(self, base_size, preference):
        """
        Calculate adjusted font size
        
        Args:
            base_size: Base font size in pixels
            preference: 'small', 'medium', 'large', 'extra-large'
        
        Returns:
            int: Adjusted font size
        """
        multipliers = {
            'small': 0.9,
            'medium': 1.0,
            'large': 1.25,
            'extra-large': 1.5,
        }
        
        multiplier = multipliers.get(preference, 1.0)
        return int(base_size * multiplier)


content_personalizer = ContentPersonalizer()
