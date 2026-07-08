"""
Adaptive Learning Agent
Analyzes student performance and adjusts learning difficulty dynamically.
Uses rule-based logic and LLM for generating feedback.
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any

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


class AdaptiveAgent:
    """Agent that adapts learning content based on student performance."""
    
    DIFFICULTY_LEVELS = ['easy', 'medium', 'advanced']
    
    def __init__(self):
        self.fail_threshold = 2
        self.quick_completion_threshold = 3
        self.quick_time_threshold = 120
    
    def analyze_quiz_history(self, student_id: int, db_session) -> Dict[str, Any]:
        """
        Analyze quiz scores from database and detect patterns.
        
        Patterns detected:
        - fail_streak: Failed 2+ quizzes in a row
        - fast_completion: Completed 3+ lessons quickly
        - stuck_behavior: Low scores with long times
        """
        from models import QuizResult, LessonProgress
        
        recent_results = QuizResult.query.filter_by(
            student_id=student_id
        ).order_by(QuizResult.completed_at.desc()).limit(10).all()
        
        analysis = {
            'total_quizzes': len(recent_results),
            'fail_streak': 0,
            'fast_completions': 0,
            'stuck_detected': False,
            'average_score': 0,
            'pattern': 'normal',
            'recent_scores': [],
            'recommendations': []
        }
        
        if not recent_results:
            return analysis
        
        scores = [r.score for r in recent_results]
        analysis['average_score'] = sum(scores) / len(scores) if scores else 0
        analysis['recent_scores'] = scores[:5]
        
        consecutive_fails = 0
        for result in recent_results:
            if result.score < 50:
                consecutive_fails += 1
            else:
                break
        analysis['fail_streak'] = consecutive_fails
        
        recent_progress = LessonProgress.query.filter_by(
            student_id=student_id,
            status='completed'
        ).order_by(LessonProgress.completed_at.desc()).limit(5).all()
        
        fast_count = sum(1 for p in recent_progress if p.time_spent and p.time_spent < self.quick_time_threshold)
        analysis['fast_completions'] = fast_count
        
        if recent_results:
            avg_time = sum(r.time_spent or 0 for r in recent_results[:3]) / min(3, len(recent_results))
            avg_score = sum(r.score for r in recent_results[:3]) / min(3, len(recent_results))
            if avg_time > 300 and avg_score < 60:
                analysis['stuck_detected'] = True
                analysis['pattern'] = 'stuck'
        
        if consecutive_fails >= self.fail_threshold:
            analysis['pattern'] = 'struggling'
            analysis['recommendations'].append('Consider lowering difficulty level')
        elif fast_count >= self.quick_completion_threshold:
            analysis['pattern'] = 'excelling'
            analysis['recommendations'].append('Ready for more challenging content')
        
        logger.info(f"Quiz analysis for student {student_id}: pattern={analysis['pattern']}")
        return analysis
    
    def adjust_lesson_difficulty(self, student_id: int, db_session) -> Dict[str, Any]:
        """
        Adjust difficulty based on performance patterns.
        
        Rules:
        - Fails 2+ quizzes → downgrade difficulty
        - Finishes 3+ lessons quickly → upgrade difficulty
        - Stuck behavior → enable hint mode
        """
        from models import Student
        
        student = db_session.get(Student, student_id)
        if not student:
            return {'success': False, 'message': 'Student not found'}
        
        analysis = self.analyze_quiz_history(student_id, db_session)
        
        result = {
            'success': True,
            'previous_difficulty': student.current_difficulty,
            'new_difficulty': student.current_difficulty,
            'hint_mode_enabled': False,
            'action_taken': 'none',
            'message': ''
        }
        
        current_idx = self.DIFFICULTY_LEVELS.index(student.current_difficulty) if student.current_difficulty in self.DIFFICULTY_LEVELS else 0
        
        if analysis['fail_streak'] >= self.fail_threshold and current_idx > 0:
            new_idx = current_idx - 1
            student.current_difficulty = self.DIFFICULTY_LEVELS[new_idx]
            result['new_difficulty'] = student.current_difficulty
            result['action_taken'] = 'downgrade'
            result['message'] = f"Difficulty lowered to {student.current_difficulty} to help you learn better"
            logger.info(f"Downgraded difficulty for student {student_id}")
        
        elif analysis['fast_completions'] >= self.quick_completion_threshold and current_idx < len(self.DIFFICULTY_LEVELS) - 1:
            new_idx = current_idx + 1
            student.current_difficulty = self.DIFFICULTY_LEVELS[new_idx]
            result['new_difficulty'] = student.current_difficulty
            result['action_taken'] = 'upgrade'
            result['message'] = f"Great job! You've been promoted to {student.current_difficulty} level"
            logger.info(f"Upgraded difficulty for student {student_id}")
        
        if analysis['stuck_detected']:
            result['hint_mode_enabled'] = True
            result['message'] = (result['message'] + " Hints have been enabled to help you." 
                               if result['message'] else "Hints have been enabled to help you.")
            logger.info(f"Enabled hints for stuck student {student_id}")
        
        try:
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            logger.error(f"Error saving difficulty adjustment: {e}")
            result['success'] = False
            result['message'] = 'Error saving changes'
        
        return result
    
    def generate_mistake_summary(self, answers: List[Dict], questions: List[Dict] = None) -> str:
        """
        Use LLM to summarize common errors and provide feedback.
        
        Args:
            answers: List of answer data with 'question', 'student_answer', 'correct_answer', 'is_correct'
            questions: Optional list of full question data
        
        Returns:
            Feedback message summarizing mistakes
        """
        wrong_answers = [a for a in answers if not a.get('is_correct', True)]
        
        if not wrong_answers:
            return "Excellent work! You got everything correct!"
        
        if not OPENAI_AVAILABLE or not openai_client:
            return self._generate_rule_based_summary(wrong_answers)
        
        try:
            mistakes_text = "\n".join([
                f"- Question: {a.get('question', 'Unknown')}\n  Student answered: {a.get('student_answer', 'Unknown')}\n  Correct answer: {a.get('correct_answer', 'Unknown')}"
                for a in wrong_answers[:5]
            ])
            
            prompt = f"""You are an encouraging educational assistant for differently-abled students. 
