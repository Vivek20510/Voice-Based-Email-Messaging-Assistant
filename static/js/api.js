/* API client functions */
const API_BASE = '';

async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        ...options
    };
    
    try {
        const response = await fetch(url, config);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`API request failed: ${endpoint}`, error);
        throw error;
    }
}

async function apiSendEmail(to, subject, body) {
    return apiRequest('/email/send', {
        method: 'POST',
        body: JSON.stringify({ to, subject, body })
    });
}

async function apiListEmails() {
    return apiRequest('/email/list');
}

async function apiReadEmail(emailId) {
    return apiRequest(`/email/read/${encodeURIComponent(emailId)}`);
}

async function apiSummarizeText(text) {
    return apiRequest('/nlp/summarize', {
        method: 'POST',
        body: JSON.stringify({ text })
    });
}

async function apiSuggestReplies(text) {
    return apiRequest('/nlp/suggest', {
        method: 'POST',
        body: JSON.stringify({ text })
    });
}

async function apiSpeakText(text, lang = 'en') {
    const response = await fetch('/voice/speak', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, lang })
    });
    
    if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);
        audio.play();
    }
}

async function getTelegramStatus() {
    return apiRequest('/telegram/status'); // Assuming we add this endpoint
}
