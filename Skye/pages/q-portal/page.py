def get_content():
    """Return the HTML content for the Gemini Portal page"""
    
    html_content = '''
        <div class="gemini-portal">
            <h2><i class="fas fa-brain"></i> Gemini Portal</h2>
            
            <div class="chat-container">
                <div class="chat-messages" id="chatMessages">
                    <div class="message system-message">
                        <div class="message-content">
                            <strong>Gemini AI</strong> is ready to help! Ask me anything - I can analyze text, generate content, answer questions, help with coding, and much more.
                        </div>
                    </div>
                </div>
                
                <div class="chat-input-container">
                    <div class="input-group">
                        <textarea id="messageInput" placeholder="Ask Gemini anything..." rows="4"></textarea>
                        <button id="sendButton" onclick="sendMessage()">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                    <div class="model-selector">
                        <label for="modelSelect">Model:</label>
                        <select id="modelSelect">
                            <option value="models/gemini-pro">Loading models...</option>
                        </select>
                    </div>
                </div>
            </div>
        </div>
        
        <style>
        .gemini-portal {
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
            background: #007bff;
            color: white;
        }
        
        .message.assistant .message-content {
            background: white;
            border: 1px solid #dee2e6;
            color: #333;
        }
        
        .message.system-message .message-content {
            background: #e3f2fd;
            border: 1px solid #bbdefb;
            color: #1976d2;
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
            border-color: #007bff;
            box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
        }
        
        .input-group textarea::placeholder {
            color: #6c757d;
        }
        
        .input-group button {
            background: #007bff;
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
            background: #0056b3;
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
            background: #f8f9fa;
            padding: 0.5rem;
            border-radius: 4px;
            overflow-x: auto;
            margin: 0.5rem 0;
            border: 1px solid #dee2e6;
        }
        
        .message-content code {
            background: #f8f9fa;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            border: 1px solid #dee2e6;
        }
        
        .message-content pre code {
            background: none;
            padding: 0;
            border: none;
        }
        </style>
        
        <script>
        let isProcessing = false;
        
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
        
        function formatGeminiResponse(text) {
            // Convert markdown-style formatting to HTML
            let formatted = text
                .replace(/```([\\s\\S]*?)```/g, '<pre><code>$1</code></pre>')
                .replace(/`([^`]+)`/g, '<code>$1</code>')
                .replace(/\\*\\*([^*]+)\\*\\*/g, '<strong>$1</strong>')
                .replace(/\\*([^*]+)\\*/g, '<em>$1</em>')
                .replace(/\\n/g, '<br>');
            
            return formatted;
        }
        
        function showTypingIndicator() {
            const indicator = document.createElement('div');
            indicator.className = 'message assistant typing-indicator';
            indicator.id = 'typingIndicator';
            indicator.innerHTML = `
                <div class="message-content">
                    <span>Gemini is thinking</span>
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
        
        async function sendMessage() {
            const messageInput = document.getElementById('messageInput');
            const sendButton = document.getElementById('sendButton');
            const modelSelect = document.getElementById('modelSelect');
            
            const message = messageInput.value.trim();
            if (!message || isProcessing) return;
            
            // Add user message
            addMessage(message, 'user');
            
            // Clear input and disable controls
            messageInput.value = '';
            sendButton.disabled = true;
            isProcessing = true;
            
            // Show typing indicator
            showTypingIndicator();
            
            try {
                const response = await fetch('/api/gemini/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: message,
                        model: modelSelect.value
                    })
                });
                
                const data = await response.json();
                
                hideTypingIndicator();
                
                if (response.ok) {
                    const formattedResponse = formatGeminiResponse(data.response);
                    addMessage(formattedResponse, 'assistant', true);
                } else {
                    addMessage(`Error: ${data.error}`, 'error');
                }
            } catch (error) {
                hideTypingIndicator();
                addMessage(`Network error: ${error.message}`, 'error');
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
        
        // Load available models
        async function loadModels() {
            try {
                const response = await fetch('/api/gemini/models');
                const data = await response.json();
                
                const modelSelect = document.getElementById('modelSelect');
                modelSelect.innerHTML = '';
                
                if (response.ok && data.models) {
                    let defaultSelected = false;
                    data.models.forEach(model => {
                        const option = document.createElement('option');
                        option.value = model.name;
                        option.textContent = model.display_name;
                        
                        // Default to Gemini 2.5 Flash if available
                        if (model.display_name.includes('Gemini 2.5 Flash') && !defaultSelected) {
                            option.selected = true;
                            defaultSelected = true;
                        }
                        
                        modelSelect.appendChild(option);
                    });
                    
                    // If Gemini 2.5 Flash wasn't found, try other Flash models
                    if (!defaultSelected) {
                        const options = modelSelect.options;
                        for (let i = 0; i < options.length; i++) {
                            if (options[i].textContent.includes('Flash')) {
                                options[i].selected = true;
                                break;
                            }
                        }
                    }
                } else {
                    // Fallback models
                    const fallbackModels = [
                        { name: 'models/gemini-pro', display_name: 'Gemini Pro' },
                        { name: 'models/gemini-1.5-flash', display_name: 'Gemini 1.5 Flash' }
                    ];
                    
                    fallbackModels.forEach(model => {
                        const option = document.createElement('option');
                        option.value = model.name;
                        option.textContent = model.display_name;
                        modelSelect.appendChild(option);
                    });
                }
            } catch (error) {
                console.error('Failed to load models:', error);
                // Use fallback
                const modelSelect = document.getElementById('modelSelect');
                modelSelect.innerHTML = '<option value="models/gemini-pro">Gemini Pro</option>';
            }
        }
        
        // Load models and focus input on page load
        loadModels();
        document.getElementById('messageInput').focus();
        </script>
    '''
    
    return {'html': html_content}