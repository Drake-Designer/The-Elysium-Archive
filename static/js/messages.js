// Message auto-dismiss handler

document.addEventListener('DOMContentLoaded', () => {
  const messages = document.querySelectorAll('.js-django-message');
  if (!messages.length) {
    return;
  }

  setTimeout(() => {
    messages.forEach((el) => {
      try {
        if (window.bootstrap && window.bootstrap.Alert) {
          const alertInstance = window.bootstrap.Alert.getOrCreateInstance(el);
          alertInstance.close();
          return;
        }

        el.classList.remove('show');
        el.addEventListener('transitionend', () => el.remove(), { once: true });
        setTimeout(() => el.remove(), 600);
      } catch (error) {
        el.remove();
      }
    });
  }, 5000);
});
