(function () {
  'use strict';
  const themeButton = document.getElementById('theme-toggle');
  const modes = ['system', 'light', 'dark'];
  const names = { system: '跟随系统', light: '浅色', dark: '深色' };
  let mode = document.documentElement.dataset.theme || 'system';
  function updateThemeButton() {
    const next = modes[(modes.indexOf(mode) + 1) % modes.length];
    themeButton.textContent = { system: '◐', light: '☀', dark: '☾' }[mode];
    themeButton.setAttribute('aria-label', `主题：${names[mode]}。点击切换为${names[next]}`);
    themeButton.title = `主题：${names[mode]}`;
  }
  themeButton.hidden = false;
  updateThemeButton();
  themeButton.addEventListener('click', () => {
    mode = modes[(modes.indexOf(mode) + 1) % modes.length];
    if (mode === 'system') delete document.documentElement.dataset.theme;
    else document.documentElement.dataset.theme = mode;
    try { localStorage.setItem('runtime-theme', mode); } catch (_) {}
    updateThemeButton();
  });
  async function copy(text) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text);
    const field = document.createElement('textarea');
    field.value = text;
    field.style.position = 'fixed';
    field.style.opacity = '0';
    document.body.appendChild(field);
    const previous = document.activeElement;
    field.select();
    const success = document.execCommand('copy');
    field.remove();
    if (previous) previous.focus();
    if (!success) throw new Error('Copy unavailable');
  }
  document.querySelectorAll('.prose pre').forEach((pre) => {
    const code = pre.querySelector('code');
    if (!code) return;
    pre.tabIndex = 0;
    pre.setAttribute('aria-label', '代码块，可横向滚动');
    const toolbar = document.createElement('div');
    toolbar.className = 'code-toolbar';
    const lang = document.createElement('span');
    const wrapper = pre.closest('[class*="language-"]');
    const match = wrapper && wrapper.className.match(/language-([\w-]+)/);
    lang.textContent = match ? match[1].toUpperCase() : 'CODE';
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'copy-code';
    button.textContent = '复制';
    button.setAttribute('aria-label', '复制此代码块');
    button.setAttribute('aria-live', 'polite');
    button.addEventListener('click', async () => {
      try { await copy(code.textContent); button.textContent = '已复制'; }
      catch (_) { button.textContent = '请选中复制'; }
      setTimeout(() => { button.textContent = '复制'; }, 2200);
    });
    toolbar.append(lang, button);
    pre.before(toolbar);
  });
  const article = document.getElementById('article-content');
  const toc = document.getElementById('toc');
  if (article && toc) {
    const headings = Array.from(article.querySelectorAll('h2,h3'));
    const nav = document.getElementById('toc-links');
    headings.forEach((heading, index) => {
      if (!heading.id) heading.id = `section-${index + 1}`;
      const a = document.createElement('a');
      a.href = '#' + encodeURIComponent(heading.id);
      a.textContent = heading.textContent;
      if (heading.tagName === 'H3') a.className = 'toc-sub';
      nav.appendChild(a);
    });
    if (headings.length) {
      toc.hidden = false;
      const details = toc.querySelector('details');
      const mobile = window.matchMedia('(max-width: 960px)');
      details.open = !mobile.matches;
      mobile.addEventListener('change', e => { details.open = !e.matches; });
    }
    if ('IntersectionObserver' in window) {
      const links = Array.from(nav.children);
      const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (!entry.isIntersecting) return;
          links.forEach(link => link.removeAttribute('aria-current'));
          const index = headings.indexOf(entry.target);
          links[index].setAttribute('aria-current', 'location');
        });
      }, { rootMargin: '-5% 0px -75% 0px' });
      headings.forEach(h => observer.observe(h));
    }
    article.querySelectorAll('img').forEach(img => { img.loading = 'lazy'; img.decoding = 'async'; });
  }
  const top = document.getElementById('back-to-top');
  const progress = document.getElementById('reading-progress');
  let queued = false;
  function updateScroll() {
    queued = false;
    top.hidden = window.scrollY < 600;
    if (progress && article) {
      const rect = article.getBoundingClientRect();
      const distance = Math.max(1, rect.height - window.innerHeight);
      const ratio = Math.min(1, Math.max(0, -rect.top / distance));
      progress.style.transform = `scaleX(${ratio})`;
    }
  }
  function queueScroll() { if (!queued) { queued = true; requestAnimationFrame(updateScroll); } }
  window.addEventListener('scroll', queueScroll, { passive: true });
  window.addEventListener('resize', queueScroll);
  window.addEventListener('load', queueScroll);
  updateScroll();
  const share = document.getElementById('share-link');
  if (share) {
    share.hidden = false;
    share.addEventListener('click', async () => {
      const status = document.getElementById('action-status');
      try { await copy(document.querySelector('link[rel="canonical"]').href); status.textContent = '文章链接已复制'; }
      catch (_) { status.textContent = '复制失败，请复制浏览器地址栏中的链接'; }
    });
  }
}());
