/**
 * Application initialization and UI event listeners
 */

document.addEventListener('DOMContentLoaded', () => {
  // Check auth state
  checkAuthGuard();

  // Load user profile details
  const user = getUser();
  if (user) {
    const displayNameElem = document.getElementById('user-display-name');
    const avatarInitialElem = document.getElementById('user-avatar-initial');
    if (displayNameElem) displayNameElem.innerText = user.username || user.first_name || 'User';
    if (avatarInitialElem) avatarInitialElem.innerText = (user.username || 'U')[0].toUpperCase();
  }

  // Load chats
  loadConversations();

  // Input auto-grow and Send button triggers
  chatInput.addEventListener('input', () => {
    chatInput.style.height = 'auto';
    chatInput.style.height = Math.min(chatInput.scrollHeight, 160) + 'px';
    updateSendButtonState();
  });

  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  sendBtn.addEventListener('click', sendMessage);

  // New Chat
  newChatBtn.addEventListener('click', () => {
    currentConversationId = null;
    renderMessages([]);
    loadConversations();
    chatInput.focus();
  });

  // Clear Chat View
  clearChatBtn.addEventListener('click', () => {
    renderMessages([]);
  });

  // Web Search Toggle
  webSearchToggle.addEventListener('click', () => {
    isWebSearchEnabled = !isWebSearchEnabled;
    webSearchToggle.classList.toggle('active', isWebSearchEnabled);
    searchStatusDot.innerText = isWebSearchEnabled ? 'ON' : 'OFF';
    searchStatusDot.style.color = isWebSearchEnabled ? '#10b981' : 'var(--text-muted)';
  });

  // Theme Toggle (Dark / Light)
  const themeToggleBtn = document.getElementById('theme-toggle-btn');
  const savedTheme = localStorage.getItem('theme') || 'dark';
  document.documentElement.setAttribute('data-theme', savedTheme);

  themeToggleBtn.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
  });

  // Mobile Sidebar Drawer
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const closeSidebarBtn = document.getElementById('close-sidebar-btn');
  const sidebar = document.getElementById('sidebar');

  if (mobileMenuBtn && sidebar) {
    mobileMenuBtn.addEventListener('click', () => {
      sidebar.classList.add('open');
    });
  }

  if (closeSidebarBtn && sidebar) {
    closeSidebarBtn.addEventListener('click', () => {
      sidebar.classList.remove('open');
    });
  }

  // Logout
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      if (confirm('Are you sure you want to log out?')) {
        logoutUser();
      }
    });
  }
});
