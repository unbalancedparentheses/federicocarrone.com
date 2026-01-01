(function() {
  var STORAGE_KEY = 'theme';
  var CYBERPUNK = 'cyberpunk';
  var DEFAULT = 'default';

  function getStoredTheme() {
    try {
      return localStorage.getItem(STORAGE_KEY);
    } catch (e) {
      return null;
    }
  }

  function setStoredTheme(theme) {
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch (e) {}
  }

  function applyTheme(theme) {
    if (theme === CYBERPUNK) {
      document.documentElement.setAttribute('data-theme', CYBERPUNK);
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
    updateToggleButton(theme);
  }

  function updateToggleButton(theme) {
    var button = document.getElementById('theme-toggle');
    if (button) {
      button.setAttribute('aria-label', theme === CYBERPUNK ? 'Switch to default theme' : 'Switch to cyberpunk theme');
      button.textContent = theme === CYBERPUNK ? '☀️' : '🌃';
    }
  }

  function toggleTheme() {
    var current = getStoredTheme() || DEFAULT;
    var next = current === CYBERPUNK ? DEFAULT : CYBERPUNK;
    setStoredTheme(next);
    applyTheme(next);
  }

  // Apply stored theme immediately to prevent flash
  var storedTheme = getStoredTheme();
  if (storedTheme) {
    applyTheme(storedTheme);
  }

  // Set up toggle button when DOM is ready
  document.addEventListener('DOMContentLoaded', function() {
    var button = document.getElementById('theme-toggle');
    if (button) {
      button.addEventListener('click', toggleTheme);
      updateToggleButton(getStoredTheme() || DEFAULT);
    }
  });
})();
