/* Main application JavaScript */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Voice Assistant App loaded');
    initEmail();
    initAudio();
    initTelegram();
    loadInitialEmails();
});

function initAudio() {
    const recordBtn = document.getElementById('record-btn');
    if (recordBtn) {
        recordBtn.addEventListener('click', toggleRecording);
    }
}

function initEmail() {
    const emailForm = document.getElementById('email-form');
    if (emailForm) {
        emailForm.addEventListener('submit', submitEmailForm);
    }

    const loadInboxBtn = document.getElementById('load-inbox');
    if (loadInboxBtn) {
        loadInboxBtn.addEventListener('click', loadInbox);
    }
}

function initTelegram() {
    loadTelegramStatus();
}

async function submitEmailForm(event) {
    event.preventDefault();
    const to = document.getElementById('to').value;
    const subject = document.getElementById('subject').value;
    const body = document.getElementById('body').value;

    try {
        const result = await apiRequest('/email/send', {
            method: 'POST',
            body: JSON.stringify({ to, subject, body })
        });
        
        if (result.status === 'sent' || result.status === 'ok') {
            showAlert('Email sent successfully!', 'success');
            document.getElementById('email-form').reset();
            loadInbox();
        } else {
            showAlert('Failed to send email', 'error');
        }
    } catch (error) {
        showAlert('Error: ' + error.message, 'error');
    }
}

function toggleRecording() {
    console.log('Toggle recording');
}

async function loadInitialEmails() {
    if (document.getElementById('load-inbox')) {
        await loadInbox();
    }
}

async function loadInbox() {
    try {
        const result = await apiListEmails();
        if (result.status === 'error') {
            throw new Error(result.message || 'Unable to load inbox');
        }
        displayInbox(Array.isArray(result.messages) ? result.messages : []);
    } catch (error) {
        console.error('Failed to load inbox:', error);
        showAlert('Failed to load emails', 'error');
    }
}

function displayInbox(emails) {
    const inboxDiv = document.getElementById('inbox-list');
    if (!inboxDiv) return;

    if (!emails || emails.length === 0) {
        inboxDiv.innerHTML = '<p>No emails found. <button type="button" class="btn btn-secondary" onclick="loadInbox()">Refresh</button></p>';
        return;
    }

    let html = '<ul>';
    emails.forEach(email => {
        const subject = email.subject || '(No subject)';
        const from = email.from || 'Unknown';
        const id = email.id || email.gmail_id || '';
        
        html += `<li>
            <div>
                <strong>${escapeHtml(subject)}</strong>
                <div class="email-from">${escapeHtml(from)}</div>
            </div>
            <button type="button" class="btn btn-secondary" onclick="readEmailItem('${escapeHtml(id)}')">Read</button>
        </li>`;
    });
    html += '</ul>';
    inboxDiv.innerHTML = html;
}

async function readEmailItem(emailId) {
    try {
        const result = await apiReadEmail(emailId);
        if (result.status === 'error') {
            throw new Error(result.message || 'Unable to read email');
        }

        const email = result.message || result;
        const body = email.body || result.body || 'No content';
        const from = email.from || 'Unknown';
        const subject = email.subject || '(No subject)';
        
        alert(`From: ${from}\nSubject: ${subject}\n\n${body}`);
    } catch (error) {
        showAlert('Failed to read email: ' + error.message, 'error');
    }
}

async function loadTelegramStatus() {
    const statusDiv = document.getElementById('telegram-status');
    if (!statusDiv) return;

    try {
        const result = await fetch('/telegram/ping');
        if (result.ok) {
            const data = await result.json();
            statusDiv.textContent = data.message || 'Connected';
        } else {
            statusDiv.textContent = 'Not connected';
        }
    } catch (error) {
        statusDiv.textContent = 'Not connected';
    }
}

function showAlert(message, type = 'error') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    const main = document.querySelector('main');
    if (main) {
        main.insertBefore(alertDiv, main.firstChild);
        setTimeout(() => alertDiv.remove(), 5000);
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}
