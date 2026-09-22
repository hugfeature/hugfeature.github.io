(function () {
  'use strict';
  const script = document.querySelector('script[data-index]');
  const form = document.getElementById('search-form');
  const input = document.getElementById('search-input');
  const status = document.getElementById('search-status');
  const results = document.getElementById('search-results');
  let indexPromise;
  let generation = 0;
  let timer;
  const normalize = text => String(text || '').normalize('NFKC').toLocaleLowerCase();
  function loadIndex() {
    if (!indexPromise) indexPromise = fetch(script.dataset.index).then(response => {
      if (!response.ok) throw new Error('Index unavailable');
      return response.json();
    }).then(posts => posts.map(post => ({ ...post, fields: [post.title, post.description, (post.tags || []).join(' ').replace(/-/g, ' '), post.content].map(normalize) }))).catch(error => { indexPromise = null; throw error; });
    return indexPromise;
  }
  async function search() {
    const current = ++generation;
    const query = input.value.trim().slice(0, 200);
    results.replaceChildren();
    const url = new URL(location.href);
    if (query) url.searchParams.set('q', query); else url.searchParams.delete('q');
    history.replaceState(null, '', url);
    if (!query) { status.textContent = '输入关键词搜索，也可以组合多个词。'; return; }
    status.textContent = '正在搜索…';
    try {
      const posts = await loadIndex();
      if (current !== generation) return;
      const terms = normalize(query).split(/\s+/).filter(Boolean);
      const matches = posts.map(post => {
        let score = 0;
        for (const term of terms) {
          const weights = [8, 4, 5, 1];
          const points = post.fields.reduce((sum, field, i) => sum + (field.includes(term) ? weights[i] : 0), 0);
          if (!points) return null;
          score += points;
        }
        return { post, score };
      }).filter(Boolean).sort((a, b) => b.score - a.score);
      status.textContent = matches.length ? `找到 ${matches.length} 篇文章${matches.length > 50 ? '，显示前 50 篇' : ''}` : '没有找到匹配文章。试试更短的关键词，或浏览专题与标签。';
      matches.slice(0, 50).forEach(({ post }) => {
        const article = document.createElement('article'); article.className = 'search-result';
        const h = document.createElement('h2');
        const a = document.createElement('a'); a.href = post.url; a.textContent = post.title; h.appendChild(a);
        const p = document.createElement('p'); p.textContent = post.description;
        const meta = document.createElement('small'); meta.textContent = `${post.date} · ${(post.tags || []).join(' / ')}`;
        article.append(h, p, meta); results.appendChild(article);
      });
    } catch (_) { if (current === generation) status.textContent = '暂时无法加载搜索索引，请重试或从文章归档继续阅读。'; }
  }
  form.addEventListener('submit', e => { e.preventDefault(); clearTimeout(timer); search(); });
  input.addEventListener('input', () => { clearTimeout(timer); generation++; timer = setTimeout(search, 180); });
  input.value = (new URLSearchParams(location.search).get('q') || '').slice(0, 200);
  if (input.value) search();
}());
