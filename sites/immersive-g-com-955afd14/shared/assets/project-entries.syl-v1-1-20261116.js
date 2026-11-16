// Home cards for projects with several entries: the entry buttons stand in for the description.
(() => {
  const ENTRIES = {"projects/shouyu-pass":[{"label":"通行证主页","url":"https://shouyulove.cn/auth/","icon":"<svg viewBox=\"0 0 256 256\" aria-hidden=\"true\"><g stroke=\"#4b5d54\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"13\" transform=\"translate(23 6)\">\n<path d=\"M38 78 H172 V188 Q172 210 150 210 H60 Q38 210 38 188 Z\" fill=\"#ece2cf\" stroke=\"none\"></path>\n<path d=\"M60 34 H150 Q172 34 172 56 V78 H38 V56 Q38 34 60 34 Z\" fill=\"#aec2b1\" stroke=\"none\"></path>\n<path d=\"M60 34 H150 Q172 34 172 56 V188 Q172 210 150 210 H60 Q38 210 38 188 V56 Q38 34 60 34 Z M38 78 H172 M92 56 H118\" fill=\"none\"></path>\n<path d=\"M105 157 C80 140 73 123 82 112 C89 104 99 108 105 117 C111 108 121 104 128 112 C137 123 130 140 105 157 Z\" fill=\"#c9a2a4\" stroke-width=\"11\"></path>\n<path d=\"M84 183 H126\" fill=\"none\"></path>\n</g></svg>"},{"label":"接入与配置中心","url":"https://shouyulove.cn/auth/dev","icon":"<svg viewBox=\"0 0 256 256\" aria-hidden=\"true\"><g stroke=\"#4b5d54\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"13\">\n<path d=\"M111.2 58.0 L115.2 32.9 L140.8 32.9 L144.8 58.0 L165.6 66.6 L186.2 51.7 L204.3 69.8 L189.4 90.4 L198.0 111.2 L223.1 115.2 L223.1 140.8 L198.0 144.8 L189.4 165.6 L204.3 186.2 L186.2 204.3 L165.6 189.4 L144.8 198.0 L140.8 223.1 L115.2 223.1 L111.2 198.0 L90.4 189.4 L69.8 204.3 L51.7 186.2 L66.6 165.6 L58.0 144.8 L32.9 140.8 L32.9 115.2 L58.0 111.2 L66.6 90.4 L51.7 69.8 L69.8 51.7 L90.4 66.6 Z\" fill=\"#d4be88\"></path>\n<circle cx=\"128\" cy=\"128\" fill=\"#ece2cf\" r=\"41\"></circle>\n<circle cx=\"128\" cy=\"119\" fill=\"#4b5d54\" r=\"9\" stroke=\"none\"></circle>\n<path d=\"M128 124 V148\" fill=\"none\" stroke-width=\"12\"></path>\n</g></svg>"}]};
  const STYLE = "/* Home cards with several entries; injected by scripts/project_entries.js. */\n.homePage .projectBlock[data-syl-entries] > .projectEntry { display: none; }\n.homePage .projectBlock[data-syl-entries] .mediaBlock__image.text > p { display: none; }\n.homePage .projectCard__entries { position: relative; z-index: 2; display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; }\n.homePage .projectCard__entry {\n  display: inline-flex;\n  align-items: center;\n  gap: 7px;\n  min-height: 44px;\n  padding: 4px 12px 4px 6px;\n  border: 1px solid rgba(52, 52, 52, .26);\n  border-radius: 999px;\n  background: rgba(255, 255, 255, .42);\n  color: #1c1c1c;\n  font-family: PSTimes, \"ShouYuSerif\", serif;\n  font-size: 15px;\n  line-height: 1.3;\n  white-space: nowrap;\n  text-decoration: none;\n  cursor: pointer;\n  pointer-events: auto;\n  -webkit-tap-highlight-color: transparent;\n  transition: border-color 180ms ease-out, background-color 180ms ease-out;\n}\n.homePage .projectCard__entry > svg:first-child { flex: none; width: 28px; height: 28px; }\n.homePage .projectCard__entryArrow { flex: none; width: 13px; height: 13px; fill: none; stroke: currentColor; stroke-width: 1.4; stroke-linecap: round; stroke-linejoin: round; transition: transform 180ms ease-out; }\n.homePage .projectCard__entry:focus-visible { outline: 2px solid currentColor; outline-offset: 3px; }\n@media (hover: hover) and (pointer: fine) {\n  .homePage .projectCard__entry:hover { border-color: rgba(52, 52, 52, .7); background: rgba(255, 255, 255, .78); }\n  .homePage .projectCard__entry:hover .projectCard__entryArrow { transform: translate(2px, -2px); }\n}\n@media (max-width: 767px) {\n  .homePage .projectCard__entries { justify-content: flex-start; }\n}\n@media (max-width: 360px) {\n  .homePage .projectCard__entry { gap: 5px; padding: 4px 10px 4px 5px; font-size: 14px; }\n  .homePage .projectCard__entry > svg:first-child { width: 24px; height: 24px; }\n  .homePage .projectCard__entryArrow { display: none; }\n}\n@media (prefers-reduced-motion: reduce) {\n  .homePage .projectCard__entry, .homePage .projectCard__entryArrow { transition: none; }\n  .homePage .projectCard__entry:hover .projectCard__entryArrow { transform: none; }\n}\n@font-face{font-family:ShouYuSerif;font-style:normal;font-weight:400;font-display:block;src:url(data:font/woff2;base64,d09GMgABAAAAAAM4ABEAAAAABlQAAALgAAEFYAAAAAAAAAAAAAAAAAAAAAAAAAAAGhQbIBxIBlYANAgEEQgKgxiCcQE2AiQDCAsGAAQgBYM0ByAXJBgGGwIFQI6SnBImHB47eCC9+jeZ7O1eckYOlewvqZTcWdWvAC0Pn7f3t40mXchpF1jAAZYW1QWapryDa+pH0uuCU3TAA5pQNEf10aJp4DPa+9ZAlTSQ8axtk8U+R5AkXdN5DJqCAHYAQEgBHGiR54mpqKIBCxVgtcIO3DwsovfEUUOI6T+q72AUD+g5rD8yEBmM9BQM6TlmWCUWAEwj8xMuY4JyKi1AuT4kVuJEISjNhHEW1RQv1cXk3PPYgBxhXQBy4yMIAKAACdyQRFVUGYDqFsizW63oGHb0hkHKREBECgoAp6nADFYB28B7hwDmoqtmt+iMbl1ojcxYpuuLV+h6cx/so01oXAjc0qgt2i2Exoz7MQczli7ywD62ts94NQ39Woa6n9S0RcuFsGNG6NIFMM1coeuisx6rrfbboq1phjt3xnOF55pmL6rDxs+MnaFHcyxhA5Upe2G3qGi6felW5tN+75kwJWH4jl91ltE2dYrCwbC5k8InfewZmvZXO/D40ryAgGbfswmh0bZlm5/nTqpTQvgwZfY6GS/3T5mCmUlanKN51uSEZ2iWxy62l3XTm2/UlHk5WExV4+W7ZzVNKTvt8kb7D2i9M6J03jhTiZcOMl4qaxa56MFziseNzA22hjzxAZs3msltSRpaBcap4284WD5vXg0AAoja47qD5+hux4xvlkD5EuDZ1ll3AF4YpaeEWo/I21IDLBQAAr/f0uMMXgMQLKfEEILK7gVQrMIMQAGCADmiAACzNpIotoAHrCRCDB4ShYMiiTROg0SVxVWJiY+wLGMjRQSTb4CxhjFoNRaX72m4euP1NZBBvRFGGWiY/modq7w9jWKQr0w5r4Vm6vTVP8oO0aDIcMOMaf/UKP31ZRBHFDEYpGHwqxutN8PAAlOIJJYYROJ00k/exiZ9jTLawNP7DGJPHEwiVnqbWbpFWaRNMhWsa3mRGDAfv0MgO/2Ey3OAYFYR8z6kHwA=) format('woff2');unicode-range:U+914D;}\n";
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
