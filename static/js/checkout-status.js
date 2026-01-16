// Checkout Status Poller - Auto-refreshes the page when payment status changes

(() => {
  const panel = document.getElementById('paymentStatusPanel');
  if (!panel) return;

  const statusUrl = panel.getAttribute('data-status-url');
  if (!statusUrl) return;

  const statusText = document.getElementById('paymentStatusText');
  const statusHint = document.getElementById('paymentStatusHint');

  let attempts = 0;
  const maxAttempts = 30;
  const intervalMs = 2500;

  const poll = async () => {
    attempts += 1;

    try {
      const res = await fetch(statusUrl, {
        method: 'GET',
        credentials: 'same-origin',
        headers: { Accept: 'application/json' },
      });

      if (!res.ok) {
        if (attempts >= maxAttempts && statusText) {
          statusText.textContent = 'Still processing. You can refresh, or check again later.';
        }
        return;
      }

      const data = await res.json();
      const status = data.status;

      if (status === 'paid' || status === 'failed') {
        window.location.reload();
        return;
      }

      if (attempts >= maxAttempts) {
        if (statusText) {
          statusText.textContent =
            'Payment is taking longer than expected. You can refresh now, or come back later from your dashboard.';
        }
        if (statusHint) statusHint.textContent = '';
      }
    } catch (err) {
      if (attempts >= maxAttempts && statusText) {
        statusText.textContent = 'Connection issue while checking status. Please refresh.';
      }
    }
  };

  poll();

  const timer = setInterval(() => {
    if (attempts >= maxAttempts) {
      clearInterval(timer);
      return;
    }
    poll();
  }, intervalMs);
})();
