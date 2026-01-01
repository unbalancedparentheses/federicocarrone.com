(function() {
  var STORAGE_KEY = 'theme';
  var THEMES = [
    { id: 'default', label: 'Default', icon: '☀️' },
    { id: 'ghost', label: 'Cypherpunk', icon: 'λ' }
  ];

  function getStoredTheme() {
    try {
      return localStorage.getItem(STORAGE_KEY) || 'default';
    } catch (e) {
      return 'default';
    }
  }

  function setStoredTheme(theme) {
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch (e) {}
  }

  function getThemeIndex(themeId) {
    for (var i = 0; i < THEMES.length; i++) {
      if (THEMES[i].id === themeId) return i;
    }
    return 0;
  }

  function applyTheme(themeId) {
    if (themeId && themeId !== 'default') {
      document.documentElement.setAttribute('data-theme', themeId);
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
    updateToggleButton(themeId);
  }

  function updateToggleButton(themeId) {
    var button = document.getElementById('theme-toggle');
    if (!button) return;

    var index = getThemeIndex(themeId);
    var nextIndex = (index + 1) % THEMES.length;
    var currentTheme = THEMES[index];
    var nextTheme = THEMES[nextIndex];

    button.textContent = currentTheme.icon;
    button.setAttribute('aria-label', 'Theme: ' + currentTheme.label + '. Click for ' + nextTheme.label);
    button.setAttribute('title', currentTheme.label);
  }

  function cycleTheme() {
    var current = getStoredTheme();
    var index = getThemeIndex(current);
    var nextIndex = (index + 1) % THEMES.length;
    var nextTheme = THEMES[nextIndex].id;

    setStoredTheme(nextTheme);
    applyTheme(nextTheme);
  }

  // Apply stored theme immediately to prevent flash
  applyTheme(getStoredTheme());

  // Set up toggle button when DOM is ready
  document.addEventListener('DOMContentLoaded', function() {
    var button = document.getElementById('theme-toggle');
    if (button) {
      button.addEventListener('click', cycleTheme);
      updateToggleButton(getStoredTheme());
    }
  });
})();
