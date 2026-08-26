/**
 * Authentication management for Araf's Assistant
 */

function getAuthToken() {
  return localStorage.getItem('authToken');
}

function getUser() {
  const user = localStorage.getItem('user');
  return user ? JSON.parse(user) : null;
}

function getAuthHeaders() {
  const token = getAuthToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Token ${token}` } : {})
  };
}

function checkAuthGuard() {
  const currentPath = window.location.pathname;
  const isAuthPage = currentPath.includes('/login/') || currentPath.includes('/register/');
  const token = getAuthToken();

  if (!token && !isAuthPage) {
    window.location.href = '/login/';
  }
}

async function logoutUser() {
  try {
    await fetch('/api/v1/auth/logout/', {
      method: 'POST',
      headers: getAuthHeaders()
    });
  } catch (e) {
    console.error('Logout request error:', e);
  } finally {
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    window.location.href = '/login/';
  }
}
