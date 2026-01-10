document.addEventListener('DOMContentLoaded', function () {
  var input = document.getElementById('id_image_alt') || document.querySelector('input[name="image_alt"]');
  if (!input) return;

  // Ensure maxlength is present as a safeguard
  try {
    input.setAttribute('maxlength', '150');
  } catch (e) {
    // ignore
  }

  var counter = document.createElement('div');
  counter.className = 'char-counter';
  counter.textContent = (input.value ? input.value.length : 0) + '/150';

  // Insert counter immediately after the input
  if (input.parentNode) {
    input.parentNode.insertBefore(counter, input.nextSibling);
  }

  function update() {
    var len = input.value.length;
    counter.textContent = len + '/150';
    if (len >= 150) {
      counter.classList.add('is-max');
    } else {
      counter.classList.remove('is-max');
    }
  }

  input.addEventListener('input', update);
});
