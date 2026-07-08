/**
 * Emotion Detection Agent
 * Uses TensorFlow.js and face-api.js for browser-based emotion detection.
 * Sends detected emotions to backend for adaptive learning adjustments.
 */

class EmotionAgent {
    constructor() {
        this.isInitialized = false;
        this.isRunning = false;
        this.video = null;
        this.canvas = null;
        this.detectionInterval = null;
        this.emotionHistory = [];
        this.historyLimit = 10;
        this.detectionIntervalMs = 3000;
        this.onEmotionDetected = null;
        this.modelsLoaded = false;
    }

    async init() {
        if (this.isInitialized) return true;
        
        try {
            console.log('[EmotionAgent] Initializing...');
            
            await this.loadFaceApiModels();
            
            this.isInitialized = true;
            console.log('[EmotionAgent] Initialized successfully');
            return true;
        } catch (error) {
            console.error('[EmotionAgent] Initialization failed:', error);
            return false;
        }
    }

    async loadFaceApiModels() {
        if (typeof faceapi === 'undefined') {
            console.log('[EmotionAgent] Loading face-api.js from CDN...');
            await this.loadScript('https://cdn.jsdelivr.net/npm/face-api.js@0.22.2/dist/face-api.min.js');
        }
        
        const MODEL_URL = 'https://cdn.jsdelivr.net/npm/@vladmandic/face-api/model';
        
        console.log('[EmotionAgent] Loading face detection models...');
        await Promise.all([
            faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL),
            faceapi.nets.faceExpressionNet.loadFromUri(MODEL_URL)
        ]);
        
