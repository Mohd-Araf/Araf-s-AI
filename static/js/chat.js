/**
 * Chat and SSE Streaming logic for Araf's Assistant
 */

let currentConversationId = null;
let isGenerating = false;
let isWebSearchEnabled = true;

// DOM Elements
const messagesContainer = document.getElementById('messages-container');
const welcomeScreen = document.getElementById('welcome-screen');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const conversationsContainer = document.getElementById('conversations-container');
const webSearchToggle = document.getElementById('web-search-toggle');
const searchStatusDot = document.getElementById('search-status-dot');
const modelSelect = document.getElementById('model-select');
const newChatBtn = document.getElementById('new-chat-btn');
const clearChatBtn = document.getElementById('clear-chat-btn');

// Markdown configuration
if (window.marked) {
  marked.setOptions({
    breaks: true,
    gfm: true,
    highlight: function(code, lang) {
      if (window.hljs && hljs.getLanguage(lang)) {
        try {
          return hljs.highlight(code, { language: lang }).value;
        } catch (e) {}
      }
      return code;
    }
  });
}

/**
 * Load conversations list
 */
async function loadConversations() {
  if (!getAuthToken()) return;

  try {
    const res = await fetch('/api/v1/chat/conversations/', {
      headers: getAuthHeaders()
    });
    if (res.status === 401) {
      logoutUser();
      return;
    }
    const data = await res.json();
    renderConversationsList(data);
  } catch (err) {
    console.error('Error fetching conversations:', err);
  }
}

function renderConversationsList(conversations) {
  conversationsContainer.innerHTML = '';

  if (!conversations || conversations.length === 0) {
    conversationsContainer.innerHTML = '<div style="color: var(--text-muted); font-size: 0.8rem; padding: 8px;">No chats yet</div>';
    return;
  }

  conversations.forEach(conv => {
    const item = document.createElement('div');
    item.className = `chat-item ${conv.id === currentConversationId ? 'active' : ''}`;
    item.dataset.id = conv.id;

    item.innerHTML = `
      <span class="chat-item-title">${escapeHtml(conv.title)}</span>
      <div class="chat-item-actions">
        <button class="icon-btn edit-btn" title="Rename">✏️</button>
        <button class="icon-btn delete-btn" title="Delete" style="color: var(--danger-color);">🗑️</button>
      </div>
    `;

    // Click to select
    item.addEventListener('click', (e) => {
      if (e.target.closest('.edit-btn') || e.target.closest('.delete-btn')) return;
      selectConversation(conv.id);
    });

    // Rename
    const editBtn = item.querySelector('.edit-btn');
    editBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      renameConversation(conv.id, conv.title);
    });

    // Delete
    const deleteBtn = item.querySelector('.delete-btn');
    deleteBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      deleteConversation(conv.id);
    });

    conversationsContainer.appendChild(item);
  });
}

/**
 * Select and load a conversation
 */
async function selectConversation(id) {
  currentConversationId = id;
  loadConversations(); // refresh active state

  try {
    const res = await fetch(`/api/v1/chat/conversations/${id}/`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) return;

    const data = await res.json();
    renderMessages(data.messages);
  } catch (err) {
    console.error('Failed to load conversation details:', err);
  }
}

function renderMessages(messages) {
  messagesContainer.innerHTML = '';

  if (!messages || messages.length === 0) {
    if (welcomeScreen) {
      messagesContainer.appendChild(welcomeScreen);
      welcomeScreen.style.display = 'flex';
    }
    return;
  }

  if (welcomeScreen) welcomeScreen.style.display = 'none';

  messages.forEach(msg => {
    appendMessageElement(msg.role, msg.content, msg.citations, false);
  });

  scrollToBottom();
}

/**
 * Append message element to UI
 */
function appendMessageElement(role, content, citations = [], isStreaming = false) {
  if (welcomeScreen) welcomeScreen.style.display = 'none';

  const wrapper = document.createElement('div');
  wrapper.className = `message-wrapper ${role}-wrapper`;

  const avatar = document.createElement('div');
  avatar.className = 'message-avatar';
  avatar.innerHTML = role === 'user' ? '👤' : '🤖';

  const bubble = document.createElement('div');
  bubble.className = `message-bubble ${isStreaming ? 'typing-cursor' : ''}`;

  const contentDiv = document.createElement('div');
  contentDiv.className = 'message-content';

  if (role === 'assistant') {
    contentDiv.innerHTML = formatMarkdown(content);
  } else {
    contentDiv.innerText = content;
  }

  bubble.appendChild(contentDiv);

  // Add citations box if present
  if (citations && citations.length > 0) {
    const citationsBox = createCitationsElement(citations);
    bubble.appendChild(citationsBox);
  }

  if (role === 'user') {
    wrapper.appendChild(bubble);
    wrapper.appendChild(avatar);
  } else {
    wrapper.appendChild(avatar);
    wrapper.appendChild(bubble);
  }

  messagesContainer.appendChild(wrapper);
  attachCodeCopyButtons(bubble);
  scrollToBottom();

  return { wrapper, bubble, contentDiv };
}

