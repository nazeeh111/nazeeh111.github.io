const form = document.querySelector('.search-form');
if (form) {
  form.hidden = false;
  const input = document.querySelector('#paper-search');
  const topics = [...document.querySelectorAll('[data-topic]')];
  const rows = [...document.querySelectorAll('.paper-row')];
  const count = document.querySelector('#result-count');
  const empty = document.querySelector('.empty-state');
  let topic = 'all';
  const params = new URLSearchParams(location.search);
  input.value = params.get('q') || '';
  if (topics.some(button => button.dataset.topic === params.get('topic'))) topic = params.get('topic');
  function filter() {
    const terms = input.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    let visible = 0;
    rows.forEach(row => {
      const matches = (topic === 'all' || row.dataset.category === topic) && terms.every(term => row.dataset.search.includes(term));
      row.hidden = !matches;
      if (matches) visible++;
    });
    topics.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.topic === topic)));
    count.textContent = `${visible} ${visible === 1 ? 'study' : 'studies'}`;
    empty.hidden = visible > 0;
    const next = new URL(location.href);
    if (input.value.trim()) next.searchParams.set('q', input.value.trim()); else next.searchParams.delete('q');
    if (topic !== 'all') next.searchParams.set('topic', topic); else next.searchParams.delete('topic');
    history.replaceState(null, '', next);
  }
  form.addEventListener('submit', event => { event.preventDefault(); filter(); });
  input.addEventListener('input', filter);
  topics.forEach(button => button.addEventListener('click', () => { topic = button.dataset.topic; filter(); }));
  form.addEventListener('reset', event => { event.preventDefault(); input.value = ''; topic = 'all'; filter(); input.focus(); });
  document.querySelector('#show-all').addEventListener('click', () => { input.value = ''; topic = 'all'; filter(); input.focus(); });
  filter();
}
const copy = document.querySelector('.copy-button');
if (copy) {
  copy.hidden = false;
  copy.addEventListener('click', async () => {
    const status = document.querySelector('#copy-status');
    try {
      await navigator.clipboard.writeText(document.querySelector('#bibtex').textContent);
      status.textContent = 'BibTeX copied.';
    } catch {
      status.textContent = 'Copy is unavailable in this browser. Select the citation above and copy it manually.';
    }
  });
}
