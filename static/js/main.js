// NarrativeForge — Main JS

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

  // ── Chip radio highlight ─────────────────────────
  document.querySelectorAll('.chip input[type="radio"]').forEach(input => {
    input.addEventListener('change', () => {
      const group = input.closest('.chip-group');
      if (group) {
        group.querySelectorAll('.chip').forEach(c => c.classList.remove('selected'));
      }
    });
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
        ? 'rgba(7,6,15,0.95)'
        : 'rgba(7,6,15,0.85)';
    }, { passive: true });
  }

  // ── Section nav fade ─────────────────────────────
  document.querySelectorAll('.specs-section:not(.hidden)').forEach(el => {
    el.style.animation = 'fadeInUp 0.35s ease';
  });

});

// Global helpers (used by inline event handlers)
function nextSection(from) {
  const cur = document.getElementById(`section-${from}`);
  const next = document.getElementById(`section-${from + 1}`);
  if (!next) return;
  cur.classList.add('hidden');
  next.classList.remove('hidden');
  next.style.animation = 'fadeInUp 0.35s ease';
  window.scrollTo({ top: 0, behavior: 'smooth' });
  updateProgress(from + 1);
}

function prevSection(from) {
  const cur = document.getElementById(`section-${from}`);
  const prev = document.getElementById(`section-${from - 1}`);
  if (!prev) return;
  cur.classList.add('hidden');
  prev.classList.remove('hidden');
  prev.style.animation = 'fadeInUp 0.35s ease';
  window.scrollTo({ top: 0, behavior: 'smooth' });
  updateProgress(from - 1);
}

function updateProgress(currentSection) {
  document.querySelectorAll('.progress-step').forEach((step, i) => {
    step.classList.toggle('active', i + 1 === currentSection);
    step.classList.toggle('done', i + 1 < currentSection);
  });
}