        this.modelsLoaded = true;
        console.log('[EmotionAgent] Models loaded successfully');
    }

    loadScript(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    async startDetection(videoElement) {
        if (!this.isInitialized) {
            const success = await this.init();
            if (!success) return false;
        }

        if (this.isRunning) {
            console.log('[EmotionAgent] Already running');
            return true;
        }

        try {
            this.video = videoElement || await this.createVideoElement();
            
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { 
                    width: 320, 
                    height: 240,
                    facingMode: 'user'
                }
            });
            
            this.video.srcObject = stream;
            await new Promise(resolve => {
                this.video.onloadedmetadata = () => {
                    this.video.play();
                    resolve();
                };
            });

            this.isRunning = true;
            this.startDetectionLoop();
            
            console.log('[EmotionAgent] Detection started');
            return true;
        } catch (error) {
            console.error('[EmotionAgent] Failed to start detection:', error);
            return false;
        }
    }

    createVideoElement() {
        const video = document.createElement('video');
        video.setAttribute('autoplay', '');
        video.setAttribute('muted', '');
        video.setAttribute('playsinline', '');
        video.style.display = 'none';
        document.body.appendChild(video);
        return video;
    }

    startDetectionLoop() {
        this.detectionInterval = setInterval(async () => {
            if (!this.isRunning || !this.video) return;
            
            try {
                const detection = await faceapi
                    .detectSingleFace(this.video, new faceapi.TinyFaceDetectorOptions())
                    .withFaceExpressions();
                
                if (detection) {
                    const emotion = this.getTopEmotion(detection.expressions);
                    this.processEmotion(emotion);
                }
            } catch (error) {
                console.error('[EmotionAgent] Detection error:', error);
            }
        }, this.detectionIntervalMs);
    }

    getTopEmotion(expressions) {
        const emotions = Object.entries(expressions);
        emotions.sort((a, b) => b[1] - a[1]);
        
        const [emotion, confidence] = emotions[0];
        
        const emotionMap = {
            'happy': 'happy',
            'sad': 'sad',
            'angry': 'frustrated',
            'fearful': 'confused',
            'disgusted': 'frustrated',
            'surprised': 'confused',
            'neutral': 'neutral'
        };
        
        return {
            emotion: emotionMap[emotion] || 'neutral',
            confidence: confidence,
            raw: emotion
        };
    }

    processEmotion(emotionData) {
        this.emotionHistory.push({
            ...emotionData,
            timestamp: Date.now()
        });
        
        if (this.emotionHistory.length > this.historyLimit) {
            this.emotionHistory.shift();
        }
        
        console.log(`[EmotionAgent] Detected: ${emotionData.emotion} (${(emotionData.confidence * 100).toFixed(1)}%)`);
        
        if (this.onEmotionDetected) {
            this.onEmotionDetected(emotionData);
        }
        
        if (emotionData.confidence > 0.5 && emotionData.emotion !== 'neutral') {
            this.sendEmotionToBackend(emotionData.emotion);
        }
    }

    async sendEmotionToBackend(emotion) {
        try {
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
            
            const response = await fetch('/api/emotion/detect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken || ''
                },
                body: JSON.stringify({
                    emotion: emotion,
                    confidence: this.getAverageConfidence(),
                    history: this.getEmotionSummary()
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('[EmotionAgent] Backend response:', data);
                
                if (data.action) {
                    this.handleBackendAction(data.action);
                }
            }
        } catch (error) {
            console.error('[EmotionAgent] Failed to send emotion:', error);
        }
    }

    getAverageConfidence() {
        if (this.emotionHistory.length === 0) return 0;
        const sum = this.emotionHistory.reduce((acc, e) => acc + e.confidence, 0);
        return sum / this.emotionHistory.length;
    }

    getEmotionSummary() {
        const summary = {};
        this.emotionHistory.forEach(e => {
            summary[e.emotion] = (summary[e.emotion] || 0) + 1;
        });
        return summary;
    }

    handleBackendAction(action) {
        console.log('[EmotionAgent] Handling action:', action);
        
        switch (action.type) {
            case 'lower_difficulty':
                this.showNotification('Taking it easier - difficulty adjusted!', 'info');
                break;
            case 'add_animations':
                this.showNotification('Adding some fun elements!', 'success');
                break;
            case 'enable_hints':
                this.showNotification('Hints enabled to help you!', 'info');
                break;
            case 'continue':
                break;
        }
        
        window.dispatchEvent(new CustomEvent('emotionAction', { detail: action }));
    }

    showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} emotion-notification`;
        notification.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 9999;
            animation: slideIn 0.3s ease;
        `;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => notification.remove(), 3000);
    }

    stopDetection() {
        this.isRunning = false;
        
        if (this.detectionInterval) {
            clearInterval(this.detectionInterval);
            this.detectionInterval = null;
        }
        
        if (this.video && this.video.srcObject) {
            this.video.srcObject.getTracks().forEach(track => track.stop());
            this.video.srcObject = null;
        }
        
        console.log('[EmotionAgent] Detection stopped');
    }

    getStatus() {
        return {
            initialized: this.isInitialized,
            running: this.isRunning,
            modelsLoaded: this.modelsLoaded,
            emotionHistory: this.emotionHistory.slice(-5)
        };
    }

    getDominantEmotion() {
        const summary = this.getEmotionSummary();
        let maxCount = 0;
        let dominant = 'neutral';
        
        for (const [emotion, count] of Object.entries(summary)) {
            if (count > maxCount) {
                maxCount = count;
                dominant = emotion;
            }
        }
        
        return dominant;
    }
}

window.emotionAgent = new EmotionAgent();

document.addEventListener('DOMContentLoaded', () => {
    const emotionToggle = document.getElementById('emotion-monitor-toggle');
    if (emotionToggle) {
        emotionToggle.addEventListener('click', async () => {
            if (window.emotionAgent.isRunning) {
                window.emotionAgent.stopDetection();
                emotionToggle.classList.remove('active');
                emotionToggle.querySelector('.status-text')?.textContent = 'OFF';
            } else {
                const success = await window.emotionAgent.startDetection();
                if (success) {
                    emotionToggle.classList.add('active');
                    emotionToggle.querySelector('.status-text')?.textContent = 'ON';
                }
            }
        });
    }
});
