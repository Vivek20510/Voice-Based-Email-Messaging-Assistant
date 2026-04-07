/* Audio recording using Web Audio API */
let mediaRecorder;
let audioChunks = [];
let isRecording = false;

async function initAudio() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            audioChunks = [];
            uploadAudio(audioBlob);
        };

        console.log('Audio initialized');
        return true;
    } catch (error) {
        console.error('Error accessing microphone:', error);
        showNotification('Microphone access denied. Please allow microphone access to use voice features.', 'error');
        return false;
    }
}

async function toggleRecording() {
    if (!mediaRecorder) {
        showNotification('Requesting microphone access...', 'info');
        const ready = await initAudio();
        if (ready) {
            startRecording();
        }
        return;
    }

    if (isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
}

function startRecording() {
    mediaRecorder.start();
    isRecording = true;
    updateRecordButton('⏹️ Stop Recording', 'recording');
    updateRecordingStatus(true);
    showNotification('Recording started...', 'info');
}

function stopRecording() {
    mediaRecorder.stop();
    isRecording = false;
    updateRecordButton('🎙️ Start Recording');
    updateRecordingStatus(false);
    showNotification('Recording stopped. Processing...', 'info');
}

function updateRecordButton(text, className = '') {
    const btn = document.getElementById('record-btn');
    if (btn) {
        btn.textContent = text;
        btn.className = className ? `btn ${className}` : 'bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors';
    }
}

function updateRecordingStatus(recording) {
    const statusDiv = document.getElementById('recording-status');
    if (statusDiv) {
        if (recording) {
            statusDiv.innerHTML = '<span class="animate-pulse text-red-600 flex items-center"><span class="mr-2">🔴</span>Recording...</span>';
            statusDiv.classList.remove('hidden');
        } else {
            statusDiv.classList.add('hidden');
        }
    }
}

async function uploadAudio(blob) {
    const formData = new FormData();
    formData.append('audio', blob, 'recording.wav');

    try {
        const response = await fetch('/voice/transcribe', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        displayTranscription(result);
        showNotification('Transcription complete!', 'success');
    } catch (error) {
        console.error('Upload failed:', error);
        showNotification('Failed to transcribe audio: ' + error.message, 'error');
        displayTranscription({ text: 'Error processing audio', language: 'unknown' });
    }
}

function displayTranscription(result) {
    const output = document.getElementById('transcription-output');
    if (output && result.text) {
        const lang = result.language ? ` (${result.language.toUpperCase()})` : '';
        output.innerHTML = `<div class="text-green-600 font-medium">Transcription${lang}:</div><div class="mt-2 p-3 bg-gray-100 rounded">${escapeHtml(result.text)}</div>`;
    } else {
        output.innerHTML = '<p class="text-red-500">Failed to transcribe audio</p>';
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 px-4 py-2 rounded-lg text-white z-50 ${
        type === 'success' ? 'bg-green-500' :
        type === 'error' ? 'bg-red-500' :
        'bg-blue-500'
    }`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}
document.addEventListener('DOMContentLoaded', () => {
    const recordBtn = document.getElementById('record-btn');
    if (recordBtn) {
        recordBtn.addEventListener('click', toggleRecording);
    }
});
