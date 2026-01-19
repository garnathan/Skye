def get_content():
    """Return the HTML content for the Claude chat page"""

    html_content = '''
        <div class="claude-portal">
            <h2><i class="fas fa-robot"></i> Claude</h2>

            <div class="chat-container">
                <div class="chat-messages" id="chatMessages">
                    <div class="message system-message">
                        <div class="message-content">
                            <strong>Claude</strong> is ready to help! I can assist with analysis, writing, coding, math, and much more.
                        </div>
                    </div>
                </div>

                <div class="chat-input-container">
                    <div class="input-group">
                        <textarea id="messageInput" placeholder="Ask Claude anything..." rows="4"></textarea>
                        <button id="sendButton" onclick="sendMessage()">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                    <div class="model-selector">
                        <label for="modelSelect">Model:</label>
                        <select id="modelSelect">
                            <option value="claude-sonnet-4-20250514">Claude Sonnet 4</option>
                            <option value="claude-opus-4-20250514">Claude Opus 4</option>
                            <option value="claude-3-5-haiku-20241022">Claude 3.5 Haiku</option>
                        </select>
                        <button class="clear-btn" onclick="clearChat()" title="Clear chat">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <style>
        .claude-portal {
            height: 100%;
            display: flex;
            flex-direction: column;
        }

        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            height: calc(100vh - 200px);
            border: 1px solid #dee2e6;
            border-radius: 8px;
            overflow: hidden;
        }

        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
            background: #f8f9fa;
        }

        .message {
            margin-bottom: 1rem;
            display: flex;
            flex-direction: column;
        }

        .message.user {
            align-items: flex-end;
        }

        .message.assistant {
            align-items: flex-start;
        }

        .message.system-message {
            align-items: center;
        }

        .message-content {
            max-width: 80%;
            padding: 0.75rem 1rem;
            border-radius: 12px;
            word-wrap: break-word;
        }

        .message.user .message-content {
            background: #d97706;
            color: white;
        }

        .message.assistant .message-content {
            background: white;
            border: 1px solid #dee2e6;
            color: #333;
        }

        .message.system-message .message-content {
            background: #fef3c7;
            border: 1px solid #fcd34d;
            color: #92400e;
            text-align: center;
        }

        .message.error .message-content {
            background: #ffebee;
            border: 1px solid #ffcdd2;
            color: #d32f2f;
        }

        .chat-input-container {
            padding: 1.5rem;
            background: white;
            border-top: 1px solid #dee2e6;
            max-width: 100%;
        }

        .input-group {
            display: flex;
            gap: 1rem;
            margin-bottom: 0.5rem;
            width: 100%;
        }

        .input-group textarea {
            flex: 1;
            border: 2px solid #dee2e6;
            border-radius: 12px;
            padding: 1rem 1.25rem;
            resize: vertical;
            font-family: inherit;
            font-size: 1rem;
            line-height: 1.5;
            min-height: 80px;
            background: white;
            color: #333;
            transition: border-color 0.2s;
        }

        .input-group textarea:focus {
            outline: none;
            border-color: #d97706;
            box-shadow: 0 0 0 3px rgba(217, 119, 6, 0.1);
        }

        .input-group textarea::placeholder {
            color: #6c757d;
        }

        .input-group button {
            background: #d97706;
            color: white;
            border: none;
            border-radius: 12px;
            padding: 1rem 1.5rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
            transition: all 0.2s;
        }

        .input-group button:hover {
            background: #b45309;
        }

        .input-group button:disabled {
            background: #6c757d;
            cursor: not-allowed;
        }

        .model-selector {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.9rem;
            color: #495057;
        }

        .model-selector select {
            border: 1px solid #ced4da;
            border-radius: 4px;
            padding: 0.25rem 0.5rem;
            background: white;
            color: #333;
        }

        .clear-btn {
            background: #dc3545;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 0.25rem 0.5rem;
            cursor: pointer;
            margin-left: auto;
            font-size: 0.85rem;
        }

        .clear-btn:hover {
            background: #c82333;
        }

        .typing-indicator {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: #6c757d;
            font-style: italic;
        }

        .typing-dots {
            display: flex;
            gap: 2px;
        }

        .typing-dots span {
            width: 4px;
            height: 4px;
            background: #6c757d;
            border-radius: 50%;
            animation: typing 1.4s infinite;
        }

        .typing-dots span:nth-child(2) {
            animation-delay: 0.2s;
        }

        .typing-dots span:nth-child(3) {
            animation-delay: 0.4s;
        }

        @keyframes typing {
            0%, 60%, 100% {
                transform: translateY(0);
            }
            30% {
                transform: translateY(-10px);
            }
        }

        .message-content pre {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 1rem;
            border-radius: 6px;
            overflow-x: auto;
            margin: 0.5rem 0;
            border: 1px solid #333;
        }

        .message-content code {
            background: #f1f1f1;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
            font-size: 0.9em;
        }

        .message-content pre code {
            background: none;
            padding: 0;
            border: none;
            color: #d4d4d4;
        }

        /* Dark mode support */
        body.dark-mode .chat-messages {
            background: #1a1a2e;
        }

        body.dark-mode .message.assistant .message-content {
            background: #16213e;
            border-color: #0f3460;
            color: #e4e4e4;
        }

        body.dark-mode .message.system-message .message-content {
            background: #422006;
            border-color: #92400e;
            color: #fcd34d;
        }

        body.dark-mode .chat-input-container {
            background: #16213e;
            border-color: #0f3460;
        }

        body.dark-mode .input-group textarea {
            background: #1a1a2e;
            color: #e4e4e4;
            border-color: #0f3460;
        }

        body.dark-mode .model-selector {
            color: #a0a0a0;
        }

        body.dark-mode .model-selector select {
            background: #1a1a2e;
            color: #e4e4e4;
            border-color: #0f3460;
        }

        body.dark-mode .message-content code {
            background: #2d2d2d;
            color: #e4e4e4;
        }
        </style>

        <script>
        let isProcessing = false;
        let conversationHistory = [];

        function addMessage(content, type = 'assistant', isHtml = false) {
            const messagesContainer = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;

            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';

            if (isHtml) {
                contentDiv.innerHTML = content;
            } else {
                contentDiv.textContent = content;
            }

            messageDiv.appendChild(contentDiv);
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;

            return messageDiv;
        }

        function formatClaudeResponse(text) {
            // Convert markdown-style formatting to HTML
            let formatted = text
                // Code blocks with language
                .replace(/```(\\w+)?\\n([\\s\\S]*?)```/g, '<pre><code class="language-$1">$2</code></pre>')
                // Inline code
                .replace(/`([^`]+)`/g, '<code>$1</code>')
                // Bold
                .replace(/\\*\\*([^*]+)\\*\\*/g, '<strong>$1</strong>')
                // Italic
                .replace(/\\*([^*]+)\\*/g, '<em>$1</em>')
                // Line breaks
                .replace(/\\n/g, '<br>');

            return formatted;
        }

        function showTypingIndicator() {
            const indicator = document.createElement('div');
            indicator.className = 'message assistant typing-indicator';
            indicator.id = 'typingIndicator';
            indicator.innerHTML = `
                <div class="message-content">
                    <span>Claude is thinking</span>
                    <div class="typing-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            `;

            const messagesContainer = document.getElementById('chatMessages');
            messagesContainer.appendChild(indicator);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        function hideTypingIndicator() {
            const indicator = document.getElementById('typingIndicator');
            if (indicator) {
                indicator.remove();
            }
        }

        function clearChat() {
            const messagesContainer = document.getElementById('chatMessages');
            messagesContainer.innerHTML = `
                <div class="message system-message">
                    <div class="message-content">
                        <strong>Claude</strong> is ready to help! I can assist with analysis, writing, coding, math, and much more.
                    </div>
                </div>
            `;
            conversationHistory = [];
        }

        async function sendMessage() {
            const messageInput = document.getElementById('messageInput');
            const sendButton = document.getElementById('sendButton');
            const modelSelect = document.getElementById('modelSelect');

            const message = messageInput.value.trim();
            if (!message || isProcessing) return;

            // Add user message
            addMessage(message, 'user');

            // Add to conversation history
            conversationHistory.push({
                role: 'user',
                content: message
            });

            // Clear input and disable controls
            messageInput.value = '';
            sendButton.disabled = true;
            isProcessing = true;

            // Show typing indicator
            showTypingIndicator();

            try {
                const response = await fetch('/api/claude/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: message,
                        model: modelSelect.value,
                        history: conversationHistory.slice(0, -1)  // Exclude current message
                    })
                });

                const data = await response.json();

                hideTypingIndicator();

                if (response.ok) {
                    const formattedResponse = formatClaudeResponse(data.response);
                    addMessage(formattedResponse, 'assistant', true);

                    // Add to conversation history
                    conversationHistory.push({
                        role: 'assistant',
                        content: data.response
                    });
                } else {
                    addMessage(`Error: ${data.error}`, 'error');
                    // Remove failed user message from history
                    conversationHistory.pop();
                }
            } catch (error) {
                hideTypingIndicator();
                addMessage(`Network error: ${error.message}`, 'error');
                // Remove failed user message from history
                conversationHistory.pop();
            } finally {
                sendButton.disabled = false;
                isProcessing = false;
                messageInput.focus();
            }
        }

        // Handle Enter key in textarea
        document.getElementById('messageInput').addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Focus input on page load
        document.getElementById('messageInput').focus();
        </script>
    '''

    return {'html': html_content}
