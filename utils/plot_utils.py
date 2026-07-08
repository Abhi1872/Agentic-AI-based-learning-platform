"""
Plot utilities for generating progress charts
"""
import io
import base64
import logging
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

plt.style.use('seaborn-v0_8-whitegrid')


def create_score_line_chart(dates, scores, title="Quiz Scores Over Time"):
    """
    Create a line chart showing score progression
    
    Args:
        dates: List of date strings (YYYY-MM-DD)
        scores: List of scores (can contain None for missing data)
        title: Chart title
    
    Returns:
        str: Base64 encoded PNG image
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
        
        valid_dates = []
        valid_scores = []
        for d, s in zip(dates, scores):
            if s is not None:
                try:
                    valid_dates.append(datetime.strptime(d, '%b %d') if ' ' in d else datetime.strptime(d, '%Y-%m-%d'))
                    valid_scores.append(s)
                except:
                    pass
        
        if valid_dates and valid_scores:
            ax.plot(range(len(valid_scores)), valid_scores, 
                   marker='o', linewidth=2, markersize=8,
                   color='#4F46E5', markerfacecolor='#818CF8')
            
            ax.fill_between(range(len(valid_scores)), valid_scores, 
                          alpha=0.2, color='#4F46E5')
            
            ax.set_xticks(range(len(valid_scores)))
            ax.set_xticklabels([d.strftime('%b %d') if hasattr(d, 'strftime') else str(d) 
                               for d in valid_dates], rotation=45, ha='right', fontsize=12)
        
        ax.set_ylim(0, 105)
        ax.set_ylabel('Score (%)', fontsize=14, fontweight='bold')
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        ax.axhline(y=80, color='#10B981', linestyle='--', alpha=0.5, label='Target (80%)')
        ax.axhline(y=60, color='#F59E0B', linestyle='--', alpha=0.5, label='Passing (60%)')
        
        ax.legend(loc='lower right', fontsize=11)
        
        ax.tick_params(axis='both', which='major', labelsize=12)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        plt.close(fig)
        
        return image_base64
        
    except Exception as e:
        logger.error(f"Error creating line chart: {e}")
        plt.close('all')
        return None


def create_difficulty_pie_chart(labels, values, title="Quizzes by Difficulty"):
    """
    Create a pie chart showing difficulty distribution
    
    Args:
        labels: List of difficulty labels
        values: List of counts
        title: Chart title
    
    Returns:
        str: Base64 encoded PNG image
    """
    try:
        if not labels or not values or sum(values) == 0:
            return None
        
        fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
        
        colors = {
            'easy': '#10B981',
            'medium': '#F59E0B',
            'advanced': '#EF4444'
        }
        
        pie_colors = [colors.get(label.lower(), '#6B7280') for label in labels]
        
        wedges, texts, autotexts = ax.pie(
            values, 
            labels=labels,
            autopct='%1.0f%%',
            colors=pie_colors,
            startangle=90,
            explode=[0.02] * len(values),
            shadow=False
        )
        
        for text in texts:
            text.set_fontsize(14)
            text.set_fontweight('bold')
        
        for autotext in autotexts:
            autotext.set_fontsize(13)
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        plt.close(fig)
        
        return image_base64
        
    except Exception as e:
        logger.error(f"Error creating pie chart: {e}")
        plt.close('all')
        return None


def create_progress_bar_chart(categories, values, title="Learning Progress"):
    """
    Create a horizontal bar chart for progress visualization
    
    Args:
        categories: List of category names
        values: List of values (percentages)
        title: Chart title
    
    Returns:
        str: Base64 encoded PNG image
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
        
        colors = ['#10B981' if v >= 80 else '#F59E0B' if v >= 50 else '#EF4444' 
                  for v in values]
        
        bars = ax.barh(categories, values, color=colors, height=0.6)
        
        for bar, value in zip(bars, values):
            width = bar.get_width()
            ax.text(width + 2, bar.get_y() + bar.get_height()/2,
                   f'{value:.0f}%',
                   ha='left', va='center', fontsize=12, fontweight='bold')
        
        ax.set_xlim(0, 110)
        ax.set_xlabel('Completion (%)', fontsize=14, fontweight='bold')
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        ax.tick_params(axis='both', which='major', labelsize=12)
        
        ax.axvline(x=100, color='#10B981', linestyle='--', alpha=0.3)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        plt.close(fig)
        
        return image_base64
        
    except Exception as e:
        logger.error(f"Error creating bar chart: {e}")
        plt.close('all')
        return None


def create_weekly_activity_chart(days, activities, title="Weekly Activity"):
    """
    Create a bar chart showing weekly activity
    
    Args:
        days: List of day names
        activities: List of activity counts
        title: Chart title
    
    Returns:
        str: Base64 encoded PNG image
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
        
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                    'Friday', 'Saturday', 'Sunday']
        
        ordered_activities = []
        for day in day_order:
            if day in days:
                idx = days.index(day)
                ordered_activities.append(activities[idx])
            else:
                ordered_activities.append(0)
        
        colors = ['#4F46E5' if a > 0 else '#E5E7EB' for a in ordered_activities]
        
        bars = ax.bar(day_order, ordered_activities, color=colors, width=0.6)
        
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2, height + 0.2,
                       f'{int(height)}',
                       ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        ax.set_ylabel('Activities', fontsize=14, fontweight='bold')
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        ax.set_xticklabels([d[:3] for d in day_order], fontsize=12)
        ax.tick_params(axis='y', labelsize=12)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        plt.close(fig)
        
        return image_base64
        
    except Exception as e:
        logger.error(f"Error creating activity chart: {e}")
        plt.close('all')
        return None


def create_engagement_gauge(score, title="Engagement Level"):
    """
    Create a gauge chart showing engagement score
    
    Args:
        score: Engagement score (0-100)
        title: Chart title
    
    Returns:
        str: Base64 encoded PNG image
    """
    try:
        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        
        if score >= 70:
            color = '#10B981'
            level = 'High'
        elif score >= 40:
            color = '#F59E0B'
            level = 'Medium'
        else:
            color = '#EF4444'
            level = 'Low'
        
        ax.barh([0], [100], color='#E5E7EB', height=0.5)
        ax.barh([0], [score], color=color, height=0.5)
        
        ax.text(50, 0, f'{score}%\n{level}', 
               ha='center', va='center', 
               fontsize=20, fontweight='bold', color=color)
        
        ax.set_xlim(0, 100)
        ax.set_ylim(-0.5, 0.5)
        ax.set_title(title, fontsize=14, fontweight='bold', pad=10)
        
        ax.set_yticks([])
        ax.set_xticks([0, 25, 50, 75, 100])
        ax.tick_params(axis='x', labelsize=10)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        
        plt.tight_layout()
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        plt.close(fig)
        
        return image_base64
        
    except Exception as e:
        logger.error(f"Error creating gauge chart: {e}")
        plt.close('all')
        return None
