// FRIDAY AI - Voice-Only Frontend
// Pure voice control. Minimal UI.
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const micStatus = document.getElementById('micStatus');
const micText = document.getElementById('micText');
const voiceOrb = document.getElementById('voiceOrb');
const voiceStatus = document.getElementById('voiceStatus');
const voiceLast = document.getElementById('voiceLast');
const actionFeedback = document.getElementById('actionFeedback');
const gifBg = document.getElementById('gifBg');
const permissionModal = document.getElementById('permissionModal');
const permissionText = document.getElementById('permissionText');

let isAwake = false;
let pendingPermission = false;
let isProcessing = false;

// GIF background
const savedTheme = localStorage.getItem('friday_theme') || 'ironman';
gifBg.style.backgroundImage = `url('/static/gifs/${savedTheme}.gif')`;

// Status updates
function updateStatus(awake) {
    isAwake = awake;
    if (awake) {
        statusDot.classList.add('awake');
        statusText.textContent = 'Awake';
        voiceStatus.textContent = 'Awake. Listening for your command...';
        voiceOrb.classList.add('active');
    } else {
        statusDot.classList.remove('awake');
        statusText.textContent = 'Standby';
        voiceStatus.textContent = 'Say "FRIDAY" to wake me';
        voiceOrb.classList.remove('active', 'processing');
    }
}

function setProcessing(val) {
    isProcessing = val;
    if (val) {
        voiceOrb.classList.add('processing');
        voiceStatus.textContent = 'Processing...';
    } else {
        voiceOrb.classList.remove('processing');
        if (isAwake) {
            voiceStatus.textContent = 'Awake. Listening for your command...';
        }
    }
}

function setMicStatus(on) {
    micText.textContent = on ? 'Mic: Listening' : 'Mic';
    micStatus.classList.toggle('on', on);
}

function setVoiceLast(text) {
    voiceLast.textContent = text ? `"${text}"` : '';
}

function setActionFeedback(text) {
    actionFeedback.textContent = text;
    actionFeedback.classList.add('show');
    setTimeout(() => actionFeedback.classList.remove('show'), 5000);
}

// API helpers
async function apiPost(url, body = {}) {
    try {
        const resp = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        if (!resp.ok) {
            throw new Error(`HTTP ${resp.status}: ${resp.statusText}`);
        }
        return await resp.json();
    } catch (e) {
        console.error(`API POST ${url} failed:`, e);
        setVoiceStatus('Connection error. Is app.py running?');
        throw e;
    }
}

async function apiGet(url) {
    try {
        const resp = await fetch(url);
        if (!resp.ok) {
            throw new Error(`HTTP ${resp.status}: ${resp.statusText}`);
        }
        return await resp.json();
    } catch (e) {
        console.error(`API GET ${url} failed:`, e);
        setVoiceStatus('Server offline. Start app.py first.');
        throw e;
    }
}

// Permission modal
function showPermissionModal(text) {
    pendingPermission = true;
    permissionText.textContent = text;
    permissionModal.classList.add('show');
    setVoiceStatus('Waiting for your permission...');
    speak(text);
}

function hidePermissionModal() {
    pendingPermission = false;
    permissionModal.classList.remove('show');
}

async function handlePermission(allow) {
    hidePermissionModal();
    try {
        const data = await apiPost('/api/confirm', { allow });
        updateStatus(data.awake);
        if (data.pending_permission) {
            showPermissionModal(data.response);
        } else {
            speak(data.response);
            setActionFeedback(data.response);
        }
    } catch (e) {
        speak('Could not confirm permission.');
    }
}

// Text-to-speech
function speak(text) {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utter = new SpeechSynthesisUtterance(text);
        utter.rate = 1;
        utter.pitch = 1;
        window.speechSynthesis.speak(utter);
    }
}

// Continuous Wake-Word Listening
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;
let restarting = false;

