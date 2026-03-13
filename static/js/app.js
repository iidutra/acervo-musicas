/**
 * Acervo Litúrgico Digital - Frontend
 */
(function() {
  'use strict';

  // ============================================================
  // TOAST NOTIFICATION SYSTEM
  // ============================================================
  const Toast = {
    container: null,

    init() {
      this.container = document.getElementById('toast-container');
      if (!this.container) {
        this.container = document.createElement('div');
        this.container.id = 'toast-container';
        this.container.className = 'toast-container';
        this.container.setAttribute('aria-live', 'polite');
        document.body.appendChild(this.container);
      }
    },

    show(message, type = 'info', duration = 5000) {
      if (!this.container) this.init();

      const icons = {
        success: '<svg class="toast-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
        error: '<svg class="toast-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
        warning: '<svg class="toast-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"/></svg>',
        info: '<svg class="toast-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
      };

      const toast = document.createElement('div');
      toast.className = `toast toast-${type}`;
      toast.setAttribute('role', 'alert');
      toast.innerHTML = `
        ${icons[type] || icons.info}
        <div class="toast-body">
          <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close" aria-label="Fechar">&times;</button>
        <div class="toast-progress" style="animation-duration:${duration}ms"></div>
      `;

      toast.querySelector('.toast-close').addEventListener('click', () => this.dismiss(toast));

      this.container.appendChild(toast);

      const timer = setTimeout(() => this.dismiss(toast), duration);
      toast._timer = timer;
    },

    dismiss(toast) {
      clearTimeout(toast._timer);
      toast.classList.add('removing');
      toast.addEventListener('animationend', () => toast.remove());
    },

    success(msg, dur) { this.show(msg, 'success', dur); },
    error(msg, dur) { this.show(msg, 'error', dur); },
    warning(msg, dur) { this.show(msg, 'warning', dur); },
    info(msg, dur) { this.show(msg, 'info', dur); },
  };

  window.Toast = Toast;

  // ============================================================
  // DJANGO MESSAGES → TOASTS
  // ============================================================
  function convertDjangoMessages() {
    document.querySelectorAll('[data-django-message]').forEach(el => {
      const type = el.dataset.djangoMessage || 'info';
      const msg = el.textContent.trim();
      if (msg) Toast.show(msg, type === 'error' ? 'error' : type);
      el.remove();
    });
  }

  // ============================================================
  // LOADING BUTTON STATES
  // ============================================================
  function initLoadingButtons() {
    document.querySelectorAll('form').forEach(form => {
      form.addEventListener('submit', function() {
        const btn = form.querySelector('[type="submit"]');
        if (btn && !btn.classList.contains('loading')) {
          btn.classList.add('loading');
          btn.disabled = true;
          const originalText = btn.innerHTML;
          btn.innerHTML = '<span class="spinner"></span> <span>' + (btn.dataset.loadingText || 'Aguarde...') + '</span>';
          // Restore after 10s failsafe
          setTimeout(() => {
            btn.classList.remove('loading');
            btn.disabled = false;
            btn.innerHTML = originalText;
          }, 10000);
        }
      });
    });
  }

  // ============================================================
  // MOBILE SIDEBAR
  // ============================================================
  function initSidebar() {
    const toggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('mobile-sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    const close = document.getElementById('close-sidebar');
    const panel = sidebar?.querySelector('.sidebar-panel');

    function openSidebar() {
      if (!sidebar) return;
      sidebar.classList.remove('hidden');
      requestAnimationFrame(() => {
        overlay?.classList.add('opacity-100');
        panel?.classList.add('open');
      });
      document.body.style.overflow = 'hidden';
    }
    function closeSidebar() {
      if (!sidebar) return;
      overlay?.classList.remove('opacity-100');
      panel?.classList.remove('open');
      setTimeout(() => {
        sidebar.classList.add('hidden');
        document.body.style.overflow = '';
      }, 300);
    }

    toggle?.addEventListener('click', openSidebar);
    close?.addEventListener('click', closeSidebar);
    overlay?.addEventListener('click', closeSidebar);
  }

  // ============================================================
  // FILE INPUT ENHANCEMENT
  // ============================================================
  function initFileInputs() {
    document.querySelectorAll('.form-file').forEach(wrapper => {
      const input = wrapper.querySelector('input[type="file"]');
      const nameEl = wrapper.querySelector('.form-file-name');

      if (!input) return;

      input.addEventListener('change', () => {
        if (input.files.length > 0) {
          wrapper.classList.add('has-file');
          if (nameEl) nameEl.textContent = input.files[0].name;
        } else {
          wrapper.classList.remove('has-file');
          if (nameEl) nameEl.textContent = '';
        }
      });

      // Drag and drop
      ['dragover', 'dragenter'].forEach(evt => {
        wrapper.addEventListener(evt, e => { e.preventDefault(); wrapper.classList.add('dragover'); });
      });
      ['dragleave', 'drop'].forEach(evt => {
        wrapper.addEventListener(evt, () => wrapper.classList.remove('dragover'));
      });
    });
  }

  // ============================================================
  // CONFIRM DELETE (styled)
  // ============================================================
  function initConfirmActions() {
    document.querySelectorAll('[data-confirm]').forEach(el => {
      el.addEventListener('click', function(e) {
        const msg = this.dataset.confirm || 'Tem certeza?';
        if (!confirm(msg)) {
          e.preventDefault();
          e.stopImmediatePropagation();
        }
      });
    });
  }

  // ============================================================
  // AUTO-DISMISS ALERTS (legacy, for pages that still use them)
  // ============================================================
  function initAlertDismiss() {
    document.querySelectorAll('.alert-dismiss').forEach(alert => {
      setTimeout(() => {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-10px)';
        setTimeout(() => alert.remove(), 300);
      }, 5000);
    });
  }

  // ============================================================
  // CHECKBOX SELECT ALL
  // ============================================================
  function initSelectAll() {
    document.querySelectorAll('[data-select-all]').forEach(toggle => {
      const target = toggle.dataset.selectAll;
      const checkboxes = document.querySelectorAll(`input[name="${target}"]`);
      toggle.addEventListener('change', () => {
        checkboxes.forEach(cb => { cb.checked = toggle.checked; });
      });
    });
  }

  // ============================================================
  // SMOOTH SCROLL FOR ANCHORS
  // ============================================================
  function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(a => {
      a.addEventListener('click', e => {
        const target = document.querySelector(a.getAttribute('href'));
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });
  }

  // ============================================================
  // INITIALIZE
  // ============================================================
  document.addEventListener('DOMContentLoaded', () => {
    Toast.init();
    convertDjangoMessages();
    initLoadingButtons();
    initSidebar();
    initFileInputs();
    initConfirmActions();
    initAlertDismiss();
    initSelectAll();
    initSmoothScroll();
  });

})();
