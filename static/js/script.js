document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    // Parse markdown configuring marked to be safer
    marked.setOptions({
        breaks: true,
        gfm: true
    });

    function scrollToBottom() {
        chatBox.scrollTo({
            top: chatBox.scrollHeight,
            behavior: 'smooth'
        });
    }

    function addMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);
        
        const avatarDiv = document.createElement('div');
        avatarDiv.classList.add('avatar');
        avatarDiv.innerHTML = sender === 'user' ? '👤' : '🎬';

        const bubbleDiv = document.createElement('div');
        bubbleDiv.classList.add('bubble');
        
        if (sender === 'bot') {
            bubbleDiv.innerHTML = marked.parse(content);
        } else {
            const p = document.createElement('p');
            p.textContent = content;
            bubbleDiv.appendChild(p);
        }

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(bubbleDiv);
        
        chatBox.appendChild(messageDiv);
        scrollToBottom();
    }

    function addTypingIndicator() {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', 'bot');
        messageDiv.id = 'typing-indicator-msg';
        
        const avatarDiv = document.createElement('div');
        avatarDiv.classList.add('avatar');
        avatarDiv.innerHTML = '🎬';

        const bubbleDiv = document.createElement('div');
        bubbleDiv.classList.add('bubble', 'typing-indicator');
        bubbleDiv.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(bubbleDiv);
        
        chatBox.appendChild(messageDiv);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator-msg');
        if (indicator) {
            indicator.remove();
        }
    }

    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        // Add user message to UI
        addMessage(message, 'user');
        userInput.value = '';
        
        // Disable input while processing
        userInput.disabled = true;
        sendBtn.disabled = true;

        // Show typing indicator
        addTypingIndicator();

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            });
            
            const data = await response.json();
            
            removeTypingIndicator();
            
            if (response.ok) {
                addMessage(data.response, 'bot');
            } else {
                addMessage("Oops! Something went wrong communicating with the server.", 'bot');
            }
        } catch (error) {
            console.error('Error:', error);
            removeTypingIndicator();
            addMessage("Oops! Network error. Please try again.", 'bot');
        } finally {
            userInput.disabled = false;
            sendBtn.disabled = false;
            userInput.focus();
        }
    }

    sendBtn.addEventListener('click', sendMessage);

    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});
