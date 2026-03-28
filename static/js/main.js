/* =============================================
   MaxCze Services — Hoofd JavaScript
   ============================================= */

document.addEventListener('DOMContentLoaded', () => {
  const THEME_STORAGE_KEY = 'maxcze_theme_preference_v1';
  const themeToggles = Array.from(document.querySelectorAll('.theme-toggle'));
  const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)');

  const setTheme = (theme, persist = true) => {
    const resolvedTheme = theme === 'dark' ? 'dark' : 'light';
    document.documentElement.dataset.theme = resolvedTheme;
    document.body.classList.toggle('theme-dark', resolvedTheme === 'dark');
    themeToggles.forEach((toggle) => {
      toggle.checked = resolvedTheme === 'dark';
      toggle.setAttribute('aria-checked', resolvedTheme === 'dark' ? 'true' : 'false');
    });

    if (!persist) {
      return;
    }

    try {
      localStorage.setItem(THEME_STORAGE_KEY, resolvedTheme);
    } catch {
      // Ignore storage failures and continue with in-memory theme state.
    }
  };

  const getStoredTheme = () => {
    try {
      const storedTheme = localStorage.getItem(THEME_STORAGE_KEY);
      return storedTheme === 'dark' || storedTheme === 'light' ? storedTheme : '';
    } catch {
      return '';
    }
  };

  const applyInitialTheme = () => {
    const storedTheme = getStoredTheme();
    if (storedTheme) {
      setTheme(storedTheme, false);
      return;
    }

    setTheme(systemPrefersDark.matches ? 'dark' : 'light', false);
  };

  applyInitialTheme();

  themeToggles.forEach((toggle) => {
    toggle.addEventListener('change', () => {
      setTheme(toggle.checked ? 'dark' : 'light');
    });
  });

  const handleSystemThemeChange = (event) => {
    if (getStoredTheme()) {
      return;
    }
    setTheme(event.matches ? 'dark' : 'light', false);
  };

  if (typeof systemPrefersDark.addEventListener === 'function') {
    systemPrefersDark.addEventListener('change', handleSystemThemeChange);
  } else if (typeof systemPrefersDark.addListener === 'function') {
    systemPrefersDark.addListener(handleSystemThemeChange);
  }

  /* ─── Cookie consent ─── */
  const COOKIE_CONSENT_KEY = 'maxcze_cookie_consent_v2';
  const COOKIE_BANNER_SESSION_KEY = 'maxcze_cookie_banner_seen_session_v1';
  const COOKIE_CONSENT_SCHEMA_VERSION = 2;
  const COOKIE_CONSENT_TTL_MS = 24 * 60 * 60 * 1000; // 1 day
  const cookieBanner = document.getElementById('cookie-banner');
  const acceptAllBtn = document.getElementById('cookie-accept-all');
  const acceptNecessaryBtn = document.getElementById('cookie-accept-necessary');
  const cookieSettingsBtn = document.getElementById('cookie-settings-btn');

  const writeConsent = (preference) => {
    const now = Date.now();
    const consent = {
      version: COOKIE_CONSENT_SCHEMA_VERSION,
      necessary: true,
      analytics: preference === 'all',
      marketing: preference === 'all',
      preference,
      updatedAt: new Date().toISOString(),
      expiresAt: new Date(now + COOKIE_CONSENT_TTL_MS).toISOString(),
    };

    try {
      localStorage.setItem(COOKIE_CONSENT_KEY, JSON.stringify(consent));
    } catch {
      // If storage is unavailable, we still hide the banner for this page view.
    }
  };

  const showCookieBanner = () => {
    if (cookieBanner) {
      cookieBanner.classList.add('zichtbaar');
    }
  };

  const hideCookieBanner = () => {
    if (cookieBanner) {
      cookieBanner.classList.remove('zichtbaar');
    }
  };

  const hasSeenBannerThisSession = () => {
    try {
      return sessionStorage.getItem(COOKIE_BANNER_SESSION_KEY) === '1';
    } catch {
      return false;
    }
  };

  const markBannerSeenThisSession = () => {
    try {
      sessionStorage.setItem(COOKIE_BANNER_SESSION_KEY, '1');
    } catch {
      // Ignore storage failures and continue gracefully.
    }
  };

  if (cookieBanner) {
    const shouldShowOnThisVisit = !hasSeenBannerThisSession();
    if (shouldShowOnThisVisit) {
      showCookieBanner();
      markBannerSeenThisSession();
    }

    acceptAllBtn?.addEventListener('click', () => {
      writeConsent('all');
      hideCookieBanner();
    });

    acceptNecessaryBtn?.addEventListener('click', () => {
      writeConsent('necessary');
      hideCookieBanner();
    });

    cookieSettingsBtn?.addEventListener('click', () => {
      showCookieBanner();
    });
  }

  /* ─── Navigatie: scroll effect ─── */
  const nav = document.querySelector('.nav');
  if (nav) {
    const onScroll = () => {
      nav.classList.toggle('gescrold', window.scrollY > 60);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ─── Hamburger menu ─── */
  const hamburger   = document.querySelector('.hamburger');
  const mobielMenu  = document.querySelector('.mobiel-menu');
  const mobielDiensten = document.querySelector('.mobiel-diensten');
  if (hamburger && mobielMenu) {
    hamburger.addEventListener('click', () => {
      const open = hamburger.classList.toggle('open');
      mobielMenu.classList.toggle('open', open);
      hamburger.setAttribute('aria-expanded', open ? 'true' : 'false');
      document.body.style.overflow = open ? 'hidden' : '';
      if (!open && mobielDiensten) {
        mobielDiensten.open = false;
      }
    });
    mobielMenu.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => {
        hamburger.classList.remove('open');
        mobielMenu.classList.remove('open');
        hamburger.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
        if (mobielDiensten) {
          mobielDiensten.open = false;
        }
      });
    });
  }

  /* ─── Desktop hover fallback voor diensten dropdown ─── */
  const navDiensten = document.querySelector('.nav-diensten');
  const navDienstenWrapper = document.querySelector('.nav-diensten-wrapper');
  const desktopHoverQuery = window.matchMedia('(hover: hover) and (pointer: fine)');

  if (navDiensten && desktopHoverQuery) {
    const openDiensten = () => {
      navDiensten.open = true;
    };

    const closeDiensten = () => {
      navDiensten.open = false;
    };

    let hoverListenersAttached = false;

    const attachHoverListeners = () => {
      if (hoverListenersAttached) {
        return;
      }
      const hoverTarget = navDienstenWrapper || navDiensten;
      hoverTarget.addEventListener('mouseenter', openDiensten);
      hoverTarget.addEventListener('mouseleave', closeDiensten);
      hoverListenersAttached = true;
    };

    const detachHoverListeners = () => {
      if (!hoverListenersAttached) {
        return;
      }
      const hoverTarget = navDienstenWrapper || navDiensten;
      hoverTarget.removeEventListener('mouseenter', openDiensten);
      hoverTarget.removeEventListener('mouseleave', closeDiensten);
      hoverListenersAttached = false;
      closeDiensten();
    };

    const syncDienstenHoverMode = (event) => {
      if (event.matches) {
        attachHoverListeners();
      } else {
        detachHoverListeners();
      }
    };

    syncDienstenHoverMode(desktopHoverQuery);
    if (typeof desktopHoverQuery.addEventListener === 'function') {
      desktopHoverQuery.addEventListener('change', syncDienstenHoverMode);
    } else if (typeof desktopHoverQuery.addListener === 'function') {
      desktopHoverQuery.addListener(syncDienstenHoverMode);
    }
  }

  /* ─── Hero achtergrond zoom ─── */
  const heroBg = document.querySelector('.hero-bg');
  if (heroBg) {
    let ticking = false;
    window.addEventListener('scroll', () => {
      if (ticking) {
        return;
      }
      ticking = true;
      window.requestAnimationFrame(() => {
        const scroll = window.scrollY;
        heroBg.style.transform = `scale(${1.05 + scroll * 0.00008})`;
        ticking = false;
      });
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
        const image = item.querySelector('.portfolio-foto');
        const src = image?.src;
        if (src) {
          lightboxImg.src = src;
          lightboxImg.alt = image?.alt || 'Project afbeelding';
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
  const foutmelding = document.getElementById('formulier-foutmelding');

  if (formulier) {
    formulier.addEventListener('submit', (e) => {
      const velden = formulier.querySelectorAll('input[required], textarea[required], select[required]');
      let geldig = true;
      let eersteOngeldigeVeld = null;

      if (foutmelding) {
        foutmelding.classList.remove('zichtbaar');
      }

      velden.forEach(veld => {
        // reset previous error styling
        veld.style.borderColor = '';
        if (veld.type === 'checkbox') {
          const lbl = formulier.querySelector(`label[for="${veld.id}"]`);
          if (lbl) lbl.style.color = '';
        }

        // checkboxes need to be validated via checked state
        if (veld.type === 'checkbox') {
          if (!veld.checked) {
            // highlight label instead of border
            const label = formulier.querySelector(`label[for="${veld.id}"]`);
            if (label) label.style.color = '#e53e3e';
            if (!eersteOngeldigeVeld) eersteOngeldigeVeld = veld;
            geldig = false;
          }
        } else {
          if (!veld.value.trim()) {
            veld.style.borderColor = '#e53e3e';
            if (!eersteOngeldigeVeld) eersteOngeldigeVeld = veld;
            geldig = false;
          }
        }
      });

      if (!geldig) {
        e.preventDefault();
        if (foutmelding) {
          foutmelding.classList.add('zichtbaar');
        }
        if (eersteOngeldigeVeld && typeof eersteOngeldigeVeld.focus === 'function') {
          eersteOngeldigeVeld.focus();
        }
        return;
      }

      // Real submit to Flask endpoint after client-side validation.
      const submitBtn = formulier.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.setAttribute('aria-busy', 'true');
      }
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
