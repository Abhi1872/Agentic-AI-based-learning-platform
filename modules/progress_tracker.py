"""
Progress Tracking Module for Agentic AI Learning Platform
Records and analyzes student learning progress
"""
import logging
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class ProgressTracker:
    """
    Tracks and analyzes student learning progress
    """
    
    def __init__(self):
        pass
    
    def calculate_lesson_progress(self, student, lessons, lesson_progress_list):
        """
        Calculate overall lesson progress for a student
        
        Args:
            student: Student object
            lessons: List of all Lesson objects
            lesson_progress_list: List of LessonProgress objects for student
        
        Returns:
            dict: Progress statistics
        """
        total_lessons = len(lessons)
        if total_lessons == 0:
            return {
                'completed': 0,
                'in_progress': 0,
                'not_started': 0,
                'completion_percentage': 0,
                'lessons': []
            }
        
        progress_map = {lp.lesson_id: lp for lp in lesson_progress_list}
        
        completed = 0
        in_progress = 0
        not_started = 0
        lesson_stats = []
        
        for lesson in lessons:
            lp = progress_map.get(lesson.id)
            
            if lp:
                if lp.status == 'completed':
                    completed += 1
                    status = 'completed'
                elif lp.status == 'in_progress':
                    in_progress += 1
                    status = 'in_progress'
                else:
                    not_started += 1
                    status = 'not_started'
                
                progress_percent = lp.progress_percent
            else:
                not_started += 1
                status = 'not_started'
                progress_percent = 0
            
            lesson_stats.append({
                'lesson_id': lesson.id,
                'title': lesson.title,
                'status': status,
                'progress_percent': progress_percent,
            })
        
        completion_percentage = (completed / total_lessons) * 100
        
        return {
            'completed': completed,
            'in_progress': in_progress,
            'not_started': not_started,
            'completion_percentage': round(completion_percentage, 1),
            'lessons': lesson_stats
        }
    
    def calculate_quiz_statistics(self, quiz_results):
        """
        Calculate quiz performance statistics
        
        Args:
            quiz_results: List of QuizResult objects
        
        Returns:
            dict: Quiz statistics
        """
        if not quiz_results:
            return {
                'total_quizzes': 0,
                'average_score': 0,
                'highest_score': 0,
                'lowest_score': 0,
                'total_time_spent': 0,
                'scores_by_difficulty': {},
                'recent_scores': []
            }
        
        scores = [r.score for r in quiz_results]
        times = [r.time_spent for r in quiz_results]
        
        scores_by_difficulty = defaultdict(list)
        for r in quiz_results:
            scores_by_difficulty[r.difficulty_at_time].append(r.score)
        
        avg_by_difficulty = {
            diff: round(sum(s) / len(s), 1)
            for diff, s in scores_by_difficulty.items()
        }
        
        recent_results = sorted(quiz_results, key=lambda x: x.completed_at, reverse=True)[:10]
        recent_scores = [
            {
                'score': r.score,
                'date': r.completed_at.strftime('%Y-%m-%d'),
                'difficulty': r.difficulty_at_time
            }
            for r in recent_results
        ]
        
        return {
            'total_quizzes': len(quiz_results),
            'average_score': round(sum(scores) / len(scores), 1),
            'highest_score': max(scores),
            'lowest_score': min(scores),
            'total_time_spent': sum(times),
            'scores_by_difficulty': avg_by_difficulty,
            'recent_scores': recent_scores
        }
    
    def get_weekly_report(self, student, quiz_results, lesson_progress, activity_logs):
        """
        Generate weekly progress report
        
        Args:
            student: Student object
            quiz_results: List of QuizResult objects
            lesson_progress: List of LessonProgress objects
            activity_logs: List of ActivityLog objects
        
        Returns:
            dict: Weekly report data
        """
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        weekly_quizzes = [r for r in quiz_results if r.completed_at >= week_ago]
        weekly_lessons = [lp for lp in lesson_progress if lp.last_accessed >= week_ago]
        weekly_activities = [a for a in activity_logs if a.created_at >= week_ago]
        
        if weekly_quizzes:
            weekly_avg_score = sum(r.score for r in weekly_quizzes) / len(weekly_quizzes)
            weekly_time = sum(r.time_spent for r in weekly_quizzes)
        else:
            weekly_avg_score = 0
            weekly_time = 0
        
        daily_activity = defaultdict(int)
        for activity in weekly_activities:
            day = activity.created_at.strftime('%A')
            daily_activity[day] += 1
        
        achievements = self._check_achievements(student, weekly_quizzes, weekly_lessons)
        
        return {
            'period': {
                'start': (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%d'),
                'end': datetime.utcnow().strftime('%Y-%m-%d')
            },
            'quizzes_taken': len(weekly_quizzes),
            'average_score': round(weekly_avg_score, 1),
            'time_spent_minutes': round(weekly_time / 60, 1),
            'lessons_accessed': len(weekly_lessons),
            'current_difficulty': student.current_difficulty,
            'streak_days': student.streak_days,
            'daily_activity': dict(daily_activity),
            'achievements': achievements
        }
    
    def _check_achievements(self, student, weekly_quizzes, weekly_lessons):
        """Check for achievements earned this week"""
        achievements = []
        
        if len(weekly_quizzes) >= 5:
            achievements.append({
                'name': 'Quiz Master',
                'description': 'Completed 5+ quizzes this week',
                'icon': 'award'
            })
        
        perfect_scores = [q for q in weekly_quizzes if q.score >= 100]
        if perfect_scores:
            achievements.append({
                'name': 'Perfect Score',
                'description': 'Achieved 100% on a quiz',
                'icon': 'star'
            })
        
        if student.streak_days >= 7:
            achievements.append({
                'name': 'Week Warrior',
                'description': '7-day learning streak',
                'icon': 'zap'
            })
        
        if len(weekly_lessons) >= 3:
            achievements.append({
                'name': 'Dedicated Learner',
                'description': 'Accessed 3+ lessons this week',
                'icon': 'book-open'
            })
        
        high_scores = [q for q in weekly_quizzes if q.score >= 80]
        if len(high_scores) >= 3:
            achievements.append({
                'name': 'Consistent Excellence',
                'description': 'Scored 80%+ on 3 quizzes',
                'icon': 'trending-up'
            })
        
        return achievements
    
    def get_progress_chart_data(self, quiz_results, days=30):
        """
        Get data formatted for progress charts
        
        Args:
            quiz_results: List of QuizResult objects
            days: Number of days to include
        
        Returns:
            dict: Chart data for visualization
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_results = [r for r in quiz_results if r.completed_at >= cutoff_date]
        
        daily_scores = defaultdict(list)
        for r in recent_results:
            date_str = r.completed_at.strftime('%Y-%m-%d')
            daily_scores[date_str].append(r.score)
        
        labels = []
        scores = []
        
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=days - 1 - i)
            date_str = date.strftime('%Y-%m-%d')
            labels.append(date.strftime('%b %d'))
            
            if date_str in daily_scores:
                avg_score = sum(daily_scores[date_str]) / len(daily_scores[date_str])
                scores.append(round(avg_score, 1))
            else:
                scores.append(None)
        
        difficulty_counts = defaultdict(int)
        for r in recent_results:
            difficulty_counts[r.difficulty_at_time] += 1
        
        return {
            'line_chart': {
                'labels': labels,
                'scores': scores,
                'title': 'Quiz Scores Over Time'
            },
            'difficulty_distribution': {
                'labels': list(difficulty_counts.keys()),
                'values': list(difficulty_counts.values()),
                'title': 'Quizzes by Difficulty'
            }
        }
    
    def update_streak(self, student, db_session):
        """
        Update student's learning streak
        
        Args:
            student: Student object
            db_session: Database session
        
        Returns:
            int: Updated streak count
        """
        now = datetime.utcnow()
        last_active = student.last_active
        
        if last_active:
            days_diff = (now.date() - last_active.date()).days
            
            if days_diff == 0:
                pass
            elif days_diff == 1:
                student.streak_days += 1
            else:
                student.streak_days = 1
        else:
            student.streak_days = 1
        
        student.last_active = now
        db_session.commit()
        
        return student.streak_days


progress_tracker = ProgressTracker()
