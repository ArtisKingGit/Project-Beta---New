/* ═══════════════════════════════════════════════════════
   Custom Select Dropdown — Auto-Enhancement Engine
   Automatically wraps all <select> elements in the DOM
   with a premium custom dropdown UI.
   ═══════════════════════════════════════════════════════ */

(function () {
  'use strict';

  // ── Utility: Build custom dropdown from a native <select> ──
  function enhanceSelect(nativeSelect) {
    // Skip if already enhanced
    if (nativeSelect.classList.contains('cs-hidden')) return;
    // Skip hidden inputs like type="hidden"
    if (nativeSelect.type === 'hidden') return;

    // 1. Hide the native select (keep in DOM for value syncing)
    nativeSelect.classList.add('cs-hidden');

    // 2. Create wrapper
    const wrapper = document.createElement('div');
    wrapper.className = 'custom-select-wrapper';

    // Copy inline flex style from parent if the select had flex styling
    const inlineStyle = nativeSelect.getAttribute('style') || '';
    const flexMatch = inlineStyle.match(/flex\s*:\s*([^;]+)/);
    if (flexMatch) {
      wrapper.style.flex = flexMatch[1].trim();
    }

    // 3. Create trigger button
    const trigger = document.createElement('div');
    trigger.className = 'custom-select-trigger';
    trigger.setAttribute('tabindex', '0');
    trigger.setAttribute('role', 'combobox');
    trigger.setAttribute('aria-expanded', 'false');

    const triggerText = document.createElement('span');
    triggerText.className = 'custom-select-trigger-text';

    const chevron = document.createElement('span');
    chevron.className = 'custom-select-chevron';
    chevron.innerHTML = '<i class="fas fa-chevron-down"></i>';

    trigger.appendChild(triggerText);
    trigger.appendChild(chevron);

    // 4. Create options panel
    const optionsPanel = document.createElement('div');
    optionsPanel.className = 'custom-select-options';
    optionsPanel.setAttribute('role', 'listbox');

    const optionsInner = document.createElement('div');
    optionsInner.className = 'custom-select-options-inner';
    optionsPanel.appendChild(optionsInner);

    // 5. Populate options from native <select>
    function buildOptions() {
      optionsInner.innerHTML = '';
      const options = nativeSelect.querySelectorAll('option');
      options.forEach((opt) => {
        const optionEl = document.createElement('div');
        optionEl.className = 'custom-select-option';
        optionEl.setAttribute('role', 'option');
        optionEl.setAttribute('data-value', opt.value);

        if (opt.disabled) {
          optionEl.classList.add('cs-disabled');
        }

        const label = document.createElement('span');
        label.textContent = opt.textContent;

        const check = document.createElement('span');
        check.className = 'custom-select-check';
        check.innerHTML = '<i class="fas fa-check"></i>';

        optionEl.appendChild(label);
        optionEl.appendChild(check);

        // Mark selected
        if (opt.selected && !opt.disabled) {
          optionEl.classList.add('cs-selected');
        }

        // Click handler
        optionEl.addEventListener('click', function () {
          if (opt.disabled) return;

          // Update native select
          nativeSelect.value = opt.value;

          // Fire change event so existing handlers work
          nativeSelect.dispatchEvent(new Event('change', { bubbles: true }));

          // Update UI
          syncTriggerText();
          markSelected(opt.value);
          closeDropdown();
        });

        optionsInner.appendChild(optionEl);
      });
    }

    // 6. Sync trigger text to reflect current native value
    function syncTriggerText() {
      const selectedOption = nativeSelect.options[nativeSelect.selectedIndex];
      if (selectedOption) {
        if (selectedOption.disabled) {
          // Show placeholder styling
          triggerText.textContent = selectedOption.textContent;
          triggerText.classList.add('cs-placeholder');
        } else {
          triggerText.textContent = selectedOption.textContent;
          triggerText.classList.remove('cs-placeholder');
        }
      } else {
        triggerText.textContent = 'Select...';
        triggerText.classList.add('cs-placeholder');
      }
    }

    // 7. Visually mark the selected option
    function markSelected(value) {
      const opts = optionsInner.querySelectorAll('.custom-select-option');
      opts.forEach((o) => {
        if (o.getAttribute('data-value') === value) {
          o.classList.add('cs-selected');
        } else {
          o.classList.remove('cs-selected');
        }
      });
    }

    // 8. Open / Close logic
    function openDropdown() {
      // Close any other open dropdowns first
      document.querySelectorAll('.custom-select-wrapper.cs-open').forEach((w) => {
        if (w !== wrapper) {
          w.classList.remove('cs-open');
          w.querySelector('.custom-select-trigger')?.setAttribute('aria-expanded', 'false');
        }
      });
      wrapper.classList.add('cs-open');
      trigger.setAttribute('aria-expanded', 'true');
    }

    function closeDropdown() {
      wrapper.classList.remove('cs-open');
      trigger.setAttribute('aria-expanded', 'false');
    }

    function toggleDropdown() {
      if (wrapper.classList.contains('cs-open')) {
        closeDropdown();
      } else {
        openDropdown();
      }
    }

    // Trigger click
    trigger.addEventListener('click', function (e) {
      e.stopPropagation();
      toggleDropdown();
    });

    // Keyboard support
    trigger.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        toggleDropdown();
      }
      if (e.key === 'Escape') {
        closeDropdown();
      }
    });

    // 9. Assemble DOM
    // Insert wrapper right before the native select, then move select inside wrapper
    nativeSelect.parentNode.insertBefore(wrapper, nativeSelect);
    wrapper.appendChild(trigger);
    wrapper.appendChild(optionsPanel);
    wrapper.appendChild(nativeSelect);

    // 10. Initial state
    buildOptions();
    syncTriggerText();

    // 11. Watch for programmatic changes to the native select
    // (e.g., when JS dynamically adds options or changes the value)
    const observer = new MutationObserver(() => {
      buildOptions();
      syncTriggerText();
      markSelected(nativeSelect.value);
    });
    observer.observe(nativeSelect, { childList: true, subtree: true, attributes: true });

    // 12. Intercept programmatic .value = ... assignments
    // MutationObserver doesn't fire when .value is set programmatically,
    // so we override the property descriptor to catch those changes.
    const nativeDescriptor = Object.getOwnPropertyDescriptor(
      HTMLSelectElement.prototype, 'value'
    );
    if (nativeDescriptor && nativeDescriptor.set) {
      Object.defineProperty(nativeSelect, 'value', {
        get() {
          return nativeDescriptor.get.call(this);
        },
        set(val) {
          nativeDescriptor.set.call(this, val);
          syncTriggerText();
          markSelected(val);
        },
        configurable: true
      });
    }

    // 13. Also listen for change events (covers cases where other code dispatches change)
    nativeSelect.addEventListener('change', () => {
      syncTriggerText();
      markSelected(nativeSelect.value);
    });

    // Store reference for external refresh
    wrapper._csRefresh = function () {
      buildOptions();
      syncTriggerText();
      markSelected(nativeSelect.value);
    };
    wrapper._csNativeSelect = nativeSelect;
  }

  // ── Global: Close dropdowns on outside click ──
  document.addEventListener('click', function () {
    document.querySelectorAll('.custom-select-wrapper.cs-open').forEach((w) => {
      w.classList.remove('cs-open');
      w.querySelector('.custom-select-trigger')?.setAttribute('aria-expanded', 'false');
    });
  });

  // ── Global: Close on Escape ──
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      document.querySelectorAll('.custom-select-wrapper.cs-open').forEach((w) => {
        w.classList.remove('cs-open');
        w.querySelector('.custom-select-trigger')?.setAttribute('aria-expanded', 'false');
      });
    }
  });

  // ── Init: Enhance all existing selects ──
  function initCustomSelects() {
    document.querySelectorAll('select:not(.cs-hidden)').forEach(enhanceSelect);
  }

  // ── Auto-enhance new <select> elements added to the DOM ──
  const bodyObserver = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      for (const node of mutation.addedNodes) {
        if (node.nodeType !== 1) continue;
        // Direct select element
        if (node.tagName === 'SELECT' && !node.classList.contains('cs-hidden')) {
          enhanceSelect(node);
        }
        // Selects nested inside added container
        if (node.querySelectorAll) {
          node.querySelectorAll('select:not(.cs-hidden)').forEach(enhanceSelect);
        }
      }
    }
  });

  // ── Public API ──
  window.refreshCustomSelect = function (selectId) {
    const nativeSelect = document.getElementById(selectId);
    if (!nativeSelect) return;
    const wrapper = nativeSelect.closest('.custom-select-wrapper');
    if (wrapper && wrapper._csRefresh) {
      wrapper._csRefresh();
    }
  };

  window.initCustomSelects = initCustomSelects;

  // ── Boot ──
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      initCustomSelects();
      bodyObserver.observe(document.body, { childList: true, subtree: true });
    });
  } else {
    initCustomSelects();
    bodyObserver.observe(document.body, { childList: true, subtree: true });
  }
})();
