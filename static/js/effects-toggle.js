// Effects toggle feature

(() => {
  'use strict';

  const storageKey = 'elysium_reduced_effects';
  const toggle = document.getElementById('effectsToggleGlobal');
  const heroVideo = document.querySelector('[data-hero-video]');
  const mediaQuery = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : null;

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
    if (!tooltipApi || !toggle) {
      return;
    }

    const tooltip = tooltipApi.getInstance(toggle);
    if (!tooltip || typeof tooltip.setContent !== 'function') {
      return;
    }

    tooltip.setContent({ '.tooltip-inner': isReduced ? 'Effects: Off' : 'Effects: On' });
  };

  const pauseHeroVideo = () => {
    if (!heroVideo) {
      return;
    }

    heroVideo.pause();
    heroVideo.removeAttribute('autoplay');
  };

  const playHeroVideo = () => {
    if (!heroVideo) {
      return;
    }

    const playPromise = heroVideo.play();
    if (playPromise && typeof playPromise.catch === 'function') {
      playPromise.catch(() => {});
    }
  };

  const applyState = (isReduced) => {
    document.body.classList.toggle('reduced-effects', isReduced);
    document.documentElement.classList.toggle('reduced-effects', isReduced);

    if (toggle) {
      toggle.setAttribute('aria-pressed', String(isReduced));
      toggle.setAttribute('title', isReduced ? 'Effects: Off' : 'Effects: On');
      toggle.classList.toggle('is-active', isReduced);

      const icon = toggle.querySelector('i');
      if (icon) {
        icon.className = isReduced ? 'fa-solid fa-eye-slash' : 'fa-solid fa-wand-magic-sparkles';
      }

      updateTooltip(isReduced);
    }

    if (isReduced) {
      pauseHeroVideo();
      return;
    }

    playHeroVideo();
  };

  const getInitialReducedState = () => {
    const stored = safeGet();
    if (stored === '1') {
      return true;
    }
    if (stored === '0') {
      return false;
    }

    if (mediaQuery) {
      return mediaQuery.matches;
    }

    return false;
  };

  const setStoredState = (isReduced) => {
    safeSet(isReduced ? '1' : '0');
  };

  const handleClick = () => {
    const next = !document.body.classList.contains('reduced-effects');
    setStoredState(next);
    applyState(next);
  };

  const handleSystemChange = () => {
    const stored = safeGet();
    if (stored === '1' || stored === '0') {
      return;
    }

    const prefersReduced = mediaQuery ? mediaQuery.matches : false;
    applyState(prefersReduced);
  };

  if (tooltipApi && toggle) {
    tooltipApi.getOrCreateInstance(toggle);
  }

  applyState(getInitialReducedState());

  if (toggle) {
    toggle.addEventListener('click', handleClick);
  }

  if (mediaQuery) {
    if (typeof mediaQuery.addEventListener === 'function') {
      mediaQuery.addEventListener('change', handleSystemChange);
    } else if (typeof mediaQuery.addListener === 'function') {
      mediaQuery.addListener(handleSystemChange);
    }
  }
})();
