/**
 * app.js — Dalang-AI Auth Portal
 * Single-page application logic for login, registration, token refresh, and profile view.
 */

(function () {
  'use strict';

  // -------------------------------------------------------------------------
  // Constants & Storage Keys
  // -------------------------------------------------------------------------
  const STORAGE_KEYS = {
    ACCESS_TOKEN: 'dalang-ai_access_token',
    REFRESH_TOKEN: 'dalang-ai_refresh_token',
    REMEMBER_ME: 'dalang-ai_remember_me',
    API_BASE_URL: 'dalang-ai_api_base_url',
  };

  const DEFAULT_API_BASE = ''; // empty string means current origin / relative

  // -------------------------------------------------------------------------
  // State
  // -------------------------------------------------------------------------
  const state = {
    accessToken: null,
    refreshToken: null,
    rememberMe: true,
    apiBaseUrl: '',
    currentUser: null,
  };

  // -------------------------------------------------------------------------
  // DOM Elements Cache
  // -------------------------------------------------------------------------
  const elements = {};

  function initElements() {
    // Navigation / Header
    elements.toggleSettingsBtn = document.getElementById('toggle-settings-btn');
    elements.settingsPanel = document.getElementById('settings-panel');
    elements.apiBaseUrlInput = document.getElementById('api-base-url');
    elements.saveSettingsBtn = document.getElementById('save-settings-btn');
    elements.resetSettingsBtn = document.getElementById('reset-settings-btn');

    // Notification toast
    elements.notification = document.getElementById('notification');
    elements.notificationMessage = document.getElementById('notification-message');
    elements.notificationClose = document.getElementById('notification-close');

    // Sections
    elements.authSection = document.getElementById('auth-section');
    elements.dashboardSection = document.getElementById('dashboard-section');

    // Tabs
    elements.tabLogin = document.getElementById('tab-login');
    elements.tabRegister = document.getElementById('tab-register');
    elements.loginPane = document.getElementById('login-pane');
    elements.registerPane = document.getElementById('register-pane');
    elements.switchToRegister = document.getElementById('switch-to-register');
    elements.switchToLogin = document.getElementById('switch-to-login');

    // Login Form
    elements.loginForm = document.getElementById('login-form');
    elements.loginUsername = document.getElementById('login-username');
    elements.loginPassword = document.getElementById('login-password');
    elements.loginRemember = document.getElementById('login-remember');
    elements.loginError = document.getElementById('login-error');
    elements.loginSubmitBtn = document.getElementById('login-submit-btn');

    // Register Form
    elements.registerForm = document.getElementById('register-form');
    elements.registerUsername = document.getElementById('register-username');
    elements.registerEmail = document.getElementById('register-email');
    elements.registerFullName = document.getElementById('register-fullname');
    elements.registerRole = document.getElementById('register-role');
    elements.registerPassword = document.getElementById('register-password');
    elements.registerConfirmPassword = document.getElementById('register-confirm-password');
    elements.registerError = document.getElementById('register-error');
    elements.registerSuccess = document.getElementById('register-success');
    elements.registerSubmitBtn = document.getElementById('register-submit-btn');
    elements.strengthFill = document.getElementById('password-strength-fill');
    elements.strengthText = document.getElementById('password-strength-text');

    // Dashboard
    elements.userAvatarInitials = document.getElementById('user-avatar-initials');
    elements.userDisplayName = document.getElementById('user-display-name');
    elements.userRoleBadge = document.getElementById('user-role-badge');
    elements.logoutBtn = document.getElementById('logout-btn');

    elements.detailUsername = document.getElementById('detail-username');
    elements.detailEmail = document.getElementById('detail-email');
    elements.detailFullName = document.getElementById('detail-fullname');
    elements.detailRole = document.getElementById('detail-role');
    elements.detailStatus = document.getElementById('detail-status');
    elements.detailId = document.getElementById('detail-id');
    elements.detailCreated = document.getElementById('detail-created');
    elements.detailUpdated = document.getElementById('detail-updated');

    elements.accessTokenDisplay = document.getElementById('access-token-display');
    elements.refreshTokenDisplay = document.getElementById('refresh-token-display');
    elements.copyAccessToken = document.getElementById('copy-access-token');
    elements.copyRefreshToken = document.getElementById('copy-refresh-token');
    elements.refreshTokenBtn = document.getElementById('refresh-token-btn');
    elements.reloadProfileBtn = document.getElementById('reload-profile-btn');
  }

  // -------------------------------------------------------------------------
  // Storage Helpers (handles localStorage vs sessionStorage based on rememberMe)
  // -------------------------------------------------------------------------
  function getStorage() {
    return state.rememberMe ? localStorage : sessionStorage;
  }

  function loadStoredSettings() {
    state.apiBaseUrl = localStorage.getItem(STORAGE_KEYS.API_BASE_URL) || DEFAULT_API_BASE;
    if (elements.apiBaseUrlInput) {
      elements.apiBaseUrlInput.value = state.apiBaseUrl;
    }

    const remembered = localStorage.getItem(STORAGE_KEYS.REMEMBER_ME);
    state.rememberMe = remembered === null ? true : remembered === 'true';
    if (elements.loginRemember) {
      elements.loginRemember.checked = state.rememberMe;
    }

    // Try localStorage first, then sessionStorage
    state.accessToken = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN) ||
      sessionStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN) || null;
    state.refreshToken = localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN) ||
      sessionStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN) || null;
  }

  function saveTokens(accessToken, refreshToken) {
    state.accessToken = accessToken;
    if (refreshToken) state.refreshToken = refreshToken;

    const storage = getStorage();
    if (accessToken) storage.setItem(STORAGE_KEYS.ACCESS_TOKEN, accessToken);
    if (refreshToken) storage.setItem(STORAGE_KEYS.REFRESH_TOKEN, refreshToken);

    // If rememberMe is true, also remove from sessionStorage to avoid staleness
    if (state.rememberMe) {
      sessionStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
      sessionStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
    } else {
      localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
      localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
    }
  }

  function clearTokens() {
    state.accessToken = null;
    state.refreshToken = null;
    state.currentUser = null;

    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
    sessionStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
    sessionStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
  }

  // -------------------------------------------------------------------------
  // API Fetch Wrapper
  // -------------------------------------------------------------------------
  function getApiUrl(endpoint) {
    const base = state.apiBaseUrl.trim().replace(/\/+$/, '');
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint : '/' + endpoint;
    return `${base}${cleanEndpoint}`;
  }

  async function apiRequest(endpoint, options = {}) {
    const url = getApiUrl(endpoint);
    const headers = {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...(options.headers || {}),
    };

    if (state.accessToken && !headers.Authorization) {
      headers.Authorization = `Bearer ${state.accessToken}`;
    }

    const config = {
      ...options,
      headers,
    };

    let response;
    try {
      response = await fetch(url, config);
    } catch (networkError) {
      throw new Error(`Network error connecting to API (${url}): ${networkError.message}`);
    }

    let data;
    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    if (!response.ok) {
      let message = 'An error occurred';
      if (typeof data === 'object' && data !== null) {
        if (typeof data.detail === 'string') {
          message = data.detail;
        } else if (Array.isArray(data.detail)) {
          // FastAPI validation error array
          message = data.detail.map(d => `${d.loc ? d.loc.slice(-1)[0] + ': ' : ''}${d.msg}`).join(', ');
        } else if (data.message) {
          message = data.message;
        }
      } else if (typeof data === 'string' && data.length > 0) {
        message = data;
      }
      const error = new Error(message);
      error.status = response.status;
      error.data = data;
      throw error;
    }

    return data;
  }

  // -------------------------------------------------------------------------
  // Notifications & UI Feedback
  // -------------------------------------------------------------------------
  let notificationTimer = null;

  function showNotification(message, type = 'info', durationMs = 4000) {
    if (!elements.notification) return;
    clearTimeout(notificationTimer);

    elements.notification.className = `notification ${type}`;
    elements.notificationMessage.textContent = message;
    elements.notification.classList.remove('hidden');

    if (durationMs > 0) {
      notificationTimer = setTimeout(hideNotification, durationMs);
    }
  }

  function hideNotification() {
    if (elements.notification) {
      elements.notification.classList.add('hidden');
    }
  }

  function setButtonLoading(button, isLoading, normalText = 'Submit') {
    if (!button) return;
    const spinner = button.querySelector('.spinner');
    const textSpan = button.querySelector('.btn-text');

    if (isLoading) {
      button.disabled = true;
      if (spinner) spinner.classList.remove('hidden');
      if (textSpan) textSpan.textContent = 'Processing...';
    } else {
      button.disabled = false;
      if (spinner) spinner.classList.add('hidden');
      if (textSpan) textSpan.textContent = normalText;
    }
  }

  function showElementError(el, message) {
    if (!el) return;
    el.textContent = message;
    el.classList.remove('hidden');
  }

  function hideElementError(el) {
    if (!el) return;
    el.textContent = '';
    el.classList.add('hidden');
  }

  // -------------------------------------------------------------------------
  // Tabs & View Management
  // -------------------------------------------------------------------------
  function switchTab(targetPaneId) {
    const isLogin = targetPaneId === 'login-pane';

    elements.tabLogin.classList.toggle('active', isLogin);
    elements.tabRegister.classList.toggle('active', !isLogin);
    elements.loginPane.classList.toggle('active', isLogin);
    elements.registerPane.classList.toggle('active', !isLogin);

    hideElementError(elements.loginError);
    hideElementError(elements.registerError);
    hideElementError(elements.registerSuccess);
  }

  function showDashboard(user) {
    state.currentUser = user;
    elements.authSection.classList.add('hidden');
    elements.dashboardSection.classList.remove('hidden');

    renderUserProfile(user);
    renderTokenSnippets();
  }

  function showAuthSection() {
    elements.dashboardSection.classList.add('hidden');
    elements.authSection.classList.remove('hidden');
    switchTab('login-pane');
  }

  // -------------------------------------------------------------------------
  // Password Strength Checker
  // -------------------------------------------------------------------------
  function evaluatePasswordStrength(password) {
    if (!password || password.length === 0) {
      return { score: 0, text: 'Min 8 characters', className: '' };
    }
    let score = 0;
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;

    if (password.length < 8) {
      return { score: 1, text: 'Too short (min 8 chars)', className: 'weak' };
    }
    if (score <= 2) {
      return { score: 2, text: 'Weak', className: 'weak' };
    }
    if (score <= 3) {
      return { score: 3, text: 'Fair', className: 'fair' };
    }
    if (score === 4) {
      return { score: 4, text: 'Good', className: 'good' };
    }
    return { score: 5, text: 'Strong', className: 'strong' };
  }

  function updatePasswordStrengthUI(password) {
    const { text, className } = evaluatePasswordStrength(password);
    elements.strengthFill.className = `strength-fill ${className}`;
    elements.strengthText.textContent = text;
  }

  // -------------------------------------------------------------------------
  // Profile & Token Rendering
  // -------------------------------------------------------------------------
  function formatDate(isoString) {
    if (!isoString) return '—';
    try {
      const d = new Date(isoString);
      return d.toLocaleString(undefined, {
        dateStyle: 'medium',
        timeStyle: 'medium',
      });
    } catch {
      return isoString;
    }
  }

  function renderUserProfile(user) {
    if (!user) return;

    const initial = (user.full_name || user.username || 'U')[0].toUpperCase();
    elements.userAvatarInitials.textContent = initial;
    elements.userDisplayName.textContent = user.full_name || user.username;
    elements.userRoleBadge.textContent = user.role || 'user';

    elements.detailUsername.textContent = user.username;
    elements.detailEmail.textContent = user.email;
    elements.detailFullName.textContent = user.full_name || '(not set)';
    elements.detailRole.textContent = user.role;
    elements.detailStatus.innerHTML = user.is_active
      ? '<span class="badge badge-success">Active</span>'
      : '<span class="badge badge-error">Disabled</span>';
    elements.detailId.textContent = user.id;
    elements.detailCreated.textContent = formatDate(user.created_at);
    elements.detailUpdated.textContent = formatDate(user.updated_at);
  }

  function renderTokenSnippets() {
    elements.accessTokenDisplay.textContent = state.accessToken || 'No token present';
    elements.refreshTokenDisplay.textContent = state.refreshToken || 'No token present';
  }

  // -------------------------------------------------------------------------
  // Auth API Handlers
  // -------------------------------------------------------------------------
  async function handleLogin(e) {
    e.preventDefault();
    hideElementError(elements.loginError);

    const username = elements.loginUsername.value.trim();
    const password = elements.loginPassword.value;

    if (!username || !password) {
      showElementError(elements.loginError, 'Please enter both username and password.');
      return;
    }

    state.rememberMe = elements.loginRemember.checked;
    localStorage.setItem(STORAGE_KEYS.REMEMBER_ME, String(state.rememberMe));

    setButtonLoading(elements.loginSubmitBtn, true, 'Sign In');

    try {
      const tokens = await apiRequest('/login', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      });

      saveTokens(tokens.access_token, tokens.refresh_token);
      showNotification('Signed in successfully!', 'success');

      // Fetch user profile
      const user = await apiRequest('/me');
      showDashboard(user);
      elements.loginForm.reset();
    } catch (err) {
      showElementError(elements.loginError, err.message || 'Login failed.');
    } finally {
      setButtonLoading(elements.loginSubmitBtn, false, 'Sign In');
    }
  }

  async function handleRegister(e) {
    e.preventDefault();
    hideElementError(elements.registerError);
    hideElementError(elements.registerSuccess);

    const username = elements.registerUsername.value.trim();
    const email = elements.registerEmail.value.trim();
    const fullName = elements.registerFullName.value.trim();
    const role = elements.registerRole.value;
    const password = elements.registerPassword.value;
    const confirmPassword = elements.registerConfirmPassword.value;

    // Client-side validations
    const usernameRegex = /^[a-zA-Z0-9_.-]{3,64}$/;
    if (!usernameRegex.test(username)) {
      showElementError(
        elements.registerError,
        'Username must be 3–64 characters and contain only letters, numbers, _, -, or .'
      );
      return;
    }

    const emailRegex = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
    if (!emailRegex.test(email)) {
      showElementError(elements.registerError, 'Please enter a valid email address.');
      return;
    }

    if (password.length < 8) {
      showElementError(elements.registerError, 'Password must be at least 8 characters long.');
      return;
    }

    if (password !== confirmPassword) {
      showElementError(elements.registerError, 'Passwords do not match.');
      return;
    }

    setButtonLoading(elements.registerSubmitBtn, true, 'Create Account');

    try {
      const payload = {
        username,
        email,
        password,
        role,
        ...(fullName ? { full_name: fullName } : {}),
      };

      const result = await apiRequest('/register', {
        method: 'POST',
        body: JSON.stringify(payload),
      });

      elements.registerSuccess.textContent = `Account created successfully for ${result.username}! You can now sign in.`;
      elements.registerSuccess.classList.remove('hidden');
      elements.registerForm.reset();
      updatePasswordStrengthUI('');

      // Auto-prefill username into login field
      elements.loginUsername.value = result.username;

      showNotification('Account created successfully! Switching to sign in...', 'success');
      setTimeout(() => {
        switchTab('login-pane');
        elements.loginPassword.focus();
      }, 1500);
    } catch (err) {
      showElementError(elements.registerError, err.message || 'Registration failed.');
    } finally {
      setButtonLoading(elements.registerSubmitBtn, false, 'Create Account');
    }
  }

  async function handleRefreshToken() {
    if (!state.refreshToken) {
      showNotification('No refresh token available to refresh.', 'warning');
      return;
    }

    setButtonLoading(elements.refreshTokenBtn, true, 'Refresh Access Token');

    try {
      const data = await apiRequest('/refresh', {
        method: 'POST',
        body: JSON.stringify({ refresh_token: state.refreshToken }),
      });

      saveTokens(data.access_token, null);
      renderTokenSnippets();
      showNotification('Access token refreshed successfully!', 'success');
    } catch (err) {
      showNotification(`Token refresh failed: ${err.message}`, 'error');
      // If refresh token is expired/invalid, sign out
      if (err.status === 401) {
        handleLogout('Session expired. Please sign in again.');
      }
    } finally {
      setButtonLoading(elements.refreshTokenBtn, false, 'Refresh Access Token');
    }
  }

  async function handleReloadProfile() {
    setButtonLoading(elements.reloadProfileBtn, true, 'Reload Profile');

    try {
      const user = await apiRequest('/me');
      renderUserProfile(user);
      showNotification('Profile refreshed!', 'success');
    } catch (err) {
      if (err.status === 401 && state.refreshToken) {
        // Try to refresh token and re-fetch profile
        try {
          await handleRefreshToken();
          const user = await apiRequest('/me');
          renderUserProfile(user);
          showNotification('Profile reloaded after token refresh!', 'success');
          return;
        } catch {
          // If refresh also fails, proceed to error
        }
      }
      showNotification(`Failed to reload profile: ${err.message}`, 'error');
      if (err.status === 401) {
        handleLogout('Session expired. Please sign in again.');
      }
    } finally {
      setButtonLoading(elements.reloadProfileBtn, false, 'Reload Profile');
    }
  }

  function handleLogout(message = 'You have signed out.') {
    clearTokens();
    showAuthSection();
    showNotification(message, 'info');
  }

  async function tryAutoLogin() {
    if (!state.accessToken) {
      showAuthSection();
      return;
    }

    try {
      const user = await apiRequest('/me');
      showDashboard(user);
      showNotification(`Welcome back, ${user.full_name || user.username}!`, 'success', 2500);
    } catch (err) {
      // Access token might be expired; attempt refresh if refresh_token is present
      if (err.status === 401 && state.refreshToken) {
        try {
          const data = await apiRequest('/refresh', {
            method: 'POST',
            body: JSON.stringify({ refresh_token: state.refreshToken }),
          });
          saveTokens(data.access_token, null);
          const user = await apiRequest('/me');
          showDashboard(user);
          showNotification(`Session restored. Welcome back, ${user.full_name || user.username}!`, 'success');
          return;
        } catch {
          // Refresh failed
        }
      }
      clearTokens();
      showAuthSection();
    }
  }

  // -------------------------------------------------------------------------
  // Password Visibility Toggle
  // -------------------------------------------------------------------------
  function setupPasswordToggles() {
    document.querySelectorAll('.toggle-password').forEach((btn) => {
      btn.addEventListener('click', () => {
        const inputId = btn.getAttribute('data-for');
        const input = document.getElementById(inputId);
        if (!input) return;

        if (input.type === 'password') {
          input.type = 'text';
          btn.textContent = '🔒';
          btn.setAttribute('aria-label', 'Hide password');
        } else {
          input.type = 'password';
          btn.textContent = '👁';
          btn.setAttribute('aria-label', 'Show password');
        }
      });
    });
  }

  // -------------------------------------------------------------------------
  // Copy to Clipboard Helpers
  // -------------------------------------------------------------------------
  function setupCopyButtons() {
    function copyText(text, btn) {
      if (!text || text === 'No token present') {
        showNotification('No token to copy.', 'warning');
        return;
      }
      navigator.clipboard.writeText(text).then(
        () => {
          const original = btn.textContent;
          btn.textContent = 'Copied!';
          setTimeout(() => {
            btn.textContent = original;
          }, 1500);
        },
        () => {
          showNotification('Clipboard write permission denied.', 'error');
        }
      );
    }

    elements.copyAccessToken.addEventListener('click', () => {
      copyText(state.accessToken, elements.copyAccessToken);
    });

    elements.copyRefreshToken.addEventListener('click', () => {
      copyText(state.refreshToken, elements.copyRefreshToken);
    });
  }

  // -------------------------------------------------------------------------
  // Settings Panel Handlers
  // -------------------------------------------------------------------------
  function setupSettings() {
    elements.toggleSettingsBtn.addEventListener('click', () => {
      elements.settingsPanel.classList.toggle('hidden');
      elements.settingsPanel.classList.toggle('visible');
    });

    elements.saveSettingsBtn.addEventListener('click', () => {
      const url = elements.apiBaseUrlInput.value.trim().replace(/\/+$/, '');
      state.apiBaseUrl = url;
      localStorage.setItem(STORAGE_KEYS.API_BASE_URL, url);
      elements.settingsPanel.classList.add('hidden');
      elements.settingsPanel.classList.remove('visible');
      showNotification(`API URL saved: ${url || '(same origin)'}`, 'success');
    });

    elements.resetSettingsBtn.addEventListener('click', () => {
      state.apiBaseUrl = DEFAULT_API_BASE;
      elements.apiBaseUrlInput.value = '';
      localStorage.removeItem(STORAGE_KEYS.API_BASE_URL);
      elements.settingsPanel.classList.add('hidden');
      elements.settingsPanel.classList.remove('visible');
      showNotification('API URL reset to same origin.', 'info');
    });
  }

  // -------------------------------------------------------------------------
  // Event Listeners Initialization
  // -------------------------------------------------------------------------
  function attachEventListeners() {
    // Tab switching
    elements.tabLogin.addEventListener('click', () => switchTab('login-pane'));
    elements.tabRegister.addEventListener('click', () => switchTab('register-pane'));
    elements.switchToRegister.addEventListener('click', (e) => {
      e.preventDefault();
      switchTab('register-pane');
    });
    elements.switchToLogin.addEventListener('click', (e) => {
      e.preventDefault();
      switchTab('login-pane');
    });

    // Form submissions
    elements.loginForm.addEventListener('submit', handleLogin);
    elements.registerForm.addEventListener('submit', handleRegister);

    // Password strength listener
    elements.registerPassword.addEventListener('input', (e) => {
      updatePasswordStrengthUI(e.target.value);
    });

    // Dashboard actions
    elements.logoutBtn.addEventListener('click', () => handleLogout());
    elements.refreshTokenBtn.addEventListener('click', handleRefreshToken);
    elements.reloadProfileBtn.addEventListener('click', handleReloadProfile);

    // Notification close
    elements.notificationClose.addEventListener('click', hideNotification);

    setupPasswordToggles();
    setupCopyButtons();
    setupSettings();
  }

  // -------------------------------------------------------------------------
  // App Bootstrapping
  // -------------------------------------------------------------------------
  function init() {
    initElements();
    loadStoredSettings();
    attachEventListeners();
    tryAutoLogin();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Export state & helpers to window for unit testing/debugging if needed
  window.__rippleAuthApp = {
    state,
    apiRequest,
    getApiUrl,
    evaluatePasswordStrength,
    saveTokens,
    clearTokens,
    handleLogin,
    handleRegister,
    handleRefreshToken,
    handleReloadProfile,
  };
})();
