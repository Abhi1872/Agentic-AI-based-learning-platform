"""
Flask Routes for Agentic AI Learning Platform
"""
import os
import logging
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user

from app import app, db, login_manager, csrf
from models import (
    Student, Lesson, Quiz, QuizQuestion, QuizResult, LessonProgress, 
    EmotionLog, ActivityLog, Game, GameSession, GameReward, 
    AttendanceRecord, Teacher, TeacherAttendance, ParentAccount, ParentStudentLink,
    FocusSession, ReadingProgress, UserPreferences
)
from datetime import date, timedelta
from sqlalchemy import func

from modules.tts_engine import text_to_speech, generate_lesson_audio
from modules.stt_engine import stt_engine, get_voice_commands
from modules.sign_language_detector import sign_language_detector
from modules.adaptive_engine import adaptive_engine
from modules.content_personalization import content_personalizer
from modules.emotion_detector import emotion_detector
from modules.progress_tracker import progress_tracker

from utils.helpers import (
    format_time_spent, format_date_relative, get_difficulty_color,
    get_difficulty_label, get_score_message, get_greeting,
    get_progress_bar_class, get_accessibility_options, generate_student_id
)
from utils.plot_utils import (
    create_score_line_chart, create_difficulty_pie_chart,
    create_progress_bar_chart, create_weekly_activity_chart
)

logger = logging.getLogger(__name__)


@login_manager.user_loader
def load_user(user_id):
    return Student.query.get(int(user_id))


@app.context_processor
def utility_processor():
    """Add utility functions to template context"""
    return {
        'format_time_spent': format_time_spent,
        'format_date_relative': format_date_relative,
        'get_difficulty_color': get_difficulty_color,
        'get_difficulty_label': get_difficulty_label,
        'get_progress_bar_class': get_progress_bar_class,
        'get_greeting': get_greeting,
    }


@app.route('/')
def index():
    """Landing page - Role Selection"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('role_select.html')


@app.route('/student/login')
def student_login_page():
    """Student login page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    students = Student.query.order_by(Student.name).all()
    return render_template('index.html', students=students)


