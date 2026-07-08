"""
Helper utilities for Agentic AI Learning Platform
"""
import os
import re
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def format_time_spent(seconds):
    """
    Format seconds into human-readable time
    
    Args:
        seconds: Number of seconds
    
    Returns:
        str: Formatted time string
    """
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def format_date_relative(dt):
    """
    Format datetime as relative time
    
    Args:
        dt: datetime object
    
    Returns:
        str: Relative time string (e.g., "2 days ago")
    """
    if not dt:
        return "Never"
    
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days == 0:
        if diff.seconds < 60:
            return "Just now"
        elif diff.seconds < 3600:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.days == 1:
        return "Yesterday"
    elif diff.days < 7:
        return f"{diff.days} days ago"
    elif diff.days < 30:
        weeks = diff.days // 7
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    else:
        return dt.strftime('%B %d, %Y')


def get_difficulty_color(difficulty):
    """
    Get color class for difficulty level
    
    Args:
        difficulty: 'easy', 'medium', or 'advanced'
    
    Returns:
        str: CSS color class
    """
    colors = {
        'easy': 'success',
        'medium': 'warning',
        'advanced': 'danger'
    }
    return colors.get(difficulty, 'secondary')


def get_difficulty_label(difficulty):
    """
    Get display label for difficulty
    
    Args:
        difficulty: difficulty level string
    
    Returns:
        str: Formatted display label
    """
    labels = {
        'easy': 'Easy',
        'medium': 'Medium',
        'advanced': 'Advanced'
    }
    return labels.get(difficulty, difficulty.capitalize())


def calculate_grade(score):
    """
    Calculate letter grade from score
    
    Args:
        score: Numeric score (0-100)
    
    Returns:
        str: Letter grade
    """
    if score >= 90:
        return 'A'
    elif score >= 80:
        return 'B'
    elif score >= 70:
        return 'C'
    elif score >= 60:
        return 'D'
    else:
        return 'F'


def get_score_message(score):
    """
    Get encouraging message based on score
    
    Args:
        score: Numeric score (0-100)
    
    Returns:
        str: Encouraging message
    """
    if score >= 90:
        return "Excellent work! You've mastered this material!"
    elif score >= 80:
        return "Great job! You have a strong understanding!"
    elif score >= 70:
        return "Good effort! Keep practicing to improve!"
    elif score >= 60:
        return "You're making progress! Review the material and try again."
    else:
        return "Don't give up! Review the lesson and practice more."


def sanitize_input(text):
    """
    Sanitize user input for safety
    
    Args:
        text: Input text
    
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
    
    text = re.sub(r'<[^>]+>', '', text)
    
    text = text.strip()
    
    return text


def generate_student_id():
    """
    Generate a unique student ID
    
    Returns:
        str: Unique student ID
    """
    import random
    import string
    
    prefix = "STU"
    random_part = ''.join(random.choices(string.digits, k=6))
    
    return f"{prefix}{random_part}"


def get_greeting(name=None):
    """
    Get time-appropriate greeting
    
    Args:
        name: Optional name to include
    
    Returns:
        str: Greeting message
    """
    hour = datetime.now().hour
    
    if hour < 12:
        greeting = "Good morning"
    elif hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    
    if name:
        return f"{greeting}, {name}!"
    return f"{greeting}!"


def get_progress_bar_class(percentage):
    """
    Get Bootstrap class for progress bar
    
    Args:
        percentage: Progress percentage (0-100)
    
    Returns:
        str: Bootstrap color class
    """
    if percentage >= 80:
        return 'bg-success'
    elif percentage >= 50:
        return 'bg-info'
    elif percentage >= 25:
        return 'bg-warning'
    else:
        return 'bg-danger'


def truncate_text(text, max_length=100, suffix='...'):
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        str: Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def parse_duration(minutes):
    """
    Parse duration in minutes to readable format
    
    Args:
        minutes: Duration in minutes
    
    Returns:
        str: Formatted duration
    """
    if minutes < 60:
        return f"{minutes} min"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    if remaining_minutes == 0:
        return f"{hours} hr"
    
    return f"{hours} hr {remaining_minutes} min"


def get_accessibility_options():
    """
    Get available accessibility options
    
    Returns:
        list: List of accessibility option dictionaries
    """
    return [
        {
            'id': 'audio_mode',
            'name': 'Audio Mode',
            'description': 'Enable text-to-speech for all content',
            'icon': 'volume-2'
        },
        {
            'id': 'sign_language',
            'name': 'Sign Language',
            'description': 'Show sign language interpretation',
            'icon': 'hand'
        },
        {
            'id': 'high_contrast',
            'name': 'High Contrast',
            'description': 'Increase color contrast for better visibility',
            'icon': 'sun'
        },
        {
            'id': 'large_text',
            'name': 'Large Text',
            'description': 'Increase text size throughout the app',
            'icon': 'type'
        },
        {
            'id': 'reduce_motion',
            'name': 'Reduce Motion',
            'description': 'Minimize animations and transitions',
            'icon': 'pause'
        },
        {
            'id': 'emotion_detection',
            'name': 'Emotion Detection',
            'description': 'Use webcam to adapt to your emotional state',
            'icon': 'smile'
        }
    ]
