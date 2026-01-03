// Effects toggle feature
(() => {
  'use strict';

  const storageKey = 'elysium_reduced_effects';
  const toggle = document.getElementById('effectsToggleGlobal');
  const heroVideo = document.querySelector('[data-hero-video]');
  if (!toggle) {
    return;
  }

  const safeGet = () => {
    try {
      return localStorage.getItem(storageKey);
    } catch (err) {
      return null;
    }
  };

  const safeSet = (value) => {
    try {
      localStorage.setItem(storageKey, value);
    } catch (err) {}
  };

  const tooltipApi = window.bootstrap && window.bootstrap.Tooltip ? window.bootstrap.Tooltip : null;

  const updateTooltip = (isReduced) => {
    if (!tooltipApi) {
      return;
    }

    const tooltip = tooltipApi.getInstance(toggle);
    if (!tooltip || typeof tooltip.setContent !== 'function') {
      return;
    }

    tooltip.setContent({ '.tooltip-inner': isReduced ? 'Effects: Off' : 'Effects: On' });
  };

  const applyState = (isReduced) => {
    document.body.classList.toggle('reduced-effects', isReduced);
    document.documentElement.classList.toggle('reduced-effects', isReduced);
    toggle.setAttribute('aria-pressed', String(isReduced));
    toggle.setAttribute('title', isReduced ? 'Effects: Off' : 'Effects: On');
    toggle.classList.toggle('is-active', isReduced);

    const icon = toggle.querySelector('i');
    if (icon) {
      icon.className = isReduced ? 'fa-solid fa-eye-slash' : 'fa-solid fa-wand-magic-sparkles';
    }

    updateTooltip(isReduced);

    if (!heroVideo) {
      return;
    }

    if (isReduced) {
      heroVideo.pause();
      return;
    }

    const playPromise = heroVideo.play();
    if (playPromise && typeof playPromise.catch === 'function') {
      playPromise.catch(() => {});
    }
  };

  if (tooltipApi) {
    tooltipApi.getOrCreateInstance(toggle);
  }

  const initial = safeGet() === '1';
  applyState(initial);

  const handleClick = () => {
    const next = !document.body.classList.contains('reduced-effects');
    safeSet(next ? '1' : '0');
    applyState(next);
  };

  toggle.addEventListener('click', handleClick);
})();