function createCitationsElement(citations) {
  const box = document.createElement('div');
  box.className = 'citations-box';
  
  let html = `<div class="citations-header">🌐 Web Search Sources (${citations.length})</div>`;
  citations.forEach((c, idx) => {
    html += `
      <div class="citation-item">
        [${idx + 1}] <a href="${escapeHtml(c.url)}" target="_blank" rel="noopener noreferrer" class="citation-link">${escapeHtml(c.title || c.url)}</a>
      </div>
    `;
  });
  box.innerHTML = html;
  return box;
}

/**
 * Send Message & Handle SSE Streaming
 */
async function sendMessage() {
  const messageText = chatInput.value.trim();
  if (!messageText || isGenerating) return;

  // Clear input & reset height
  chatInput.value = '';
  chatInput.style.height = 'auto';
  sendBtn.disabled = true;
  isGenerating = true;

  // 1. Render User Message
  appendMessageElement('user', messageText);

  // 2. Prepare Placeholder Assistant Message
  const { bubble, contentDiv } = appendMessageElement('assistant', '', [], true);
  let accumulatedText = '';
  let citations = [];

  try {
    const selectedModel = modelSelect.value;
    const response = await fetch('/api/v1/chat/stream/', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        conversation_id: currentConversationId,
        message: messageText,
        enable_web_search: isWebSearchEnabled,
        model: selectedModel
      })
    });

    if (!response.ok) {
      bubble.classList.remove('typing-cursor');
      contentDiv.innerHTML = '<span style="color: var(--danger-color);">Error connecting to AI service. Please try again.</span>';
      isGenerating = false;
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop(); // keep incomplete line in buffer

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const jsonStr = line.slice(6).trim();
          if (!jsonStr) continue;

          try {
            const data = JSON.parse(jsonStr);

            if (data.type === 'init') {
              currentConversationId = data.conversation_id;
              if (data.citations && data.citations.length > 0) {
                citations = data.citations;
              }
            } else if (data.type === 'chunk') {
              accumulatedText += data.chunk;
              contentDiv.innerHTML = formatMarkdown(accumulatedText);
              attachCodeCopyButtons(bubble);
              scrollToBottom();
            } else if (data.type === 'done') {
              // Finalize
            } else if (data.type === 'error') {
              accumulatedText += `\n\n*[Error: ${data.error}]*`;
              contentDiv.innerHTML = formatMarkdown(accumulatedText);
            }
          } catch (e) {
            console.error('SSE parse error:', e);
          }
        }
      }
    }

    // Finished streaming
    bubble.classList.remove('typing-cursor');
    contentDiv.innerHTML = formatMarkdown(accumulatedText);
    
    if (citations.length > 0) {
      bubble.appendChild(createCitationsElement(citations));
    }
    attachCodeCopyButtons(bubble);
    loadConversations(); // refresh list to show updated title

  } catch (err) {
    bubble.classList.remove('typing-cursor');
    contentDiv.innerHTML = `<span style="color: var(--danger-color);">Network error: ${err.message}</span>`;
  } finally {
    isGenerating = false;
    updateSendButtonState();
  }
}

/**
 * Helpers
 */
function formatMarkdown(text) {
  if (window.marked && window.DOMPurify) {
    return DOMPurify.sanitize(marked.parse(text));
  }
  return escapeHtml(text).replace(/\n/g, '<br>');
}

function attachCodeCopyButtons(container) {
  const preElements = container.querySelectorAll('pre');
  preElements.forEach(pre => {
    if (pre.querySelector('.copy-code-btn')) return;

    const copyBtn = document.createElement('button');
    copyBtn.className = 'copy-code-btn';
    copyBtn.innerText = '📋 Copy';

    copyBtn.addEventListener('click', () => {
      const code = pre.querySelector('code')?.innerText || pre.innerText;
      navigator.clipboard.writeText(code).then(() => {
        copyBtn.innerText = '✅ Copied!';
        setTimeout(() => { copyBtn.innerText = '📋 Copy'; }, 2000);
      });
    });

    pre.appendChild(copyBtn);
  });
}

function scrollToBottom() {
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.innerText = text || '';
  return div.innerHTML;
}

function updateSendButtonState() {
  sendBtn.disabled = !chatInput.value.trim() || isGenerating;
}

function useSuggestion(text) {
  chatInput.value = text;
  updateSendButtonState();
  sendMessage();
}

async function renameConversation(id, oldTitle) {
  const newTitle = prompt('Enter new chat title:', oldTitle);
  if (!newTitle || newTitle.trim() === oldTitle) return;

  try {
    await fetch(`/api/v1/chat/conversations/${id}/`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify({ title: newTitle.trim() })
    });
    loadConversations();
  } catch (e) {
    alert('Failed to rename conversation');
  }
}

async function deleteConversation(id) {
  if (!confirm('Are you sure you want to delete this chat?')) return;

  try {
    await fetch(`/api/v1/chat/conversations/${id}/`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });

    if (currentConversationId === id) {
      currentConversationId = null;
      renderMessages([]);
    }
    loadConversations();
  } catch (e) {
    alert('Failed to delete conversation');
  }
}
