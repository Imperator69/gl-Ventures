/* Progressive enhancement: all content and navigation work without JavaScript. */
document.documentElement.classList.add('js');

const header = document.getElementById('header');
const menuButton = header.querySelector('.menu-toggle');
const nav = document.getElementById('main-nav');

function setMenu(open) {
  menuButton.setAttribute('aria-expanded', String(open));
  menuButton.setAttribute('aria-label', open ? menuButton.dataset.closeLabel : menuButton.dataset.openLabel);
  header.classList.toggle('menu-open', open);
}
menuButton.addEventListener('click', () => setMenu(menuButton.getAttribute('aria-expanded') !== 'true'));
nav.addEventListener('click', event => { if (event.target.closest('a')) setMenu(false); });
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && header.classList.contains('menu-open')) { setMenu(false); menuButton.focus(); }
});
document.addEventListener('click', event => {
  if (header.classList.contains('menu-open') && !header.contains(event.target)) setMenu(false);
});
window.matchMedia('(min-width: 64.0625rem)').addEventListener('change', event => { if (event.matches) setMenu(false); });

/* Solid header once the page is scrolled; mobile quick contact after the hero,
   hidden while the contact section itself is on screen. */
const quick = document.querySelector('.quick-contact');
const contact = document.getElementById('contact');
let ticking = false;
function onScroll() {
  header.classList.toggle('scrolled', window.scrollY > 24);
  if (quick) {
    const pastHero = window.scrollY > window.innerHeight * 0.6;
    const atContact = contact && contact.getBoundingClientRect().top < window.innerHeight * 0.85;
    quick.classList.toggle('show', pastHero && !atContact);
  }
  ticking = false;
}
window.addEventListener('scroll', () => {
  if (!ticking) { ticking = true; requestAnimationFrame(onScroll); }
}, { passive: true });
onScroll();

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

/* Reveal sections on scroll and highlight the current section in the nav. */
if ('IntersectionObserver' in window) {
  const reveal = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) { entry.target.classList.add('in'); reveal.unobserve(entry.target); }
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
  document.querySelectorAll('.reveal').forEach(el => reveal.observe(el));

  const links = new Map();
  nav.querySelectorAll('a[href^="#"]').forEach(a => {
    const section = document.querySelector(a.getAttribute('href'));
    if (section) links.set(section, a);
  });
  if (links.size) {
    const spy = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          links.forEach(a => a.classList.remove('active'));
          links.get(entry.target).classList.add('active');
        }
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    links.forEach((_, section) => spy.observe(section));
  }
} else {
  document.querySelectorAll('.reveal').forEach(el => el.classList.add('in'));
}