Analyze these quiz mistakes and provide a brief, positive, and helpful summary (2-3 sentences).
Focus on what the student can improve, not what they did wrong. Use simple language.

Mistakes:
{mistakes_text}

Provide encouraging feedback that helps the student understand their mistakes without being discouraging."""
            
            response = openai_client.chat.completions.create(
                model="gpt-5",
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=200
            )
            
            feedback = response.choices[0].message.content.strip()
            logger.info("Generated LLM feedback for mistakes")
            return feedback
            
        except Exception as e:
            logger.error(f"LLM feedback generation failed: {e}")
            return self._generate_rule_based_summary(wrong_answers)
    
    def _generate_rule_based_summary(self, wrong_answers: List[Dict]) -> str:
        """Fallback rule-based summary when LLM is unavailable."""
        count = len(wrong_answers)
        
        if count == 1:
            return "You got 1 question wrong. Review the explanation and try again - you're doing great!"
        elif count <= 3:
            return f"You missed {count} questions. Take your time reviewing the lesson content. You're making good progress!"
        else:
            return f"You had some challenges with {count} questions. Consider reviewing the lesson again - every attempt helps you learn!"
    
    def get_personalized_content(self, student_id: int, lesson, db_session) -> Dict[str, Any]:
        """
        Get personalized lesson content based on student's current state.
        """
        from models import Student
        
        student = db_session.get(Student, student_id)
        if not student:
            return {'content': lesson.content_easy, 'difficulty': 'easy', 'hints_enabled': False}
        
        analysis = self.analyze_quiz_history(student_id, db_session)
        
        difficulty = student.current_difficulty
        content_map = {
            'easy': lesson.content_easy,
            'medium': lesson.content_medium,
            'advanced': lesson.content_advanced
        }
        
        return {
            'content': content_map.get(difficulty, lesson.content_easy),
            'difficulty': difficulty,
            'hints_enabled': analysis.get('stuck_detected', False),
            'recommendations': analysis.get('recommendations', [])
        }
    
    def get_lesson_version(self, student_id: int, lesson_name: str, db_session=None) -> str:
        """
        Get the appropriate lesson difficulty version for a student.
        
        Args:
            student_id: Student identifier
            lesson_name: Name of the lesson
            db_session: Database session (optional)
        
        Returns:
            Difficulty level: 'beginner', 'intermediate', or 'advanced'
        """
        import json
        import os
        
        difficulty_map = {
            'easy': 'beginner',
            'medium': 'intermediate', 
            'advanced': 'advanced'
        }
        
        try:
            from models import Student, QuizResult
            
            student = Student.query.get(student_id) if student_id else None
            
            if not student:
                return 'beginner'
            
            analysis = self.analyze_quiz_history(student_id, db_session or Student.query.session)
            
            if analysis['pattern'] == 'struggling' or analysis['fail_streak'] >= 2:
                return 'beginner'
            elif analysis['pattern'] == 'excelling' or (analysis['average_score'] >= 80 and analysis['fast_completions'] >= 2):
                return 'advanced'
            elif analysis['average_score'] >= 60:
                return 'intermediate'
            else:
                return difficulty_map.get(student.current_difficulty, 'beginner')
                
        except Exception as e:
            logger.error(f"Error getting lesson version: {e}")
            return 'beginner'
    
    def get_next_lesson(self, student_id: int, db_session=None) -> Optional[str]:
        """
        Get the next recommended lesson for a student based on their progress.
        
        Args:
            student_id: Student identifier
            db_session: Database session
        
        Returns:
            Lesson name or None if all completed
        """
        lesson_sequence = [
            'programming_basics',
            'data_structures',
            'oops',
            'databases',
            'networking',
            'operating_systems'
        ]
        
        try:
            from models import LessonProgress
            
            completed_lessons = set()
            progress_records = LessonProgress.query.filter_by(
                student_id=student_id,
                status='completed'
            ).all()
            
            for p in progress_records:
                if hasattr(p, 'lesson') and p.lesson:
                    lesson_title = p.lesson.title.lower().replace(' ', '_').replace('-', '_')
                    completed_lessons.add(lesson_title)
            
            for lesson in lesson_sequence:
                if lesson not in completed_lessons:
                    return lesson
            
            return lesson_sequence[0]
            
        except Exception as e:
            logger.error(f"Error getting next lesson: {e}")
            return 'programming_basics'
    
    def update_learning_path(self, student_id: int, performance_data: Dict[str, Any], db_session=None) -> Dict[str, Any]:
        """
        Update the student's learning path based on performance data.
        
        Args:
            student_id: Student identifier
            performance_data: Dict containing score, time_spent, lesson_name
            db_session: Database session
        
        Returns:
            Updated learning path recommendations
        """
        try:
            from models import Student, LessonProgress
            
            student = Student.query.get(student_id)
            if not student:
                return {'success': False, 'message': 'Student not found'}
            
            score = performance_data.get('score', 0)
            time_spent = performance_data.get('time_spent', 0)
            lesson_name = performance_data.get('lesson_name', '')
            
            current_difficulty = self.get_lesson_version(student_id, lesson_name, db_session)
            next_lesson = self.get_next_lesson(student_id, db_session)
            
            recommendations = []
            new_difficulty = current_difficulty
            
            if score >= 90 and time_spent < 120:
                if current_difficulty == 'beginner':
                    new_difficulty = 'intermediate'
                    recommendations.append('Ready to advance to intermediate level!')
                elif current_difficulty == 'intermediate':
                    new_difficulty = 'advanced'
                    recommendations.append('Excellent! Moving to advanced level.')
            elif score < 50:
                if current_difficulty == 'advanced':
                    new_difficulty = 'intermediate'
                    recommendations.append('Let\'s practice at intermediate level first.')
                elif current_difficulty == 'intermediate':
                    new_difficulty = 'beginner'
                    recommendations.append('Taking time to reinforce the basics.')
            
            return {
                'success': True,
                'current_difficulty': current_difficulty,
                'recommended_difficulty': new_difficulty,
                'next_lesson': next_lesson,
                'recommendations': recommendations,
                'analysis': self.analyze_quiz_history(student_id, db_session or Student.query.session)
            }
            
        except Exception as e:
            logger.error(f"Error updating learning path: {e}")
            return {'success': False, 'message': str(e)}


adaptive_agent = AdaptiveAgent()
