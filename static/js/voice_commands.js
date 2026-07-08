/**
 * Voice Commands System for NeuroAid Learning Platform
 * Uses Web Speech API for continuous speech recognition and voice control
 */

class VoiceCommandManager {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        this.isSupported = false;
        this.currentAudio = null;
        this.currentLesson = null;
        this.lessons = [];
        this.quizMode = false;
        this.currentQuestionIndex = 0;
        this.feedbackSynthesis = null;
        this.micButton = null;
        this.statusIndicator = null;
        this.lastCommand = '';
        this.commandTimeout = null;
        
        this.commands = {
            'start lesson': this.handleStartLesson.bind(this),
            'play lesson': this.handleStartLesson.bind(this),
            'stop': this.handleStop.bind(this),
            'pause': this.handleStop.bind(this),
            'repeat': this.handleRepeat.bind(this),
            'again': this.handleRepeat.bind(this),
            'next': this.handleNext.bind(this),
            'next lesson': this.handleNext.bind(this),
            'previous': this.handlePrevious.bind(this),
            'previous lesson': this.handlePrevious.bind(this),
            'open quiz': this.handleOpenQuiz.bind(this),
            'take quiz': this.handleOpenQuiz.bind(this),
            'start quiz': this.handleOpenQuiz.bind(this),
            'submit': this.handleSubmit.bind(this),
            'submit quiz': this.handleSubmit.bind(this),
            'option a': () => this.selectOption('A'),
            'option b': () => this.selectOption('B'),
            'option c': () => this.selectOption('C'),
            'option d': () => this.selectOption('D'),
            'select a': () => this.selectOption('A'),
            'select b': () => this.selectOption('B'),
            'select c': () => this.selectOption('C'),
            'select d': () => this.selectOption('D'),
            'a': () => this.selectOption('A'),
            'b': () => this.selectOption('B'),
            'c': () => this.selectOption('C'),
            'd': () => this.selectOption('D'),
            'read question': this.handleReadQuestion.bind(this),
            'read options': this.handleReadOptions.bind(this),
            'help': this.handleHelp.bind(this),
            'commands': this.handleHelp.bind(this),
            'home': this.handleHome.bind(this),
            'dashboard': this.handleHome.bind(this),
            'go back': this.handleGoBack.bind(this),
            'back': this.handleGoBack.bind(this),
            'read': this.handleReadContent.bind(this),
            'read aloud': this.handleReadContent.bind(this),
            'louder': this.handleVolume.bind(this, 'up'),
            'volume up': this.handleVolume.bind(this, 'up'),
            'softer': this.handleVolume.bind(this, 'down'),
            'volume down': this.handleVolume.bind(this, 'down'),
            'mute': this.handleMute.bind(this),
            'unmute': this.handleUnmute.bind(this),
            'play lesson': this.handlePlayLesson.bind(this),
            'read lesson': this.handlePlayLesson.bind(this),

        };
        
        this.lessonVoiceMap = {
    // Lesson 1
    "introduction": 1,
    "programming": 1,
    "intro": 1,

    // Lesson 2
    "variables": 2,
    "data types": 2,
    "datatypes": 2,

    // Lesson 3
    "control": 3,
    "control structures": 3,
    "conditions": 3,
    "loops": 3,

    // Lesson 4
    "functions": 4,
    "modular programming": 4,
    "modules": 4,

    // Lesson 5
    "data structures": 5,
    "structures": 5,

    // Lesson 6
    "algorithms": 6,
    "problem solving": 6
};

