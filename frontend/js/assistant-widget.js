(function () {
    // Inject CSS if not already present (optional, but good practice. We assume it's added to <head> so we skip injecting styles here, but we will inject the HTML)

    const widgetHTML = `
    <div class="ai-assistant-widget">
        <button class="ai-assistant-toggle" id="aiToggleBtn" title="Chat with Farmly">
            <i class="fas fa-robot"></i>
        </button>
        
        <div class="ai-assistant-window" id="aiChatWindow">
            <div class="ai-window-header">
                <div class="ai-window-header-title">
                    <i class="fas fa-sparkles"></i> Farmly
                </div>
                <div class="ai-window-actions">
                    <button class="ai-header-btn" id="aiNewChatBtn" title="New Chat"><i class="fas fa-plus"></i></button>
                    <button class="ai-header-btn" id="aiHistoryBtn" title="Previous Chats"><i class="fas fa-history"></i></button>
                    <button class="ai-close-btn" id="aiCloseBtn" title="Close Chat"><i class="fas fa-times"></i></button>
                </div>
            </div>
            
            <div class="ai-chat-messages" id="aiChatMessages">
                <div class="ai-welcome-banner" id="aiWelcomeBanner">
                    <div class="ai-welcome-icon">
                        <i class="fas fa-robot"></i>
                    </div>
                    <h3>Hi there! I am Farmly.</h3>
                    <p>I'm here to help you with crop management, disease prevention, and best farming practices.</p>
                    <div class="ai-suggested-prompts">
                        <button class="ai-prompt-btn" data-prompt="What features does AgroFast offer?">
                            <i class="fas fa-info-circle"></i> What is Farmly?
                        </button>
                        <button class="ai-prompt-btn" data-prompt="How do I treat tomato blight?">
                            <i class="fas fa-leaf"></i> How do I treat tomato blight?
                        </button>
                        <button class="ai-prompt-btn" data-prompt="When is the best time to plant maize?">
                            <i class="fas fa-calendar-alt"></i> Best time to plant maize?
                        </button>
                        <button class="ai-prompt-btn" data-prompt="What are natural ways to control aphids?">
                            <i class="fas fa-bug"></i> Natural ways to control aphids?
                        </button>
                    </div>
                </div>
                
                <div class="ai-message-wrapper ai ai-typing-indicator-wrapper" id="aiTypingIndicator">
                    <div class="ai-avatar"><i class="fas fa-robot"></i></div>
                    <div class="ai-typing-bubble">
                        <div class="ai-dot"></div>
                        <div class="ai-dot"></div>
                        <div class="ai-dot"></div>
                    </div>
                </div>
            </div>

            <div class="ai-history-panel" id="aiHistoryPanel">
                <div class="ai-history-header">
                    <h4>Chat History</h4>
                    <button class="ai-history-close-btn" id="aiHistoryCloseBtn" title="Back"><i class="fas fa-arrow-left"></i></button>
                </div>
                <div class="ai-history-list" id="aiHistoryList">
                    <!-- History items injected here -->
                </div>
            </div>
            
            <div class="ai-voice-status" id="aiVoiceStatus" style="display: none;">
                <div class="ai-voice-indicator">
                    <span class="ai-voice-pulse"></span>
                    <span id="aiVoiceText">Listening... Speak now</span>
                </div>
                <button class="ai-voice-cancel" id="aiVoiceCancel" title="Cancel voice input"><i class="fas fa-times"></i></button>
            </div>

            <div class="ai-input-area">
                <div class="ai-input-wrapper">
                    <textarea class="ai-chat-input" id="aiChatInput" placeholder="Ask anything about farming..." rows="1"></textarea>
                </div>
                <button class="ai-mic-btn" id="aiMicBtn" title="Voice Input (Click to speak)">
                    <i class="fas fa-microphone"></i>
                </button>
                <button class="ai-send-btn" id="aiSendBtn" disabled>
                    <i class="fas fa-paper-plane"></i>
                </button>
            </div>
        </div>
    </div>
    `;

    // Wait for DOM to load, then inject widget
    document.addEventListener('DOMContentLoaded', () => {
        document.body.insertAdjacentHTML('beforeend', widgetHTML);
        initAIAssistant();
    });

    function initAIAssistant() {
        const toggleBtn = document.getElementById('aiToggleBtn');
        const closeBtn = document.getElementById('aiCloseBtn');
        const chatWindow = document.getElementById('aiChatWindow');
        const chatInput = document.getElementById('aiChatInput');
        const sendBtn = document.getElementById('aiSendBtn');
        const chatMessages = document.getElementById('aiChatMessages');
        const typingIndicator = document.getElementById('aiTypingIndicator');
        const welcomeBanner = document.getElementById('aiWelcomeBanner');

        // Voice Recognition Elements & State
        const micBtn = document.getElementById('aiMicBtn');
        const voiceStatus = document.getElementById('aiVoiceStatus');
        const voiceText = document.getElementById('aiVoiceText');
        const voiceCancel = document.getElementById('aiVoiceCancel');

        let recognition = null;
        let isListening = false;

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (SpeechRecognition) {
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = true;

            const getLanguageCode = () => {
                const lang = localStorage.getItem('selectedLanguage') || localStorage.getItem('agrofast_lang') || 'en';
                const langMap = {
                    'en': 'en-US',
                    'sw': 'sw-KE',
                    'af': 'af-ZA',
                    'zu': 'zu-ZA',
                    've': 'en-ZA'
                };
                return langMap[lang] || 'en-US';
            };

            recognition.onstart = () => {
                isListening = true;
                if (micBtn) {
                    micBtn.classList.add('recording');
                    micBtn.setAttribute('title', 'Stop listening');
                    micBtn.innerHTML = '<i class="fas fa-square"></i>';
                }
                if (voiceStatus) voiceStatus.style.display = 'flex';
                if (voiceText) voiceText.textContent = 'Listening... Speak now';
            };

            recognition.onresult = (event) => {
                let interimTranscript = '';
                let finalTranscript = '';

                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript;
                    } else {
                        interimTranscript += event.results[i][0].transcript;
                    }
                }

                const currentText = finalTranscript || interimTranscript;
                if (currentText && chatInput) {
                    chatInput.value = currentText;
                    autoGrow();
                    if (voiceText) voiceText.textContent = `"${currentText}"`;
                }
            };

            recognition.onerror = (event) => {
                console.warn('Speech recognition error:', event.error);
                stopListening();
                if (event.error === 'not-allowed') {
                    appendMessage("Microphone permission was denied. Please allow microphone access in your browser to use voice input.", 'error');
                } else if (event.error !== 'no-speech' && event.error !== 'aborted') {
                    appendMessage(`Voice recognition error: ${event.error}`, 'error');
                }
            };

            recognition.onend = () => {
                stopListening();
            };
        }

        function startListening() {
            if (!recognition) {
                appendMessage("Voice recognition is not supported in this browser. Please use Chrome, Edge, or Safari.", 'error');
                return;
            }
            try {
                const lang = localStorage.getItem('selectedLanguage') || 'en';
                const langMap = { 'en': 'en-US', 'sw': 'sw-KE', 'af': 'af-ZA', 'zu': 'zu-ZA' };
                recognition.lang = langMap[lang] || 'en-US';
                recognition.start();
            } catch (err) {
                console.error("Error starting speech recognition:", err);
                stopListening();
            }
        }

        function stopListening() {
            isListening = false;
            if (micBtn) {
                micBtn.classList.remove('recording');
                micBtn.setAttribute('title', 'Voice Input (Click to speak)');
                micBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            }
            if (voiceStatus) voiceStatus.style.display = 'none';
            if (recognition) {
                try { recognition.stop(); } catch (e) {}
            }
        }

        if (micBtn) {
            micBtn.addEventListener('click', () => {
                if (isListening) {
                    stopListening();
                } else {
                    startListening();
                }
            });
        }

        // History & New Chat Elements
        const newChatBtn = document.getElementById('aiNewChatBtn');
        const historyBtn = document.getElementById('aiHistoryBtn');
        const historyPanel = document.getElementById('aiHistoryPanel');
        const historyCloseBtn = document.getElementById('aiHistoryCloseBtn');
        const historyList = document.getElementById('aiHistoryList');

        let isChatOpen = false;
        let chatHistory = [];
        let currentChatId = null;
        let currentUid = null;
        let userScans = [];
        let userFarms = [];
        let allChats = {};

        async function initFirebaseChat() {
            try {
                const { getApp } = await import("https://www.gstatic.com/firebasejs/12.7.0/firebase-app.js");
                const { getAuth, onAuthStateChanged } = await import("https://www.gstatic.com/firebasejs/12.7.0/firebase-auth.js");
                const { getDatabase, ref, get, set, onValue } = await import("https://www.gstatic.com/firebasejs/12.7.0/firebase-database.js");

                const app = getApp();
                const auth = getAuth(app);
                const db = getDatabase(app);

                let unsubScans = null;
                let unsubFarms = null;
                let unsubChats = null;

                onAuthStateChanged(auth, async (user) => {
                    if (user) {
                        currentUid = user.uid;

                        // Load all chats & listen for updates to display in history panel
                        unsubChats = onValue(ref(db, `users/${user.uid}/chats`), (snapshot) => {
                            allChats = snapshot.val() || {};
                            renderHistoryList();
                            
                            // If we don't have an active chat session, load the most recent one
                            if (!currentChatId) {
                                const chatKeys = Object.keys(allChats);
                                if (chatKeys.length > 0) {
                                    chatKeys.sort((a, b) => (allChats[b].metadata?.timestamp || 0) - (allChats[a].metadata?.timestamp || 0));
                                    loadChat(chatKeys[0]);
                                } else {
                                    startNewChat();
                                }
                            }
                        });

                        // Listen to scans realtime to provide chatbot context
                        unsubScans = onValue(ref(db, `users/${user.uid}/history`), (snapshot) => {
                            const val = snapshot.val();
                            userScans = val ? Object.values(val) : [];
                        });

                        // Listen to farms realtime to provide chatbot context
                        unsubFarms = onValue(ref(db, `users/${user.uid}/farms`), (snapshot) => {
                            const val = snapshot.val();
                            userFarms = val ? Object.values(val) : [];
                        });
                    } else {
                        currentUid = null;
                        chatHistory = [];
                        currentChatId = null;
                        userScans = [];
                        userFarms = [];
                        allChats = {};
                        if (unsubScans) { unsubScans(); unsubScans = null; }
                        if (unsubFarms) { unsubFarms(); unsubFarms = null; }
                        if (unsubChats) { unsubChats(); unsubChats = null; }
                        clearChatUI();
                    }
                });

                window.saveChatHistory = async (history) => {
                    if (currentUid && db && ref && set && currentChatId) {
                        try {
                            const firstQuery = history.find(m => m.role === 'user')?.content || "New Chat";
                            const cleanTitle = firstQuery.length > 35 ? firstQuery.substring(0, 35) + "..." : firstQuery;
                            const timestamp = Date.now();
                            
                            await set(ref(db, `users/${currentUid}/chats/${currentChatId}`), {
                                metadata: {
                                    id: currentChatId,
                                    title: cleanTitle,
                                    timestamp: timestamp
                                },
                                messages: history
                            });
                        } catch (e) {
                            console.error("Error saving chat history:", e);
                        }
                    }
                };

            } catch (error) {
                console.warn("Firebase not yet initialized: ", error);
                setTimeout(initFirebaseChat, 500);
            }
        }

        function renderHistoryList() {
            if (!historyList) return;
            historyList.innerHTML = "";

            const chatEntries = Object.entries(allChats);
            if (chatEntries.length === 0) {
                historyList.innerHTML = '<p style="color: var(--text-muted); text-align: center; margin-top: 20px; font-size: 13px;">No past chats yet</p>';
                return;
            }

            chatEntries.sort((a, b) => (b[1].metadata?.timestamp || 0) - (a[1].metadata?.timestamp || 0));

            chatEntries.forEach(([id, chatData]) => {
                const meta = chatData.metadata || { title: "Conversation", timestamp: Date.now() };
                const dateStr = new Date(meta.timestamp).toLocaleDateString(undefined, {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });

                const isActive = id === currentChatId;

                const item = document.createElement("div");
                item.className = `ai-history-item ${isActive ? 'active' : ''}`;

                const titleDiv = document.createElement("div");
                titleDiv.className = "ai-history-title";
                titleDiv.textContent = meta.title;

                const dateDiv = document.createElement("div");
                dateDiv.className = "ai-history-date";
                dateDiv.innerHTML = '<i class="far fa-clock"></i> ';
                dateDiv.appendChild(document.createTextNode(dateStr));

                item.appendChild(titleDiv);
                item.appendChild(dateDiv);
                item.addEventListener("click", () => {
                    loadChat(id);
                    historyPanel.classList.remove("active");
                });
                historyList.appendChild(item);
            });
        }

        function loadChat(chatId) {
            const chatData = allChats[chatId];
            if (!chatData) return;

            currentChatId = chatId;
            chatHistory = chatData.messages || [];

            const messages = chatMessages.querySelectorAll('.ai-message-wrapper:not(#aiTypingIndicator)');
            messages.forEach(m => m.remove());

            if (chatHistory.length > 0 && welcomeBanner) {
                welcomeBanner.style.display = 'none';
            } else if (welcomeBanner) {
                welcomeBanner.style.display = 'block';
            }

            chatHistory.forEach(msg => {
                const sender = msg.role === 'user' ? 'user' : 'ai';
                appendMessage(msg.content, sender, sender === 'ai');
            });
        }

        function startNewChat() {
            currentChatId = "chat_" + Date.now();
            chatHistory = [];
            clearChatUI();
        }

        function clearChatUI() {
            const messages = chatMessages.querySelectorAll('.ai-message-wrapper:not(#aiTypingIndicator)');
            messages.forEach(m => m.remove());
            if (welcomeBanner) welcomeBanner.style.display = 'block';
        }

        // Run initialization
        initFirebaseChat();

        // Toggle chat window
        toggleBtn.addEventListener('click', () => {
            isChatOpen = !isChatOpen;
            if (isChatOpen) {
                chatWindow.classList.add('active');
                chatInput.focus();
                toggleBtn.style.transform = 'scale(0)';
            } else {
                chatWindow.classList.remove('active');
                toggleBtn.style.transform = 'scale(1)';
            }
        });

        // Close btn
        closeBtn.addEventListener('click', () => {
            isChatOpen = false;
            chatWindow.classList.remove('active');
            toggleBtn.style.transform = 'scale(1)';
        });

        // Toggle History Panel
        if (historyBtn && historyPanel) {
            historyBtn.addEventListener('click', () => {
                historyPanel.classList.toggle('active');
            });
        }

        if (historyCloseBtn && historyPanel) {
            historyCloseBtn.addEventListener('click', () => {
                historyPanel.classList.remove('active');
            });
        }

        // New Chat Button click
        if (newChatBtn) {
            newChatBtn.addEventListener('click', () => {
                startNewChat();
                if (historyPanel) historyPanel.classList.remove('active');
            });
        }

        // Auto-grow textarea
        const autoGrow = () => {
            chatInput.style.height = "46px";
            chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + "px";

            if (chatInput.value.trim().length > 0) {
                sendBtn.disabled = false;
                sendBtn.style.opacity = "1";
            } else {
                sendBtn.disabled = true;
                sendBtn.style.opacity = "0.5";
            }
        };

        chatInput.addEventListener('input', autoGrow);

        // Handle Enter key (Send message but allow Shift+Enter for new line)
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Suggested Prompts
        const promptBtns = document.querySelectorAll('.ai-prompt-btn');
        promptBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const prompt = btn.getAttribute('data-prompt');
                chatInput.value = prompt;
                autoGrow();
                chatInput.focus();
            });
        });

        sendBtn.addEventListener('click', sendMessage);

        // Expose global helper to query AI assistant from other UI widgets (e.g. Crop Scanner)
        window.askAgroFastAI = (promptText) => {
            isChatOpen = true;
            chatWindow.classList.add('active');
            toggleBtn.style.transform = 'scale(0)';
            
            // Start a new chat to avoid prolonged chats!
            startNewChat();
            
            chatInput.value = promptText;
            autoGrow();
            sendMessage();
        };

        function scrollToBottom() {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function appendMessage(text, sender, isMarkdown = false) {
            if (welcomeBanner) welcomeBanner.style.display = 'none';

            if (sender === 'error') {
                const msgDiv = document.createElement('div');
                msgDiv.className = 'ai-message error';
                msgDiv.textContent = text;
                chatMessages.insertBefore(msgDiv, typingIndicator);
                scrollToBottom();
                return;
            }

            const wrapperDiv = document.createElement('div');
            wrapperDiv.className = `ai-message-wrapper ${sender}`;

            const avatarDiv = document.createElement('div');
            avatarDiv.className = 'ai-avatar';
            if (sender === 'ai') {
                avatarDiv.innerHTML = '<i class="fas fa-robot"></i>';
            } else {
                avatarDiv.innerHTML = '<i class="fas fa-user" style="color: var(--primary)"></i>';
            }

            const msgDiv = document.createElement('div');
            msgDiv.className = `ai-message ${sender}`;

            if (isMarkdown && sender === 'ai' && typeof marked !== 'undefined') {
                msgDiv.innerHTML = marked.parse(text);
            } else {
                msgDiv.textContent = text;
            }

            if (sender === 'ai') {
                const speakBtn = document.createElement('button');
                speakBtn.className = 'ai-speak-btn';
                speakBtn.title = 'Listen to response';
                speakBtn.innerHTML = '<i class="fas fa-volume-up"></i>';

                let isSpeaking = false;
                speakBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    if ('speechSynthesis' in window) {
                        if (isSpeaking || window.speechSynthesis.speaking) {
                            window.speechSynthesis.cancel();
                            isSpeaking = false;
                            speakBtn.classList.remove('speaking');
                            speakBtn.innerHTML = '<i class="fas fa-volume-up"></i>';
                            return;
                        }

                        // Strip markdown / html formatting for clean text reading
                        const cleanText = msgDiv.innerText || msgDiv.textContent;
                        const utterance = new SpeechSynthesisUtterance(cleanText);
                        
                        const lang = localStorage.getItem('selectedLanguage') || localStorage.getItem('agrofast_lang') || 'en';
                        const langMap = {
                            'en': 'en-US',
                            'sw': 'sw-KE',
                            'af': 'af-ZA',
                            'zu': 'zu-ZA',
                            've': 'en-ZA'
                        };
                        utterance.lang = langMap[lang] || 'en-US';
                        utterance.rate = 0.95;

                        utterance.onstart = () => {
                            isSpeaking = true;
                            speakBtn.classList.add('speaking');
                            speakBtn.innerHTML = '<i class="fas fa-volume-mute"></i>';
                        };

                        utterance.onend = utterance.onerror = () => {
                            isSpeaking = false;
                            speakBtn.classList.remove('speaking');
                            speakBtn.innerHTML = '<i class="fas fa-volume-up"></i>';
                        };

                        window.speechSynthesis.speak(utterance);
                    } else {
                        alert("Text-to-speech is not supported in your browser.");
                    }
                });

                msgDiv.appendChild(speakBtn);
            }

            wrapperDiv.appendChild(avatarDiv);
            wrapperDiv.appendChild(msgDiv);

            chatMessages.insertBefore(wrapperDiv, typingIndicator);
            scrollToBottom();
        }

        async function sendMessage() {
            const message = chatInput.value.trim();
            if (!message) return;

            // Immediately display user message
            appendMessage(message, 'user');

            // Save user message to conversational history
            chatHistory.push({ role: 'user', content: message });

            // Reset input
            chatInput.value = '';
            autoGrow();

            // Show typing indicator
            typingIndicator.classList.add('active');
            scrollToBottom();

            try {
                const response = await fetch(`${window.getBackendUrl()}/chat`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ 
                        message, 
                        history: chatHistory,
                        scans: userScans,
                        farms: userFarms
                    })
                });

                const data = await response.json();
                typingIndicator.classList.remove('active');

                if (response.ok) {
                    appendMessage(data.response, 'ai', true);
                    // Save assistant message to conversational history
                    chatHistory.push({ role: 'model', content: data.response });
                    // Save to database
                    if (window.saveChatHistory) {
                        await window.saveChatHistory(chatHistory);
                    }
                } else {
                    // Remove failed user message from history
                    chatHistory.pop();
                    appendMessage(data.error || "Sorry, I'm having trouble connecting right now.", 'error');
                }
            } catch (error) {
                // Remove failed user message from history
                chatHistory.pop();
                typingIndicator.classList.remove('active');
                appendMessage("Network error. Please make sure the backend is running.", 'error');
            }
        }
    }
})();
