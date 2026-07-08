/**
 * Accessibility Agent JavaScript
 * Tracks user behavior and manages accessibility settings.
 */

class AccessibilityManager {
    constructor() {
        this.settings = {
            audioMode: false,
            largeText: false,
            reducedMotion: false,
            signLanguage: false,
            highContrast: false,
            fontSize: 18
        };
        this.behaviorEvents = [];
        this.eventFlushInterval = 30000;
        this.startTime = Date.now();
        this.scrollPositions = [];
    }

    init() {
        console.log('[Accessibility] Initializing...');
        
        this.loadSettings();
        this.applySettings();
        this.startBehaviorTracking();
        this.setupEventListeners();
        
        setInterval(() => this.flushEvents(), this.eventFlushInterval);
        
        console.log('[Accessibility] Initialized');
    }

    async loadSettings() {
        try {
            const response = await fetch('/api/accessibility/settings');
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.settings = { ...this.settings, ...data.settings };
                    this.applySettings();
                }
            }
        } catch (error) {
            console.error('[Accessibility] Failed to load settings:', error);
        }
    }

    applySettings() {
        const root = document.documentElement;
        
        if (this.settings.largeText) {
            root.style.setProperty('--base-font-size', '20px');
            document.body.classList.add('large-text-mode');
        } else {
            root.style.setProperty('--base-font-size', `${this.settings.fontSize}px`);
            document.body.classList.remove('large-text-mode');
        }
        
        if (this.settings.reducedMotion) {
            root.style.setProperty('--animation-duration', '0s');
            document.body.classList.add('reduced-motion');
        } else {
            root.style.setProperty('--animation-duration', '0.3s');
            document.body.classList.remove('reduced-motion');
        }
        
        if (this.settings.highContrast) {
            document.body.classList.add('high-contrast-mode');
        } else {
            document.body.classList.remove('high-contrast-mode');
        }
        
        if (this.settings.audioMode) {
            document.body.classList.add('audio-mode');
        } else {
            document.body.classList.remove('audio-mode');
        }
        
        console.log('[Accessibility] Settings applied:', this.settings);
    }

    startBehaviorTracking() {
        this.trackScrollSpeed();
        this.trackZoomLevel();
        this.trackReadingTime();
        this.trackStruggleEvents();
    }

    trackScrollSpeed() {
        let lastScrollY = window.scrollY;
        let lastScrollTime = Date.now();
        
        window.addEventListener('scroll', () => {
            const currentTime = Date.now();
            const timeDiff = currentTime - lastScrollTime;
            
            if (timeDiff > 100) {
                const scrollDiff = Math.abs(window.scrollY - lastScrollY);
                const speed = scrollDiff / (timeDiff / 1000);
                
                this.scrollPositions.push(speed);
                if (this.scrollPositions.length > 10) {
                    this.scrollPositions.shift();
                }
                
                const avgSpeed = this.scrollPositions.reduce((a, b) => a + b, 0) / this.scrollPositions.length;
                
                if (avgSpeed < 50) {
                    this.addEvent('scroll_speed', avgSpeed);
                }
                
                lastScrollY = window.scrollY;
                lastScrollTime = currentTime;
            }
        });
    }

    trackZoomLevel() {
        const checkZoom = () => {
            const zoom = Math.round(window.devicePixelRatio * 100);
            if (zoom > 100) {
                this.addEvent('zoom_level', zoom);
            }
        };
        
        window.addEventListener('resize', checkZoom);
        checkZoom();
    }

    trackReadingTime() {
        const lessonContent = document.querySelector('.lesson-content, .content-area');
        if (!lessonContent) return;
        
        let readingStartTime = null;
        let wordsInView = 0;
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    readingStartTime = Date.now();
                    const text = entry.target.textContent || '';
                    wordsInView = text.split(/\s+/).length;
                } else if (readingStartTime && wordsInView > 0) {
                    const timeSpent = (Date.now() - readingStartTime) / 1000;
                    const wpm = (wordsInView / timeSpent) * 60;
                    
                    if (wpm > 0 && wpm < 500) {
                        this.addEvent('reading_time', wpm);
                    }
                    
                    readingStartTime = null;
                }
            });
        });
        
        observer.observe(lessonContent);
    }

    trackStruggleEvents() {
        document.addEventListener('click', (e) => {
            const target = e.target.closest('button, a');
            if (!target) return;
            
            if (target.matches('[data-help], .help-btn, .hint-btn')) {
                this.addEvent('help_click', 1);
            }
            
            if (target.matches('.back-btn, [data-back]')) {
                this.addEvent('back_navigation', 1);
            }
        });
        
        let repeatClicks = {};
        document.addEventListener('click', (e) => {
            const section = e.target.closest('.lesson-section, .content-section');
            if (section) {
                const id = section.id || section.dataset.section;
                if (id) {
                    repeatClicks[id] = (repeatClicks[id] || 0) + 1;
                    if (repeatClicks[id] >= 3) {
                        this.addEvent('repeat_section', 1);
                        repeatClicks[id] = 0;
                    }
                }
            }
        });
    }

    addEvent(type, value) {
        this.behaviorEvents.push({
            type: type,
            value: value,
            timestamp: Date.now()
        });
        
        if (this.behaviorEvents.length > 50) {
            this.flushEvents();
        }
    }

    async flushEvents() {
        if (this.behaviorEvents.length === 0) return;
        
        const events = [...this.behaviorEvents];
        this.behaviorEvents = [];
        
        try {
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
            
            const response = await fetch('/api/accessibility/track', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken || ''
                },
                body: JSON.stringify({ events: events })
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.recommendations && data.recommendations.length > 0) {
                    this.showRecommendations(data.recommendations);
                }
                if (data.changes_made && data.changes_made.length > 0) {
                    await this.loadSettings();
                }
            }
        } catch (error) {
            console.error('[Accessibility] Failed to send events:', error);
            this.behaviorEvents = [...events, ...this.behaviorEvents];
        }
    }

    showRecommendations(recommendations) {
        const container = document.getElementById('accessibility-recommendations');
        if (!container) return;
        
        container.innerHTML = recommendations.map(rec => `
            <div class="alert alert-info accessibility-recommendation">
                <i data-feather="info" class="me-2"></i>
                ${rec}
            </div>
        `).join('');
        
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    }

    async updateSetting(setting, value) {
        this.settings[setting] = value;
        this.applySettings();
        
        try {
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
            
            await fetch('/api/accessibility/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken || ''
                },
                body: JSON.stringify({ [setting]: value })
            });
        } catch (error) {
            console.error('[Accessibility] Failed to save setting:', error);
        }
    }

    toggleAudioMode() {
        this.updateSetting('audioMode', !this.settings.audioMode);
    }

    toggleLargeText() {
        this.updateSetting('largeText', !this.settings.largeText);
    }

    toggleReducedMotion() {
        this.updateSetting('reducedMotion', !this.settings.reducedMotion);
    }

    toggleHighContrast() {
        this.updateSetting('highContrast', !this.settings.highContrast);
    }
}

window.accessibilityManager = new AccessibilityManager();

document.addEventListener('DOMContentLoaded', () => {
    window.accessibilityManager.init();
});
