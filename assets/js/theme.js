(function () {
  'use strict';
  try {
    const theme = localStorage.getItem('runtime-theme');
    if (theme === 'light' || theme === 'dark') document.documentElement.dataset.theme = theme;
  } catch (_) { /* System theme works even when storage is disabled. */ }
}());
