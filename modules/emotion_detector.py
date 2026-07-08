"""
Emotion Detection Module for Agentic AI Learning Platform
Detects student emotions via webcam for adaptive learning
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class EmotionDetector:
    """
    Emotion detection using browser-based webcam access
    Provides interface for frontend emotion recognition
    """
    
    EMOTIONS = {
        'happy': {
            'description': 'Student appears happy and engaged',
            'learning_impact': 'positive',
            'action': 'continue',
            'icon': 'smile'
        },
        'confused': {
            'description': 'Student appears confused',
            'learning_impact': 'negative',
            'action': 'simplify_content',
            'icon': 'help-circle'
        },
        'frustrated': {
            'description': 'Student appears frustrated',
            'learning_impact': 'negative',
            'action': 'offer_break',
            'icon': 'frown'
        },
        'focused': {
            'description': 'Student is focused and concentrating',
            'learning_impact': 'positive',
            'action': 'continue',
            'icon': 'eye'
        },
        'bored': {
            'description': 'Student appears bored or disengaged',
            'learning_impact': 'neutral',
            'action': 'increase_engagement',
            'icon': 'meh'
        },
        'tired': {
            'description': 'Student appears tired',
            'learning_impact': 'negative',
            'action': 'suggest_break',
            'icon': 'moon'
        },
        'neutral': {
            'description': 'Student expression is neutral',
            'learning_impact': 'neutral',
            'action': 'continue',
            'icon': 'minus'
        }
    }
    
    def __init__(self):
        self.is_initialized = True
        self.detection_enabled = False
        self.current_emotion = 'neutral'
        self.emotion_history = []
    
    def is_available(self):
        """Check if emotion detection is available"""
        return self.is_initialized
    
    def get_emotion_info(self, emotion_name):
        """
        Get information about an emotion
        
        Args:
            emotion_name: Name of the emotion
        
        Returns:
            dict: Emotion information
        """
        return self.EMOTIONS.get(emotion_name, self.EMOTIONS['neutral'])
    
    def get_all_emotions(self):
        """Get list of all detectable emotions"""
        return list(self.EMOTIONS.keys())
    
    def process_emotion(self, emotion, confidence, student_id):
        """
        Process a detected emotion from the frontend
        
        Args:
            emotion: Detected emotion name
            confidence: Detection confidence (0-1)
            student_id: ID of the student
        
        Returns:
            dict: Processing result with recommended action
        """
        emotion_info = self.get_emotion_info(emotion)
        
        record = {
            'emotion': emotion,
            'confidence': confidence,
            'student_id': student_id,
            'timestamp': datetime.utcnow().isoformat(),
            'action': emotion_info['action']
        }
        
        self.emotion_history.append(record)
        
        if len(self.emotion_history) > 100:
            self.emotion_history = self.emotion_history[-100:]
        
        return {
            'emotion': emotion,
            'confidence': confidence,
            'info': emotion_info,
            'recommended_action': emotion_info['action'],
            'message': self._get_response_message(emotion, emotion_info['action'])
        }
    
    def _get_response_message(self, emotion, action):
        """Generate appropriate response message based on emotion and action"""
        messages = {
            'continue': "Keep going, you're doing great!",
            'simplify_content': "Let me make this easier to understand.",
            'offer_break': "Would you like to take a short break?",
            'increase_engagement': "Let's try something more interactive!",
            'suggest_break': "You might benefit from a short rest.",
        }
        return messages.get(action, "Keep up the good work!")
    
    def get_engagement_level(self, recent_emotions):
        """
        Calculate engagement level from recent emotions
        
        Args:
            recent_emotions: List of recent emotion records
        
        Returns:
            dict: Engagement level and score
        """
        if not recent_emotions:
            return {'level': 'unknown', 'score': 50}
        
        positive_emotions = ['happy', 'focused']
        negative_emotions = ['confused', 'frustrated', 'bored', 'tired']
        
        positive_count = sum(1 for e in recent_emotions if e['emotion'] in positive_emotions)
        negative_count = sum(1 for e in recent_emotions if e['emotion'] in negative_emotions)
        total = len(recent_emotions)
        
        if total == 0:
            return {'level': 'unknown', 'score': 50}
        
        score = ((positive_count - negative_count) / total + 1) * 50
        score = max(0, min(100, score))
        
        if score >= 70:
            level = 'high'
        elif score >= 40:
            level = 'medium'
        else:
            level = 'low'
        
        return {'level': level, 'score': round(score)}
    
    def get_adaptive_recommendations(self, engagement_level):
        """
        Get recommendations based on engagement level
        
        Args:
            engagement_level: Engagement level dict
        
        Returns:
            list: List of recommendations
        """
        recommendations = []
        
        if engagement_level['level'] == 'low':
            recommendations.extend([
                {'type': 'break', 'message': 'Consider taking a 5-minute break'},
                {'type': 'simplify', 'message': 'Try switching to simpler content'},
                {'type': 'audio', 'message': 'Enable audio mode for a change of pace'},
            ])
        elif engagement_level['level'] == 'medium':
            recommendations.extend([
                {'type': 'interactive', 'message': 'Try the quiz to test your knowledge'},
                {'type': 'review', 'message': 'Review the key points section'},
            ])
        else:
            recommendations.extend([
                {'type': 'challenge', 'message': 'Ready for more challenging content!'},
                {'type': 'continue', 'message': 'Great focus! Keep going!'},
            ])
        
        return recommendations


emotion_detector = EmotionDetector()
