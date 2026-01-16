// Dashboard tab switching

(() => {
  'use strict';

  const initDashboardTabs = () => {
    const tabContainer = document.getElementById('dashboardContent');
    const buttons = document.querySelectorAll('[data-dashboard-tab]');
    if (!tabContainer || !buttons.length) {
      return;
    }

    const normalizeTab = (tabName) => {
      if (!tabName) {
        return null;
      }

      const clean = String(tabName).trim().toLowerCase();

      if (clean === 'my-archive' || clean === 'my_archive') {
        return 'archive';
      }

      if (clean === 'profile' || clean === 'archive' || clean === 'delete') {
        return clean;
      }

      return null;
    };

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

    const setUrlTab = (tabName) => {
      const url = new URL(window.location.href);
      url.searchParams.set('tab', tabName === 'archive' ? 'my-archive' : tabName);
      window.history.replaceState({}, '', url);
    };

    buttons.forEach((button) => {
      button.addEventListener('click', (event) => {
        const tabName = normalizeTab(button.getAttribute('data-dashboard-tab'));
        if (!tabName) {
          return;
        }

        event.preventDefault();
        setActive(tabName);
        setUrlTab(tabName);
      });
    });

    const urlTab = normalizeTab(new URLSearchParams(window.location.search).get('tab'));
    if (urlTab) {
      setActive(urlTab);
      setUrlTab(urlTab);
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDashboardTabs);
    return;
  }

  initDashboardTabs();
})();
