/**
 * Spaghetti Western Discovery — High Performance Web App
 * ES6+ Vanilla JavaScript (Zero Dependencies, 100/100 Lighthouse Target)
 */

(() => {
  'use strict';

  // --- State ---
  let allMovies = [];
  let currentMovie = null;
  let activeFilter = 'all';
  let isSpinning = false;
  let soundEnabled = true;
  const recentDraws = [];
  const MAX_RECENTS = 8;

  // --- DOM Elements ---
  const drawBtn = document.getElementById('draw-btn');
  const cardDrawBtn = document.getElementById('card-draw-btn');
  const shareBtn = document.getElementById('share-btn');
  const filterPills = document.querySelectorAll('.filter-pill');
  const tickerText = document.getElementById('ticker-text');
  const filmCard = document.getElementById('film-card');
  const toast = document.getElementById('toast');
  const toastText = document.getElementById('toast-text');
  const soundBtn = document.getElementById('sound-btn');
  const soundIcon = document.getElementById('sound-icon');
  const soundText = document.getElementById('sound-text');
  const recentList = document.getElementById('recent-list');
  const clearHistoryBtn = document.getElementById('clear-history-btn');

  // Film Card Elements
  const filmVaultNumber = document.getElementById('film-vault-number');
  const filmTitle = document.getElementById('film-title');
  const filmYear = document.getElementById('film-year');
  const altTitlesBox = document.getElementById('alt-titles-box');
  const filmAltTitles = document.getElementById('film-alt-titles');
  const filmDirector = document.getElementById('film-director');
  const filmStar = document.getElementById('film-star');
  const filmCostars = document.getElementById('film-costars');
  const filmMusic = document.getElementById('film-music');
  const filmSynopsis = document.getElementById('film-synopsis');
  const flickfinderCardLink = document.getElementById('flickfinder-card-link');

  // Badge Counts
  const vaultCountBadge = document.getElementById('vault-count-badge');
  const countAll = document.getElementById('count-all');
  const countCult = document.getElementById('count-cult');
  const countGolden = document.getElementById('count-golden');
  const countMusic = document.getElementById('count-music');
  const countSeventies = document.getElementById('count-seventies');

  // --- Web Audio API Synthesizer (Zero External Assets) ---
  let audioCtx = null;

  function initAudio() {
    if (!audioCtx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) {
        audioCtx = new AudioContext();
      }
    }
    if (audioCtx && audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
  }

  function playDrawSound() {
    if (!soundEnabled) return;
    try {
      initAudio();
      if (!audioCtx) return;

      const now = audioCtx.currentTime;

      // 1. Revolver cylinder click / mechanical tick
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(440, now);
      osc.frequency.exponentialRampToValueAtTime(110, now + 0.08);
      gain.gain.setValueAtTime(0.3, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + 0.08);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start(now);
      osc.stop(now + 0.08);

      // 2. Resonant Western Saloon chime
      const bellOsc = audioCtx.createOscillator();
      const bellGain = audioCtx.createGain();
      bellOsc.type = 'sine';
      bellOsc.frequency.setValueAtTime(587.33, now + 0.05); // D5
      bellGain.gain.setValueAtTime(0.15, now + 0.05);
      bellGain.gain.exponentialRampToValueAtTime(0.001, now + 0.4);
      bellOsc.connect(bellGain);
      bellGain.connect(audioCtx.destination);
      bellOsc.start(now + 0.05);
      bellOsc.stop(now + 0.4);
    } catch (e) {
      // Audio autoplay policy fallback
    }
  }

  // --- Data Loading & Initialization ---
  async function loadWesternsData() {
    try {
      const response = await fetch('westerns.json');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      allMovies = await response.json();
      updateFilterCounts();

      // Check initial URL routing
      const params = new URLSearchParams(window.location.search);
      const filmSlug = params.get('film');

      if (filmSlug) {
        const matched = allMovies.find(m => m.slug === filmSlug);
        if (matched) {
          renderMovieCard(matched, false);
          return;
        }
      }

      // If no valid film in URL, draw a random one
      drawRandomMovie(false);
    } catch (err) {
      console.error('Error loading westerns.json:', err);
      filmTitle.textContent = 'Error Loading Archive';
      filmSynopsis.textContent = 'Could not load westerns data. Please ensure westerns.json is present.';
    }
  }

  function updateFilterCounts() {
    if (!allMovies.length) return;

    const total = allMovies.length;
    const cultCount = allMovies.filter(m => m.tags.includes('cult_icons')).length;
    const goldenCount = allMovies.filter(m => m.tags.includes('golden_era')).length;
    const musicCount = allMovies.filter(m => m.tags.includes('morricone')).length;
    const seventiesCount = allMovies.filter(m => m.tags.includes('seventies')).length;

    if (vaultCountBadge) vaultCountBadge.textContent = `📦 ${total} Films in Vault`;
    if (countAll) countAll.textContent = total;
    if (countCult) countCult.textContent = cultCount;
    if (countGolden) countGolden.textContent = goldenCount;
    if (countMusic) countMusic.textContent = musicCount;
    if (countSeventies) countSeventies.textContent = seventiesCount;
  }

  // --- Filter Management ---
  function getFilteredMovies() {
    if (activeFilter === 'all') {
      return allMovies;
    }
    return allMovies.filter(m => m.tags && m.tags.includes(activeFilter));
  }

  function setFilter(filterKey) {
    activeFilter = filterKey;
    filterPills.forEach(pill => {
      const isActive = pill.dataset.filter === filterKey;
      pill.classList.toggle('active', isActive);
      pill.setAttribute('aria-checked', isActive ? 'true' : 'false');
    });

    // Auto-draw a movie from the newly selected filter
    drawRandomMovie(true);
  }

  // --- Randomizer & Slot Machine Roulette ---
  function drawRandomMovie(animate = true) {
    if (isSpinning || !allMovies.length) return;

    const pool = getFilteredMovies();
    if (!pool.length) return;

    // Pick random movie, avoiding immediate duplicate if pool > 1
    let selected;
    if (pool.length === 1) {
      selected = pool[0];
    } else {
      do {
        const randomIndex = Math.floor(Math.random() * pool.length);
        selected = pool[randomIndex];
      } while (currentMovie && selected.slug === currentMovie.slug && pool.length > 1);
    }

    if (!animate) {
      renderMovieCard(selected, true);
      return;
    }

    // Play slot machine animation
    isSpinning = true;
    playDrawSound();

    if (drawBtn) {
      drawBtn.classList.add('pressed');
      setTimeout(() => drawBtn.classList.remove('pressed'), 200);
    }

    // Ticker suspense reel
    tickerText.classList.add('spinning');
    filmCard.classList.add('fade-out');

    let rollCount = 0;
    const maxRolls = 6;
    const intervalTime = 55;

    const rollInterval = setInterval(() => {
      const randomCandidate = pool[Math.floor(Math.random() * pool.length)];
      tickerText.textContent = `ROLLING: ${randomCandidate.title.toUpperCase()}`;
      rollCount++;

      if (rollCount >= maxRolls) {
        clearInterval(rollInterval);
        tickerText.classList.remove('spinning');
        tickerText.textContent = `★ ${selected.title.toUpperCase()} (${selected.year}) ★`;
        
        setTimeout(() => {
          renderMovieCard(selected, true);
          filmCard.classList.remove('fade-out');
          filmCard.classList.add('fade-in');
          setTimeout(() => filmCard.classList.remove('fade-in'), 400);
          isSpinning = false;
        }, 50);
      }
    }, intervalTime);
  }

  // --- Render Film Card & Update Metadata ---
  function renderMovieCard(movie, pushState = true) {
    if (!movie) return;
    currentMovie = movie;

    // 1. Update Card Content
    filmVaultNumber.textContent = `VAULT ENTRY #${String(movie.id).padStart(3, '0')}`;
    filmTitle.textContent = movie.title;
    filmYear.textContent = `(${movie.year})`;

    // Alternative Titles
    if (movie.alt_titles && movie.alt_titles.length > 0) {
      filmAltTitles.textContent = movie.alt_titles.join(' • ');
      altTitlesBox.style.display = 'block';
    } else {
      altTitlesBox.style.display = 'none';
    }

    // Personnel Grid
    filmDirector.textContent = movie.director || 'Unknown Director';
    filmStar.textContent = movie.lead_actor || 'Ensemble Cast';
    filmCostars.textContent = (movie.co_stars && movie.co_stars.length > 0)
      ? movie.co_stars.slice(0, 4).join(', ') + (movie.co_stars.length > 4 ? ', ...' : '')
      : 'Various';
    filmMusic.textContent = movie.music || 'Archive Score';

    // Synopsis
    filmSynopsis.textContent = movie.synopsis || 'No editorial synopsis currently available for this title.';

    // FlickFinder Card Link
    if (flickfinderCardLink) {
      flickfinderCardLink.href = 'https://flickfuture.com/flickfinder';
    }

    // 2. Update Ticker HUD
    tickerText.textContent = `★ ${movie.title.toUpperCase()} (${movie.year}) ★`;

    // 3. Update SEO Title & Structured Data
    const fullTitle = `${movie.title} (${movie.year}) — Spaghetti Western Discovery`;
    document.title = fullTitle;
    updateStructuredData(movie);

    // 4. Update URL without page reload
    if (pushState) {
      const newUrl = `${window.location.pathname}?film=${encodeURIComponent(movie.slug)}`;
      window.history.pushState({ film: movie.slug }, fullTitle, newUrl);
    }

    // 5. Add to Recent Draws History
    addToRecentHistory(movie);
  }

  // --- Dynamic Schema.org Structured Data ---
  function updateStructuredData(movie) {
    const scriptTag = document.getElementById('schema-jsonld');
    if (!scriptTag) return;

    const movieSchema = {
      "@context": "https://schema.org",
      "@type": "Movie",
      "name": movie.title,
      "datePublished": movie.year,
      "description": movie.synopsis,
      "genre": ["Spaghetti Western", "Western", "Cult Cinema"],
      "director": {
        "@type": "Person",
        "name": movie.director
      },
      "actor": [
        {
          "@type": "Person",
          "name": movie.lead_actor
        }
      ],
      "url": `https://spaghetti-westerns.softcoverbooks.co.za/?film=${movie.slug}`
    };

    scriptTag.textContent = JSON.stringify(movieSchema, null, 2);
  }

  // --- History Drawer ---
  function addToRecentHistory(movie) {
    // Avoid duplicate at front
    const existingIndex = recentDraws.findIndex(m => m.slug === movie.slug);
    if (existingIndex !== -1) {
      recentDraws.splice(existingIndex, 1);
    }
    recentDraws.unshift(movie);
    if (recentDraws.length > MAX_RECENTS) {
      recentDraws.pop();
    }
    renderRecentHistory();
  }

  function renderRecentHistory() {
    if (!recentList) return;
    if (recentDraws.length === 0) {
      recentList.innerHTML = '<p class="recent-empty">Your drawn films will appear here for quick reference.</p>';
      return;
    }

    recentList.innerHTML = recentDraws.map(m => `
      <button type="button" class="recent-chip" data-slug="${m.slug}">
        <span>🎬</span> ${m.title} (${m.year})
      </button>
    `).join('');

    // Attach click handlers
    recentList.querySelectorAll('.recent-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const slug = chip.dataset.slug;
        const targetMovie = allMovies.find(m => m.slug === slug);
        if (targetMovie) {
          renderMovieCard(targetMovie, true);
        }
      });
    });
  }

  // --- Share & Clipboard ---
  async function shareCurrentFilm() {
    if (!currentMovie) return;

    const shareUrl = `${window.location.origin}${window.location.pathname}?film=${encodeURIComponent(currentMovie.slug)}`;
    const shareTitle = `${currentMovie.title} (${currentMovie.year}) — Spaghetti Western Discovery`;
    const shareText = `Check out "${currentMovie.title}" (${currentMovie.year}) on Spaghetti Western Discovery!`;

    if (navigator.share && /mobile|android|iphone|ipad/i.test(navigator.userAgent)) {
      try {
        await navigator.share({
          title: shareTitle,
          text: shareText,
          url: shareUrl
        });
        return;
      } catch (e) {
        // Fallback to clipboard if share cancelled or failed
      }
    }

    // Fallback: Clipboard Copy
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(shareUrl).then(() => {
        showToast(`Link for "${currentMovie.title}" copied! 📋`);
      }).catch(() => {
        fallbackCopyText(shareUrl);
      });
    } else {
      fallbackCopyText(shareUrl);
    }
  }

  function fallbackCopyText(text) {
    const tempInput = document.createElement('input');
    tempInput.value = text;
    document.body.appendChild(tempInput);
    tempInput.select();
    try {
      document.execCommand('copy');
      showToast(`Link for "${currentMovie.title}" copied! 📋`);
    } catch (err) {
      showToast('Please copy link manually.');
    }
    document.body.removeChild(tempInput);
  }

  function showToast(message) {
    if (!toast || !toastText) return;
    toastText.textContent = message;
    toast.classList.add('show');
    setTimeout(() => {
      toast.classList.remove('show');
    }, 3000);
  }

  // --- Sound Setting Management ---
  function initSoundSetting() {
    const saved = localStorage.getItem('sw_sound_enabled');
    if (saved !== null) {
      soundEnabled = saved === 'true';
    }
    updateSoundUI();
  }

  function toggleSound() {
    soundEnabled = !soundEnabled;
    localStorage.setItem('sw_sound_enabled', String(soundEnabled));
    updateSoundUI();
    if (soundEnabled) {
      playDrawSound();
    }
  }

  function updateSoundUI() {
    if (soundIcon) soundIcon.textContent = soundEnabled ? '🔊' : '🔇';
    if (soundText) soundText.textContent = soundEnabled ? 'Sound: On' : 'Sound: Off';
    if (soundBtn) {
      soundBtn.setAttribute('aria-label', soundEnabled ? 'Sound is on, click to mute' : 'Sound is muted, click to unmute');
    }
  }

  // --- Event Listeners ---
  function attachEventListeners() {
    // Centerpiece draw button
    if (drawBtn) {
      drawBtn.addEventListener('click', () => drawRandomMovie(true));
    }

    // Card draw again button
    if (cardDrawBtn) {
      cardDrawBtn.addEventListener('click', () => {
        drawRandomMovie(true);
        // Scroll smoothly towards the card if on small screen
        drawBtn.scrollIntoView({ behavior: 'smooth', block: 'center' });
      });
    }

    // Share button
    if (shareBtn) {
      shareBtn.addEventListener('click', shareCurrentFilm);
    }

    // Filter pills
    filterPills.forEach(pill => {
      pill.addEventListener('click', () => {
        const filter = pill.dataset.filter;
        if (filter) setFilter(filter);
      });
    });

    // Sound toggle
    if (soundBtn) {
      soundBtn.addEventListener('click', toggleSound);
    }

    // Clear history
    if (clearHistoryBtn) {
      clearHistoryBtn.addEventListener('click', () => {
        recentDraws.length = 0;
        renderRecentHistory();
      });
    }

    // Browser History Back/Forward (popstate)
    window.addEventListener('popstate', (e) => {
      const params = new URLSearchParams(window.location.search);
      const slug = params.get('film');
      if (slug && allMovies.length) {
        const matched = allMovies.find(m => m.slug === slug);
        if (matched) {
          renderMovieCard(matched, false);
          return;
        }
      }
      if (allMovies.length) {
        drawRandomMovie(false);
      }
    });

    // Global Keyboard Shortcut: Space or Enter to draw
    window.addEventListener('keydown', (e) => {
      if (e.code === 'Space' && e.target === document.body) {
        e.preventDefault();
        drawRandomMovie(true);
      }
    });
  }

  // --- Bootstrapping ---
  document.addEventListener('DOMContentLoaded', () => {
    initSoundSetting();
    attachEventListeners();
    loadWesternsData();
  });

})();
