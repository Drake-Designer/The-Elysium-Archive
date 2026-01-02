// Toggle reduced effects for motion-sensitive users

(() => {
  const storageKey = 'elysium_reduced_effects';
  const toggleMobile = document.getElementById('effectsToggleGlobal');
  const toggleDesktop = document.getElementById('effectsToggleGlobalDesktop');
  const heroVideo = document.querySelector('[data-hero-video]');

  const buttons = [toggleMobile, toggleDesktop].filter(Boolean);

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

  const updateTooltip = (toggle, isReduced) => {
    const Tooltip = window.bootstrap?.Tooltip;
    if (!Tooltip) return;

    const tooltip = Tooltip.getInstance(toggle);
    if (!tooltip || typeof tooltip.setContent !== 'function') return;

    tooltip.setContent({ '.tooltip-inner': isReduced ? 'Effects: Off' : 'Effects: On' });
  };

  const applyState = (isReduced) => {
    document.body.classList.toggle('reduced-effects', isReduced);
    document.documentElement.classList.toggle('reduced-effects', isReduced);

    // Update both buttons (mobile and desktop)
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
      updateTooltip(toggle, isReduced);
    });

    if (!heroVideo) return;

    if (isReduced) {
      heroVideo.pause();
      return;
    }

    const playPromise = heroVideo.play();
    if (playPromise && typeof playPromise.catch === 'function') {
      playPromise.catch(() => {});
    }
  };

  // Initialize tooltips for both buttons
  const Tooltip = window.bootstrap?.Tooltip;
  if (Tooltip) {
    buttons.forEach((toggle) => {
      Tooltip.getOrCreateInstance(toggle);
    });
  }

  const initial = safeGet() === '1';
  applyState(initial);

  // Attach click handlers to both buttons
  const handleClick = () => {
    const next = !document.body.classList.contains('reduced-effects');
    safeSet(next ? '1' : '0');
    applyState(next);
  };

  buttons.forEach((toggle) => {
    toggle.addEventListener('click', handleClick);
  });
})();
