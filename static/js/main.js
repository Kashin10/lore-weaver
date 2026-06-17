// NarrativeForge — Main JS (Enhanced UX)

document.addEventListener('DOMContentLoaded', () => {

  // ── Stagger animation for cards ──────────────────
  const cards = document.querySelectorAll('.project-card, .character-card, .step-card');
  cards.forEach((card, i) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = `opacity 0.4s ease ${i * 0.07}s, transform 0.4s ease ${i * 0.07}s`;
    setTimeout(() => {
      card.style.opacity = '1';
      card.style.transform = 'translateY(0)';
    }, 50 + i * 70);
  });

  // ── Auto-resize textareas ─────────────────────────
  document.querySelectorAll('.form-textarea').forEach(textarea => {
    textarea.addEventListener('input', () => {
      textarea.style.height = 'auto';
      textarea.style.height = Math.max(80, textarea.scrollHeight) + 'px';
    });
  });

  // ── Navbar scroll effect ─────────────────────────
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      navbar.style.background = window.scrollY > 20
        ? 'rgba(7,6,15,0.97)'
        : 'rgba(7,6,15,0.85)';
    }, { passive: true });
  }

  // ── Mobile hamburger ─────────────────────────────
  const hamburger = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobileMenu');
  if (hamburger && mobileMenu) {
    hamburger.addEventListener('click', () => {
      const open = mobileMenu.classList.toggle('open');
      hamburger.setAttribute('aria-expanded', open);
      hamburger.innerHTML = open ? '✕' : '☰';
    });
    document.addEventListener('click', (e) => {
      if (!navbar.contains(e.target)) {
        mobileMenu.classList.remove('open');
        hamburger.innerHTML = '☰';
      }
    });
  }

  // ── Character counter on textareas ───────────────
  document.querySelectorAll('[data-maxchars]').forEach(el => {
    const max = parseInt(el.dataset.maxchars);
    const counter = document.createElement('span');
    counter.className = 'char-counter';
    counter.textContent = `0 / ${max}`;
    el.parentNode.appendChild(counter);
    el.addEventListener('input', () => {
      const len = el.value.length;
      counter.textContent = `${len} / ${max}`;
      counter.classList.toggle('char-counter-warn', len > max * 0.8);
      counter.classList.toggle('char-counter-over', len > max);
    });
  });

  // ── Custom delete modal ───────────────────────────
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', (e) => {
      e.preventDefault();
      const message = el.dataset.confirm;
      const detail = el.dataset.confirmDetail || '';
      showConfirmModal(message, detail, () => {
        if (el.tagName === 'BUTTON' && el.form) {
          el.removeAttribute('data-confirm');
          el.form.submit();
        } else if (el.tagName === 'A') {
          window.location = el.href;
        }
      });
    });
  });

  // ── Loading overlay on all generate forms ────────
  document.querySelectorAll('[data-loading]').forEach(form => {
    form.addEventListener('submit', () => {
      const message = form.dataset.loading || 'Processing...';
      showLoadingOverlay(message);
    });
  });

  // ── Soft validation hints ─────────────────────────
  window.softValidate = function(sectionNum) {
    const hints = {
      1: [{ name: 'setting', hint: 'Adding a setting description greatly enriches your narrative.' }],
      2: [{ name: 'tone', hint: 'Selecting a Tone has the biggest impact on AI output quality.' },
          { name: 'plot_type', hint: 'A Plot Type helps structure your story meaningfully.' }]
    };
    const checks = hints[sectionNum] || [];
    let shown = false;
    checks.forEach(({ name, hint }) => {
      const el = document.querySelector(`[name="${name}"]`);
      if (el && (!el.value || el.value === '')) {
        if (!shown) {
          showInlineHint(el, hint);
          shown = true;
        }
      }
    });
  };

  // ── Auto-dismiss flash messages ───────────────────
  document.querySelectorAll('.flash').forEach(flash => {
    setTimeout(() => {
      flash.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
      flash.style.opacity = '0';
      flash.style.transform = 'translateY(-10px)';
      setTimeout(() => flash.remove(), 500);
    }, 5000);

    const closeBtn = flash.querySelector('.flash-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => flash.remove());
    }
  });

});

