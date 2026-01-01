// Toggle reduced effects for motion-sensitive users

(() => {
  const storageKey = 'elysium_reduced_effects';
  const toggle = document.getElementById('effectsToggleGlobal');
  const heroVideo = document.querySelector('[data-hero-video]');

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
    } catch (err) {
      // Ignore storage errors (e.g., blocked storage).
    }
  };

  const applyState = (isReduced) => {
    document.body.classList.toggle('reduced-effects', isReduced);
    document.documentElement.classList.toggle('reduced-effects', isReduced);

    if (toggle) {
      toggle.setAttribute('aria-pressed', String(isReduced));
      toggle.setAttribute('title', isReduced ? 'Effects: Off' : 'Effects: On');
      toggle.classList.toggle('is-active', isReduced);
      // Update icon based on state
      const icon = toggle.querySelector('i');
      if (icon) {
        icon.className = isReduced ? 'fa-solid fa-eye-slash' : 'fa-solid fa-wand-magic-sparkles';
      }
      // Update Bootstrap tooltip if initialized
      const tooltip = bootstrap.Tooltip.getInstance(toggle);
      if (tooltip) {
        tooltip.setContent({ '.tooltip-inner': isReduced ? 'Effects: Off' : 'Effects: On' });
      }
    }

    if (heroVideo) {
      if (isReduced) {
        heroVideo.pause();
      } else {
        const playPromise = heroVideo.play();
        if (playPromise && typeof playPromise.catch === 'function') {
          playPromise.catch(() => {});
        }
      }
    }
  };

  // Initialize tooltip
  if (toggle) {
    new bootstrap.Tooltip(toggle);
  }

  const initial = safeGet() === '1';
  applyState(initial);

  if (toggle) {
    toggle.addEventListener('click', () => {
      const next = !document.body.classList.contains('reduced-effects');
      safeSet(next ? '1' : '0');
      applyState(next);
    });
  }
})();