function startListening() {
    if (!SpeechRecognition) {
        micText.textContent = 'Mic: Not supported';
        setVoiceStatus('Speech recognition not supported. Use Chrome or Edge browser.');
        console.error('SpeechRecognition API not available. Use Chrome/Edge.');
        return;
    }

    try {
        recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            console.log('Speech recognition started');
            setMicStatus(true);
            updateDebugMic(true, 'Listening');
        };

        recognition.onerror = (e) => {
            console.error('Speech recognition error:', e.error, e);
            setMicStatus(false);
            if (e.error === 'not-allowed' || e.error === 'service-not-allowed') {
                micText.textContent = 'Mic: Permission denied';
                setVoiceStatus('Microphone permission denied. Please allow mic access.');
                updateDebugMic(false, 'Permission denied');
            } else if (e.error === 'no-speech') {
                // Ignore no-speech errors, restart
            } else {
                setVoiceStatus(`Mic error: ${e.error}`);
                updateDebugMic(false, e.error);
            }
            if (!restarting) {
                setTimeout(() => { if (!restarting) startListening(); }, 1500);
            }
        };

        recognition.onend = () => {
            console.log('Speech recognition ended, restarting...');
            setMicStatus(false);
            updateDebugMic(false, 'Idle');
            if (!restarting) {
                setTimeout(() => { if (!restarting) startListening(); }, 1000);
            }
        };

        recognition.onresult = async (event) => {
            let transcript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                if (event.results[i].isFinal) {
                    transcript += event.results[i][0].transcript;
                }
            }
            const heard = transcript.trim().toLowerCase();
            if (!heard) return;

            console.log('Heard:', heard);
            setVoiceLast(heard);

            // Wake word detection
            if (!isAwake) {
                if (heard.includes('friday') || heard.includes('wake up') || heard.includes('hey friday')) {
                    updateStatus(true);
                    try {
                        const data = await apiPost('/api/wake');
                        updateStatus(data.awake);
                        setVoiceStatus('FRIDAY at your service. How can I help?');
                        speak(data.response);
                    } catch (e) {
                        setVoiceStatus('Connection error.');
                    }
                }
                return;
            }

            // Awake - treat as command
            setProcessing(true);
            try {
                const data = await apiPost('/api/chat', { message: heard });
                updateStatus(data.awake);
                setProcessing(false);

                if (data.pending_permission) {
                    showPermissionModal(data.response);
                } else if (data.awake) {
                    setVoiceStatus(data.response);
                    speak(data.response);
                    setActionFeedback(data.response);
                }
            } catch (e) {
                setProcessing(false);
                setVoiceStatus('Connection error.');
            }
        };

        recognition.start();
        console.log('Recognition started successfully');
    } catch (e) {
        console.error('Failed to start speech recognition:', e);
        setVoiceStatus('Failed to start microphone. Check permissions.');
    }
}

// Permission events
document.getElementById('permYes').addEventListener('click', () => handlePermission(true));
document.getElementById('permNo').addEventListener('click', () => handlePermission(false));

// Debug bar
const debugServer = document.getElementById('debugServer');
const debugBrowser = document.getElementById('debugBrowser');
const debugMic = document.getElementById('debugMic');

function updateDebugServer(ok, text) {
    debugServer.innerHTML = `Server: <span class="${ok ? 'ok' : 'fail'}">${text}</span>`;
}
function updateDebugBrowser(ok, text) {
    debugBrowser.innerHTML = `Browser: <span class="${ok ? 'ok' : 'warn'}">${text}</span>`;
}
function updateDebugMic(ok, text) {
    debugMic.innerHTML = `Mic: <span class="${ok ? 'ok' : 'fail'}">${text}</span>`;
}

// Init
(function init() {
    console.log('FRIDAY initializing...');
    console.log('SpeechRecognition available:', !!SpeechRecognition);

    const browserSupport = !!SpeechRecognition;
    updateDebugBrowser(browserSupport, browserSupport ? 'Voice Ready' : 'Not Supported (use Chrome/Edge)');

    (async function connect() {
        try {
            const data = await apiGet('/api/status');
            console.log('Server status:', data);
            updateStatus(data.awake);
            updateDebugServer(true, 'Online');
            if (data.pending_permission) {
                showPermissionModal('FRIDAY requires permission to proceed.');
            }
        } catch (e) {
            console.error('Failed to connect to server:', e);
            updateDebugServer(false, 'Offline');
            statusText.textContent = 'Server Offline';
            statusDot.style.background = '#f87171';
            setVoiceStatus('Server offline. Start app.py first.');
        }

        setTimeout(startListening, 500);
    })();
})();
