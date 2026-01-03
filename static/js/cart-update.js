/**
 * Handles cart quantity updates with visual feedback.
 */

document.addEventListener('DOMContentLoaded', function () {
  // Select all quantity update forms in the cart
  const updateForms = document.querySelectorAll('.cart-update-form');

  updateForms.forEach(function (form) {
    const quantityInput = form.querySelector('.cart-quantity-input');
    const updateBtn = form.querySelector('.cart-update-btn');
    const row = form.closest('.cart-item-row');

    // Track the original quantity to detect changes
    let originalQuantity = parseInt(quantityInput.value);

    // Show visual feedback when quantity changes
    quantityInput.addEventListener('input', function () {
      const currentQuantity = parseInt(quantityInput.value);

      if (currentQuantity !== originalQuantity) {
        updateBtn.classList.add('btn-warning');
        updateBtn.classList.remove('btn-outline-primary');
        row.classList.add('table-warning');
      } else {
        updateBtn.classList.remove('btn-warning');
        updateBtn.classList.add('btn-outline-primary');
        row.classList.remove('table-warning');
      }
    });

    // Show loading state on form submission
    form.addEventListener('submit', function () {
      updateBtn.disabled = true;
      updateBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
      row.style.opacity = '0.6';
    });
  });
});
