"""
Text-to-Speech Engine for Agentic AI Learning Platform
Provides audio playback of lessons for visually impaired students
"""
import os
import logging
from gtts import gTTS
import hashlib

logger = logging.getLogger(__name__)

AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'audio')


def ensure_audio_dir():
    """Ensure the audio directory exists"""
    if not os.path.exists(AUDIO_DIR):
        os.makedirs(AUDIO_DIR)


def get_audio_filename(text, lang='en'):
    """Generate a unique filename based on text content"""
    text_hash = hashlib.md5(text.encode()).hexdigest()[:12]
    return f"tts_{text_hash}_{lang}.mp3"


def text_to_speech(text, lang='en', slow=False):
    """
    Convert text to speech and save as audio file
    
    Args:
        text: The text to convert to speech
        lang: Language code (default: 'en')
        slow: Whether to speak slowly (default: False)
    
    Returns:
        str: Relative path to the audio file, or None on error
    """
    if not text or not text.strip():
        return None
    
    try:
        ensure_audio_dir()
        
        filename = get_audio_filename(text, lang)
        filepath = os.path.join(AUDIO_DIR, filename)
        
        if os.path.exists(filepath):
            logger.debug(f"Audio file already exists: {filename}")
            return f"/static/audio/{filename}"
        
        tts = gTTS(text=text, lang=lang, slow=slow)
        tts.save(filepath)
        
        logger.info(f"Generated audio file: {filename}")
        return f"/static/audio/{filename}"
        
    except Exception as e:
        logger.error(f"Error generating TTS: {str(e)}")
        return None


def generate_lesson_audio(lesson_content, lesson_id, difficulty):
    """
    Generate audio for an entire lesson
    
    Args:
        lesson_content: The lesson text content
        lesson_id: ID of the lesson
        difficulty: Difficulty level
    
    Returns:
        str: Path to audio file or None
    """
    cache_key = f"lesson_{lesson_id}_{difficulty}"
    filename = f"{cache_key}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)
    
    if os.path.exists(filepath):
        return f"/static/audio/{filename}"
    
    return text_to_speech(lesson_content, slow=True)


def split_text_for_tts(text, max_chars=500):
    """
    Split long text into chunks for TTS processing
    
    Args:
        text: The text to split
        max_chars: Maximum characters per chunk
    
    Returns:
        list: List of text chunks
    """
    if len(text) <= max_chars:
        return [text]
    
    chunks = []
    sentences = text.replace('!', '.').replace('?', '.').split('.')
    current_chunk = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        if len(current_chunk) + len(sentence) + 1 <= max_chars:
            current_chunk += sentence + ". "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def get_supported_languages():
    """Return list of supported TTS languages"""
    return [
        {'code': 'en', 'name': 'English'},
        {'code': 'es', 'name': 'Spanish'},
        {'code': 'fr', 'name': 'French'},
        {'code': 'de', 'name': 'German'},
        {'code': 'hi', 'name': 'Hindi'},
        {'code': 'zh-CN', 'name': 'Chinese (Simplified)'},
    ]


def generate_audio(text, lang='en', slow=False):
    """
    Generate audio from text and return the file path.
    This is a convenience wrapper around text_to_speech.
    
    Args:
        text: The text to convert to speech
        lang: Language code (default: 'en')
        slow: Whether to speak slowly (default: False)
    
    Returns:
        str: Path to the audio file, or None on error
    """
    return text_to_speech(text, lang=lang, slow=slow)
