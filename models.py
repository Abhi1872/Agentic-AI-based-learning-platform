from datetime import datetime, date
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import secrets


class Student(UserMixin, db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=True)
    
    def set_password(self, password):
        """Set the password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    current_difficulty = db.Column(db.String(20), default='easy')
    preferred_mode = db.Column(db.String(20), default='text')
    audio_enabled = db.Column(db.Boolean, default=False)
    sign_language_enabled = db.Column(db.Boolean, default=False)
    emotion_detection_enabled = db.Column(db.Boolean, default=False)
    font_size = db.Column(db.Integer, default=18)
    high_contrast = db.Column(db.Boolean, default=False)
    reduce_motion = db.Column(db.Boolean, default=False)
    
    total_lessons_completed = db.Column(db.Integer, default=0)
    total_quizzes_taken = db.Column(db.Integer, default=0)
    average_score = db.Column(db.Float, default=0.0)
    streak_days = db.Column(db.Integer, default=0)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    total_coins = db.Column(db.Integer, default=0)
    total_stars = db.Column(db.Integer, default=0)
    games_unlocked = db.Column(db.Boolean, default=False)
    
    learning_style = db.Column(db.String(50), default='visual')
    special_needs_type = db.Column(db.String(50), nullable=True)
    focus_duration_avg = db.Column(db.Integer, default=0)
    reading_speed_wpm = db.Column(db.Integer, default=0)
    
    quiz_results = db.relationship('QuizResult', backref='student', lazy=True)
    lesson_progress = db.relationship('LessonProgress', backref='student', lazy=True)
    game_sessions = db.relationship('GameSession', backref='student', lazy=True)
    game_rewards = db.relationship('GameReward', backref='student', lazy=True)
    attendance_records = db.relationship('AttendanceRecord', backref='student', lazy=True)
    
    def get_completed_quizzes_count(self):
        """Get the number of completed quizzes"""
        return QuizResult.query.filter_by(student_id=self.id).count()
    
    def can_access_games(self):
        """Check if student has completed at least 2 quizzes to unlock games"""
        return self.get_completed_quizzes_count() >= 2


class Lesson(db.Model):
    __tablename__ = 'lessons'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    subject = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), default='general')
    
    content_easy = db.Column(db.Text, nullable=False)
    content_medium = db.Column(db.Text, nullable=False)
    content_advanced = db.Column(db.Text, nullable=False)
    
    estimated_time = db.Column(db.Integer, default=10)
    order_index = db.Column(db.Integer, default=0)
    difficulty_tier = db.Column(db.String(20), default='beginner')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    quizzes = db.relationship('Quiz', backref='lesson', lazy=True)
    progress = db.relationship('LessonProgress', backref='lesson', lazy=True)


class Quiz(db.Model):
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    questions = db.relationship('QuizQuestion', backref='quiz', lazy=True)


class QuizQuestion(db.Model):
    __tablename__ = 'quiz_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(500), nullable=False)
    option_b = db.Column(db.String(500), nullable=False)
    option_c = db.Column(db.String(500), nullable=False)
    option_d = db.Column(db.String(500), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    explanation = db.Column(db.Text, nullable=True)
    order_index = db.Column(db.Integer, default=0)


class QuizResult(db.Model):
    __tablename__ = 'quiz_results'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    
    score = db.Column(db.Float, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False)
    time_spent = db.Column(db.Integer, default=0)
    difficulty_at_time = db.Column(db.String(20), nullable=False)
    
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)


class LessonProgress(db.Model):
    __tablename__ = 'lesson_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    
    status = db.Column(db.String(20), default='not_started')
    progress_percent = db.Column(db.Float, default=0.0)
    time_spent = db.Column(db.Integer, default=0)
    difficulty_used = db.Column(db.String(20), default='easy')
    
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)


class EmotionLog(db.Model):
    __tablename__ = 'emotion_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    emotion = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, default=0.0)
    context = db.Column(db.String(50), nullable=True)
    
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)


class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    activity_type = db.Column(db.String(50), nullable=False)
    details = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Game(db.Model):
    __tablename__ = 'games'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    game_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    instructions = db.Column(db.Text, nullable=True)
    
    min_difficulty = db.Column(db.Integer, default=1)
    max_difficulty = db.Column(db.Integer, default=5)
    base_coins = db.Column(db.Integer, default=10)
    base_stars = db.Column(db.Integer, default=1)
    
    is_active = db.Column(db.Boolean, default=True)
    icon = db.Column(db.String(50), default='gamepad-2')
    color_theme = db.Column(db.String(20), default='primary')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    sessions = db.relationship('GameSession', backref='game', lazy=True)


class GameSession(db.Model):
    __tablename__ = 'game_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    
    difficulty_level = db.Column(db.Integer, default=1)
    score = db.Column(db.Integer, default=0)
    moves_made = db.Column(db.Integer, default=0)
    time_spent = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    
    coins_earned = db.Column(db.Integer, default=0)
    stars_earned = db.Column(db.Integer, default=0)
    
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)


class GameReward(db.Model):
    __tablename__ = 'game_rewards'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    reward_type = db.Column(db.String(50), nullable=False)
    reward_name = db.Column(db.String(100), nullable=False)
    reward_icon = db.Column(db.String(50), default='award')
    description = db.Column(db.Text, nullable=True)
    
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)


class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(20), default='present')
    check_in_time = db.Column(db.DateTime, nullable=True)
    check_out_time = db.Column(db.DateTime, nullable=True)
    
    marked_by = db.Column(db.String(50), default='self')
    notes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('student_id', 'date', name='unique_student_date'),
    )


class Teacher(db.Model):
    __tablename__ = 'teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=True)
    
    subject = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    attendance_records = db.relationship('TeacherAttendance', backref='teacher', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)


class TeacherAttendance(db.Model):
    __tablename__ = 'teacher_attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    
    date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(20), default='present')
    check_in_time = db.Column(db.DateTime, nullable=True)
    check_out_time = db.Column(db.DateTime, nullable=True)
    
    notes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('teacher_id', 'date', name='unique_teacher_date'),
    )


class ParentAccount(db.Model):
    __tablename__ = 'parent_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(256), nullable=True)
    
    access_token = db.Column(db.String(64), unique=True, nullable=True)
    audio_mode_enabled = db.Column(db.Boolean, default=False)
    high_contrast = db.Column(db.Boolean, default=False)
    font_size = db.Column(db.Integer, default=18)
    
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def generate_access_token(self):
        self.access_token = secrets.token_urlsafe(32)
        return self.access_token


class ParentStudentLink(db.Model):
    __tablename__ = 'parent_student_links'
    
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent_accounts.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    relationship = db.Column(db.String(50), default='parent')
    can_view_reports = db.Column(db.Boolean, default=True)
    notifications_enabled = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    parent = db.relationship('ParentAccount', backref='student_links')
    student = db.relationship('Student', backref='parent_links')
    
    __table_args__ = (
        db.UniqueConstraint('parent_id', 'student_id', name='unique_parent_student'),
    )


class FocusSession(db.Model):
    __tablename__ = 'focus_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    activity_type = db.Column(db.String(50), nullable=False)
    activity_id = db.Column(db.Integer, nullable=True)
    
    duration_seconds = db.Column(db.Integer, default=0)
    focus_score = db.Column(db.Float, default=0.0)
    distractions_count = db.Column(db.Integer, default=0)
    
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime, nullable=True)
    
    student = db.relationship('Student', backref='focus_sessions')


class ReadingProgress(db.Model):
    __tablename__ = 'reading_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    words_read = db.Column(db.Integer, default=0)
    time_spent_seconds = db.Column(db.Integer, default=0)
    words_per_minute = db.Column(db.Float, default=0.0)
    accuracy_percent = db.Column(db.Float, default=0.0)
    
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=True)
    
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    student = db.relationship('Student', backref='reading_progress')


class UserPreferences(db.Model):
    """User accessibility preferences tracked by the Accessibility Agent."""
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, unique=True)
    
    audio_mode = db.Column(db.Boolean, default=False)
    large_text = db.Column(db.Boolean, default=False)
    reduced_motion = db.Column(db.Boolean, default=False)
    sign_language = db.Column(db.Boolean, default=False)
    
    reading_speed_avg = db.Column(db.Float, default=0.0)
    zoom_preference = db.Column(db.Integer, default=100)
    scroll_speed_avg = db.Column(db.Float, default=0.0)
    struggle_count = db.Column(db.Integer, default=0)
    
    ai_mode_enabled = db.Column(db.Boolean, default=True)
    emotion_monitor_enabled = db.Column(db.Boolean, default=False)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    student = db.relationship('Student', backref='user_preferences')
