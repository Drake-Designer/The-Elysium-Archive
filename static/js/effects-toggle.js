// Toggle reduced effects for motion-sensitive users

(() => {
  const storageKey = 'elysium_reduced_effects';
  const toggleMobile = document.getElementById('effectsToggleGlobal');
  const toggleDesktop = document.getElementById('effectsToggleGlobalDesktop');
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

    // Update both buttons (mobile and desktop)
    const buttons = [toggleMobile, toggleDesktop].filter(Boolean);
    buttons.forEach((toggle) => {
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
    });

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

  // Initialize tooltips for both buttons
  if (toggleMobile) {
    new bootstrap.Tooltip(toggleMobile);
  }
  if (toggleDesktop) {
    new bootstrap.Tooltip(toggleDesktop);
  }

  const initial = safeGet() === '1';
  applyState(initial);

  // Attach click handlers to both buttons
  if (toggleMobile) {
    toggleMobile.addEventListener('click', () => {
      const next = !document.body.classList.contains('reduced-effects');
      safeSet(next ? '1' : '0');
      applyState(next);
    });
  }

  if (toggleDesktop) {
    toggleDesktop.addEventListener('click', () => {
      const next = !document.body.classList.contains('reduced-effects');
      safeSet(next ? '1' : '0');
      applyState(next);
    });
  }
})();
