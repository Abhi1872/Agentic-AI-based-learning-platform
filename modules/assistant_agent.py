"""
Parent & Teacher AI Assistant Agent
Generates summaries, reports, and insights for parents and teachers.
Uses LLM for generating readable reports.
"""
import os
import logging
from datetime import datetime, timedelta, date
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
    # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
    # do not change this unless explicitly requested by the user
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except Exception as e:
    OPENAI_AVAILABLE = False
    openai_client = None
    logger.warning(f"OpenAI not available: {e}")


class AssistantAgent:
    """AI Assistant for generating reports and summaries for parents and teachers."""
    
    def __init__(self):
        self.report_cache = {}
    
    def generate_weekly_summary(self, student_id: int, db_session) -> Dict[str, Any]:
        """
        Generate a weekly summary of student activity.
        
        Includes:
        - Attendance record
        - Quiz performance
        - Lesson completion
        - Overall progress
        """
        from models import (
            Student, AttendanceRecord, QuizResult, LessonProgress,
            GameSession, FocusSession
        )
        
        student = Student.query.get(student_id)
        if not student:
            return {'success': False, 'message': 'Student not found'}
        
        week_ago = datetime.utcnow() - timedelta(days=7)
        today = date.today()
        week_start = today - timedelta(days=7)
        
        attendance = AttendanceRecord.query.filter(
            AttendanceRecord.student_id == student_id,
            AttendanceRecord.date >= week_start
        ).all()
        
        days_present = sum(1 for a in attendance if a.status == 'present')
        attendance_rate = (days_present / 7) * 100 if attendance else 0
        
        quiz_results = QuizResult.query.filter(
            QuizResult.student_id == student_id,
            QuizResult.completed_at >= week_ago
        ).all()
        
        quizzes_taken = len(quiz_results)
        avg_score = sum(r.score for r in quiz_results) / quizzes_taken if quizzes_taken else 0
        
        lessons_completed = LessonProgress.query.filter(
            LessonProgress.student_id == student_id,
            LessonProgress.status == 'completed',
            LessonProgress.completed_at >= week_ago
        ).count()
        
        lessons_in_progress = LessonProgress.query.filter(
            LessonProgress.student_id == student_id,
            LessonProgress.status == 'in_progress'
        ).count()
        
        game_sessions = GameSession.query.filter(
            GameSession.student_id == student_id,
            GameSession.started_at >= week_ago
        ).all()
        
        games_played = len(game_sessions)
        games_completed = sum(1 for g in game_sessions if g.completed)
        
        focus_sessions = FocusSession.query.filter(
            FocusSession.student_id == student_id,
            FocusSession.started_at >= week_ago
        ).all()
        
        total_focus_time = sum(f.duration_seconds or 0 for f in focus_sessions)
        avg_focus_score = sum(f.focus_score or 0 for f in focus_sessions) / len(focus_sessions) if focus_sessions else 0
        
        summary = {
            'success': True,
            'student_name': student.name,
            'student_id': student.student_id,
            'week_start': week_start.isoformat(),
            'week_end': today.isoformat(),
            'attendance': {
                'days_present': days_present,
                'total_days': 7,
                'rate': round(attendance_rate, 1)
            },
            'quizzes': {
                'taken': quizzes_taken,
                'average_score': round(avg_score, 1),
                'scores': [r.score for r in quiz_results]
            },
            'lessons': {
                'completed': lessons_completed,
                'in_progress': lessons_in_progress
            },
            'games': {
                'played': games_played,
                'completed': games_completed,
                'coins_earned': student.total_coins,
                'stars_earned': student.total_stars
            },
            'focus': {
                'total_minutes': round(total_focus_time / 60, 1),
                'average_score': round(avg_focus_score, 1)
            },
            'current_level': student.current_difficulty,
            'streak_days': student.streak_days
        }
        
        summary['narrative'] = self._generate_narrative_summary(summary)
        
        return summary
    
    def _generate_narrative_summary(self, data: Dict) -> str:
        """Generate a human-readable narrative from summary data."""
        if OPENAI_AVAILABLE and openai_client:
            try:
                prompt = f"""Create a brief, encouraging weekly progress report for a parent about their child's learning.
Use simple, positive language. The child may have special learning needs.

Data:
- Student: {data['student_name']}
- Attendance: {data['attendance']['days_present']}/7 days ({data['attendance']['rate']}%)
- Quizzes taken: {data['quizzes']['taken']}, Average score: {data['quizzes']['average_score']}%
- Lessons completed: {data['lessons']['completed']}, In progress: {data['lessons']['in_progress']}
- Games played: {data['games']['played']}, Completed: {data['games']['completed']}
- Current level: {data['current_level']}
- Learning streak: {data['streak_days']} days

Write 3-4 sentences summarizing the week and highlighting achievements. Be encouraging!"""
                
                response = openai_client.chat.completions.create(
                    model="gpt-5",
                    messages=[{"role": "user", "content": prompt}],
                    max_completion_tokens=200
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                logger.error(f"LLM narrative failed: {e}")
        
        return self._rule_based_narrative(data)
    
    def _rule_based_narrative(self, data: Dict) -> str:
        """Generate narrative using rule-based approach."""
        parts = []
        
        name = data['student_name'].split()[0]
        parts.append(f"{name} had a productive week of learning!")
        
        if data['attendance']['rate'] >= 80:
            parts.append(f"Great attendance with {data['attendance']['days_present']} days present.")
        elif data['attendance']['rate'] >= 50:
            parts.append(f"Attended {data['attendance']['days_present']} days this week.")
        
        if data['quizzes']['taken'] > 0:
            if data['quizzes']['average_score'] >= 80:
                parts.append(f"Excellent quiz performance with {data['quizzes']['average_score']}% average!")
            elif data['quizzes']['average_score'] >= 60:
                parts.append(f"Good progress on quizzes with {data['quizzes']['average_score']}% average.")
            else:
                parts.append(f"Working through quizzes - practice makes perfect!")
        
        if data['lessons']['completed'] > 0:
            parts.append(f"Completed {data['lessons']['completed']} lesson(s) this week.")
        
        if data['streak_days'] > 0:
            parts.append(f"Currently on a {data['streak_days']}-day learning streak!")
        
        return " ".join(parts)
    
    def generate_strengths_weaknesses(self, student_id: int, db_session) -> Dict[str, Any]:
        """
        Generate a detailed strengths and weaknesses report.
        Uses rule-based analysis plus LLM for generating readable report.
        """
        from models import Student, QuizResult, LessonProgress, Quiz, Lesson
        from sqlalchemy import func
        
        student = Student.query.get(student_id)
        if not student:
            return {'success': False, 'message': 'Student not found'}
        
        all_results = QuizResult.query.filter_by(student_id=student_id).all()
        
        subject_scores = {}
        for result in all_results:
            quiz = Quiz.query.get(result.quiz_id)
            if quiz and quiz.lesson:
                subject = quiz.lesson.subject
                if subject not in subject_scores:
                    subject_scores[subject] = []
                subject_scores[subject].append(result.score)
        
        subject_averages = {
            subject: sum(scores) / len(scores)
            for subject, scores in subject_scores.items()
        }
        
        sorted_subjects = sorted(subject_averages.items(), key=lambda x: x[1], reverse=True)
        
        strengths = [s[0] for s in sorted_subjects if s[1] >= 70][:3]
        weaknesses = [s[0] for s in sorted_subjects if s[1] < 60][:3]
        
        progress = LessonProgress.query.filter_by(
            student_id=student_id,
            status='completed'
        ).all()
        
        completion_rate = (len(progress) / max(1, Lesson.query.count())) * 100
        
        improvement_areas = []
        if student.focus_duration_avg and student.focus_duration_avg < 10:
            improvement_areas.append('Focus duration - try shorter learning sessions')
        if student.reading_speed_wpm and student.reading_speed_wpm < 100:
            improvement_areas.append('Reading speed - audio mode may help')
        if weaknesses:
            improvement_areas.append(f'Subject areas: {", ".join(weaknesses)}')
        
        report = {
            'success': True,
            'student_name': student.name,
            'strengths': strengths if strengths else ['Making good progress overall'],
            'areas_for_improvement': weaknesses if weaknesses else ['Keep up the great work!'],
            'improvement_suggestions': improvement_areas,
            'subject_performance': subject_averages,
            'completion_rate': round(completion_rate, 1),
            'current_level': student.current_difficulty,
            'special_needs_type': student.special_needs_type
        }
        
        report['detailed_report'] = self._generate_detailed_report(report)
        
        return report
    
    def _generate_detailed_report(self, data: Dict) -> str:
        """Generate a detailed readable report."""
        if OPENAI_AVAILABLE and openai_client:
            try:
                prompt = f"""Create a brief, professional report about a student's academic strengths and areas for improvement.
Use encouraging, constructive language suitable for parents of a child with potential learning differences.

Student: {data['student_name']}
Strengths: {', '.join(data['strengths'])}
Areas for improvement: {', '.join(data['areas_for_improvement'])}
Suggestions: {', '.join(data['improvement_suggestions']) if data['improvement_suggestions'] else 'None specific'}
Subject scores: {data['subject_performance']}
Current level: {data['current_level']}
Special needs: {data['special_needs_type'] or 'Not specified'}

Write a 4-5 sentence report highlighting strengths first, then gently addressing improvement areas with specific, actionable suggestions."""
                
                response = openai_client.chat.completions.create(
                    model="gpt-5",
                    messages=[{"role": "user", "content": prompt}],
                    max_completion_tokens=300
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                logger.error(f"LLM report failed: {e}")
        
        parts = [f"{data['student_name']} shows strong abilities in {', '.join(data['strengths'][:2]) if data['strengths'] else 'multiple areas'}."]
        
        if data['areas_for_improvement'] and data['areas_for_improvement'][0] != 'Keep up the great work!':
            parts.append(f"Areas to focus on include {', '.join(data['areas_for_improvement'][:2])}.")
        
        if data['improvement_suggestions']:
            parts.append(f"We recommend: {data['improvement_suggestions'][0]}.")
        
        parts.append(f"Overall completion rate: {data['completion_rate']}%.")
        
        return " ".join(parts)
    
    def get_parent_dashboard_data(self, student_id: int, db_session) -> Dict[str, Any]:
        """Get comprehensive data for parent dashboard."""
        weekly = self.generate_weekly_summary(student_id, db_session)
        strengths = self.generate_strengths_weaknesses(student_id, db_session)
        
        if not weekly.get('success'):
            return weekly
        
        return {
            'success': True,
            'weekly_summary': weekly,
            'strengths_report': strengths,
            'last_updated': datetime.utcnow().isoformat()
        }


assistant_agent = AssistantAgent()
