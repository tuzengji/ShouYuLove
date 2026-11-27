// 作品集：分类按钮标出当前所在的分类；标题旁那颗手绘爱心点一下会转一圈。
(() => {
  const { still } = SylNext;
  const chips = new Map([...document.querySelectorAll('.chips a')].map((chip) => [chip.hash.slice(1), chip]));
  if (window.IntersectionObserver && chips.size) {
    const here = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        chips.forEach((chip, name) => chip.classList.toggle('is-here', name === entry.target.id));
        const chip = chips.get(entry.target.id), row = chip.closest('ul');
        row.scrollTo({ left: chip.offsetLeft - row.offsetLeft - 16, behavior: still.matches ? 'auto' : 'smooth' });
      }
    }, { rootMargin: '-30% 0px -65% 0px' });
    chips.forEach((_, name) => here.observe(document.getElementById(name)));
  }
  const mascot = document.querySelector('.mascot');
  mascot?.addEventListener('click', () => {
    mascot.classList.remove('is-spun');
    void mascot.offsetWidth; // restart the animation on a second tap
    mascot.classList.add('is-spun');
  });
  mascot?.addEventListener('animationend', (event) => { if (event.animationName === 'spin') mascot.classList.remove('is-spun'); });
})();
