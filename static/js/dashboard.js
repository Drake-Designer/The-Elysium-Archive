// Dashboard tab switching
(() => {
  'use strict';

  const initDashboardTabs = () => {
    const tabContainer = document.getElementById('dashboardContent');
    const buttons = document.querySelectorAll('[data-dashboard-tab]');
    if (!tabContainer || !buttons.length) {
      return;
    }

    const setActive = (tabName) => {
      const targetPane = document.getElementById(tabName);
      if (!targetPane) {
        return;
      }

      tabContainer.querySelectorAll('.tab-pane').forEach((pane) => {
        pane.classList.remove('active', 'show');
      });
      targetPane.classList.add('active', 'show');

      buttons.forEach((button) => {
        const isActive = button.getAttribute('data-dashboard-tab') === tabName;
        button.classList.toggle('active', isActive);
        button.setAttribute('aria-selected', isActive ? 'true' : 'false');
      });
    };

    buttons.forEach((button) => {
      button.addEventListener('click', (event) => {
        const tabName = button.getAttribute('data-dashboard-tab');
        if (!tabName) {
          return;
        }

        event.preventDefault();
        setActive(tabName);
      });
    });
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDashboardTabs);
    return;
  }

  initDashboardTabs();
})();
