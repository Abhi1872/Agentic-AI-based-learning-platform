"""
Adaptive Learning Engine for Agentic AI Learning Platform
Analyzes student performance and adjusts difficulty dynamically
"""
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AdaptiveEngine:
    """
    Rule-based adaptive learning engine with ML-ready structure
    Adjusts difficulty based on student performance metrics
    """
    
    DIFFICULTY_LEVELS = ['easy', 'medium', 'advanced']
    
    
    THRESHOLDS = {
        'upgrade': {
            'min_score': 80,
            'min_quizzes': 2,
            'min_speed_percentile': 70,
        },
        'downgrade': {
            'max_score': 50,
            'min_quizzes': 2,
            'max_speed_percentile': 30,
        },
        'maintain': {
            'min_score': 50,
            'max_score': 80,
        }
    }
    
    def __init__(self):
        self.student_profiles = {}
    
    def analyze_performance(self, student_id, quiz_results):
        """
        Analyze student performance from quiz results
        
        Args:
            student_id: Student identifier
            quiz_results: List of QuizResult objects
        
        Returns:
            dict: Performance analysis with metrics
        """
        if not quiz_results:
            return {
                'average_score': 0,
                'total_quizzes': 0,
                'improvement_trend': 'neutral',
                'speed_rating': 'average',
                'accuracy_rating': 'needs_improvement',
                'recommended_difficulty': 'easy'
            }
        
        scores = [r.score for r in quiz_results]
        times = [r.time_spent for r in quiz_results if r.time_spent > 0]
        
        avg_score = sum(scores) / len(scores)
        
        if len(scores) >= 3:
            recent_avg = sum(scores[-3:]) / 3
            older_avg = sum(scores[:-3]) / max(len(scores) - 3, 1) if len(scores) > 3 else avg_score
            
            if recent_avg > older_avg + 5:
                improvement_trend = 'improving'
            elif recent_avg < older_avg - 5:
                improvement_trend = 'declining'
            else:
                improvement_trend = 'stable'
        else:
            improvement_trend = 'neutral'
        
        avg_time = sum(times) / len(times) if times else 0
        if avg_time < 60:
            speed_rating = 'fast'
        elif avg_time < 180:
            speed_rating = 'average'
        else:
            speed_rating = 'slow'
        
        if avg_score >= 80:
            accuracy_rating = 'excellent'
        elif avg_score >= 60:
            accuracy_rating = 'good'
        elif avg_score >= 40:
            accuracy_rating = 'needs_improvement'
        else:
            accuracy_rating = 'struggling'
        
        recommended = self._calculate_recommended_difficulty(
            avg_score, len(quiz_results), improvement_trend
        )
        
        return {
            'average_score': round(avg_score, 1),
            'total_quizzes': len(quiz_results),
            'improvement_trend': improvement_trend,
            'speed_rating': speed_rating,
            'accuracy_rating': accuracy_rating,
            'recommended_difficulty': recommended
        }
    
    def _calculate_recommended_difficulty(self, avg_score, num_quizzes, trend):
        """Calculate recommended difficulty level"""
        if num_quizzes < 2:
            return 'easy'
        
        if avg_score >= 85 and trend in ['improving', 'stable']:
            return 'advanced'
        elif avg_score >= 65:
            return 'medium'
        else:
            return 'easy'
    
    def should_adjust_difficulty(self, student, recent_results):
        """
        Determine if difficulty should be adjusted
        
        Args:
            student: Student object
            recent_results: Recent quiz results
        
        Returns:
            tuple: (should_adjust, new_difficulty, reason)
        """
        if len(recent_results) < 2:
            return (False, student.current_difficulty, "Not enough data")
        
        recent_scores = [r.score for r in recent_results[-3:]]
        avg_recent = sum(recent_scores) / len(recent_scores)
        
        current_idx = self.DIFFICULTY_LEVELS.index(student.current_difficulty)
        
        if avg_recent >= self.THRESHOLDS['upgrade']['min_score']:
            if current_idx < len(self.DIFFICULTY_LEVELS) - 1:
                new_difficulty = self.DIFFICULTY_LEVELS[current_idx + 1]
                return (True, new_difficulty, f"Excellent performance (avg: {avg_recent:.0f}%)")
        
        elif avg_recent <= self.THRESHOLDS['downgrade']['max_score']:
            if current_idx > 0:
                new_difficulty = self.DIFFICULTY_LEVELS[current_idx - 1]
                return (True, new_difficulty, f"Need more practice (avg: {avg_recent:.0f}%)")
        
        return (False, student.current_difficulty, "Performance is appropriate for current level")
    
    def get_personalized_recommendations(self, student, performance):
        """
        Generate personalized learning recommendations
        
        Args:
            student: Student object
            performance: Performance analysis dict
        
        Returns:
            list: List of recommendation dictionaries
        """
        recommendations = []
        
        if performance['improvement_trend'] == 'declining':
            recommendations.append({
                'type': 'encouragement',
                'icon': 'heart',
                'title': 'Take Your Time',
                'message': "It's okay to slow down. Consider reviewing previous lessons before moving forward."
            })
        
        if performance['accuracy_rating'] == 'struggling':
            recommendations.append({
                'type': 'study_tip',
                'icon': 'book',
                'title': 'Review Materials',
                'message': 'Try re-reading the lesson content with audio enabled for better understanding.'
            })
        
        if performance['speed_rating'] == 'slow':
            recommendations.append({
                'type': 'accessibility',
                'icon': 'accessibility',
                'title': 'Accessibility Options',
                'message': 'Consider enabling text-to-speech or using simpler text mode for easier reading.'
            })
        
        if performance['improvement_trend'] == 'improving':
            recommendations.append({
                'type': 'achievement',
                'icon': 'star',
                'title': 'Great Progress!',
                'message': "You're improving steadily. Keep up the excellent work!"
            })
        
        if performance['average_score'] >= 80:
            recommendations.append({
                'type': 'challenge',
                'icon': 'trending-up',
                'title': 'Ready for a Challenge?',
                'message': 'Consider trying lessons at a higher difficulty level.'
            })
        
        if not recommendations:
            recommendations.append({
                'type': 'general',
                'icon': 'thumbs-up',
                'title': 'Keep Going!',
                'message': "You're doing well. Continue at your own pace."
            })
        
        return recommendations
    
    def calculate_engagement_score(self, student, activity_logs):
        """
        Calculate student engagement score
        
        Args:
            student: Student object
            activity_logs: List of ActivityLog objects
        
        Returns:
            dict: Engagement metrics
        """
        if not activity_logs:
            return {
                'score': 0,
                'level': 'new',
                'sessions_this_week': 0,
                'avg_session_length': 0
            }
        
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_logs = [log for log in activity_logs if log.created_at >= week_ago]
        
        unique_days = len(set(log.created_at.date() for log in recent_logs))
        
        if unique_days >= 5:
            engagement_score = 100
            level = 'highly_engaged'
        elif unique_days >= 3:
            engagement_score = 75
            level = 'engaged'
        elif unique_days >= 1:
            engagement_score = 50
            level = 'moderate'
        else:
            engagement_score = 25
            level = 'low'
        
        return {
            'score': engagement_score,
            'level': level,
            'sessions_this_week': unique_days,
            'streak': student.streak_days
        }


adaptive_engine = AdaptiveEngine()
