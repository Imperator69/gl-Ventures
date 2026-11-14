/* Progressive enhancement: all content and navigation work without JavaScript. */
const root = document.documentElement;
root.classList.add('js');

const header = document.getElementById('header');
const menuButton = header.querySelector('.menu-toggle');
const nav = document.getElementById('main-nav');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

/* Menu (full screen on small screens) */
function setMenu(open) {
  menuButton.setAttribute('aria-expanded', String(open));
  menuButton.setAttribute('aria-label', open ? menuButton.dataset.closeLabel : menuButton.dataset.openLabel);
  header.classList.toggle('menu-open', open);
  root.classList.toggle('menu-locked', open);
}
menuButton.addEventListener('click', () => setMenu(menuButton.getAttribute('aria-expanded') !== 'true'));
nav.addEventListener('click', event => { if (event.target.closest('a')) setMenu(false); });
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && header.classList.contains('menu-open')) { setMenu(false); menuButton.focus(); }
});
window.matchMedia('(min-width: 64.0625rem)').addEventListener('change', event => { if (event.matches) setMenu(false); });

/* Keep the visitor in the same section when switching language. */
function syncLanguageLink() {
  const link = document.querySelector('.lang-link');
  if (!link) return;
  const url = new URL(link.href);
  url.hash = window.location.hash;
  link.href = url.pathname + url.hash;
}
window.addEventListener('hashchange', syncLanguageLink);
syncLanguageLink();

/* Accordion behaviour for browsers without <details name>. */
document.querySelectorAll('.disclosure').forEach(detail => {
  detail.addEventListener('toggle', () => {
    if (!detail.open) return;
    detail.parentElement.querySelectorAll('.disclosure').forEach(other => { if (other !== detail) other.open = false; });
  });
});

/* Services: on large screens the section pins and the three services replace
   each other while scrolling. Elsewhere they stay a normal list of cards. */
const services = document.querySelector('.services-section');
const panels = services ? [...services.querySelectorAll('.service')] : [];
const serviceLinks = services ? [...services.querySelectorAll('.services-nav a')] : [];
const serviceBar = services ? services.querySelector('.services-progress span') : null;
const pinQuery = window.matchMedia('(min-width: 64rem) and (min-height: 41rem) and (prefers-reduced-motion: no-preference)');
let pinned = false;

function panelScrollTop(index) {
  const top = services.getBoundingClientRect().top + window.scrollY;
  const range = services.offsetHeight - window.innerHeight;
  return top + range * ((index + 0.5) / panels.length);
}
function goToPanel(index, smooth = true) {
  window.scrollTo({ top: panelScrollTop(index), behavior: smooth ? 'smooth' : 'instant' });
}
function updateServices() {
  if (!pinned) return;
  const range = services.offsetHeight - window.innerHeight;
  const progress = clamp(-services.getBoundingClientRect().top / range, 0, 1);
  const current = Math.min(panels.length - 1, Math.floor(progress * panels.length));
  panels.forEach((panel, i) => {
    panel.classList.toggle('is-active', i === current);
    panel.classList.toggle('is-past', i < current);
  });
  serviceLinks.forEach((link, i) => {
    link.classList.toggle('is-current', i === current);
    if (i === current) link.setAttribute('aria-current', 'true'); else link.removeAttribute('aria-current');
  });
  if (serviceBar) serviceBar.style.transform = `scaleX(${progress})`;
}
function setPinned(on) {
  pinned = on;
  services.classList.toggle('is-pinned', on);
  if (!on) {
    panels.forEach(panel => panel.classList.remove('is-active', 'is-past'));
    serviceLinks.forEach(link => { link.classList.remove('is-current'); link.removeAttribute('aria-current'); });
  }
  updateServices();
}
if (services && panels.length) {
  setPinned(pinQuery.matches);
  pinQuery.addEventListener('change', event => setPinned(event.matches));
  /* While pinned, links to a single service scroll to its position in the sequence. */
  document.addEventListener('click', event => {
    const link = event.target.closest('a[href*="#"]');
    if (!pinned || !link || link.pathname !== window.location.pathname) return;
    const index = panels.findIndex(panel => '#' + panel.id === link.hash);
    if (index < 0) return;
    event.preventDefault();
    goToPanel(index);
    history.replaceState(null, '', link.hash);
  });
  /* Keyboard focus inside a hidden service brings it on screen. */
  panels.forEach((panel, index) => panel.addEventListener('focusin', () => {
    if (pinned && !panel.classList.contains('is-active')) goToPanel(index, false);
  }));
  const initial = panels.findIndex(panel => '#' + panel.id === window.location.hash);
  if (pinned && initial >= 0) window.addEventListener('load', () => goToPanel(initial, false));
}

/* One scroll handler: header state, progress bar, current nav section, hero depth,
   portrait drift, pinned services and the mobile quick-contact bar. */
const progressBar = header.querySelector('.scroll-progress');
const hero = document.querySelector('.hero, .page-hero');
const drifting = [...document.querySelectorAll('[data-drift]')];
const quick = document.querySelector('.quick-contact');
const spyLinks = [...nav.querySelectorAll('a[href^="#"]')]
  .map(link => ({ link, section: document.querySelector(link.getAttribute('href')) }))
  .filter(item => item.section);
let activeLink = null;
const contact = document.getElementById('contact');
let ticking = false;

function onScroll() {
  ticking = false;
  const y = window.scrollY;
  const viewport = window.innerHeight;
  header.classList.toggle('scrolled', y > 24);
  if (progressBar) {
    const total = document.documentElement.scrollHeight - viewport;
    progressBar.style.transform = `scaleX(${total > 0 ? clamp(y / total, 0, 1) : 0})`;
  }
  if (!reducedMotion.matches) {
    if (hero && y < hero.offsetHeight) hero.style.setProperty('--p', clamp(y / hero.offsetHeight, 0, 1).toFixed(4));
    drifting.forEach(el => {
      const rect = el.getBoundingClientRect();
      if (rect.bottom < 0 || rect.top > viewport) return;
      el.style.setProperty('--py', clamp((rect.top + rect.height / 2 - viewport / 2) / viewport, -1, 1).toFixed(4));
    });
  }
  updateServices();
  /* Highlight the section that crosses the middle of the screen; only touch the DOM when it changes. */
  let current = null;
  for (const item of spyLinks) {
    if (item.section.getBoundingClientRect().top <= viewport * 0.45) current = item.link;
  }
  if (current !== activeLink) {
    if (activeLink) activeLink.classList.remove('active');
    if (current) current.classList.add('active');
    activeLink = current;
  }
  if (quick) {
    const atContact = contact && contact.getBoundingClientRect().top < viewport * 0.85;
    quick.classList.toggle('show', y > viewport * 0.6 && !atContact);
  }
}
function requestTick() {
  if (!ticking) { ticking = true; requestAnimationFrame(onScroll); }
}
window.addEventListener('scroll', requestTick, { passive: true });
window.addEventListener('resize', requestTick);
onScroll();

/* Reveal on scroll; siblings stagger. */
if ('IntersectionObserver' in window) {
  const reveal = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) { entry.target.classList.add('in'); reveal.unobserve(entry.target); }
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
  document.querySelectorAll('.reveal, .steps').forEach(el => {
    if (el.classList.contains('reveal')) {
      const siblings = [...el.parentElement.children].filter(child => child.classList.contains('reveal'));
      el.style.setProperty('--i', Math.min(siblings.indexOf(el), 5));
    }
    reveal.observe(el);
  });
} else {
  document.querySelectorAll('.reveal, .steps').forEach(el => el.classList.add('in'));
}
