// 配置
const CONFIG = {
    apiUrl: localStorage.getItem('apiUrl') || 'http://127.0.0.1:8001',
    topK: parseInt(localStorage.getItem('topK')) || 5,
    enableRewrite: localStorage.getItem('enableRewrite') !== 'false',
};

let sessionId = null;
let isStreaming = false;

// DOM 元素
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const clearBtn = document.getElementById('clearBtn');
const settingsBtn = document.getElementById('settingsBtn');
const settingsModal = document.getElementById('settingsModal');
const closeModal = document.getElementById('closeModal');
const saveSettings = document.getElementById('saveSettings');
const streamMode = document.getElementById('streamMode');
const debugMode = document.getElementById('debugMode');

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    loadSettings();
    setupEventListeners();
    autoResizeTextarea();
    restoreHistoryOnLoad();
});

async function restoreHistoryOnLoad() {
    try {
        const url = `${CONFIG.apiUrl}/api/chat/history`;
        const response = await fetch(url, { method: 'GET', credentials: 'include' });
        if (!response.ok) return;

        const result = await response.json();
        if (!result || result.code !== 'OK') return;

        const data = result.data || {};
        if (data.session_id) sessionId = data.session_id;

        const history = Array.isArray(data.history) ? data.history : [];
        if (history.length === 0) return;

        const welcomeMsg = document.querySelector('.welcome-message');
        if (welcomeMsg) welcomeMsg.remove();
        chatMessages.innerHTML = '';

        for (const m of history) {
            if (!m || !m.role) continue;
            if (m.role !== 'user' && m.role !== 'assistant') continue;
            addMessage(m.role, m.content || '');
        }
        scrollToBottom();
    } catch (e) {
        console.warn('恢复历史失败:', e);
    }
}

// 设置事件监听
function setupEventListeners() {
    sendBtn.addEventListener('click', handleSend);
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    });
    userInput.addEventListener('input', autoResizeTextarea);

    clearBtn.addEventListener('click', clearChat);
    settingsBtn.addEventListener('click', () => settingsModal.classList.add('show'));
    closeModal.addEventListener('click', () => settingsModal.classList.remove('show'));
    saveSettings.addEventListener('click', handleSaveSettings);

    // 快捷按钮
    document.querySelectorAll('.quick-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const query = btn.getAttribute('data-query');
            userInput.value = query;
            handleSend();
        });
    });

    settingsModal.addEventListener('click', (e) => {
        if (e.target === settingsModal) {
            settingsModal.classList.remove('show');
        }
    });
}

// 自动调整输入框高度
function autoResizeTextarea() {
    userInput.style.height = 'auto';
    userInput.style.height = Math.min(userInput.scrollHeight, 150) + 'px';
}

// 加载设置
function loadSettings() {
    document.getElementById('apiUrl').value = CONFIG.apiUrl;
    document.getElementById('topK').value = CONFIG.topK;
    document.getElementById('enableRewrite').checked = CONFIG.enableRewrite;
}

// 保存设置
function handleSaveSettings() {
    CONFIG.apiUrl = document.getElementById('apiUrl').value;
    CONFIG.topK = parseInt(document.getElementById('topK').value);
    CONFIG.enableRewrite = document.getElementById('enableRewrite').checked;

    localStorage.setItem('apiUrl', CONFIG.apiUrl);
    localStorage.setItem('topK', CONFIG.topK);
    localStorage.setItem('enableRewrite', CONFIG.enableRewrite);

    settingsModal.classList.remove('show');
    showToast('设置已保存');
}

// 发送消息
async function handleSend() {
    const query = userInput.value.trim();
    if (!query || isStreaming) return;

    const welcomeMsg = document.querySelector('.welcome-message');
    if (welcomeMsg) welcomeMsg.remove();

    addMessage('user', query);
    userInput.value = '';
    autoResizeTextarea();

    isStreaming = true;
    sendBtn.disabled = true;

    const msgId = 'msg-' + Date.now();
    addMessage('assistant', '', msgId);
    showTyping(msgId);

    try {
        if (streamMode.checked) {
            await handleStreamChat(query, msgId);
        } else {
            await handleNormalChat(query, msgId);
        }
    } catch (error) {
        console.error('发送失败:', error);
        updateMessage(msgId, '抱歉，发生了错误：' + error.message);
        showToast('发送失败：' + error.message);
    } finally {
        isStreaming = false;
        sendBtn.disabled = false;
        hideTyping(msgId);
    }
}

