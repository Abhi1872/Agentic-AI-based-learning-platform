"""
Accessibility Agent
Tracks user behavior and automatically enables accessibility features.
Supports special education needs for differently-abled students.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class AccessibilityAgent:
    """Agent that manages and auto-enables accessibility features."""
    
    SLOW_READING_THRESHOLD = 100
    SLOW_SCROLL_THRESHOLD = 5
    STRUGGLE_THRESHOLD = 3
    
    def __init__(self):
        self.event_buffer = {}
    
    def update_accessibility_preferences(self, student_id: int, events: List[Dict], db_session) -> Dict[str, Any]:
        """
        Track user behavior events and update accessibility preferences.
        
        Events tracked:
        - reading_time: Time spent reading content
        - zoom_level: Current zoom level
        - scroll_speed: Scroll speed (slow indicates reading difficulty)
        - struggle_events: Clicks on help, repeated sections, etc.
        
        Returns recommendations for accessibility settings.
        """
        from models import Student, UserPreferences
        
        student = Student.query.get(student_id)
        if not student:
            return {'success': False, 'message': 'Student not found'}
        
        prefs = UserPreferences.query.filter_by(student_id=student_id).first()
        if not prefs:
            prefs = UserPreferences(student_id=student_id)
            db_session.add(prefs)
        
        analysis = self._analyze_events(events)
        recommendations = []
        changes_made = []
        
        if analysis.get('slow_reading', False) and not prefs.audio_mode:
            prefs.audio_mode = True
            recommendations.append('Audio mode enabled - content will be read aloud')
            changes_made.append('audio_mode')
            logger.info(f"Auto-enabled audio mode for student {student_id}")
        
        if analysis.get('high_zoom', False) and not prefs.large_text:
            prefs.large_text = True
            recommendations.append('Large text mode enabled for better readability')
            changes_made.append('large_text')
            logger.info(f"Auto-enabled large text for student {student_id}")
        
        if analysis.get('struggle_detected', False) and not prefs.reduced_motion:
            prefs.reduced_motion = True
            recommendations.append('Reduced motion enabled to minimize distractions')
            changes_made.append('reduced_motion')
            logger.info(f"Auto-enabled reduced motion for student {student_id}")
        
        prefs.reading_speed_avg = analysis.get('avg_reading_speed', prefs.reading_speed_avg or 0)
        prefs.zoom_preference = analysis.get('avg_zoom', prefs.zoom_preference or 100)
        prefs.scroll_speed_avg = analysis.get('avg_scroll_speed', prefs.scroll_speed_avg or 0)
        prefs.struggle_count = (prefs.struggle_count or 0) + analysis.get('struggle_count', 0)
        prefs.updated_at = datetime.utcnow()
        
        try:
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            logger.error(f"Error saving preferences: {e}")
            return {'success': False, 'message': 'Error saving preferences'}
        
        return {
            'success': True,
            'changes_made': changes_made,
            'recommendations': recommendations,
            'current_settings': self.get_current_settings(student_id, db_session)
        }
    
    def _analyze_events(self, events: List[Dict]) -> Dict[str, Any]:
        """Analyze behavior events to detect accessibility needs."""
        analysis = {
            'slow_reading': False,
            'high_zoom': False,
            'struggle_detected': False,
            'avg_reading_speed': 0,
            'avg_zoom': 100,
            'avg_scroll_speed': 0,
            'struggle_count': 0
        }
        
        if not events:
            return analysis
        
        reading_times = []
        zoom_levels = []
        scroll_speeds = []
        struggle_events = 0
        
        for event in events:
            event_type = event.get('type', '')
            
            if event_type == 'reading_time':
                reading_times.append(event.get('value', 0))
            elif event_type == 'zoom_level':
                zoom_levels.append(event.get('value', 100))
            elif event_type == 'scroll_speed':
                scroll_speeds.append(event.get('value', 0))
            elif event_type in ['help_click', 'repeat_section', 'back_navigation']:
                struggle_events += 1
        
        if reading_times:
            avg_reading = sum(reading_times) / len(reading_times)
            analysis['avg_reading_speed'] = avg_reading
            if avg_reading < self.SLOW_READING_THRESHOLD:
                analysis['slow_reading'] = True
        
        if zoom_levels:
            avg_zoom = sum(zoom_levels) / len(zoom_levels)
            analysis['avg_zoom'] = avg_zoom
            if avg_zoom > 125:
                analysis['high_zoom'] = True
        
        if scroll_speeds:
            avg_scroll = sum(scroll_speeds) / len(scroll_speeds)
            analysis['avg_scroll_speed'] = avg_scroll
            if avg_scroll < self.SLOW_SCROLL_THRESHOLD:
                analysis['slow_reading'] = True
        
        analysis['struggle_count'] = struggle_events
        if struggle_events >= self.STRUGGLE_THRESHOLD:
            analysis['struggle_detected'] = True
        
        return analysis
    
    def get_current_settings(self, student_id: int, db_session) -> Dict[str, Any]:
        """Get current accessibility settings for a student."""
        from models import Student, UserPreferences
        
        student = Student.query.get(student_id)
        prefs = UserPreferences.query.filter_by(student_id=student_id).first()
        
        settings = {
            'audio_mode': False,
            'large_text': False,
            'reduced_motion': False,
            'sign_language': False,
            'high_contrast': False,
            'font_size': 18
        }
        
        if student:
            settings['high_contrast'] = student.high_contrast
            settings['font_size'] = student.font_size
            settings['audio_mode'] = student.audio_enabled
            settings['sign_language'] = student.sign_language_enabled
            settings['reduced_motion'] = student.reduce_motion
        
        if prefs:
            settings['audio_mode'] = settings['audio_mode'] or prefs.audio_mode
            settings['large_text'] = prefs.large_text
            settings['reduced_motion'] = settings['reduced_motion'] or prefs.reduced_motion
            settings['sign_language'] = prefs.sign_language
        
        return settings
    
    def update_manual_settings(self, student_id: int, settings: Dict[str, Any], db_session) -> Dict[str, Any]:
        """Update accessibility settings manually."""
        from models import Student, UserPreferences
        
        student = Student.query.get(student_id)
        if not student:
            return {'success': False, 'message': 'Student not found'}
        
        prefs = UserPreferences.query.filter_by(student_id=student_id).first()
        if not prefs:
            prefs = UserPreferences(student_id=student_id)
            db_session.add(prefs)
        
        if 'audio_mode' in settings:
            prefs.audio_mode = settings['audio_mode']
            student.audio_enabled = settings['audio_mode']
        if 'large_text' in settings:
            prefs.large_text = settings['large_text']
        if 'reduced_motion' in settings:
            prefs.reduced_motion = settings['reduced_motion']
            student.reduce_motion = settings['reduced_motion']
        if 'sign_language' in settings:
            prefs.sign_language = settings['sign_language']
            student.sign_language_enabled = settings['sign_language']
        if 'high_contrast' in settings:
            student.high_contrast = settings['high_contrast']
        if 'font_size' in settings:
            student.font_size = settings['font_size']
        
        prefs.updated_at = datetime.utcnow()
        
        try:
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            logger.error(f"Error updating settings: {e}")
            return {'success': False, 'message': 'Error saving settings'}
        
        return {
            'success': True,
            'message': 'Settings updated successfully',
            'current_settings': self.get_current_settings(student_id, db_session)
        }
    
    def get_recommended_settings(self, student_id: int, db_session) -> Dict[str, Any]:
        """Get AI-recommended accessibility settings based on behavior history."""
        from models import UserPreferences, Student
        
        prefs = UserPreferences.query.filter_by(student_id=student_id).first()
        student = Student.query.get(student_id)
        
        recommendations = []
        
        if prefs:
            if prefs.reading_speed_avg and prefs.reading_speed_avg < self.SLOW_READING_THRESHOLD:
                recommendations.append({
                    'setting': 'audio_mode',
                    'reason': 'Your reading speed suggests audio support could help'
                })
            
            if prefs.zoom_preference and prefs.zoom_preference > 125:
                recommendations.append({
                    'setting': 'large_text',
                    'reason': 'You often use higher zoom levels'
                })
            
            if prefs.struggle_count and prefs.struggle_count >= self.STRUGGLE_THRESHOLD:
                recommendations.append({
                    'setting': 'reduced_motion',
                    'reason': 'Reducing animations may help you focus better'
                })
        
        if student and student.special_needs_type:
            if 'dyslexia' in student.special_needs_type.lower():
                recommendations.append({
                    'setting': 'large_text',
                    'reason': 'Larger text can help with dyslexia'
                })
            if 'adhd' in student.special_needs_type.lower():
                recommendations.append({
                    'setting': 'reduced_motion',
                    'reason': 'Fewer animations help with ADHD focus'
                })
        
        return {
            'recommendations': recommendations,
            'current_settings': self.get_current_settings(student_id, db_session)
        }


accessibility_agent = AccessibilityAgent()
