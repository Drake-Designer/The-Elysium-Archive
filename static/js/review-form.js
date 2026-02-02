/**
 * Review Form Character Counter
 * Manages character counting for review title and body fields
 */

document.addEventListener('DOMContentLoaded', () => {
  // Title field character counter
  const titleInput = document.getElementById('review-title-input');
  const titleCounter = document.getElementById('title-counter');

  if (titleInput && titleCounter) {
    const titleMaxLength = parseInt(titleInput.getAttribute('data-max-length')) || 50;

    const updateTitleCounter = () => {
      let currentLength = titleInput.value.length;

      // Force truncate if exceeds max length
      if (currentLength > titleMaxLength) {
        titleInput.value = titleInput.value.substring(0, titleMaxLength);
        currentLength = titleMaxLength;
      }

      titleCounter.textContent = `${currentLength} / ${titleMaxLength}`;

      // Add warning/error classes based on character count
      titleCounter.classList.remove('warning', 'error');
      if (currentLength >= titleMaxLength) {
        titleCounter.classList.add('error');
      } else if (currentLength >= titleMaxLength * 0.9) {
        titleCounter.classList.add('warning');
      }
    };

    // Update counter on input and enforce max length
    titleInput.addEventListener('input', updateTitleCounter);
    titleInput.addEventListener('keydown', (e) => {
      // Block input if at max length and not a control key
      const isControlKey =
        e.key === 'Backspace' ||
        e.key === 'Delete' ||
        e.key === 'ArrowLeft' ||
        e.key === 'ArrowRight' ||
        e.key === 'Tab' ||
        e.ctrlKey ||
        e.metaKey;
      if (titleInput.value.length >= titleMaxLength && !isControlKey) {
        e.preventDefault();
      }
    });

    // Initialize counter
    updateTitleCounter();
  }

  // Body field character counter
  const bodyInput = document.getElementById('review-body-input');
  const bodyCounter = document.getElementById('body-counter');

  if (bodyInput && bodyCounter) {
    const bodyMaxLength = parseInt(bodyInput.getAttribute('data-max-length')) || 1000;

    const updateBodyCounter = () => {
      let currentLength = bodyInput.value.length;

      // Force truncate if exceeds max length
      if (currentLength > bodyMaxLength) {
        bodyInput.value = bodyInput.value.substring(0, bodyMaxLength);
        currentLength = bodyMaxLength;
      }

      bodyCounter.textContent = `${currentLength} / ${bodyMaxLength}`;

      // Add warning/error classes based on character count
      bodyCounter.classList.remove('warning', 'error');
      if (currentLength >= bodyMaxLength) {
        bodyCounter.classList.add('error');
      } else if (currentLength >= bodyMaxLength * 0.9) {
        bodyCounter.classList.add('warning');
      }
    };

    // Update counter on input and enforce max length
    bodyInput.addEventListener('input', updateBodyCounter);
    bodyInput.addEventListener('keydown', (e) => {
      // Block input if at max length and not a control key
      const isControlKey =
        e.key === 'Backspace' ||
        e.key === 'Delete' ||
        e.key === 'ArrowLeft' ||
        e.key === 'ArrowRight' ||
        e.key === 'ArrowUp' ||
        e.key === 'ArrowDown' ||
        e.key === 'Tab' ||
        e.ctrlKey ||
        e.metaKey;
      if (bodyInput.value.length >= bodyMaxLength && !isControlKey) {
        e.preventDefault();
      }
    });

    // Initialize counter
    updateBodyCounter();
  }
});
