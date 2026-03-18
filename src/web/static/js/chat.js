// Script principal pour l'interface de chat ORLYNE

class OrlyneChat {
    constructor() {
        this.socket = null;
        this.messageHistory = [];
        this.isTyping = false;
        this.currentConversationId = null;
        this.energyLevel = 100;
        this.currentEmotion = 'enthousiaste';
        
        this.initElements();
        this.initEventListeners();
        this.connectWebSocket();
        this.loadHistory();
        this.startHeartbeat();
    }
    
    initElements() {
        this.messagesContainer = document.getElementById('messages');
        this.userInput = document.getElementById('user-input');
        this.sendButton = document.getElementById('send-button');
        this.languageSelect = document.getElementById('language-select');
        this.runCodeBtn = document.getElementById('run-code');
        this.formatCodeBtn = document.getElementById('format-code');
        this.explainCodeBtn = document.getElementById('explain-code');
        this.debugCodeBtn = document.getElementById('debug-code');
        this.suggestionButtons = document.querySelectorAll('.suggestion');
        
        // Stats elements
        this.modelStat = document.getElementById('model-stat');
        this.moodStat = document.getElementById('mood-stat');
        this.languagesStat = document.getElementById('languages-stat');
    }
    
    initEventListeners() {
        // Envoi de message
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-resize textarea
        this.userInput.addEventListener('input', () => {
            this.userInput.style.height = 'auto';
            this.userInput.style.height = (this.userInput.scrollHeight) + 'px';
        });
        
        // Code actions
        this.runCodeBtn.addEventListener('click', () => this.executeCode());
        this.formatCodeBtn.addEventListener('click', () => this.formatCode());
        this.explainCodeBtn.addEventListener('click', () => this.explainCode());
        this.debugCodeBtn.addEventListener('click', () => this.debugCode());
        
        // Suggestions
        this.suggestionButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                this.userInput.value = btn.textContent;
                this.sendMessage();
            });
        });
        
        // Gestion de la déconnexion
        window.addEventListener('beforeunload', () => {
            if (this.socket) {
                this.socket.close();
            }
        });
    }
    
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.socket = new WebSocket(wsUrl);
        
        this.socket.onopen = () => {
            console.log('WebSocket connecté');
            this.showToast('Connecté à Orlyne !', 'success');
        };
        
        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleIncomingMessage(data);
        };
        
        this.socket.onclose = () => {
            console.log('WebSocket déconnecté');
            this.showToast('Déconnecté, reconnexion...', 'warning');
            setTimeout(() => this.connectWebSocket(), 3000);
        };
        
        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.showToast('Erreur de connexion', 'error');
        };
    }
    
    sendMessage() {
        const message = this.userInput.value.trim();
        if (!message) return;
        
        // Afficher le message utilisateur
        this.addMessage(message, 'user');
        
        // Envoyer via WebSocket
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                prompt: message,
                max_length: 2048,
                temperature: 0.7
            }));
            
            // Afficher l'indicateur de frappe
            this.showTypingIndicator();
        } else {
            // Fallback HTTP
            this.sendMessageHTTP(message);
        }
        
        // Vider l'input
        this.userInput.value = '';
        this.userInput.style.height = 'auto';
        
        // Sauvegarder dans l'historique
        this.saveToHistory(message, 'user');
    }
    
    async sendMessageHTTP(message) {
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    prompt: message,
                    max_length: 2048,
                    temperature: 0.7
                })
            });
            
            const data = await response.json();
            this.hideTypingIndicator();
            this.addMessage(data.response, 'orlyne', data);
            
            // Mettre à jour les stats
            this.updateStats(data);
            
        } catch (error) {
            console.error('Erreur:', error);
            this.hideTypingIndicator();
            this.addMessage("Désolée, j'ai eu un problème technique. Réessaie ! 😅", 'orlyne');
        }
    }
    
    handleIncomingMessage(data) {
        this.hideTypingIndicator();
        
        if (data.response) {
            this.addMessage(data.response, 'orlyne', data);
            this.updateStats(data);
            
            // Mettre à jour l'émotion si présente
            if (data.emotion) {
                this.currentEmotion = data.emotion;
                this.updateEmotionIndicator();
            }
            
            if (data.energy) {
                this.energyLevel = data.energy;
                this.updateEnergyBar();
            }
        }
    }
    
    addMessage(text, sender, metadata = {}) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = sender === 'user' ? '👤' : '🤖';
        
        const content = document.createElement('div');
        content.className = 'content';
        
        // Traitement du texte (code, liens, etc.)
        const formattedText = this.formatMessage(text);
        content.innerHTML = formattedText;
        
        // Ajouter timestamp
        const timestamp = document.createElement('div');
        timestamp.className = 'timestamp';
        timestamp.textContent = new Date().toLocaleTimeString();
        content.appendChild(timestamp);
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    formatMessage(text) {
        // Échapper le HTML
        let escaped = this.escapeHtml(text);
        
        // Détection et formatage du code
        escaped = escaped.replace(/```(\w*)\n([\s\S]*?)```/g, (match, language, code) => {
            return `<pre><code class="language-${language}">${this.escapeHtml(code)}</code></pre>`;
        });
        
        // Détection du code inline
        escaped = escaped.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Détection des liens
        escaped = escaped.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
        
        // Retours à la ligne
        escaped = escaped.replace(/\n/g, '<br>');
        
        return escaped;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    showTypingIndicator() {
        if (this.isTyping) return;
        
        this.isTyping = true;
        
        const indicator = document.createElement('div');
        indicator.className = 'message orlyne typing';
        indicator.id = 'typing-indicator';
        
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = '🤖';
        
        const content = document.createElement('div');
        content.className = 'content typing-indicator';
        content.innerHTML = '<span></span><span></span><span></span>';
        
        indicator.appendChild(avatar);
        indicator.appendChild(content);
        
        this.messagesContainer.appendChild(indicator);
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        this.isTyping = false;
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }
    
    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
    
    async executeCode() {
        const code = this.userInput.value.trim();
        if (!code) {
            this.showToast('Entre du code à exécuter', 'warning');
            return;
        }
        
        const language = this.languageSelect.value;
        
        this.showTypingIndicator();
        
        try {
            const response = await fetch('/api/code/execute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    code: code,
                    language: language === 'auto' ? 'python' : language,
                    timeout: 30
                })
            });
            
            const data = await response.json();
            this.hideTypingIndicator();
            
            // Formatage du résultat
            let resultText = `**Exécution ${data.success ? 'réussie' : 'échouée'}**\n\n`;
            
            if (data.output) {
                resultText += `**Sortie:**\n\`\`\`\n${data.output}\n\`\`\`\n`;
            }
            
            if (data.error) {
                resultText += `**Erreur:**\n\`\`\`\n${data.error}\n\`\`\`\n`;
            }
            
            resultText += `\nCode de sortie: ${data.exit_code}`;
            
            this.addMessage(resultText, 'orlyne');
            
        } catch (error) {
            console.error('Erreur exécution:', error);
            this.hideTypingIndicator();
            this.showToast("Erreur lors de l'exécution", 'error');
        }
    }
    
    async formatCode() {
        // Logique de formatage à implémenter
        this.showToast('Formatage de code bientôt disponible', 'info');
    }
    
    async explainCode() {
        const code = this.userInput.value.trim();
        if (!code) {
            this.showToast('Entre du code à expliquer', 'warning');
            return;
        }
        
        const language = this.languageSelect.value;
        
        this.userInput.value = `Explique ce code ${language} :\n\n${code}`;
        this.sendMessage();
    }
    
    async debugCode() {
        const code = this.userInput.value.trim();
        if (!code) {
            this.showToast('Entre du code à déboguer', 'warning');
            return;
        }
        
        const language = this.languageSelect.value;
        
        this.userInput.value = `Débuggue ce code ${language} :\n\n${code}`;
        this.sendMessage();
    }
    
    updateStats(data) {
        if (data.model) {
            this.modelStat.textContent = data.model.split('/').pop();
        }
        
        if (data.emotion) {
            this.moodStat.textContent = this.getEmojiForEmotion(data.emotion) + ' ' + data.emotion;
        }
        
        // Mettre à jour les langages
        fetch('/api/languages')
            .then(res => res.json())
            .then(data => {
                this.languagesStat.textContent = data.count + '+';
            });
    }
    
    getEmojiForEmotion(emotion) {
        const emojis = {
            'joie': '😊',
            'tristesse': '😔',
            'colère': '😠',
            'enthousiasme': '🤩',
            'curiosité': '🤔',
            'empathie': '🤗',
            'fatigue': '😴',
            'concentration': '🧠',
            'humour': '😏'
        };
        return emojis[emotion.toLowerCase()] || '😐';
    }
    
    updateEmotionIndicator() {
        let indicator = document.querySelector('.emotion-indicator');
        
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.className = 'emotion-indicator';
            document.body.appendChild(indicator);
        }
        
        const emoji = this.getEmojiForEmotion(this.currentEmotion);
        indicator.innerHTML = `
            <span class="emotion-emoji">${emoji}</span>
            <span class="emotion-text">${this.currentEmotion}</span>
            <div class="energy-bar">
                <div class="energy-fill" style="width: ${this.energyLevel}%"></div>
            </div>
        `;
    }
    
    updateEnergyBar() {
        const fill = document.querySelector('.energy-fill');
        if (fill) {
            fill.style.width = `${this.energyLevel}%`;
        }
    }
    
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
    
    saveToHistory(message, role) {
        this.messageHistory.push({
            role: role,
            content: message,
            timestamp: new Date().toISOString()
        });
        
        // Sauvegarde locale
        localStorage.setItem('orlyne_history', JSON.stringify(this.messageHistory.slice(-50)));
    }
    
    loadHistory() {
        const saved = localStorage.getItem('orlyne_history');
        if (saved) {
            try {
                this.messageHistory = JSON.parse(saved);
                // Afficher les derniers messages
                this.messageHistory.slice(-10).forEach(msg => {
                    this.addMessage(msg.content, msg.role);
                });
            } catch (e) {
                console.error('Erreur chargement historique:', e);
            }
        }
    }
    
    startHeartbeat() {
        // Mise à jour périodique des stats
        setInterval(() => {
            fetch('/api/status')
                .then(res => res.json())
                .then(data => {
                    if (data.mood) {
                        this.currentEmotion = data.mood;
                        this.updateEmotionIndicator();
                    }
                    if (data.energy) {
                        this.energyLevel = data.energy;
                        this.updateEnergyBar();
                    }
                })
                .catch(err => console.log('Heartbeat error:', err));
        }, 30000); // Toutes les 30 secondes
    }
}

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    window.orlyneChat = new OrlyneChat();
});