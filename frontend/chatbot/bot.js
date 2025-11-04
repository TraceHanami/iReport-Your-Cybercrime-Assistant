 
// chatbot.js - Chatbot integration for iReport
class ChatbotManager {
    constructor() {
        this.currentSession = null;
        this.messages = [];
        this.isOpen = false;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadChatHistory();
        this.initializeBot();
    }

    setupEventListeners() {
        // Chat toggle
        const chatToggle = document.getElementById('chatbotToggle');
        if (chatToggle) {
            chatToggle.addEventListener('click', () => this.toggleChat());
        }

        // Send message
        const sendButton = document.getElementById('sendMessage');
        const messageInput = document.getElementById('messageInput');
        
        if (sendButton && messageInput) {
            sendButton.addEventListener('click', () => this.sendMessage());
            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.sendMessage();
                }
            });
        }

        // Clear chat
        const clearButton = document.getElementById('clearChat');
        if (clearButton) {
            clearButton.addEventListener('click', () => this.clearChat());
        }

        // Quick actions
        const quickActions = document.querySelectorAll('.quick-action');
        quickActions.forEach(action => {
            action.addEventListener('click', (e) => this.handleQuickAction(e));
        });

        // Chat suggestions
        const suggestions = document.querySelectorAll('.suggestion-item');
        suggestions.forEach(suggestion => {
            suggestion.addEventListener('click', (e) => this.handleSuggestion(e));
        });
    }

    initializeBot() {
        // Initialize chatbot with welcome message
        this.addBotMessage('Hello! I\'m your iReport assistant. How can I help you today?', 'info');
        
        // Show quick actions
        this.showQuickActions();
    }

    async toggleChat() {
        const chatContainer = document.getElementById('chatbotContainer');
        if (!chatContainer) return;

        this.isOpen = !this.isOpen;
        
        if (this.isOpen) {
            chatContainer.classList.add('open');
            this.focusInput();
        } else {
            chatContainer.classList.remove('open');
        }
    }

    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        if (!messageInput) return;

        const message = messageInput.value.trim();
        if (!message) return;

        // Add user message to chat
        this.addUserMessage(message);
        messageInput.value = '';

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Start session if not already started
            if (!this.currentSession) {
                const sessionResponse = await API_SERVICE.startChatSession();
                if (sessionResponse.success) {
                    this.currentSession = sessionResponse.data.session_id;
                }
            }

            // Send message to backend
            const response = await API_SERVICE.sendChatMessage(this.currentSession, message);
            
            if (response.success) {
                // Add bot response
                this.addBotMessage(response.data.response, 'info');
            } else {
                throw new Error(response.message || 'Failed to get response');
            }

        } catch (error) {
            console.error('Chatbot error:', error);
            this.addBotMessage(
                'I apologize, but I\'m having trouble connecting right now. Please try again later or contact support.',
                'error'
            );
        } finally {
            this.hideTypingIndicator();
            this.scrollToBottom();
        }
    }

    addUserMessage(message) {
        this.messages.push({
            type: 'user',
            content: message,
            timestamp: new Date()
        });

        this.renderMessage('user', message);
    }

    addBotMessage(message, type = 'info') {
        this.messages.push({
            type: 'bot',
            content: message,
            timestamp: new Date(),
            messageType: type
        });

        this.renderMessage('bot', message, type);
    }

    renderMessage(sender, content, type = 'info') {
        const messagesContainer = document.getElementById('chatMessages');
        if (!messagesContainer) return;

        const messageElement = APP_UTILS.DOM.createElement('div', {
            className: `message ${sender}-message ${type}`
        });

        const messageContent = APP_UTILS.DOM.createElement('div', {
            className: 'message-content'
        }, [content]);

        const timestamp = APP_UTILS.DOM.createElement('div', {
            className: 'message-timestamp'
        }, [APP_UTILS.Date.formatDate(new Date(), 'hh:mm')]);

        messageElement.appendChild(messageContent);
        messageElement.appendChild(timestamp);
        messagesContainer.appendChild(messageElement);

        this.scrollToBottom();
    }

    showTypingIndicator() {
        const messagesContainer = document.getElementById('chatMessages');
        if (!messagesContainer) return;

        const typingIndicator = APP_UTILS.DOM.createElement('div', {
            className: 'message bot-message typing-indicator',
            id: 'typingIndicator'
        });

        const typingContent = APP_UTILS.DOM.createElement('div', {
            className: 'typing-dots'
        }, [
            APP_UTILS.DOM.createElement('span', {}, []),
            APP_UTILS.DOM.createElement('span', {}, []),
            APP_UTILS.DOM.createElement('span', {}, [])
        ]);

        typingIndicator.appendChild(typingContent);
        messagesContainer.appendChild(typingIndicator);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    showQuickActions() {
        const quickActionsContainer = document.getElementById('quickActions');
        if (!quickActionsContainer) return;

        const actions = [
            { icon: 'fas fa-clipboard-list', text: 'File Complaint', action: 'file_complaint' },
            { icon: 'fas fa-search', text: 'Track Case', action: 'track_case' },
            { icon: 'fas fa-question-circle', text: 'Get Help', action: 'get_help' },
            { icon: 'fas fa-phone', text: 'Emergency', action: 'emergency' }
        ];

        const actionsHTML = actions.map(action => `
            <button class="quick-action btn btn-outline-primary btn-sm" data-action="${action.action}">
                <i class="${action.icon} me-1"></i>
                ${action.text}
            </button>
        `).join('');

        quickActionsContainer.innerHTML = actionsHTML;

        // Re-attach event listeners
        const quickActionButtons = document.querySelectorAll('.quick-action');
        quickActionButtons.forEach(btn => {
            btn.addEventListener('click', (e) => this.handleQuickAction(e));
        });
    }

    handleQuickAction(e) {
        const action = e.target.closest('.quick-action').getAttribute('data-action');
        
        switch (action) {
            case 'file_complaint':
                this.guideFileComplaint();
                break;
            case 'track_case':
                this.guideTrackCase();
                break;
            case 'get_help':
                this.provideHelp();
                break;
            case 'emergency':
                this.handleEmergency();
                break;
        }
    }

    handleSuggestion(e) {
        const suggestion = e.target.textContent;
        document.getElementById('messageInput').value = suggestion;
        this.sendMessage();
    }

    guideFileComplaint() {
        this.addBotMessage('I can help you file a complaint. Here\'s what I need to know:', 'info');
        this.addBotMessage('1. What type of crime are you reporting? (theft, assault, fraud, etc.)', 'info');
        this.addBotMessage('2. When and where did it happen?', 'info');
        this.addBotMessage('3. Can you describe what occurred?', 'info');
        this.addBotMessage('You can type your answers, or I can guide you through each step.', 'info');
    }

    guideTrackCase() {
        this.addBotMessage('To track your complaint, I\'ll need your Case ID.', 'info');
        this.addBotMessage('You can find it in your email confirmation or in your complaint history.', 'info');
        this.addBotMessage('Please provide your Case ID, and I\'ll get the latest status for you.', 'info');
    }

    provideHelp() {
        this.addBotMessage('I\'m here to help! Here are some things I can assist with:', 'info');
        this.addBotMessage('• Filing new complaints', 'info');
        this.addBotMessage('• Tracking existing cases', 'info');
        this.addBotMessage('• Answering questions about iReport', 'info');
        this.addBotMessage('• Providing safety information', 'info');
        this.addBotMessage('What would you like to know?', 'info');
    }

    handleEmergency() {
        this.addBotMessage('🚨 <strong>EMERGENCY ASSISTANCE</strong> 🚨', 'emergency');
        this.addBotMessage('If this is a life-threatening emergency, please:', 'emergency');
        this.addBotMessage('1. <strong>Call emergency services immediately: 100</strong>', 'emergency');
        this.addBotMessage('2. Provide your location and nature of emergency', 'emergency');
        this.addBotMessage('3. Stay on the line until help arrives', 'emergency');
        this.addBotMessage('For non-emergency police assistance, you can also call: 112', 'emergency');
    }

    async loadChatHistory() {
        if (!isAuthenticated()) return;

        try {
            const response = await API_SERVICE.getUserChatSessions();
            if (response.success && response.data.sessions.length > 0) {
                // Load the most recent session
                const recentSession = response.data.sessions[0];
                this.currentSession = recentSession.id;
                
                // Load session history
                const historyResponse = await API_SERVICE.getChatSessionHistory(this.currentSession);
                if (historyResponse.success) {
                    this.loadSessionHistory(historyResponse.data.messages);
                }
            }
        } catch (error) {
            console.error('Load chat history error:', error);
        }
    }

    loadSessionHistory(messages) {
        if (!messages || messages.length === 0) return;

        // Clear current messages
        this.messages = [];
        const messagesContainer = document.getElementById('chatMessages');
        if (messagesContainer) {
            messagesContainer.innerHTML = '';
        }

        // Load historical messages
        messages.forEach(msg => {
            if (msg.sender === 'user') {
                this.addUserMessage(msg.content);
            } else {
                this.addBotMessage(msg.content, msg.type || 'info');
            }
        });

        this.scrollToBottom();
    }

    async clearChat() {
        const confirmed = await APP_UTILS.Notification.showConfirm(
            'Clear chat history? This action cannot be undone.',
            'Clear Chat'
        );

        if (!confirmed) return;

        // Clear local messages
        this.messages = [];
        const messagesContainer = document.getElementById('chatMessages');
        if (messagesContainer) {
            messagesContainer.innerHTML = '';
        }

        // Delete session from backend if exists
        if (this.currentSession) {
            try {
                await API_SERVICE.deleteChatSession(this.currentSession);
            } catch (error) {
                console.error('Delete session error:', error);
            }
            this.currentSession = null;
        }

        // Restart with welcome message
        this.initializeBot();
    }

    focusInput() {
        const messageInput = document.getElementById('messageInput');
        if (messageInput) {
            messageInput.focus();
        }
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('chatMessages');
        if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }

    // Utility methods for chatbot responses
    generateQuickReplies() {
        const replies = [
            'How do I file a complaint?',
            'Where can I track my case?',
            'What information do I need to file a report?',
            'How long does it take to resolve a case?'
        ];

        return replies;
    }

    // Auto-suggest based on user input
    setupAutoSuggest() {
        const messageInput = document.getElementById('messageInput');
        if (!messageInput) return;

        messageInput.addEventListener('input', (e) => {
            this.handleInputSuggestions(e.target.value);
        });
    }

    handleInputSuggestions(input) {
        const suggestionsContainer = document.getElementById('suggestions');
        if (!suggestionsContainer) return;

        if (input.length < 2) {
            suggestionsContainer.style.display = 'none';
            return;
        }

        const suggestions = this.generateSuggestions(input);
        if (suggestions.length > 0) {
            const suggestionsHTML = suggestions.map(suggestion => `
                <div class="suggestion-item">${suggestion}</div>
            `).join('');

            suggestionsContainer.innerHTML = suggestionsHTML;
            suggestionsContainer.style.display = 'block';

            // Re-attach event listeners
            const suggestionItems = document.querySelectorAll('.suggestion-item');
            suggestionItems.forEach(item => {
                item.addEventListener('click', (e) => this.handleSuggestion(e));
            });
        } else {
            suggestionsContainer.style.display = 'none';
        }
    }

    generateSuggestions(input) {
        const commonQuestions = {
            'file': ['How to file a complaint?', 'What information do I need for filing?'],
            'track': ['How to track my case?', 'Where can I find my Case ID?'],
            'status': ['What is my case status?', 'How long does investigation take?'],
            'help': ['Get help with iReport', 'Contact support'],
            'emergency': ['Emergency contact numbers', 'Immediate police assistance']
        };

        const inputLower = input.toLowerCase();
        const suggestions = [];

        Object.entries(commonQuestions).forEach(([keyword, questions]) => {
            if (inputLower.includes(keyword)) {
                suggestions.push(...questions);
            }
        });

        return suggestions.slice(0, 3); // Return top 3 suggestions
    }

    // Analytics for chatbot usage
    trackChatbotUsage(action, data = {}) {
        const usageData = {
            action: action,
            session_id: this.currentSession,
            timestamp: new Date().toISOString(),
            user_id: getUserId(),
            ...data
        };

        // In a real application, you'd send this to your analytics service
        console.log('Chatbot usage:', usageData);
    }
}

// Initialize Chatbot Manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.chatbotManager = new ChatbotManager();
});