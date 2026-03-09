/* =============================================
   MaxCze Service — Hoofd JavaScript
   ============================================= */

document.addEventListener('DOMContentLoaded', () => {

  /* ─── Navigatie: scroll effect ─── */
  const nav = document.querySelector('.nav');
  if (nav) {
    const onScroll = () => {
      nav.classList.toggle('gescrold', window.scrollY > 60);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ─── Navigatie: actief linkje ─── */
  const huidigePagina = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a, .mobiel-menu a').forEach(a => {
    const href = a.getAttribute('href');
    if (href === huidigePagina || (huidigePagina === '' && href === 'index.html')) {
      a.classList.add('actief');
    }
  });

  /* ─── Hamburger menu ─── */
  const hamburger   = document.querySelector('.hamburger');
  const mobielMenu  = document.querySelector('.mobiel-menu');
  if (hamburger && mobielMenu) {
    hamburger.addEventListener('click', () => {
      const open = hamburger.classList.toggle('open');
      mobielMenu.classList.toggle('open', open);
      document.body.style.overflow = open ? 'hidden' : '';
    });
    mobielMenu.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => {
        hamburger.classList.remove('open');
        mobielMenu.classList.remove('open');
        document.body.style.overflow = '';
      });
    });
  }

  /* ─── Hero achtergrond zoom ─── */
  const heroBg = document.querySelector('.hero-bg');
  if (heroBg) {
    window.addEventListener('scroll', () => {
      const scroll = window.scrollY;
      heroBg.style.transform = `scale(${1.05 + scroll * 0.00008})`;
    }, { passive: true });
  }

  /* ─── Scroll fade-in animaties ─── */
  const fadeEls = document.querySelectorAll('.fade-in');
  if (fadeEls.length) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.classList.add('zichtbaar');
          observer.unobserve(e.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

    fadeEls.forEach(el => observer.observe(el));
  }

  /* ─── Portfolio filter ─── */
  const filterBtns = document.querySelectorAll('.filter-btn');
  const portfolioItems = document.querySelectorAll('.portfolio-item');

  if (filterBtns.length && portfolioItems.length) {
    filterBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        filterBtns.forEach(b => b.classList.remove('actief'));
        btn.classList.add('actief');

        const categorie = btn.dataset.filter;
        portfolioItems.forEach(item => {
          const match = categorie === 'alles' || item.dataset.categorie === categorie;
          item.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
          if (match) {
            item.style.opacity = '1';
            item.style.transform = 'scale(1)';
            item.style.display = '';
          } else {
            item.style.opacity = '0';
            item.style.transform = 'scale(0.95)';
            setTimeout(() => {
              if (item.dataset.categorie !== categorie && categorie !== 'alles') {
                item.style.display = 'none';
              }
            }, 300);
          }
        });
      });
    });
  }

  /* ─── Lightbox voor portfolio ─── */
  const lightbox     = document.getElementById('lightbox');
  const lightboxImg  = document.getElementById('lightbox-img');
  const lightboxSluit = document.getElementById('lightbox-sluit');

  if (lightbox && lightboxImg) {
    document.querySelectorAll('.portfolio-item').forEach(item => {
      item.addEventListener('click', () => {
        const src = item.querySelector('.portfolio-foto')?.src;
        if (src) {
          lightboxImg.src = src;
          lightbox.classList.add('open');
          document.body.style.overflow = 'hidden';
        }
      });
    });

    const sluitLightbox = () => {
      lightbox.classList.remove('open');
      document.body.style.overflow = '';
    };

    lightboxSluit?.addEventListener('click', sluitLightbox);
    lightbox.addEventListener('click', (e) => {
      if (e.target === lightbox) sluitLightbox();
    });
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') sluitLightbox();
    });
  }

  /* ─── Contactformulier ─── */
  const formulier = document.getElementById('contact-formulier');
  const succes    = document.getElementById('formulier-succes');

  if (formulier) {
    formulier.addEventListener('submit', (e) => {
      e.preventDefault();
      const velden = formulier.querySelectorAll('input[required], textarea[required], select[required]');
      let geldig = true;

      velden.forEach(veld => {
        veld.style.borderColor = '';
        if (!veld.value.trim()) {
          veld.style.borderColor = '#e53e3e';
          geldig = false;
        }
      });

      if (!geldig) return;

      // Simuleer verzenden
      const submitBtn = formulier.querySelector('button[type="submit"]');
      submitBtn.textContent = 'Verzenden...';
      submitBtn.disabled = true;

      setTimeout(() => {
        formulier.style.display = 'none';
        if (succes) succes.classList.add('zichtbaar');
      }, 1200);
    });
  }

  /* ─── Cijfer tellers (homepage) ─── */
  const tellers = document.querySelectorAll('[data-teller]');
  if (tellers.length) {
    const telObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const el = entry.target;
          const doel = parseInt(el.dataset.teller, 10);
          const suffix = el.dataset.suffix || '';
          const duur = 1800;
          const stap = 20;
          const stappen = duur / stap;
          let huidig = 0;

          const interval = setInterval(() => {
            huidig += doel / stappen;
            if (huidig >= doel) {
              huidig = doel;
              clearInterval(interval);
            }
            el.textContent = Math.floor(huidig) + suffix;
          }, stap);

          telObserver.unobserve(el);
        }
      });
    }, { threshold: 0.5 });

    tellers.forEach(t => telObserver.observe(t));
  }

  /* ─── Smooth scroll voor interne links ─── */
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', (e) => {
      const doel = document.querySelector(link.getAttribute('href'));
      if (doel) {
        e.preventDefault();
        doel.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

});
