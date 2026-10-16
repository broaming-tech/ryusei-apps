'use strict';
(() => {
  const buttons = [...document.querySelectorAll('.filter')];
  const cards = [...document.querySelectorAll('.card[data-kind]')];
  const status = document.querySelector('#filter-result');
  function setFilter(kind) {
    let shown = 0;
    buttons.forEach(button => {
      const selected = button.dataset.filter === kind;
      button.setAttribute('aria-pressed', String(selected));
    });
    cards.forEach(card => {
      const visible = kind === 'all' || card.dataset.kind === kind;
      card.hidden = !visible;
      if (visible) shown++;
    });
    if (status) status.textContent = `${shown}作品を表示中`;
  }
  buttons.forEach(button => button.addEventListener('click', () => setFilter(button.dataset.filter)));
  // Icons are obtained from Apple's official iTunes metadata at build/deployment time.
  // Missing artwork reveals a neutral, non-deceptive letter fallback.
  document.querySelectorAll('.app-icon img').forEach(img => {
    const markUnavailable = () => img.classList.add('failed');
    img.addEventListener('error', markUnavailable, {once: true});
    if (img.complete && img.naturalWidth === 0) markUnavailable();
  });
})();