// ── Loading Overlay ───────────────────────────────
function showLoadingOverlay(message) {
  const overlay = document.getElementById('loadingOverlay');
  if (!overlay) return;
  const lines = [
    message,
    'Consulting the ancient archives...',
    'Weaving the threads of fate...',
    'Summoning forgotten lore...',
    'Forging your world...'
  ];
  const textEl = overlay.querySelector('.loading-text');
  let i = 0;
  overlay.classList.remove('hidden');
  if (textEl) {
    textEl.textContent = lines[0];
    setInterval(() => {
      i = (i + 1) % lines.length;
      textEl.style.opacity = '0';
      setTimeout(() => {
        textEl.textContent = lines[i];
        textEl.style.opacity = '1';
      }, 300);
    }, 2500);
  }
}

// ── Confirm Modal ─────────────────────────────────
function showConfirmModal(title, detail, onConfirm) {
  const modal = document.getElementById('confirmModal');
  if (!modal) { if (confirm(title)) onConfirm(); return; }
  modal.querySelector('.modal-title').textContent = title;
  modal.querySelector('.modal-detail').textContent = detail;
  modal.classList.remove('hidden');

  const confirmBtn = modal.querySelector('.modal-confirm');
  const cancelBtn  = modal.querySelector('.modal-cancel');

  const cleanup = () => modal.classList.add('hidden');
  confirmBtn.onclick = () => { cleanup(); onConfirm(); };
  cancelBtn.onclick  = cleanup;
  modal.querySelector('.modal-backdrop').onclick = cleanup;
}

// ── Inline hint ───────────────────────────────────
function showInlineHint(el, message) {
  const existing = el.parentNode.querySelector('.inline-hint');
  if (existing) existing.remove();
  const hint = document.createElement('span');
  hint.className = 'inline-hint';
  hint.textContent = '💡 ' + message;
  el.parentNode.appendChild(hint);
  setTimeout(() => hint.remove(), 4000);
}

// ── Section navigation (Narrative Wizard) ─────────
let currentSection = 1;

function nextSection(from) {
  softValidate && softValidate(from);
  const cur  = document.getElementById(`section-${from}`);
  const next = document.getElementById(`section-${from + 1}`);
  if (!next) return;
  if (from === 3) updateStep4Summary();
  cur.classList.add('hidden');
  next.classList.remove('hidden');
  next.style.animation = 'fadeInUp 0.35s ease';
  currentSection = from + 1;
  updateProgress(currentSection);
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function prevSection(from) {
  const cur  = document.getElementById(`section-${from}`);
  const prev = document.getElementById(`section-${from - 1}`);
  if (!prev) return;
  cur.classList.add('hidden');
  prev.classList.remove('hidden');
  prev.style.animation = 'fadeInUp 0.35s ease';
  currentSection = from - 1;
  updateProgress(currentSection);
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function updateProgress(current) {
  document.querySelectorAll('.progress-step').forEach((step, i) => {
    step.classList.toggle('active', i + 1 === current);
    step.classList.toggle('done', i + 1 < current);
  });
}

function updateStep4Summary() {
  const get = name => {
    const el = document.querySelector(`[name="${name}"]`);
    return el ? el.value : '';
  };
  const genre   = get('genre');
  const tone    = get('tone');
  const setting = get('setting');
  const plot    = get('plot_type');
  const proto   = get('protagonist_archetype');
  const parts   = [genre, tone, setting && `set in ${setting}`, plot, proto && `with ${proto} as protagonist`].filter(Boolean);
  const summary = document.getElementById('generateSummary');
  if (summary && parts.length > 0) {
    summary.textContent = `Generating: ${parts.join(' · ')}`;
  }
}

window.quickGenerate = function() {
  const cur  = document.getElementById(`section-${currentSection}`);
  const next = document.getElementById('section-4');
  if (cur && next) {
    cur.classList.add('hidden');
    next.classList.remove('hidden');
    next.style.animation = 'fadeInUp 0.35s ease';
    currentSection = 4;
    updateProgress(currentSection);
    updateStep4Summary();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
};

