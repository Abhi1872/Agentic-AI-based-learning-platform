"""
Speech-to-Text Engine for Agentic AI Learning Platform
Provides voice input for students with limited mobility
"""
import logging

logger = logging.getLogger(__name__)


class STTEngine:
    """Speech-to-Text engine wrapper"""
    
    def __init__(self):
        self.recognizer = None
        self._init_recognizer()
    
    def _init_recognizer(self):
        """Initialize the speech recognizer"""
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            logger.info("Speech recognizer initialized successfully")
        except ImportError:
            logger.warning("SpeechRecognition library not available")
            self.recognizer = None
    
    def is_available(self):
        """Check if STT is available"""
        return self.recognizer is not None
    
    def transcribe_audio_file(self, audio_path, language='en-US'):
        """
        Transcribe audio from a file
        
        Args:
            audio_path: Path to audio file
            language: Language code for recognition
        
        Returns:
            dict: Contains 'success', 'text', and 'error' keys
        """
        if not self.is_available():
            return {
                'success': False,
                'text': '',
                'error': 'Speech recognition not available'
            }
        
        try:
            import speech_recognition as sr
            
            with sr.AudioFile(audio_path) as source:
                audio = self.recognizer.record(source)
            
            text = self.recognizer.recognize_google(audio, language=language)
            
            return {
                'success': True,
                'text': text,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"STT error: {str(e)}")
            return {
                'success': False,
                'text': '',
                'error': str(e)
            }


def get_voice_commands():
    """
    Return list of supported voice commands
    
    Returns:
        list: List of command dictionaries with 'command' and 'action' keys
    """
    return [
        {'command': 'next', 'action': 'navigate_next', 'description': 'Go to next page or question'},
        {'command': 'previous', 'action': 'navigate_prev', 'description': 'Go to previous page or question'},
        {'command': 'read', 'action': 'read_aloud', 'description': 'Read current content aloud'},
        {'command': 'repeat', 'action': 'repeat_audio', 'description': 'Repeat the last audio'},
        {'command': 'pause', 'action': 'pause_audio', 'description': 'Pause audio playback'},
        {'command': 'play', 'action': 'play_audio', 'description': 'Resume audio playback'},
        {'command': 'home', 'action': 'go_home', 'description': 'Return to dashboard'},
        {'command': 'quiz', 'action': 'start_quiz', 'description': 'Start the quiz'},
        {'command': 'submit', 'action': 'submit_answer', 'description': 'Submit current answer'},
        {'command': 'option a', 'action': 'select_a', 'description': 'Select option A'},
        {'command': 'option b', 'action': 'select_b', 'description': 'Select option B'},
        {'command': 'option c', 'action': 'select_c', 'description': 'Select option C'},
        {'command': 'option d', 'action': 'select_d', 'description': 'Select option D'},
        {'command': 'help', 'action': 'show_help', 'description': 'Show available commands'},
    ]


def parse_voice_command(text):
    """
    Parse voice input and match to a command
    
    Args:
        text: Transcribed voice text
    
    Returns:
        dict or None: Matched command or None if no match
    """
    if not text:
        return None
    
    text_lower = text.lower().strip()
    commands = get_voice_commands()
    
    for cmd in commands:
        if cmd['command'] in text_lower:
            return cmd
    
    return None


stt_engine = STTEngine()


def convert_speech_to_text(audio_file, language='en-US'):
    """
    Convert speech audio file to text.
    
    Args:
        audio_file: Path to audio file or file-like object
        language: Language code for recognition (default: 'en-US')
    
    Returns:
        dict: Contains 'success', 'text', and 'error' keys
    """
    import tempfile
    import os
    
    try:
        if hasattr(audio_file, 'read'):
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp.write(audio_file.read())
                tmp_path = tmp.name
            
            result = stt_engine.transcribe_audio_file(tmp_path, language)
            
            try:
                os.unlink(tmp_path)
            except:
                pass
            
            return result
        else:
            return stt_engine.transcribe_audio_file(audio_file, language)
            
    except Exception as e:
        logger.error(f"Speech to text conversion error: {e}")
        return {
            'success': False,
            'text': '',
            'error': str(e)
        }
