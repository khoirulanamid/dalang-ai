/**
 * Kalkulator Dingin — Logic & UI Controller
 * Mengendalikan operasi aritmatika, presisi desimal, riwayat, dan keyboard shortcuts.
 */

(function () {
  'use strict';

  // State
  let currentInput = '0';
  let previousInput = null;
  let activeOperator = null;
  let shouldResetInput = false;
  let calculationHistory = [];
  let isErrorState = false;

  // DOM Elements
  const displayEl = document.getElementById('calc-display');
  const exprEl = document.getElementById('calc-expression');
  const historyDrawer = document.getElementById('history-drawer');
  const historyList = document.getElementById('history-list');
  const historyBadge = document.getElementById('history-badge');
  const btnToggleHistory = document.getElementById('btn-toggle-history');
  const btnClearHistory = document.getElementById('btn-clear-history');
  const keypad = document.querySelector('.keypad-grid');

  // Math Precision Helper
  function preciseCalculate(a, op, b) {
    const numA = parseFloat(a);
    const numB = parseFloat(b);

    if (isNaN(numA) || isNaN(numB)) return 'Error';

    let result = 0;
    switch (op) {
      case '+':
        result = numA + numB;
        break;
      case '−':
      case '-':
        result = numA - numB;
        break;
      case '×':
      case '*':
        result = numA * numB;
        break;
      case '÷':
      case '/':
        if (numB === 0) {
          return 'Pembagian Nol';
        }
        result = numA / numB;
        break;
      default:
        return 'Error';
    }

    // Fix floating point artifact: 0.1 + 0.2 = 0.30000000000000004
    const factor = 1e12;
    const rounded = Math.round(result * factor) / factor;
    return String(rounded);
  }

  function updateDisplay() {
    if (isErrorState) {
      displayEl.textContent = currentInput;
      displayEl.style.fontSize = '1.4rem';
      displayEl.style.color = '#f87171'; // Red accent
      return;
    }

    displayEl.style.color = 'var(--display-text)';

    // Format number with thousands separators for integer part
    let formatted = currentInput;
    if (!currentInput.includes('e') && !currentInput.includes('E')) {
      const parts = currentInput.split('.');
      parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
      formatted = parts.join('.');
    }

    // Dynamic font scaling
    if (formatted.length > 14) {
      displayEl.style.fontSize = '1.3rem';
    } else if (formatted.length > 10) {
      displayEl.style.fontSize = '1.7rem';
    } else {
      displayEl.style.fontSize = '2.3rem';
    }

    displayEl.textContent = formatted;

    // Expression line
    if (previousInput !== null && activeOperator !== null) {
      exprEl.textContent = `${previousInput} ${activeOperator}`;
    } else {
      exprEl.textContent = '';
    }

    // Highlight active operator key
    document.querySelectorAll('.key-op').forEach((btn) => {
      if (btn.dataset.op === activeOperator && shouldResetInput) {
        btn.classList.add('active-op');
      } else {
        btn.classList.remove('active-op');
      }
    });
  }

  function inputDigit(digit) {
    if (isErrorState) {
      clearAll();
    }

    if (shouldResetInput) {
      currentInput = digit;
      shouldResetInput = false;
    } else {
      if (currentInput === '0') {
        currentInput = digit;
      } else {
        if (currentInput.length < 18) {
          currentInput += digit;
        }
      }
    }
    updateDisplay();
  }

  function inputDecimal() {
    if (isErrorState) {
      clearAll();
    }

    if (shouldResetInput) {
      currentInput = '0.';
      shouldResetInput = false;
      updateDisplay();
      return;
    }

    if (!currentInput.includes('.')) {
      currentInput += '.';
      updateDisplay();
    }
  }

  function handleOperator(nextOp) {
    if (isErrorState) return;

    if (previousInput === null) {
      previousInput = currentInput;
    } else if (!shouldResetInput) {
      // Chained operation: perform pending calculation first
      const result = preciseCalculate(previousInput, activeOperator, currentInput);
      if (result === 'Pembagian Nol' || result === 'Error') {
        currentInput = result;
        isErrorState = true;
        updateDisplay();
        return;
      }
      currentInput = result;
      previousInput = result;
    }

    activeOperator = nextOp;
    shouldResetInput = true;
    updateDisplay();
  }

  function executeEquals() {
    if (isErrorState || previousInput === null || activeOperator === null) {
      return;
    }

    const exprText = `${previousInput} ${activeOperator} ${currentInput}`;
    const result = preciseCalculate(previousInput, activeOperator, currentInput);

    if (result === 'Pembagian Nol' || result === 'Error') {
      currentInput = result;
      isErrorState = true;
      updateDisplay();
      return;
    }

    // Add to history
    addHistoryItem(exprText, result);

    currentInput = result;
    previousInput = null;
    activeOperator = null;
    shouldResetInput = true;
    updateDisplay();
  }

  function negateNumber() {
    if (isErrorState || currentInput === '0') return;
    if (currentInput.startsWith('-')) {
      currentInput = currentInput.slice(1);
    } else {
      currentInput = '-' + currentInput;
    }
    updateDisplay();
  }

  function calculatePercent() {
    if (isErrorState) return;
    const num = parseFloat(currentInput);
    if (!isNaN(num)) {
      const res = num / 100;
      currentInput = String(Math.round(res * 1e12) / 1e12);
      updateDisplay();
    }
  }

  function backspace() {
    if (isErrorState || shouldResetInput) {
      clearAll();
      return;
    }

    if (currentInput.length > 1) {
      currentInput = currentInput.slice(0, -1);
    } else {
      currentInput = '0';
    }
    updateDisplay();
  }

  function clearAll() {
    currentInput = '0';
    previousInput = null;
    activeOperator = null;
    shouldResetInput = false;
    isErrorState = false;
    updateDisplay();
  }

  // History Management
  function addHistoryItem(expression, result) {
    calculationHistory.unshift({ expression, result });
    if (calculationHistory.length > 50) {
      calculationHistory.pop();
    }
    renderHistory();
  }

  function renderHistory() {
    if (calculationHistory.length === 0) {
      historyList.innerHTML = '<div class="history-empty">Belum ada riwayat perhitungan.</div>';
      historyBadge.classList.add('hidden');
      return;
    }

    historyBadge.textContent = calculationHistory.length;
    historyBadge.classList.remove('hidden');

    historyList.innerHTML = '';
    calculationHistory.forEach((item, idx) => {
      const card = document.createElement('div');
      card.className = 'history-item';
      card.setAttribute('role', 'button');
      card.setAttribute('tabindex', '0');
      card.setAttribute('aria-label', `${item.expression} sama dengan ${item.result}`);
      card.innerHTML = `
        <span class="hist-expr">${item.expression} =</span>
        <span class="hist-res">${item.result}</span>
      `;
      // Click to load result
      card.addEventListener('click', () => {
        currentInput = item.result;
        previousInput = null;
        activeOperator = null;
        shouldResetInput = true;
        isErrorState = false;
        updateDisplay();
        toggleHistory(false);
      });
      historyList.appendChild(card);
    });
  }

  function toggleHistory(force) {
    const isOpen = typeof force === 'boolean' ? force : !historyDrawer.classList.contains('open');
    if (isOpen) {
      historyDrawer.classList.add('open');
      btnToggleHistory.setAttribute('aria-expanded', 'true');
    } else {
      historyDrawer.classList.remove('open');
      btnToggleHistory.setAttribute('aria-expanded', 'false');
    }
  }

  // Event Listeners
  keypad.addEventListener('click', (e) => {
    const btn = e.target.closest('.key');
    if (!btn) return;

    const action = btn.dataset.action;
    switch (action) {
      case 'number':
        inputDigit(btn.dataset.val);
        break;
      case 'decimal':
        inputDecimal();
        break;
      case 'operator':
        handleOperator(btn.dataset.op);
        break;
      case 'calculate':
        executeEquals();
        break;
      case 'clear':
        clearAll();
        break;
      case 'backspace':
        backspace();
        break;
      case 'negate':
        negateNumber();
        break;
      case 'percent':
        calculatePercent();
        break;
    }
  });

  btnToggleHistory.addEventListener('click', () => toggleHistory());
  btnClearHistory.addEventListener('click', () => {
    calculationHistory = [];
    renderHistory();
  });

  // Keyboard Shortcuts (Accessibility WCAG 2.1 AA)
  window.addEventListener('keydown', (e) => {
    // If active in an input outside, ignore
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

    const key = e.key;

    if (key >= '0' && key <= '9') {
      e.preventDefault();
      inputDigit(key);
      highlightButton(`key-${key}`);
    } else if (key === '.' || key === ',') {
      e.preventDefault();
      inputDecimal();
      highlightButton('key-decimal');
    } else if (key === '+') {
      e.preventDefault();
      handleOperator('+');
      highlightButton('key-add');
    } else if (key === '-') {
      e.preventDefault();
      handleOperator('−');
      highlightButton('key-subtract');
    } else if (key === '*' || key === 'x' || key === 'X') {
      e.preventDefault();
      handleOperator('×');
      highlightButton('key-multiply');
    } else if (key === '/') {
      e.preventDefault();
      handleOperator('÷');
      highlightButton('key-divide');
    } else if (key === 'Enter' || key === '=') {
      e.preventDefault();
      executeEquals();
      highlightButton('key-equals');
    } else if (key === 'Backspace') {
      e.preventDefault();
      backspace();
      highlightButton('key-backspace');
    } else if (key === 'Escape') {
      e.preventDefault();
      if (historyDrawer.classList.contains('open')) {
        toggleHistory(false);
      } else {
        clearAll();
        highlightButton('key-clear');
      }
    } else if (key === '%') {
      e.preventDefault();
      calculatePercent();
      highlightButton('key-percent');
    } else if (key === 'h' || key === 'H') {
      e.preventDefault();
      toggleHistory();
    }
  });

  function highlightButton(id) {
    const btn = document.getElementById(id);
    if (btn) {
      btn.classList.add('active-press');
      setTimeout(() => btn.classList.remove('active-press'), 120);
    }
  }

  // Initial State
  updateDisplay();
})();