// 流式聊天处理
async function handleStreamChat(query, msgId) {
    const url = `${CONFIG.apiUrl}/api/chat/stream`;
    const payload = {
        query: query,
        session_id: sessionId,
        top_k: CONFIG.topK,
        enable_heavy_rewrite: CONFIG.enableRewrite
    };

    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload)
    });

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';
    let fullContent = '';
    let debugData = null;

    hideTyping(msgId);

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();

        for (const line of lines) {
            if (!line.trim() || !line.startsWith('data: ')) continue;

            const data = line.slice(6);
            if (data === '[DONE]') continue;

            try {
                const event = JSON.parse(data);

                if (event.type === 'meta') {
                    // 后端在开头发 meta，包含 session_id
                    if (event.session_id) sessionId = event.session_id;
                    debugData = event;
                } else if (event.type === 'delta') {
                    fullContent += event.content || '';
                    updateMessage(msgId, fullContent);
                } else if (event.type === 'done') {
                    debugData = { ...(debugData || {}), ...event, full_content: fullContent };
                } else if (event.type === 'error') {
                    throw new Error(event.message || '未知错误');
                }
            } catch (e) {
                console.error('解析SSE事件失败:', e, line);
            }
        }
    }

    if (debugMode.checked && debugData) {
        addDebugInfo(msgId, debugData);
    }
}

// 普通聊天处理
async function handleNormalChat(query, msgId) {
    const url = `${CONFIG.apiUrl}/api/chat`;
    const payload = {
        query: query,
        session_id: sessionId,
        top_k: CONFIG.topK,
        enable_heavy_rewrite: CONFIG.enableRewrite
    };

    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload)
    });

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();
    hideTyping(msgId);

    // 后端统一返回 ApiResponse: { code, message, data }
    if (!result || result.code !== 'OK') {
        throw new Error((result && result.message) ? result.message : '请求失败');
    }
    const data = result.data || {};

    updateMessage(msgId, data.answer || data.clarify_question || '');
    if (data.session_id) sessionId = data.session_id;

    if (debugMode.checked) {
        addDebugInfo(msgId, data);
    }
}

// 添加消息到聊天区域
function addMessage(role, content, msgId = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;
    if (msgId) messageDiv.id = msgId;

    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.textContent = role === 'user' ? '👤' : '🤖';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = formatMarkdown(content);

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);

    setTimeout(() => messageDiv.classList.add('fade-in'), 10);
    scrollToBottom();

    return msgId || messageDiv.id;
}

// 更新消息内容
function updateMessage(msgId, content) {
    const messageDiv = document.getElementById(msgId);
    if (!messageDiv) return;

    const contentDiv = messageDiv.querySelector('.message-content');
    if (contentDiv) {
        contentDiv.innerHTML = formatMarkdown(content);
        scrollToBottom();
    }
}

// 显示打字动画
function showTyping(msgId) {
    const messageDiv = document.getElementById(msgId);
    if (!messageDiv) return;

    const contentDiv = messageDiv.querySelector('.message-content');
    if (contentDiv) {
        contentDiv.innerHTML = '<span class="typing-indicator"><span></span><span></span><span></span></span>';
    }
}

// 隐藏打字动画
function hideTyping(msgId) {
    const messageDiv = document.getElementById(msgId);
    if (!messageDiv) return;

    const typingIndicator = messageDiv.querySelector('.typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// 清空对话
function clearChat() {
    if (!confirm('确定要清空对话吗？')) return;

    chatMessages.innerHTML = '';
    sessionId = null;
    showToast('对话已清空');

    const welcomeDiv = document.createElement('div');
    welcomeDiv.className = 'welcome-message';
    welcomeDiv.innerHTML = `
        <h2>👋 欢迎使用 RAG 智能助手</h2>
        <p>我可以帮您查询和分析文档内容</p>
    `;
    chatMessages.appendChild(welcomeDiv);
}

// 添加调试信息
function addDebugInfo(msgId, data) {
    const messageDiv = document.getElementById(msgId);
    if (!messageDiv) return;

    const debugDiv = document.createElement('div');
    debugDiv.className = 'debug-info';
    debugDiv.innerHTML = `
        <details>
            <summary>🔍 调试信息</summary>
            <pre>${JSON.stringify(data, null, 2)}</pre>
        </details>
    `;

    messageDiv.appendChild(debugDiv);
}

// 显示提示消息
function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// 自动滚动到底部
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 简单的 Markdown 渲染
function formatMarkdown(text) {
    if (!text) return '';

    let html = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

    // 代码块
    html = html.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
        return `<pre><code class="language-${lang || 'text'}">${code.trim()}</code></pre>`;
    });

    // 行内代码
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

    // 粗体
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

    // 斜体
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');

    // 链接
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');

    // 换行
    html = html.replace(/\n/g, '<br>');

    return html;
}