@app.route('/login', methods=['POST'])
def login():
    """Handle student login"""
    student_id = request.form.get('student_id')
    password = request.form.get('password', '')
    
    if not student_id:
        flash('Please select a student profile.', 'error')
        return redirect(url_for('student_login_page'))
    
    student = Student.query.filter_by(student_id=student_id).first()
    
    if not student:
        flash('Student not found.', 'error')
        return redirect(url_for('student_login_page'))
    
    if student.password_hash and not student.check_password(password):
        flash('Invalid password. Please try again.', 'error')
        return redirect(url_for('student_login_page'))
    
    login_user(student)
    progress_tracker.update_streak(student, db.session)
    
    activity = ActivityLog(
        student_id=student.id,
        activity_type='login',
        details='Student logged in'
    )
    db.session.add(activity)
    db.session.commit()
    
    flash(f'Welcome back, {student.name}!', 'success')
    return redirect(url_for('dashboard'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register new student"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not name:
            flash('Please enter your name.', 'error')
            return redirect(url_for('register'))
        
        if len(name) > 100:
            flash('Name is too long. Please use a shorter name.', 'error')
            return redirect(url_for('register'))
        
        if email:
            if len(email) > 120:
                flash('Email is too long.', 'error')
                return redirect(url_for('register'))
            existing = Student.query.filter_by(email=email).first()
            if existing:
                flash('This email is already registered.', 'error')
                return redirect(url_for('register'))
        
        student_id = generate_student_id()
        while Student.query.filter_by(student_id=student_id).first():
            student_id = generate_student_id()
        
        student = Student(
            student_id=student_id,
            name=name,
            email=email if email else None,
            current_difficulty='easy'
        )
        
        if password:
            student.set_password(password)
        
        db.session.add(student)
        db.session.commit()
        
        login_user(student)
        flash(f'Welcome, {name}! Your student ID is {student_id}. Save it for future logins.', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    """Logout current user"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    from modules.adaptive_agent import adaptive_agent
    
    lessons = Lesson.query.filter_by(is_active=True).order_by(Lesson.order_index).all()
    
    lesson_progress_list = LessonProgress.query.filter_by(student_id=current_user.id).all()
    quiz_results = QuizResult.query.filter_by(student_id=current_user.id).all()
    
    progress_stats = progress_tracker.calculate_lesson_progress(
        current_user, lessons, lesson_progress_list
    )
    
    performance = adaptive_engine.analyze_performance(current_user.id, quiz_results)
    
    recommendations = adaptive_engine.get_personalized_recommendations(
        current_user, performance
    )
    
    progress_map = {lp.lesson_id: lp for lp in lesson_progress_list}
    
    next_lesson_name = adaptive_agent.get_next_lesson(current_user.id, db.session)
    next_lesson = None
    if next_lesson_name:
        lesson_name_map = {
            'programming_basics': 'Programming Basics',
            'data_structures': 'Data Structures',
            'oops': 'Object Oriented Programming',
            'databases': 'Databases',
            'networking': 'Networking',
            'operating_systems': 'Operating Systems'
        }
        lesson_title = lesson_name_map.get(next_lesson_name, next_lesson_name.replace('_', ' ').title())
        next_lesson = Lesson.query.filter(Lesson.title.ilike(f'%{lesson_title}%')).first()
        if not next_lesson and lessons:
            completed_ids = {lp.lesson_id for lp in lesson_progress_list if lp.status == 'completed'}
            for lesson in lessons:
                if lesson.id not in completed_ids:
                    next_lesson = lesson
                    break
    
    return render_template('dashboard.html',
        student=current_user,
        lessons=lessons,
        progress_map=progress_map,
        progress_stats=progress_stats,
        performance=performance,
        recommendations=recommendations,
        next_lesson=next_lesson,
        accessibility_options=get_accessibility_options()
    )


@app.route('/lesson/<int:lesson_id>')
@login_required
def lesson(lesson_id):
    """View a lesson"""
    lesson = Lesson.query.get_or_404(lesson_id)
    
    difficulty = current_user.current_difficulty
    content = content_personalizer.get_content_for_level(lesson, difficulty)
    
    lesson_progress = LessonProgress.query.filter_by(
        student_id=current_user.id,
        lesson_id=lesson_id
    ).first()
    
    if not lesson_progress:
        lesson_progress = LessonProgress(
            student_id=current_user.id,
            lesson_id=lesson_id,
            status='in_progress',
            started_at=datetime.utcnow(),
            difficulty_used=difficulty
        )
        db.session.add(lesson_progress)
    else:
        lesson_progress.status = 'in_progress'
        lesson_progress.last_accessed = datetime.utcnow()
    
    db.session.commit()
    
    content_formats = content_personalizer.get_content_formats(content, lesson_id)
    
    audio_url = None
    if current_user.audio_enabled:
        audio_url = generate_lesson_audio(content, lesson_id, difficulty)
    
    quiz = Quiz.query.filter_by(lesson_id=lesson_id, difficulty=difficulty).first()
    
    activity = ActivityLog(
        student_id=current_user.id,
        activity_type='lesson_view',
        details=f'Viewed lesson: {lesson.title}'
    )
    db.session.add(activity)
    db.session.commit()
    
    all_lessons = Lesson.query.filter_by(is_active=True).order_by(Lesson.order_index).all()
    current_index = next((i for i, l in enumerate(all_lessons) if l.id == lesson_id), 0)
    prev_lesson = all_lessons[current_index - 1] if current_index > 0 else None
    next_lesson = all_lessons[current_index + 1] if current_index < len(all_lessons) - 1 else None
    
    return render_template('lesson.html',
        lesson=lesson,
        content=content,
        content_formats=content_formats,
        lesson_progress=lesson_progress,
        audio_url=audio_url,
        quiz=quiz,
        difficulty=difficulty,
        prev_lesson=prev_lesson,
        next_lesson=next_lesson,
        voice_commands=get_voice_commands()
    )


@app.route('/lesson/<int:lesson_id>/complete', methods=['POST'])
@login_required
def complete_lesson(lesson_id):
    """Mark a lesson as completed"""
    lesson_progress = LessonProgress.query.filter_by(
        student_id=current_user.id,
        lesson_id=lesson_id
    ).first()
    
    if lesson_progress:
        lesson_progress.status = 'completed'
        lesson_progress.progress_percent = 100
        lesson_progress.completed_at = datetime.utcnow()
        
        current_user.total_lessons_completed += 1
        
        db.session.commit()
        flash('Lesson completed! Great job!', 'success')
    
    lesson = Lesson.query.get(lesson_id)
    quiz = Quiz.query.filter_by(
        lesson_id=lesson_id, 
        difficulty=current_user.current_difficulty
    ).first()
    
    if quiz:
        return redirect(url_for('take_quiz', quiz_id=quiz.id))
    
    return redirect(url_for('dashboard'))


@app.route('/quiz/<int:quiz_id>')
@login_required
def take_quiz(quiz_id):
    """Take a quiz"""
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = QuizQuestion.query.filter_by(quiz_id=quiz_id).order_by(QuizQuestion.order_index).all()
    
    if not questions:
        flash('This quiz has no questions yet.', 'warning')
        return redirect(url_for('dashboard'))
    
    activity = ActivityLog(
        student_id=current_user.id,
        activity_type='quiz_start',
        details=f'Started quiz for lesson {quiz.lesson_id}'
    )
    db.session.add(activity)
    db.session.commit()
    
    session['quiz_start_time'] = datetime.utcnow().timestamp()
    
    return render_template('quiz.html',
        quiz=quiz,
        questions=questions,
        lesson=quiz.lesson,
        total_questions=len(questions),
        voice_commands=get_voice_commands()
    )


@app.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    """Submit quiz answers"""
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = QuizQuestion.query.filter_by(quiz_id=quiz_id).all()
    
    correct_count = 0
    answers = {}
    
    for question in questions:
        answer = request.form.get(f'question_{question.id}')
        answers[question.id] = answer
        
        if answer and answer.upper() == question.correct_answer.upper():
            correct_count += 1
    
    total = len(questions)
    score = (correct_count / total * 100) if total > 0 else 0
    
    start_time = session.get('quiz_start_time', datetime.utcnow().timestamp())
    time_spent = int(datetime.utcnow().timestamp() - start_time)
    
    quiz_result = QuizResult(
        student_id=current_user.id,
        quiz_id=quiz_id,
        score=score,
        total_questions=total,
        correct_answers=correct_count,
        time_spent=time_spent,
        difficulty_at_time=current_user.current_difficulty
    )
    db.session.add(quiz_result)
    
    current_user.total_quizzes_taken += 1
    
    all_results = QuizResult.query.filter_by(student_id=current_user.id).all()
    all_scores = [r.score for r in all_results] + [score]
    current_user.average_score = sum(all_scores) / len(all_scores)
    
    recent_results = QuizResult.query.filter_by(
        student_id=current_user.id
    ).order_by(QuizResult.completed_at.desc()).limit(5).all()
    
    should_adjust, new_difficulty, reason = adaptive_engine.should_adjust_difficulty(
        current_user, recent_results + [quiz_result]
    )
    
    difficulty_changed = False
    if should_adjust and new_difficulty != current_user.current_difficulty:
        old_difficulty = current_user.current_difficulty
        current_user.current_difficulty = new_difficulty
        difficulty_changed = True
    
    db.session.commit()
    
    session.pop('quiz_start_time', None)
    
    return render_template('quiz_result.html',
        quiz=quiz,
        questions=questions,
        answers=answers,
        score=score,
        correct_count=correct_count,
        total=total,
        time_spent=time_spent,
        difficulty_changed=difficulty_changed,
        new_difficulty=new_difficulty if difficulty_changed else None,
        message=get_score_message(score)
    )


@app.route('/progress')
@login_required
def progress():
    """View progress and analytics"""
    quiz_results = QuizResult.query.filter_by(
        student_id=current_user.id
    ).order_by(QuizResult.completed_at.desc()).all()
    
    lessons = Lesson.query.filter_by(is_active=True).all()
    lesson_progress_list = LessonProgress.query.filter_by(student_id=current_user.id).all()
    activity_logs = ActivityLog.query.filter_by(student_id=current_user.id).all()
    
    quiz_stats = progress_tracker.calculate_quiz_statistics(quiz_results)
    
    lesson_stats = progress_tracker.calculate_lesson_progress(
        current_user, lessons, lesson_progress_list
    )
    
    weekly_report = progress_tracker.get_weekly_report(
        current_user, quiz_results, lesson_progress_list, activity_logs
    )
    
    chart_data = progress_tracker.get_progress_chart_data(quiz_results)
    
    score_chart = None
    if chart_data['line_chart']['scores']:
        valid_scores = [s for s in chart_data['line_chart']['scores'] if s is not None]
        if valid_scores:
            score_chart = create_score_line_chart(
                chart_data['line_chart']['labels'],
                chart_data['line_chart']['scores']
            )
    
    difficulty_chart = None
    if chart_data['difficulty_distribution']['values']:
        difficulty_chart = create_difficulty_pie_chart(
            chart_data['difficulty_distribution']['labels'],
            chart_data['difficulty_distribution']['values']
        )
    
    activity_chart = None
    if weekly_report['daily_activity']:
        activity_chart = create_weekly_activity_chart(
            list(weekly_report['daily_activity'].keys()),
            list(weekly_report['daily_activity'].values())
        )
    
    performance = adaptive_engine.analyze_performance(current_user.id, quiz_results)
    recommendations = adaptive_engine.get_personalized_recommendations(current_user, performance)
    
    return render_template('progress.html',
        student=current_user,
        quiz_stats=quiz_stats,
        lesson_stats=lesson_stats,
        weekly_report=weekly_report,
        performance=performance,
        recommendations=recommendations,
        score_chart=score_chart,
        difficulty_chart=difficulty_chart,
        activity_chart=activity_chart
    )


@app.route('/settings')
@login_required
def settings():
    """User settings page"""
    return render_template('settings.html',
        student=current_user,
        accessibility_options=get_accessibility_options()
    )


@app.route('/settings/update', methods=['POST'])
@login_required
def update_settings():
    """Update user settings"""
    current_user.audio_enabled = request.form.get('audio_enabled') == 'on'
    current_user.sign_language_enabled = request.form.get('sign_language_enabled') == 'on'
    current_user.emotion_detection_enabled = request.form.get('emotion_detection_enabled') == 'on'
    current_user.high_contrast = request.form.get('high_contrast') == 'on'
    current_user.reduce_motion = request.form.get('reduce_motion') == 'on'
    
    font_size = request.form.get('font_size', '18')
    try:
        current_user.font_size = int(font_size)
    except ValueError:
        current_user.font_size = 18
    
    db.session.commit()
    flash('Settings updated successfully!', 'success')
    return redirect(url_for('settings'))


@app.route('/api/tts', methods=['POST'])
@login_required
def api_tts():
    """Generate TTS audio for text"""
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    audio_url = text_to_speech(text)
    
    if audio_url:
        return jsonify({'audio_url': audio_url})
    return jsonify({'error': 'Failed to generate audio'}), 500


@app.route('/api/emotion', methods=['POST'])
@login_required
def api_emotion():
    """Log detected emotion"""
    data = request.get_json()
    emotion = data.get('emotion', 'neutral')
    confidence = data.get('confidence', 0.5)
    context = data.get('context', 'lesson')
    
    result = emotion_detector.process_emotion(emotion, confidence, current_user.id)
    
    emotion_log = EmotionLog(
        student_id=current_user.id,
        emotion=emotion,
        confidence=confidence,
        context=context
    )
    db.session.add(emotion_log)
    db.session.commit()
    
    return jsonify(result)


@app.route('/help')
def help_page():
    """Help and accessibility information"""
    return render_template('help.html',
        voice_commands=get_voice_commands(),
        gesture_mappings=sign_language_detector.get_gesture_mappings(),
        asl_alphabet=sign_language_detector.get_asl_alphabet(),
        accessibility_options=get_accessibility_options()
    )


@app.route('/sign-language')
@login_required
def sign_language_page():
    """Sign language detection page with webcam"""
    return render_template('sign_language.html',
        gesture_mappings=sign_language_detector.get_gesture_mappings(),
        asl_alphabet=sign_language_detector.get_asl_alphabet()
    )


@app.route('/api/sign-language', methods=['POST'])
@login_required
def api_sign_language():
    """Process sign language detection from webcam image"""
    data = request.get_json()
    image_data = data.get('image', '')
    
    if not image_data:
        return jsonify({'error': 'No image provided'}), 400
    
    detection_result = sign_language_detector.detect_gesture(image_data)
    
    if detection_result['gesture'] != 'none':
        activity_log = ActivityLog(
            student_id=current_user.id,
            activity_type='sign_language_gesture',
            details=f"Detected gesture: {detection_result['gesture']}"
        )
        db.session.add(activity_log)
        db.session.commit()
    
    return jsonify({
        'success': True,
        'gesture': detection_result['gesture'],
        'action': detection_result['action'],
        'confidence': detection_result.get('confidence', 0),
        'description': detection_result['description']
    })


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return render_template('error.html', 
        error_code=404, 
        error_message='Page not found'
    ), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return render_template('error.html',
        error_code=500,
        error_message='Something went wrong. Please try again.'
    ), 500


@app.route('/games')
@login_required
def games():
    """Games hub - accessible games for learning"""
    can_play = current_user.can_access_games()
    quizzes_completed = current_user.get_completed_quizzes_count()
    quizzes_needed = max(0, 2 - quizzes_completed)
    
    all_games = Game.query.filter_by(is_active=True).all()
    
    game_sessions = GameSession.query.filter_by(student_id=current_user.id).all()
    session_map = {}
    for gs in game_sessions:
        if gs.game_id not in session_map:
            session_map[gs.game_id] = []
        session_map[gs.game_id].append(gs)
    
    rewards = GameReward.query.filter_by(student_id=current_user.id).order_by(GameReward.earned_at.desc()).limit(10).all()
    
    return render_template('games.html',
        games=all_games,
        can_play=can_play,
        quizzes_needed=quizzes_needed,
        quizzes_completed=quizzes_completed,
        session_map=session_map,
        rewards=rewards,
        total_coins=current_user.total_coins,
        total_stars=current_user.total_stars
    )


@app.route('/games/<int:game_id>')
@login_required
def play_game(game_id):
    """Play a specific game"""
    if not current_user.can_access_games():
        flash('Complete 2 quizzes to unlock games!', 'warning')
        return redirect(url_for('games'))
    
    game = Game.query.get_or_404(game_id)
    
    last_session = GameSession.query.filter_by(
        student_id=current_user.id,
        game_id=game_id
    ).order_by(GameSession.started_at.desc()).first()
    
    current_difficulty = 1
    if last_session and last_session.completed:
        current_difficulty = min(last_session.difficulty_level + 1, game.max_difficulty)
    
    game_data = get_game_content(game.game_type, current_difficulty)
    
    return render_template('play_game.html',
        game=game,
        difficulty=current_difficulty,
        game_data=game_data
    )


@app.route('/games/<int:game_id>/complete', methods=['POST'])
@login_required
def complete_game(game_id):
    """Complete a game session"""
    game = Game.query.get_or_404(game_id)
    data = request.get_json()
    
    score = data.get('score', 0)
    moves = data.get('moves', 0)
    time_spent = data.get('time_spent', 0)
    difficulty = data.get('difficulty', 1)
    
    coins_earned = game.base_coins * difficulty
    stars_earned = game.base_stars if score >= 80 else 0
    
    game_session = GameSession(
        student_id=current_user.id,
        game_id=game_id,
        difficulty_level=difficulty,
        score=score,
        moves_made=moves,
        time_spent=time_spent,
        completed=True,
        coins_earned=coins_earned,
        stars_earned=stars_earned,
        completed_at=datetime.utcnow()
    )
    db.session.add(game_session)
    
    current_user.total_coins += coins_earned
    current_user.total_stars += stars_earned
    
    if score >= 90 and difficulty == game.max_difficulty:
        existing_reward = GameReward.query.filter_by(
            student_id=current_user.id,
            reward_name=f'{game.name} Master'
        ).first()
        if not existing_reward:
            reward = GameReward(
                student_id=current_user.id,
                reward_type='badge',
                reward_name=f'{game.name} Master',
                reward_icon='award',
                description=f'Mastered {game.name} at maximum difficulty!'
            )
            db.session.add(reward)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'coins_earned': coins_earned,
        'stars_earned': stars_earned,
        'total_coins': current_user.total_coins,
        'total_stars': current_user.total_stars,
        'message': 'Great job! Keep it up!'
    })


def get_game_content(game_type, difficulty):
    """Get game content based on type and difficulty"""
    if game_type == 'matching':
        pairs = [
            ('Variable', 'A named storage location'),
            ('Function', 'A reusable block of code'),
            ('Loop', 'Repeats code multiple times'),
            ('Array', 'An ordered collection of items'),
            ('String', 'Text data in quotes'),
            ('Boolean', 'True or False value'),
            ('Integer', 'A whole number'),
            ('If statement', 'Makes decisions in code'),
        ]
        num_pairs = min(3 + difficulty, len(pairs))
        return {'pairs': pairs[:num_pairs]}
    
    elif game_type == 'sequence':
        sequences = [
            ['Start', 'Get input', 'Process data', 'Show output', 'End'],
            ['Define function', 'Set parameters', 'Write body', 'Return result', 'Call function'],
            ['Create variable', 'Assign value', 'Use in calculation', 'Print result'],
        ]
        return {'sequence': sequences[min(difficulty - 1, len(sequences) - 1)]}
    
    elif game_type == 'memory':
        cards = ['Python', 'JavaScript', 'HTML', 'CSS', 'SQL', 'Git', 'API', 'Debug']
        num_cards = min(4 + difficulty * 2, len(cards))
        return {'cards': cards[:num_cards]}
    
    elif game_type == 'dragdrop':
        problems = [
            {
                'question': 'Complete the print statement:',
                'template': '_____("Hello World")',
                'answer': 'print',
                'options': ['print', 'say', 'write', 'show']
            },
            {
                'question': 'Create a variable:',
                'template': 'name _____ "Alice"',
                'answer': '=',
                'options': ['=', '==', ':', '->']
            },
        ]
        return {'problem': problems[min(difficulty - 1, len(problems) - 1)]}
    
    return {}


@app.route('/attendance')
@login_required
def attendance():
    """Student attendance page"""
    today = date.today()
    
    today_record = AttendanceRecord.query.filter_by(
        student_id=current_user.id,
        date=today
    ).first()
    
    week_start = today - timedelta(days=today.weekday())
    week_records = AttendanceRecord.query.filter(
        AttendanceRecord.student_id == current_user.id,
        AttendanceRecord.date >= week_start,
        AttendanceRecord.date <= today
    ).all()
    
    month_start = today.replace(day=1)
    month_records = AttendanceRecord.query.filter(
        AttendanceRecord.student_id == current_user.id,
        AttendanceRecord.date >= month_start,
        AttendanceRecord.date <= today
    ).all()
    
    weekly_present = sum(1 for r in week_records if r.status == 'present')
    monthly_present = sum(1 for r in month_records if r.status == 'present')
    
    return render_template('attendance.html',
        today=today,
        today_record=today_record,
        week_records=week_records,
        month_records=month_records,
        weekly_present=weekly_present,
        weekly_total=len(week_records),
        monthly_present=monthly_present,
        monthly_total=len(month_records)
    )


@app.route('/attendance/mark', methods=['POST'])
@login_required
def mark_attendance():
    """Mark attendance for today"""
    today = date.today()
    
    existing = AttendanceRecord.query.filter_by(
        student_id=current_user.id,
        date=today
    ).first()
    
    if existing:
        flash('Attendance already marked for today!', 'info')
        return redirect(url_for('attendance'))
    
    record = AttendanceRecord(
        student_id=current_user.id,
        date=today,
        status='present',
        check_in_time=datetime.utcnow(),
        marked_by='self'
    )
    db.session.add(record)
    db.session.commit()
    
    flash('Attendance marked successfully! Great to see you today!', 'success')
    return redirect(url_for('attendance'))


@app.route('/attendance/voice', methods=['POST'])
@login_required
def voice_attendance():
    """Mark attendance via voice command"""
    data = request.get_json()
    confirmed = data.get('confirmed', False)
    
    if confirmed:
        today = date.today()
        existing = AttendanceRecord.query.filter_by(
            student_id=current_user.id,
            date=today
        ).first()
        
        if not existing:
            record = AttendanceRecord(
                student_id=current_user.id,
                date=today,
                status='present',
                check_in_time=datetime.utcnow(),
                marked_by='voice'
            )
            db.session.add(record)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Attendance marked successfully!'})
        return jsonify({'success': False, 'message': 'Already marked today'})
    
    return jsonify({'success': False, 'message': 'Not confirmed'})


@app.route('/teacher/login', methods=['GET', 'POST'])
def teacher_login_page():
    """Teacher login page"""
    if request.method == 'GET':
        return render_template('teacher_login.html')
    return redirect(url_for('teacher_login'))


@app.route('/teacher/authenticate', methods=['POST'])
def teacher_login():
    """Handle teacher login"""
    teacher_id = request.form.get('teacher_id', '').strip()
    password = request.form.get('password', '')
    
    if not teacher_id:
        flash('Please enter your Teacher ID.', 'error')
        return redirect(url_for('teacher_login_page'))
    
    teacher = Teacher.query.filter_by(teacher_id=teacher_id).first()
    
    if not teacher:
        flash('Teacher not found.', 'error')
        return redirect(url_for('teacher_login_page'))
    
    if teacher.password_hash and not teacher.check_password(password):
        flash('Invalid password.', 'error')
        return redirect(url_for('teacher_login_page'))
    
    session['teacher_id'] = teacher.id
    flash(f'Welcome, {teacher.name}!', 'success')
    return redirect(url_for('teacher_dashboard'))


@app.route('/teacher/logout')
def teacher_logout():
    """Teacher logout"""
    session.pop('teacher_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/teacher/dashboard')
def teacher_dashboard():
    """Teacher dashboard - view all students"""
    teacher_id = session.get('teacher_id')
    if not teacher_id:
        return redirect(url_for('teacher_login_page'))
    
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        session.pop('teacher_id', None)
        return redirect(url_for('teacher_login_page'))
    
    students = Student.query.order_by(Student.name).all()
    total_students = len(students)
    
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    
    active_today = Student.query.filter(
        func.date(Student.last_active) == today
    ).count()
    
    total_quizzes_completed = QuizResult.query.count()
    
    all_scores = db.session.query(func.avg(QuizResult.score)).scalar()
    avg_class_score = all_scores or 0
    
    students_data = []
    for student in students:
        attendance = AttendanceRecord.query.filter(
            AttendanceRecord.student_id == student.id,
            AttendanceRecord.date >= week_start
        ).all()
        attendance_rate = len([a for a in attendance if a.status == 'present']) / max(len(attendance), 1) * 100
        
        students_data.append({
            'student': student,
            'attendance_rate': attendance_rate
        })
    
    struggling_students = [s for s in students if s.average_score < 60 and s.total_quizzes_taken > 0][:5]
    top_students = sorted([s for s in students if s.total_quizzes_taken > 0], 
                         key=lambda x: x.average_score, reverse=True)[:5]
    
    recent_activities = ActivityLog.query.order_by(
        ActivityLog.created_at.desc()
    ).limit(10).all()
    
    for activity in recent_activities:
        activity.student = Student.query.get(activity.student_id)
    
    return render_template('teacher_dashboard.html',
        teacher=teacher,
        students_data=students_data,
        total_students=total_students,
        active_today=active_today,
        total_quizzes_completed=total_quizzes_completed,
        avg_class_score=avg_class_score,
        struggling_students=struggling_students,
        top_students=top_students,
        recent_activities=recent_activities
    )


@app.route('/teacher/attendance')
def teacher_attendance_page():
    """Teacher attendance management page"""
    teacher_id = session.get('teacher_id')
    if not teacher_id:
        return redirect(url_for('teacher_login_page'))
    
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        session.pop('teacher_id', None)
        return redirect(url_for('teacher_login_page'))
    
    students = Student.query.order_by(Student.name).all()
    today = date.today()
    
    attendance_records = {}
    for student in students:
        record = AttendanceRecord.query.filter_by(
            student_id=student.id,
            date=today
        ).first()
        if record:
            attendance_records[student.id] = record.status
    
    return render_template('teacher_attendance.html',
        teacher=teacher,
        students=students,
        today=today,
        attendance_records=attendance_records
    )


@app.route('/teacher/attendance/mark', methods=['POST'])
def teacher_mark_attendance():
    """Mark attendance for students"""
    teacher_id = session.get('teacher_id')
    if not teacher_id:
        return redirect(url_for('teacher_login_page'))
    
    students = Student.query.all()
    today = date.today()
    
    for student in students:
        status = request.form.get(f'status_{student.id}', 'present')
        notes = request.form.get(f'notes_{student.id}', '').strip()
        
        existing = AttendanceRecord.query.filter_by(
            student_id=student.id,
            date=today
        ).first()
        
        if existing:
            existing.status = status
            existing.notes = notes
            existing.marked_by = 'teacher'
        else:
            record = AttendanceRecord(
                student_id=student.id,
                date=today,
                status=status,
                check_in_time=datetime.utcnow() if status == 'present' else None,
                marked_by='teacher',
                notes=notes
            )
            db.session.add(record)
    
    db.session.commit()
    flash('Attendance saved successfully!', 'success')
    return redirect(url_for('teacher_attendance_page'))


@app.route('/parent/login', methods=['GET', 'POST'])
def parent_login():
    """Parent login page"""
    if request.method == 'POST':
        parent_id = request.form.get('parent_id', '').strip()
        access_token = request.form.get('access_token', '').strip()
        
        parent = None
        if access_token:
            parent = ParentAccount.query.filter_by(access_token=access_token).first()
        elif parent_id:
            parent = ParentAccount.query.filter_by(parent_id=parent_id).first()
        
        if parent:
            session['parent_id'] = parent.id
            parent.last_login = datetime.utcnow()
            db.session.commit()
            flash(f'Welcome, {parent.name}!', 'success')
            return redirect(url_for('parent_dashboard'))
        
        flash('Invalid credentials. Please try again.', 'error')
    
    return render_template('parent_login.html')


@app.route('/parent/logout')
def parent_logout():
    """Parent logout"""
    session.pop('parent_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('parent_login'))


@app.route('/parent/dashboard')
def parent_dashboard():
    """Parent dashboard - view child's progress"""
    parent_id = session.get('parent_id')
    if not parent_id:
        return redirect(url_for('parent_login'))
    
    parent = ParentAccount.query.get(parent_id)
    if not parent:
        session.pop('parent_id', None)
        return redirect(url_for('parent_login'))
    
    links = ParentStudentLink.query.filter_by(parent_id=parent_id).all()
    students_data = []
    
    for link in links:
        student = link.student
        quiz_results = QuizResult.query.filter_by(student_id=student.id).order_by(QuizResult.completed_at.desc()).limit(10).all()
        lesson_progress = LessonProgress.query.filter_by(student_id=student.id).all()
        
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        attendance = AttendanceRecord.query.filter(
            AttendanceRecord.student_id == student.id,
            AttendanceRecord.date >= week_start
        ).all()
        
        focus_sessions = FocusSession.query.filter_by(student_id=student.id).order_by(FocusSession.started_at.desc()).limit(20).all()
        avg_focus = sum(fs.focus_score for fs in focus_sessions) / len(focus_sessions) if focus_sessions else 0
        
        reading_records = ReadingProgress.query.filter_by(student_id=student.id).order_by(ReadingProgress.recorded_at.desc()).limit(10).all()
        avg_wpm = sum(r.words_per_minute for r in reading_records) / len(reading_records) if reading_records else 0
        
        completed_lessons = sum(1 for lp in lesson_progress if lp.status == 'completed')
        total_lessons = Lesson.query.filter_by(is_active=True).count()
        
        strengths = []
        improvements = []
        if quiz_results:
            scores_by_difficulty = {}
            for qr in quiz_results:
                if qr.difficulty_at_time not in scores_by_difficulty:
                    scores_by_difficulty[qr.difficulty_at_time] = []
                scores_by_difficulty[qr.difficulty_at_time].append(qr.score)
            
            for diff, scores in scores_by_difficulty.items():
                avg = sum(scores) / len(scores)
                if avg >= 80:
                    strengths.append(f'{diff.title()} level quizzes')
                elif avg < 60:
                    improvements.append(f'{diff.title()} level content')
        
        attendance_present = len([a for a in attendance if a.status == 'present'])
        attendance_absent = len([a for a in attendance if a.status == 'absent'])
        attendance_late = len([a for a in attendance if a.status == 'late'])
        
        weekly_lessons = LessonProgress.query.filter(
            LessonProgress.student_id == student.id,
            LessonProgress.last_accessed >= week_start
        ).count()
        
        weekly_quizzes = QuizResult.query.filter(
            QuizResult.student_id == student.id,
            QuizResult.completed_at >= week_start
        ).count()
        
        weekly_games = GameSession.query.filter(
            GameSession.student_id == student.id,
            GameSession.started_at >= week_start
        ).count()
        
        this_week_scores = [qr.score for qr in quiz_results if qr.completed_at.date() >= week_start]
        last_week_start = week_start - timedelta(days=7)
        last_week_scores = QuizResult.query.filter(
            QuizResult.student_id == student.id,
            QuizResult.completed_at >= last_week_start,
            QuizResult.completed_at < week_start
        ).all()
        last_week_avg = sum(qr.score for qr in last_week_scores) / len(last_week_scores) if last_week_scores else 0
        this_week_avg = sum(this_week_scores) / len(this_week_scores) if this_week_scores else 0
        score_trend = this_week_avg - last_week_avg
        
        recent_sessions = FocusSession.query.filter_by(student_id=student.id).order_by(FocusSession.started_at.desc()).limit(10).all()
        avg_session_time = sum(fs.duration_seconds for fs in recent_sessions) / len(recent_sessions) / 60 if recent_sessions else 0
        
        badges = GameReward.query.filter_by(student_id=student.id).limit(5).all()
        
        students_data.append({
            'student': student,
            'quiz_results': quiz_results,
            'lesson_progress': lesson_progress,
            'completed_lessons': completed_lessons,
            'total_lessons': total_lessons,
            'attendance': attendance,
            'attendance_rate': len([a for a in attendance if a.status == 'present']) / max(len(attendance), 1) * 100,
            'attendance_present': attendance_present,
            'attendance_absent': attendance_absent,
            'attendance_late': attendance_late,
            'avg_focus': avg_focus,
            'avg_wpm': avg_wpm,
            'strengths': strengths,
            'improvements': improvements,
            'games_unlocked': student.can_access_games(),
            'total_coins': student.total_coins,
            'total_stars': student.total_stars,
            'weekly_lessons': weekly_lessons,
            'weekly_quizzes': weekly_quizzes,
            'weekly_games': weekly_games,
            'score_trend': score_trend,
            'avg_session_time': round(avg_session_time, 1),
            'badges': [{'name': b.reward_name, 'icon': b.reward_icon} for b in badges]
        })
    
    return render_template('parent_dashboard.html',
        parent=parent,
        students_data=students_data
    )


# ============================================================================
# AI Agent API Routes
# ============================================================================

from modules.adaptive_agent import adaptive_agent
from modules.accessibility_agent import accessibility_agent
from modules.assistant_agent import assistant_agent


@app.route('/api/emotion/detect', methods=['POST'])
@login_required
def api_emotion_detect():
    """Receive emotion detection data and trigger adaptive responses."""
    try:
        data = request.get_json()
        emotion = data.get('emotion', 'neutral')
        confidence = data.get('confidence', 0)
        history = data.get('history', {})
        
        emotion_log = EmotionLog(
            student_id=current_user.id,
            emotion=emotion,
            confidence=confidence,
            context='learning'
        )
        db.session.add(emotion_log)
        db.session.commit()
        
        action = {'type': 'continue', 'message': 'Keep up the good work!'}
        
        if emotion == 'frustrated' and confidence > 0.6:
            result = adaptive_agent.adjust_lesson_difficulty(current_user.id, db.session)
            if result.get('action_taken') == 'downgrade':
                action = {'type': 'lower_difficulty', 'message': result.get('message', 'Difficulty adjusted')}
            else:
                action = {'type': 'enable_hints', 'message': 'Hints enabled to help you'}
        
        elif emotion == 'confused' and confidence > 0.5:
            action = {'type': 'enable_hints', 'message': 'Hints enabled to help you understand better'}
        
        elif emotion == 'bored' and confidence > 0.5:
            action = {'type': 'add_animations', 'message': 'Adding some interactive elements!'}
        
        elif emotion == 'happy':
            action = {'type': 'continue', 'message': 'Great to see you enjoying learning!'}
        
        logger.info(f"Emotion detected for student {current_user.id}: {emotion} -> action: {action['type']}")
        
        return jsonify({
            'success': True,
            'emotion': emotion,
            'action': action
        })
    except Exception as e:
        logger.error(f"Emotion detection error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/accessibility/settings', methods=['GET'])
@login_required
def api_get_accessibility_settings():
    """Get current accessibility settings for the user."""
    try:
        settings = accessibility_agent.get_current_settings(current_user.id, db.session)
        return jsonify({'success': True, 'settings': settings})
    except Exception as e:
        logger.error(f"Get accessibility settings error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/accessibility/settings', methods=['POST'])
@login_required
def api_update_accessibility_settings():
    """Update accessibility settings manually."""
    try:
        settings = request.get_json()
        result = accessibility_agent.update_manual_settings(current_user.id, settings, db.session)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Update accessibility settings error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/accessibility/track', methods=['POST'])
@login_required
def api_track_accessibility_events():
    """Track user behavior events for accessibility adaptation."""
    try:
        data = request.get_json()
        events = data.get('events', [])
        result = accessibility_agent.update_accessibility_preferences(
            current_user.id, events, db.session
        )
        return jsonify(result)
    except Exception as e:
        logger.error(f"Track accessibility events error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/accessibility/recommendations', methods=['GET'])
@login_required
def api_get_accessibility_recommendations():
    """Get AI-recommended accessibility settings."""
    try:
        result = accessibility_agent.get_recommended_settings(current_user.id, db.session)
        return jsonify({'success': True, **result})
    except Exception as e:
        logger.error(f"Get recommendations error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/adaptive/status', methods=['GET'])
@login_required
def api_get_adaptive_status():
    """Get current adaptive learning status for the user."""
    try:
        analysis = adaptive_agent.analyze_quiz_history(current_user.id, db.session)
        return jsonify({
            'success': True,
            'current_difficulty': current_user.current_difficulty,
            'analysis': analysis
        })
    except Exception as e:
        logger.error(f"Get adaptive status error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/adaptive/adjust', methods=['POST'])
@login_required
def api_trigger_adaptive_adjustment():
    """Manually trigger adaptive difficulty adjustment."""
    try:
        result = adaptive_agent.adjust_lesson_difficulty(current_user.id, db.session)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Adaptive adjustment error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/ai/toggle', methods=['POST'])
@login_required
def api_toggle_ai_mode():
    """Toggle AI mode on/off for the current user."""
    from models import UserPreferences
    try:
        data = request.get_json()
        enabled = data.get('enabled', True)
        
        prefs = UserPreferences.query.filter_by(student_id=current_user.id).first()
        if not prefs:
            prefs = UserPreferences(student_id=current_user.id)
            db.session.add(prefs)
        
        prefs.ai_mode_enabled = enabled
        db.session.commit()
        
        return jsonify({'success': True, 'ai_mode_enabled': enabled})
    except Exception as e:
        logger.error(f"Toggle AI mode error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/emotion/toggle', methods=['POST'])
@login_required
def api_toggle_emotion_monitor():
    """Toggle emotion monitoring on/off for the current user."""
    from models import UserPreferences
    try:
        data = request.get_json()
        enabled = data.get('enabled', False)
        
        prefs = UserPreferences.query.filter_by(student_id=current_user.id).first()
        if not prefs:
            prefs = UserPreferences(student_id=current_user.id)
            db.session.add(prefs)
        
        prefs.emotion_monitor_enabled = enabled
        db.session.commit()
        
        return jsonify({'success': True, 'emotion_monitor_enabled': enabled})
    except Exception as e:
        logger.error(f"Toggle emotion monitor error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/assistant/weekly-summary/<int:student_id>', methods=['GET'])
@login_required
def api_get_weekly_summary(student_id):
    """Get weekly summary for a student (for parent/teacher dashboard)."""
    try:
        result = assistant_agent.generate_weekly_summary(student_id, db.session)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Weekly summary error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/assistant/report/<int:student_id>', methods=['GET'])
@login_required
def api_get_student_report(student_id):
    """Get strengths/weaknesses report for a student."""
    try:
        result = assistant_agent.generate_strengths_weaknesses(student_id, db.session)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Student report error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/ai/preferences', methods=['GET'])
@login_required
def api_get_ai_preferences():
    """Get current AI preferences for the user."""
    from models import UserPreferences
    try:
        prefs = UserPreferences.query.filter_by(student_id=current_user.id).first()
        
        return jsonify({
            'success': True,
            'ai_mode_enabled': prefs.ai_mode_enabled if prefs else True,
            'emotion_monitor_enabled': prefs.emotion_monitor_enabled if prefs else False
        })
    except Exception as e:
        logger.error(f"Get AI preferences error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/lessons/<lesson_name>')
@login_required
def lesson_page(lesson_name):
    """Render individual lesson page with adaptive difficulty."""
    from modules.adaptive_agent import adaptive_agent
    from modules.progress_tracker import progress_tracker
    
    valid_lessons = [
        'programming_basics', 'data_structures', 'databases',
        'networking', 'operating_systems', 'oops',
        'algorithms', 'computer_architecture', 'software_engineering',
        'compiler_design', 'theory_of_computation', 'machine_learning'
    ]
    
    if lesson_name not in valid_lessons:
        flash('Lesson not found', 'error')
        return redirect(url_for('dashboard'))
    
    difficulty = request.args.get('difficulty')
    if not difficulty:
        difficulty = adaptive_agent.get_lesson_version(
            current_user.id, lesson_name, db.session
        )
    
    quiz = None
    lessons = Lesson.query.filter(
        Lesson.title.ilike(f'%{lesson_name.replace("_", " ")}%')
    ).first()
    
    if lessons:
        quiz = Quiz.query.filter_by(lesson_id=lessons.id).first()
    
    return render_template(
        f'lessons/{lesson_name}.html',
        lesson_name=lesson_name,
        difficulty=difficulty,
        student=current_user,
        quiz_id=quiz.id if quiz else None
    )


@app.route('/api/lesson/progress', methods=['POST'])
@login_required
def api_save_lesson_progress():
    """Save lesson progress for a student."""
    try:
        data = request.get_json()
        lesson_name = data.get('lesson_name')
        time_spent = data.get('time_spent', 0)
        completed = data.get('completed', False)
        
        lesson = Lesson.query.filter(
            Lesson.title.ilike(f'%{lesson_name.replace("_", " ")}%')
        ).first()
        
        if lesson:
            progress = LessonProgress.query.filter_by(
                student_id=current_user.id,
                lesson_id=lesson.id
            ).first()
            
            if not progress:
                progress = LessonProgress(
                    student_id=current_user.id,
                    lesson_id=lesson.id
                )
                db.session.add(progress)
            
            progress.time_spent = (progress.time_spent or 0) + time_spent
            progress.last_accessed = datetime.utcnow()
            
            if completed:
                progress.status = 'completed'
                progress.completed_at = datetime.utcnow()
                progress.progress_percent = 100
            else:
                progress.status = 'in_progress'
            
            db.session.commit()
            
            return jsonify({'success': True})
        
        return jsonify({'success': False, 'message': 'Lesson not found'}), 404
        
    except Exception as e:
        logger.error(f"Save lesson progress error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/tts', methods=['GET'])
@login_required
def api_text_to_speech():
    """Generate audio from text."""
    from modules.tts_engine import text_to_speech
    import re
    
    text = request.args.get('text', '')
    lang = request.args.get('lang', 'en')
    slow = request.args.get('slow', 'false').lower() == 'true'
    
    if not text:
        return jsonify({'success': False, 'message': 'No text provided'}), 400
    
    if len(text) > 5000:
        text = text[:5000]
    
    text = re.sub(r'[<>{}[\]\\]', '', text)
    
    valid_langs = ['en', 'es', 'fr', 'de', 'hi', 'zh-CN']
    if lang not in valid_langs:
        lang = 'en'
    
    try:
        audio_url = text_to_speech(text, lang=lang, slow=slow)
        
        if audio_url and audio_url.startswith('/static/audio/'):
            return jsonify({
                'success': True,
                'audio_url': audio_url
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to generate audio'
            }), 500
            
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return jsonify({'success': False, 'message': 'Audio generation failed'}), 500


@app.route('/api/stt', methods=['POST'])
@login_required
def api_speech_to_text():
    """Convert speech to text."""
    from modules.stt_engine import convert_speech_to_text
    import mimetypes
    
    if 'audio' not in request.files:
        return jsonify({
            'success': False,
            'text': '',
            'error': 'No audio file provided'
        }), 400
    
    audio_file = request.files['audio']
    
    if audio_file.content_length and audio_file.content_length > 10 * 1024 * 1024:
        return jsonify({
            'success': False,
            'text': '',
            'error': 'Audio file too large (max 10MB)'
        }), 400
    
    allowed_types = ['audio/wav', 'audio/webm', 'audio/ogg', 'audio/mp3', 'audio/mpeg', 'audio/x-wav']
    content_type = audio_file.content_type or ''
    if content_type and content_type not in allowed_types:
        return jsonify({
            'success': False,
            'text': '',
            'error': 'Invalid audio format'
        }), 400
    
    language = request.form.get('language', 'en-US')
    valid_languages = ['en-US', 'en-GB', 'es-ES', 'fr-FR', 'de-DE', 'hi-IN']
    if language not in valid_languages:
        language = 'en-US'
    
    try:
        result = convert_speech_to_text(audio_file, language)
        return jsonify({
            'success': result.get('success', False),
            'text': result.get('text', ''),
            'error': result.get('error')
        })
        
    except Exception as e:
        logger.error(f"STT error: {e}")
        return jsonify({
            'success': False,
            'text': '',
            'error': 'Speech recognition failed'
        }), 500


@app.route('/api/accessibility/settings', methods=['GET', 'POST'])
@login_required
def api_accessibility_settings():
    """Get or update accessibility settings."""
    from modules.accessibility_agent import accessibility_agent
    
    if request.method == 'GET':
        try:
            settings = accessibility_agent.get_current_settings(current_user.id, db.session)
            return jsonify({
                'success': True,
                'settings': settings
            })
        except Exception as e:
            logger.error(f"Get accessibility settings error: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500
    
    else:
        try:
            data = request.get_json()
            result = accessibility_agent.update_manual_settings(
                current_user.id, data, db.session
            )
            return jsonify(result)
        except Exception as e:
            logger.error(f"Update accessibility settings error: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/accessibility/update', methods=['POST'])
@login_required
def api_accessibility_update():
    """Update a single accessibility setting."""
    from modules.accessibility_agent import accessibility_agent
    
    try:
        data = request.get_json()
        result = accessibility_agent.update_manual_settings(
            current_user.id, data, db.session
        )
        return jsonify(result)
    except Exception as e:
        logger.error(f"Update accessibility error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/accessibility/track', methods=['POST'])
@login_required
def api_accessibility_track():
    """Track accessibility behavior events."""
    from modules.accessibility_agent import accessibility_agent
    
    try:
        data = request.get_json()
        events = data.get('events', [])
        
        result = accessibility_agent.update_accessibility_preferences(
            current_user.id, events, db.session
        )
        return jsonify(result)
    except Exception as e:
        logger.error(f"Track accessibility error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/accessibility/recommendations', methods=['GET'])
@login_required
def api_accessibility_recommendations():
    """Get AI-recommended accessibility settings."""
    from modules.accessibility_agent import accessibility_agent
    
    try:
        result = accessibility_agent.get_recommended_settings(current_user.id, db.session)
        return jsonify({
            'success': True,
            **result
        })
    except Exception as e:
        logger.error(f"Get accessibility recommendations error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/adaptive/difficulty', methods=['GET'])
@login_required
def api_get_adaptive_difficulty():
    """Get adaptive difficulty for a lesson."""
    from modules.adaptive_agent import adaptive_agent
    
    lesson_name = request.args.get('lesson', 'programming_basics')
    
    try:
        difficulty = adaptive_agent.get_lesson_version(
            current_user.id, lesson_name, db.session
        )
        next_lesson = adaptive_agent.get_next_lesson(current_user.id, db.session)
        
        return jsonify({
            'success': True,
            'difficulty': difficulty,
            'next_lesson': next_lesson
        })
    except Exception as e:
        logger.error(f"Get adaptive difficulty error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/adaptive/update-path', methods=['POST'])
@login_required
def api_update_learning_path():
    """Update learning path based on performance."""
    from modules.adaptive_agent import adaptive_agent
    
    try:
        data = request.get_json()
        result = adaptive_agent.update_learning_path(
            current_user.id, data, db.session
        )
        return jsonify(result)
    except Exception as e:
        logger.error(f"Update learning path error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/lessons', methods=['GET'])
@login_required
def api_get_lessons():
    """Get all available lessons for voice commands."""
    try:
        lessons = Lesson.query.filter_by(is_active=True).order_by(Lesson.order_index).all()
        lessons_data = [{
            'id': lesson.id,
            'title': lesson.title,
            'description': lesson.description,
            'subject': lesson.subject,
            'category': lesson.category,
            'estimated_time': lesson.estimated_time
        } for lesson in lessons]
        
        return jsonify({
            'success': True,
            'lessons': lessons_data
        })
    except Exception as e:
        logger.error(f"Get lessons API error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/quiz/<int:quiz_id>/questions', methods=['GET'])
@login_required
def api_get_quiz_questions(quiz_id):
    """Get quiz questions for voice reading."""
    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        questions = QuizQuestion.query.filter_by(quiz_id=quiz_id).order_by(QuizQuestion.order_index).all()
        
        questions_data = [{
            'id': q.id,
            'question_text': q.question_text,
            'option_a': q.option_a,
            'option_b': q.option_b,
            'option_c': q.option_c,
            'option_d': q.option_d,
            'order_index': q.order_index
        } for q in questions]
        
        return jsonify({
            'success': True,
            'quiz_id': quiz_id,
            'lesson_id': quiz.lesson_id,
            'questions': questions_data
        })
    except Exception as e:
        logger.error(f"Get quiz questions API error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
