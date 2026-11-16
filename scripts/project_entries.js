// Home cards for projects with several entries: the entry buttons stand in for the description.
(() => {
  const ENTRIES = /*__ENTRIES__*/{};
  const STYLE = /*__STYLE__*/'';
  const ARROW = '<svg class="projectCard__entryArrow" viewBox="0 0 24 24" aria-hidden="true"><path d="M14 5h5v5m0-5-9 9M10 5H5v14h14v-5"/></svg>';
  if (!Object.keys(ENTRIES).length) return;

  const style = document.createElement('style');
  style.textContent = STYLE;
  document.head.appendChild(style);

  const build = (entries) => {
    const box = document.createElement('div');
    box.className = 'projectCard__entries';
    for (const entry of entries) {
      const link = document.createElement('a');
      link.className = 'projectCard__entry';
      link.href = entry.url;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      link.innerHTML = entry.icon + '<span></span>' + ARROW;
      link.querySelector('span').textContent = entry.label;
      box.appendChild(link);
    }
    // The card opens its detail page on click; the buttons only open their own address.
    for (const type of ['click', 'pointerdown', 'pointerup', 'mousedown', 'mouseup', 'touchstart', 'touchend']) {
      box.addEventListener(type, (event) => event.stopPropagation());
    }
    return box;
  };

  const apply = () => {
    for (const card of document.querySelectorAll('.homePage .projectBlock[data-uri]:not([data-syl-entries])')) {
      const entries = ENTRIES[card.dataset.uri];
      const copy = card.querySelector('.mediaBlock__image.text');
      if (!entries || !copy) continue;
      card.dataset.sylEntries = '';
      copy.append(build(entries));
    }
  };

  let queued = false;
  new MutationObserver(() => {
    if (queued) return;
    queued = true;
    requestAnimationFrame(() => { queued = false; apply(); });
  }).observe(document.documentElement, { childList: true, subtree: true });
  apply();
})();
