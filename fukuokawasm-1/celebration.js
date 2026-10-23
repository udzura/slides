(() => {
  const trigger = document.querySelector('[data-celebrate]');
  if (!trigger) return;

  const style = document.createElement('style');
  style.textContent = `
    .celebration-layer { position:fixed; inset:0; z-index:10000;
      overflow:hidden; pointer-events:none; }
    .celebration-particle { position:absolute; display:block; line-height:1;
      user-select:none; will-change:transform,opacity; }
    @media print { .celebration-layer { display:none !important; } }
  `;
  document.head.append(style);

  let layer;
  let animations = [];
  trigger.addEventListener('click', (event) => {
    event.stopPropagation();
    animations.forEach((animation) => animation.cancel());
    layer?.remove();

    const bounds = trigger.getBoundingClientRect();
    const slide = trigger.closest('section');
    const scale = slide ? slide.getBoundingClientRect().width / slide.offsetWidth : 1;
    const origin = { x: bounds.left + bounds.width / 2, y: bounds.top + bounds.height / 2 };
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const burst = document.createElement('div');
    burst.className = 'celebration-layer';
    burst.setAttribute('aria-hidden', 'true');
    document.body.append(burst);
    layer = burst;

    const emoji = ['🎉', '✨', '🎊', '🌟'];
    const colors = ['#b53d27', '#d8a438', '#47614b', '#3f627e', '#aa66cc'];
    animations = Array.from({ length: reduced ? 5 : 48 }, (_, index) => {
      const particle = document.createElement('span');
      particle.className = 'celebration-particle';
      const isEmoji = reduced || index % 6 === 0;
      const size = (isEmoji ? 32 : 8 + Math.random() * 5) * scale;
      Object.assign(particle.style, {
        left: `${origin.x - size / 2 + (reduced ? (index - 2) * 40 * scale : 0)}px`,
        top: `${origin.y - size / 2 - (reduced ? 58 * scale : 0)}px`,
        width: `${size}px`, height: `${isEmoji ? size : size * 1.6}px`,
        fontSize: `${size}px`,
        background: isEmoji ? 'none' : colors[index % colors.length],
      });
      if (isEmoji) particle.textContent = emoji[(reduced ? index : Math.floor(index / 6)) % emoji.length];
      burst.append(particle);

      const vx = (Math.random() - 0.5) * 840 * scale;
      const vy = (-550 - Math.random() * 200) * scale;
      const gravity = (480 + Math.random() * 140) * scale;
      const rotation = (Math.random() - 0.5) * 1080;
      const frames = reduced ? [{ opacity: 0 }, { opacity: 1, offset: 0.2 }, { opacity: 0 }]
        : Array.from({ length: 9 }, (_, step) => {
          const t = step / 8;
          return {
            offset: t,
            opacity: t < 0.6 ? 1 : (1 - t) / 0.4,
            transform: `translate(${vx * t}px, ${vy * t + gravity * t * t}px) `
              + `rotate(${rotation * t}deg) scale(${step === 0 ? 0.35 : 1})`,
          };
        });
      return particle.animate(frames, {
        duration: reduced ? 500 : 1300 + Math.random() * 500,
        easing: 'linear', fill: 'forwards',
      });
    });
    Promise.allSettled(animations.map((animation) => animation.finished)).then(() => {
      burst.remove();
      if (layer === burst) {
        layer = undefined;
        animations = [];
      }
    });
  });

  // Keep native button activation while preventing Space/Enter from advancing slides.
  for (const type of ['keydown', 'keyup']) {
    trigger.addEventListener(type, (event) => {
      if (event.key === ' ' || event.key === 'Enter') event.stopPropagation();
    });
  }
})();