        this.init();
    }

    init() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            this.isSupported = true;
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = true;
            this.recognition.interimResults = true;
            this.recognition.lang = 'en-US';
            this.recognition.maxAlternatives = 3;
            
            this.setupRecognitionEvents();
        } else {
            console.warn('[VoiceCommands] Speech recognition not supported in this browser');
        }
        
        if ('speechSynthesis' in window) {
            this.feedbackSynthesis = window.speechSynthesis;
        }
        
        this.createMicrophoneUI();
        this.loadLessonData();
        this.detectPageContext();
        
        // Auto-start listening when page loads
        this.autoStartListening();
        
        // Read quiz questions aloud if on quiz page
        if (this.quizMode) {
            setTimeout(() => this.readCurrentQuizQuestion(), 1500);
        }
    }
    
    autoStartListening() {
        if (!this.isSupported) return;
        
        // Check if user has previously granted permission
        if (navigator.permissions) {
            navigator.permissions.query({ name: 'microphone' }).then(result => {
                if (result.state === 'granted') {
                    // Start listening immediately
                    setTimeout(() => {
                        this.startListening();
                    }, 1000);
                }
            }).catch(() => {
                // Permissions API not available, try to start anyway
                console.log('[VoiceCommands] Permissions API not available');
            });
        }
    }
    
    readCurrentQuizQuestion() {
        const questions = document.querySelectorAll('.quiz-question');
        if (questions.length > 0) {
            const firstQuestion = questions[0];
            const questionText = firstQuestion.querySelector('h2')?.textContent || '';
            const options = firstQuestion.querySelectorAll('.option-item label');
            
            let text = `Quiz started. Question 1: ${questionText}. `;
            options.forEach((opt, j) => {
                const letter = ['A', 'B', 'C', 'D'][j];
                const optText = opt.querySelector('.option-text')?.textContent || '';
                text += `Option ${letter}: ${optText}. `;
            });
            text += 'Say option A, B, C, or D to select your answer.';
            
            this.speak(text);
        }
    }

    setupRecognitionEvents() {
        this.isStarting = false;
        this.abortCount = 0;
        this.maxAborts = 5;
        this.hadSuccessfulSession = false;
        
        this.recognition.onstart = () => {
            this.isListening = true;
            this.isStarting = false;
            this.updateMicUI(true);
            console.log('[VoiceCommands] Listening started - speak a command');
        };

        this.recognition.onend = () => {
            this.isStarting = false;
            console.log('[VoiceCommands] Recognition ended');
            
            if (this.isListening && this.abortCount < this.maxAborts) {
                setTimeout(() => {
                    if (this.isListening && !this.isStarting) {
                        this.isStarting = true;
                        try {
                            this.recognition.start();
                        } catch (e) {
                            this.isStarting = false;
                            console.log('[VoiceCommands] Restart error:', e.message);
                        }
                    }
                }, 1000);
            } else if (this.abortCount >= this.maxAborts) {
                console.log('[VoiceCommands] Too many aborts, stopping. Click mic to restart.');
                this.isListening = false;
                this.updateMicUI(false);
                this.showFeedback('Microphone stopped. Click mic button to restart.');
            }
        };

        this.recognition.onresult = (event) => {
            this.abortCount = 0;
            this.hadSuccessfulSession = true;
            
            let finalTranscript = '';
            let interimTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript.toLowerCase().trim();
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }

            if (this.statusIndicator) {
                this.statusIndicator.textContent = interimTranscript || finalTranscript || 'Listening...';
            }

            if (finalTranscript) {
                console.log('[VoiceCommands] Heard:', finalTranscript);
                this.showFeedback(`Heard: "${finalTranscript}"`);
                this.processCommand(finalTranscript);
            }
        };

        this.recognition.onerror = (event) => {
            this.isStarting = false;
            
            if (event.error === 'aborted') {
                this.abortCount++;
                console.log('[VoiceCommands] Aborted, count:', this.abortCount);
                return;
            }
            
            console.error('[VoiceCommands] Error:', event.error);
            
            if (event.error === 'not-allowed') {
                this.showFeedback('Microphone access denied. Please allow microphone permission.');
                this.isListening = false;
                this.updateMicUI(false);
            } else if (event.error === 'no-speech') {
                this.abortCount = 0;
            }
        };
    }

    createMicrophoneUI() {
        if (document.getElementById('voice-control-container')) return;
        
        const container = document.createElement('div');
        container.id = 'voice-control-container';
        container.innerHTML = `
            <style>
                #voice-control-container {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    z-index: 9999;
                    display: flex;
                    flex-direction: column;
                    align-items: flex-end;
                    gap: 10px;
                }
                #voice-mic-btn {
                    width: 60px;
                    height: 60px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border: none;
                    color: white;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                    transition: all 0.3s ease;
                }
                #voice-mic-btn:hover {
                    transform: scale(1.1);
                    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
                }
                #voice-mic-btn.listening {
                    background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
                    animation: pulse 1.5s ease-in-out infinite;
                }
                @keyframes pulse {
                    0%, 100% { box-shadow: 0 4px 15px rgba(245, 87, 108, 0.4); }
                    50% { box-shadow: 0 4px 30px rgba(245, 87, 108, 0.8); }
                }
                #voice-mic-btn svg {
                    width: 28px;
                    height: 28px;
                }
                #voice-status {
                    background: rgba(0, 0, 0, 0.8);
                    color: white;
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-size: 14px;
                    max-width: 250px;
                    text-align: center;
                    display: none;
                }
                #voice-status.active {
                    display: block;
                }
                #voice-feedback {
                    position: fixed;
                    top: 80px;
                    left: 50%;
                    transform: translateX(-50%);
                    background: rgba(0, 0, 0, 0.9);
                    color: white;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-size: 16px;
                    z-index: 10000;
                    display: none;
                    max-width: 80%;
                    text-align: center;
                }
                #voice-feedback.show {
                    display: block;
                    animation: fadeInOut 3s ease-in-out;
                }
                @keyframes fadeInOut {
                    0% { opacity: 0; transform: translateX(-50%) translateY(-10px); }
                    15% { opacity: 1; transform: translateX(-50%) translateY(0); }
                    85% { opacity: 1; }
                    100% { opacity: 0; }
                }
            </style>
            <div id="voice-feedback"></div>
            <div id="voice-status">Listening...</div>
            <button id="voice-mic-btn" title="Toggle Voice Commands" aria-label="Toggle voice commands">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                    <line x1="12" y1="19" x2="12" y2="23"></line>
                    <line x1="8" y1="23" x2="16" y2="23"></line>
                </svg>
            </button>
        `;
        
        document.body.appendChild(container);
        
        this.micButton = document.getElementById('voice-mic-btn');
        this.statusIndicator = document.getElementById('voice-status');
        
        this.micButton.addEventListener('click', () => this.toggleListening());
        
        if (!this.isSupported) {
            this.micButton.style.opacity = '0.5';
            this.micButton.title = 'Voice commands not supported in this browser';
        }
    }

    updateMicUI(listening) {
        if (this.micButton) {
            if (listening) {
                this.micButton.classList.add('listening');
                this.statusIndicator.classList.add('active');
            } else {
                this.micButton.classList.remove('listening');
                this.statusIndicator.classList.remove('active');
            }
        }
    }

    showFeedback(message) {
        const feedback = document.getElementById('voice-feedback');
        if (feedback) {
            feedback.textContent = message;
            feedback.classList.remove('show');
            void feedback.offsetWidth;
            feedback.classList.add('show');
            setTimeout(() => feedback.classList.remove('show'), 3000);
        }
    }

    toggleListening() {
        if (!this.isSupported) {
            this.showFeedback('Voice commands not supported in this browser');
            return;
        }

        if (this.isListening) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }

    startListening() {
        if (!this.isSupported) return;
        
        this.isListening = true;
        try {
            this.recognition.start();
            this.showFeedback('Microphone activated - listening for commands');
            this.speak('Voice commands activated');
        } catch (e) {
            console.error('[VoiceCommands] Start error:', e);
        }
    }

    stopListening() {
        this.isListening = false;
        try {
            this.recognition.stop();
            this.showFeedback('Microphone deactivated');
        } catch (e) {}
        this.updateMicUI(false);
    }

    loadLessonData() {
    const lessonLinks = document.querySelectorAll('a[href^="/lesson/"]');

    this.lessons = Array.from(lessonLinks).map(link => {
        const match = link.getAttribute('href').match(/\/lesson\/(\d+)/);
        return {
            id: match ? parseInt(match[1]) : null,
            title: link.textContent.trim()
        };
    }).filter(l => l.id && l.title);

    console.log('[VoiceCommands] Lessons loaded from page:', this.lessons);
}



    detectPageContext() {
        const path = window.location.pathname;
        
        if (path.includes('/quiz')) {
            this.quizMode = true;
            const lessonMatch = path.match(/\/lesson\/(\d+)/);
            if (lessonMatch) {
                this.currentLesson = { id: parseInt(lessonMatch[1]) };
            }
        } else if (path.includes('/lesson/')) {
            const lessonMatch = path.match(/\/lesson\/(\d+)/);
            if (lessonMatch) {
                this.currentLesson = { id: parseInt(lessonMatch[1]) };
            }
        }
        
        this.currentAudio = document.getElementById('lessonAudio') || 
                           document.querySelector('audio');
    }

    processCommand(transcript) {
        const text = transcript.toLowerCase().trim();
        
        if (text === this.lastCommand && Date.now() - this.lastCommandTime < 2000) {
            return;
        }
        this.lastCommand = text;
        this.lastCommandTime = Date.now();
        
        for (const [command, handler] of Object.entries(this.commands)) {
            if (text.includes(command)) {
                console.log('[VoiceCommands] Executing command:', command);
                this.showFeedback(`Command: "${command}"`);
                
                const args = text.replace(command, '').trim();
                handler(args);
                return;
            }
        }
        
        if (this.quizMode) {
            this.handleQuizAnswer(text);
        }
    }

    speak(text, callback) {
        if (!this.feedbackSynthesis) {
            if (callback) callback();
            return;
        }
        
        this.feedbackSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US';
        utterance.rate = 0.9;
        utterance.pitch = 1;
        
        if (callback) {
            utterance.onend = callback;
        }
        
        this.feedbackSynthesis.speak(utterance);
    }

    async generateTTS(text) {
        try {
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
            const response = await fetch(`/api/tts?text=${encodeURIComponent(text.substring(0, 2000))}`);
            if (response.ok) {
                const data = await response.json();
                return data.audio_url;
            }
        } catch (e) {
            console.error('[VoiceCommands] TTS error:', e);
        }
        return null;
    }

    handleStartLesson(spokenText) {
    console.log('[VoiceCommands] Spoken:', spokenText);

    if (!spokenText) {
        this.speak('Please say the lesson name');
        return;
    }

    const text = spokenText.toLowerCase();

    // Step A: find all buttons/links
    const buttons = document.querySelectorAll('a, button');
    console.log('[VoiceCommands] Total buttons found:', buttons.length);

    // Step B: loop through them
    for (const btn of buttons) {

        // Step C: check only "Continue Learning" buttons
        if (!btn.textContent.toLowerCase().includes('continue')) {
            continue;
        }

        // Step D: read parent container text
        const container = btn.closest('div');
        if (!container) continue;

        const containerText = container.innerText.toLowerCase();
        console.log('[VoiceCommands] Checking container:', containerText);

        // Step E: match spoken word with lesson text
        if (containerText.includes(text.split(' ')[0])) {
            this.speak('Opening lesson');
            setTimeout(() => {
                btn.click();
            }, 800);
            return;
        }
    }

    this.speak('Lesson not found on dashboard');
}

    handleStop() {
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.speak('Audio stopped');
        }
        if (this.feedbackSynthesis) {
            this.feedbackSynthesis.cancel();
        }
    }

    handlePlayLesson() {
    // Find the Read Aloud button
    const readBtn =
        document.getElementById('readAloudBtn') ||
        document.querySelector('button, a');

    if (readBtn && readBtn.textContent.toLowerCase().includes('read')) {
        this.speak('Reading lesson');
        readBtn.click();
    } else {
        this.speak('Read aloud button not found');
    }
}


    handleRepeat() {
        if (this.currentAudio && this.currentAudio.src) {
            this.currentAudio.currentTime = 0;
            this.currentAudio.play();
            this.speak('Replaying audio');
        } else {
            const playBtn = document.getElementById('playAudioBtn');
            if (playBtn) {
                playBtn.click();
            }
        }
    }

    handleNext() {
        const nextBtn = document.querySelector('a[href*="/lesson/"][class*="outline-primary"]:has(svg[class*="arrow-right"])') ||
                       document.querySelector('a:has(i[data-feather="arrow-right"])') ||
                       document.querySelector('.nav-buttons a:last-child, .action-buttons a[href*="lesson"]:last-child');
        
        if (nextBtn && nextBtn.href && nextBtn.href.includes('/lesson/')) {
            this.speak('Going to next lesson');
            setTimeout(() => {
                window.location.href = nextBtn.href;
            }, 1000);
        } else {
            this.speak('No next lesson available');
        }
    }

    handlePrevious() {
        const prevBtn = document.querySelector('a:has(i[data-feather="arrow-left"])') ||
                       document.querySelector('.nav-buttons a:first-child');
        
        if (prevBtn && prevBtn.href && prevBtn.href.includes('/lesson/')) {
            this.speak('Going to previous lesson');
            setTimeout(() => {
                window.location.href = prevBtn.href;
            }, 1000);
        } else {
            this.speak('No previous lesson available');
        }
    }

    handleOpenQuiz() {
        const quizBtn = document.querySelector('a[href*="/quiz/"]');
        if (quizBtn) {
            this.speak('Opening quiz. Questions will be read aloud.');
            setTimeout(() => {
                window.location.href = quizBtn.href;
            }, 1500);
        } else if (window.location.pathname.includes('/lesson/')) {
            const lessonId = this.currentLesson?.id;
            if (lessonId) {
                this.speak('Looking for quiz');
                window.location.href = `/quiz/${lessonId}`;
            }
        } else {
            this.speak('Please navigate to a lesson first to take its quiz');
        }
    }

    handleSubmit() {
        if (this.quizMode) {
            const submitBtn = document.getElementById('submitQuizBtn') || 
                             document.querySelector('button[type="submit"]');
            if (submitBtn) {
                this.speak('Submitting quiz');
                setTimeout(() => {
                    submitBtn.click();
                }, 1000);
            }
        } else {
            const completeForm = document.querySelector('form[action*="complete"]');
            if (completeForm) {
                this.speak('Marking lesson complete');
                setTimeout(() => {
                    completeForm.submit();
                }, 1000);
            }
        }
    }

    selectOption(option) {
        if (!this.quizMode) {
            this.speak('This command is only available during a quiz');
            return;
        }
        
        const optionLower = option.toLowerCase();
        const radioInput = document.querySelector(`input[type="radio"][value="${option.toUpperCase()}"]:not(:checked)`) ||
                          document.querySelector(`input[id*="_${optionLower}"]`);
        
        if (radioInput) {
            radioInput.checked = true;
            radioInput.dispatchEvent(new Event('change', { bubbles: true }));
            
            const label = document.querySelector(`label[for="${radioInput.id}"]`);
            const optionText = label?.querySelector('.option-text')?.textContent || option;
            
            this.speak(`Selected option ${option.toUpperCase()}`);
            this.showFeedback(`Selected: Option ${option.toUpperCase()}`);
        } else {
            this.speak(`Could not find option ${option}`);
        }
    }

    handleQuizAnswer(text) {
        const answerMappings = {
            'first': 'A', 'one': 'A', '1': 'A', 'first option': 'A',
            'second': 'B', 'two': 'B', '2': 'B', 'second option': 'B',
            'third': 'C', 'three': 'C', '3': 'C', 'third option': 'C',
            'fourth': 'D', 'four': 'D', '4': 'D', 'fourth option': 'D'
        };
        
        for (const [word, option] of Object.entries(answerMappings)) {
            if (text.includes(word)) {
                this.selectOption(option);
                return;
            }
        }
    }

    async handleReadQuestion() {
        if (!this.quizMode) {
            this.speak('This command is only available during a quiz');
            return;
        }
        
        const visibleQuestion = document.querySelector('.quiz-question h2, .question-header h2');
        if (visibleQuestion) {
            const questionText = visibleQuestion.textContent;
            this.speak(questionText);
        }
    }

    async handleReadOptions() {
        if (!this.quizMode) {
            this.speak('This command is only available during a quiz');
            return;
        }
        
        const options = document.querySelectorAll('.option-item label');
        if (options.length > 0) {
            let optionTexts = [];
            options.forEach((opt, i) => {
                const letter = ['A', 'B', 'C', 'D'][i];
                const text = opt.querySelector('.option-text')?.textContent || opt.textContent;
                optionTexts.push(`Option ${letter}: ${text}`);
            });
            
            this.speak(optionTexts.join('. '));
        }
    }

    handleHelp() {
        const helpText = `
            Available voice commands:
            Say "start lesson" followed by the lesson name to play a lesson.
            Say "stop" to pause audio.
            Say "repeat" to replay current audio.
            Say "next" or "previous" to navigate lessons.
            Say "open quiz" to start the quiz.
            Say "option A, B, C, or D" to select an answer.
            Say "submit" to submit your answers.
            Say "read question" or "read options" during a quiz.
            Say "home" to go to dashboard.
        `;
        this.speak(helpText);
        this.showFeedback('Voice help: Say "stop" when done listening');
    }

    handleHome() {
        this.speak('Going to dashboard');
        setTimeout(() => {
            window.location.href = '/dashboard';
        }, 1000);
    }

    handleGoBack() {
        this.speak('Going back');
        setTimeout(() => {
            window.history.back();
        }, 1000);
    }

    async handleReadContent() {
        const content = document.querySelector('.lesson-content, .content-text, .card-body');
        if (content) {
            const text = content.innerText.substring(0, 2000);
            this.speak('Reading content aloud');
            
            const audioUrl = await this.generateTTS(text);
            if (audioUrl) {
                this.playAudioUrl(audioUrl);
            } else {
                this.speak(text);
            }
        }
    }

    handleVolume(direction) {
        if (this.currentAudio) {
            if (direction === 'up') {
                this.currentAudio.volume = Math.min(1, this.currentAudio.volume + 0.2);
            } else {
                this.currentAudio.volume = Math.max(0, this.currentAudio.volume - 0.2);
            }
            this.speak(`Volume ${direction}`);
        }
    }

    handleMute() {
        if (this.currentAudio) {
            this.currentAudio.muted = true;
            this.speak('Audio muted');
        }
    }

    handleUnmute() {
        if (this.currentAudio) {
            this.currentAudio.muted = false;
            this.speak('Audio unmuted');
        }
    }

    playAudioUrl(url) {
        if (!this.currentAudio) {
            this.currentAudio = new Audio();
            document.body.appendChild(this.currentAudio);
        }
        this.currentAudio.src = url;
        this.currentAudio.play();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.voiceCommandManager = new VoiceCommandManager();
});
