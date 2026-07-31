document.addEventListener('DOMContentLoaded', () => {
    const chatBox   = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn   = document.getElementById('send-btn');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar   = document.getElementById('sidebar');

    // Set welcome timestamp
    const welcomeTime = document.getElementById('welcome-time');
    if (welcomeTime) welcomeTime.textContent = getTime();

    // Marked.js options
    marked.setOptions({ breaks: true, gfm: true });

    // ── Sidebar toggle ────────────────────────────────────
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
    });

    // ── Sidebar nav items ─────────────────────────────────
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', () => {
            document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            const q = item.getAttribute('data-q');
            if (q) sendQuery(q);
        });
    });

    // ── Suggestion chips ──────────────────────────────────
    document.querySelectorAll('.chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const q = chip.getAttribute('data-q');
            if (q) {
                hideSuggestions();
                sendQuery(q);
            }
        });
    });

    function hideSuggestions() {
        const s = document.getElementById('suggestions');
        if (s) { s.style.transition = 'opacity 0.3s'; s.style.opacity = '0'; setTimeout(() => s.remove(), 300); }
    }

    // ── Helpers ───────────────────────────────────────────
    function getTime() {
        return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    function scrollToBottom() {
        chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });
    }

    // ── Add message ───────────────────────────────────────
    function addMessage(content, sender) {
        const wrapper = document.createElement('div');
        wrapper.classList.add('message', sender);

        const avatar = document.createElement('div');
        avatar.classList.add('msg-avatar', sender === 'bot' ? 'bot-avatar' : 'user-avatar');
        avatar.textContent = sender === 'bot' ? '🎬' : '👤';

        const msgContent = document.createElement('div');
        msgContent.classList.add('msg-content');

        const name = document.createElement('div');
        name.classList.add('msg-name');
        name.textContent = sender === 'bot' ? 'CineBot' : 'You';

        const bubble = document.createElement('div');
        bubble.classList.add('bubble', sender === 'bot' ? 'bot-bubble' : 'user-bubble');

        if (sender === 'bot') {
            bubble.innerHTML = marked.parse(content);
        } else {
            bubble.textContent = content;
        }

        const time = document.createElement('div');
        time.classList.add('msg-time');
        time.textContent = getTime();

        msgContent.appendChild(name);
        msgContent.appendChild(bubble);
        msgContent.appendChild(time);

        wrapper.appendChild(avatar);
        wrapper.appendChild(msgContent);
        chatBox.appendChild(wrapper);
        scrollToBottom();
    }

    // ── Typing indicator ──────────────────────────────────
    function showTyping() {
        const wrapper = document.createElement('div');
        wrapper.classList.add('message', 'bot');
        wrapper.id = 'typing-msg';

        const avatar = document.createElement('div');
        avatar.classList.add('msg-avatar', 'bot-avatar');
        avatar.textContent = '🎬';

        const msgContent = document.createElement('div');
        msgContent.classList.add('msg-content');

        const name = document.createElement('div');
        name.classList.add('msg-name');
        name.textContent = 'CineBot';

        const bubble = document.createElement('div');
        bubble.classList.add('typing-bubble');
        bubble.innerHTML = `
            <div class="typing-status" style="font-size: 0.85rem; color: var(--gold); margin-bottom: 6px; font-weight: 500;">Researching movie...</div>
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;

        msgContent.appendChild(name);
        msgContent.appendChild(bubble);
        wrapper.appendChild(avatar);
        wrapper.appendChild(msgContent);
        chatBox.appendChild(wrapper);
        scrollToBottom();
    }

    function hideTyping() {
        const el = document.getElementById('typing-msg');
        if (el) el.remove();
    }

    // ── Send message ──────────────────────────────────────
    async function sendQuery(query) {
        hideSuggestions();
        addMessage(query, 'user');
        userInput.value = '';

        userInput.disabled = true;
        sendBtn.disabled = true;
        showTyping();

        try {
            const res = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: query })
            });
            const data = await res.json();
            hideTyping();
            addMessage(res.ok ? data.response : 'Oops! Something went wrong. Please try again.', 'bot');
        } catch (err) {
            console.error(err);
            hideTyping();
            addMessage('Network error. Please check your connection and try again.', 'bot');
        } finally {
            userInput.disabled = false;
            sendBtn.disabled = false;
            userInput.focus();
        }
    }

    async function sendMessage() {
        const msg = userInput.value.trim();
        if (!msg) return;
        await sendQuery(msg);
    }

    // ── Event listeners ───────────────────────────────────
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keydown', e => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // ── Auto-focus ─────────────────────────────────────────
    userInput.focus();
});
