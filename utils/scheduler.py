"""
Scheduler Utility
Handles scheduled tasks like weekly report generation.
Uses a simple cron-like approach for Replit environment.
"""
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Callable, Dict, Any, List

logger = logging.getLogger(__name__)


class TaskScheduler:
    """Simple task scheduler for running periodic jobs."""
    
    def __init__(self):
        self.tasks: Dict[str, Dict] = {}
        self.running = False
        self.thread = None
    
    def add_task(self, name: str, func: Callable, interval_seconds: int, run_immediately: bool = False):
        """Add a scheduled task."""
        self.tasks[name] = {
            'func': func,
            'interval': interval_seconds,
            'last_run': None if run_immediately else datetime.utcnow(),
            'next_run': datetime.utcnow() if run_immediately else datetime.utcnow() + timedelta(seconds=interval_seconds)
        }
        logger.info(f"Scheduled task '{name}' every {interval_seconds} seconds")
    
    def remove_task(self, name: str):
        """Remove a scheduled task."""
        if name in self.tasks:
            del self.tasks[name]
            logger.info(f"Removed task '{name}'")
    
    def start(self):
        """Start the scheduler in a background thread."""
        if self.running:
            logger.warning("Scheduler already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info("Scheduler started")
    
    def stop(self):
        """Stop the scheduler."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Scheduler stopped")
    
    def _run_loop(self):
        """Main scheduler loop."""
        while self.running:
            now = datetime.utcnow()
            
            for name, task in list(self.tasks.items()):
                if now >= task['next_run']:
                    try:
                        logger.info(f"Running scheduled task: {name}")
                        task['func']()
                        task['last_run'] = now
                        task['next_run'] = now + timedelta(seconds=task['interval'])
                    except Exception as e:
                        logger.error(f"Error in scheduled task '{name}': {e}")
            
            time.sleep(60)
    
    def run_task_now(self, name: str) -> bool:
        """Manually run a task immediately."""
        if name not in self.tasks:
            return False
        
        try:
            self.tasks[name]['func']()
            self.tasks[name]['last_run'] = datetime.utcnow()
            return True
        except Exception as e:
            logger.error(f"Error running task '{name}': {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status."""
        return {
            'running': self.running,
            'tasks': {
                name: {
                    'interval_seconds': task['interval'],
                    'last_run': task['last_run'].isoformat() if task['last_run'] else None,
                    'next_run': task['next_run'].isoformat()
                }
                for name, task in self.tasks.items()
            }
        }


scheduler = TaskScheduler()


def generate_weekly_reports():
    """Generate weekly reports for all students with parent links."""
    from app import app, db
    from models import Student, ParentStudentLink
    from modules.assistant_agent import assistant_agent
    
    with app.app_context():
        try:
            links = ParentStudentLink.query.all()
            student_ids = set(link.student_id for link in links)
            
            for student_id in student_ids:
                try:
                    summary = assistant_agent.generate_weekly_summary(student_id, db.session)
                    if summary.get('success'):
                        logger.info(f"Generated weekly report for student {student_id}")
                except Exception as e:
                    logger.error(f"Failed to generate report for student {student_id}: {e}")
            
            logger.info(f"Completed weekly reports for {len(student_ids)} students")
        except Exception as e:
            logger.error(f"Weekly report generation failed: {e}")


def cleanup_old_emotion_logs():
    """Clean up emotion logs older than 30 days."""
    from app import app, db
    from models import EmotionLog
    
    with app.app_context():
        try:
            cutoff = datetime.utcnow() - timedelta(days=30)
            deleted = EmotionLog.query.filter(EmotionLog.recorded_at < cutoff).delete()
            db.session.commit()
            logger.info(f"Cleaned up {deleted} old emotion logs")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Emotion log cleanup failed: {e}")


def init_scheduler():
    """Initialize the scheduler with default tasks."""
    SECONDS_PER_WEEK = 7 * 24 * 60 * 60
    SECONDS_PER_DAY = 24 * 60 * 60
    
    scheduler.add_task(
        'weekly_reports',
        generate_weekly_reports,
        SECONDS_PER_WEEK,
        run_immediately=False
    )
    
    scheduler.add_task(
        'cleanup_emotion_logs',
        cleanup_old_emotion_logs,
        SECONDS_PER_DAY,
        run_immediately=False
    )
    
    scheduler.start()
    logger.info("Scheduler initialized with default tasks")


def manual_generate_report(student_id: int) -> Dict[str, Any]:
    """Manually generate a report for a specific student."""
    from app import db
    from modules.assistant_agent import assistant_agent
    
    return assistant_agent.generate_weekly_summary(student_id, db.session)
