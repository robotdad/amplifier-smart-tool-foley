/* Progressive enhancement only. All content and links work without JavaScript. */
for (const button of document.querySelectorAll('[data-copy]')) {
  button.addEventListener('click', async () => {
    const code = document.getElementById(button.dataset.copy);
    const status = button.closest('.copy-region').querySelector('[role="status"]');
    try {
      await navigator.clipboard.writeText(code.textContent);
      status.textContent = 'Copied. Paste this into your agent or terminal.';
    } catch {
      const range = document.createRange();
      range.selectNodeContents(code);
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
      status.textContent = 'Text selected. Use your usual copy command.';
    }
  });
}
const search = document.getElementById('tool-search');
if (search) {
  const platform = document.getElementById('platform');
  const cards = [...document.querySelectorAll('[data-tool]')];
  const count = document.getElementById('result-count');
  const empty = document.getElementById('empty-results');
  function filter() {
    const words = search.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    let visible = 0;
    for (const card of cards) {
      const matches = words.every(word => card.dataset.search.includes(word)) &&
        (!platform.value || card.dataset.platforms.split(' ').includes(platform.value));
      card.hidden = !matches;
      if (matches) visible++;
    }
    count.textContent = `${visible} of ${cards.length} tools`;
    empty.hidden = visible !== 0;
  }
  search.addEventListener('input', filter);
  platform.addEventListener('change', filter);
  document.getElementById('clear-filters').addEventListener('click', () => {
    search.value = ''; platform.value = ''; filter(); search.focus();
  });
  filter();
}

// GIFs have no pause API. Use a matching still when motion is paused or reduced.
const motionImages = [...document.querySelectorAll('[data-motion-src]')];
const demoVideos = [...document.querySelectorAll('[data-demo-video]')];
if (motionImages.length || demoVideos.length) {
  const preference = window.matchMedia('(prefers-reduced-motion: reduce)');
  let paused = preference.matches;
  let motionRequest = 0;
  function showStill(video, visible) {
    const still = video.parentElement.querySelector('[data-brand-still]');
    if (!still) return;
    if (visible && document.activeElement === video) {
      document.querySelector('[data-motion-toggle]').focus();
    }
    still.hidden = !visible;
    video.hidden = visible;
  }
  function setMotion() {
    const request = ++motionRequest;
    for (const img of motionImages) {
      img.src = paused ? img.dataset.stillSrc : img.dataset.motionSrc;
    }
    for (const video of demoVideos) {
      if (paused) {
        video.pause();
        showStill(video, true);
      } else {
        video.play().catch(() => {
          if (request !== motionRequest) return;
          // Keep the readable still and explicit retry control if autoplay is denied.
          paused = true;
          setMotion();
        });
      }
    }
    for (const button of document.querySelectorAll('[data-motion-toggle]')) {
      button.hidden = false;
      button.textContent = paused ? 'Play motion' : 'Pause motion';
      button.setAttribute('aria-pressed', String(paused));
    }
  }
  for (const video of demoVideos) {
    showStill(video, true);
    video.addEventListener('playing', () => {
      if (paused) video.pause();
      else showStill(video, false);
    });
    video.addEventListener('pause', () => {
      if (!video.paused) return;
      showStill(video, true);
      if (!paused) {
        paused = true;
        setMotion();
      }
    });
  }
  for (const button of document.querySelectorAll('[data-motion-toggle]')) {
    button.addEventListener('click', () => { paused = !paused; setMotion(); });
  }
  preference.addEventListener('change', event => { paused = event.matches; setMotion(); });
  setMotion();
}
