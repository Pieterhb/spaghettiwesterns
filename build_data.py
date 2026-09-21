#!/usr/bin/env python3
"""
build_data.py
Converts Complete_Westerns.csv into an optimized, minified westerns.json,
generates a static, crawlable archive.html directory of all 560 films for SEO,
and outputs a complete sitemap.xml for Cloudflare Pages deployment.
"""

import csv
import json
import re
import html
import sys
from datetime import datetime

SITE_URL = "https://spaghetti-westerns.softcoverbooks.co.za"

# Famous Spaghetti Western icons to tag for the "Cult Icons" filter
CULT_ICONS = [
    "Clint Eastwood", "Franco Nero", "Giuliano Gemma", "Klaus Kinski",
    "Terence Hill", "Bud Spencer", "Lee Van Cleef", "Tomas Milian",
    "Gianni Garko", "Anthony Steffen", "George Hilton", "Charles Bronson",
    "Jack Palance", "Gordon Mitchell", "Peter Lee Lawrence", "Craig Hill",
    "John Ireland", "Eli Wallach", "Gian Maria Volonté", "Woody Strode",
    "Henry Fonda", "James Coburn", "Robert Woods", "Mark Damon",
    "Fernando Sancho", "Rosalba Neri", "Eduardo Fajardo", "Yul Brynner"
]

def make_slug(title: str, year: str) -> str:
    combined = f"{title} {year}".lower()
    slug = re.sub(r'[^a-z0-9]+', '-', combined).strip('-')
    return slug

def classify_tags(movie: dict) -> list:
    tags = ["all"]
    try:
        year = int(movie.get("Year", 0))
    except ValueError:
        year = 0

    # Era classifications
    if 1964 <= year <= 1969:
        tags.append("golden_era")
    elif year >= 1970:
        tags.append("seventies")

    # Music / Morricone & Nicolai
    music = (movie.get("Music") or "").lower()
    if "morricone" in music or "nicolai" in music:
        tags.append("morricone")

    # Cult Stars filter
    lead = movie.get("Lead_Actor", "")
    co_stars = movie.get("Co_Stars", "")
    all_cast = f"{lead}, {co_stars}"
    for icon in CULT_ICONS:
        if icon.lower() in all_cast.lower():
            tags.append("cult_icons")
            break

    return tags

def get_alpha_key(title: str) -> str:
    cleaned = title.strip()
    # Strip leading articles for alphabetization if desired, or keep direct initial
    first_char = cleaned[0].upper() if cleaned else '#'
    if first_char.isalpha():
        return first_char
    return '#'

def generate_archive_html(movies: list, output_file: str = "archive.html"):
    """Generates a complete static, crawlable HTML directory of all 560 films."""
    
    # Sort movies alphabetically by title
    sorted_movies = sorted(movies, key=lambda m: (m['title'].strip().lower(), m['year']))
    
    # Group by letter
    letter_groups = {}
    for m in sorted_movies:
        key = get_alpha_key(m['title'])
        if key not in letter_groups:
            letter_groups[key] = []
        letter_groups[key].append(m)

    letters = sorted(letter_groups.keys(), key=lambda k: (k == '#', k))

    # Generate alpha jump links
    jump_links = []
    for l in letters:
        count = len(letter_groups[l])
        jump_links.append(f'<a href="#{l}" class="alpha-jump-pill">{l} <span class="jump-count">({count})</span></a>')
    jump_html = " ".join(jump_links)

    # Generate letter sections
    sections_html = []
    for l in letters:
        group = letter_groups[l]
        cards_html = []
        for m in group:
            t = html.escape(m['title'])
            y = html.escape(m['year'])
            slug = html.escape(m['slug'])
            director = html.escape(m['director'] or 'Unknown')
            lead = html.escape(m['lead_actor'] or 'Ensemble')
            music = html.escape(m['music'] or 'Archival')
            synopsis = html.escape(m['synopsis'][:170] + ('...' if len(m['synopsis']) > 170 else ''))

            cards_html.append(f"""
        <article class="archive-card">
          <div class="archive-card-header">
            <h3 class="archive-card-title">
              <a href="/?film={slug}" class="archive-link" title="Discover {t} ({y})">
                {t} <span class="archive-year">({y})</span>
              </a>
            </h3>
          </div>
          <div class="archive-card-meta">
            <span class="meta-tag">🎬 <strong>Dir:</strong> {director}</span>
            <span class="meta-tag">⭐ <strong>Star:</strong> {lead}</span>
            <span class="meta-tag">🎵 <strong>Score:</strong> {music}</span>
          </div>
          <p class="archive-card-synopsis">{synopsis}</p>
          <div class="archive-card-footer">
            <a href="/?film={slug}" class="archive-view-btn">View Film Card →</a>
          </div>
        </article>""")

        section_block = f"""
      <section class="archive-letter-section" id="{l}">
        <div class="letter-header">
          <h2 class="letter-heading">{l}</h2>
          <span class="letter-badge">{len(group)} Films</span>
          <a href="#top" class="letter-top-link">↑ Top</a>
        </div>
        <div class="archive-grid">
          {"".join(cards_html)}
        </div>
      </section>"""
        sections_html.append(section_block)

    archive_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Complete A–Z Spaghetti Western Film Archive (560+ Titles) — Directory</title>
  <meta name="description" content="Browse the complete index of 560+ Spaghetti Western and Euro-Western films (1961–1977). Complete directory of directors, actors, soundtracks, and synopses.">
  <meta name="keywords" content="Spaghetti Western archive, Euro-Western filmography, Italian Western database, Sergio Leone films, Franco Nero westerns, Giuliano Gemma, Ennio Morricone scores">
  <meta name="theme-color" content="#1a1412">
  <link rel="canonical" href="{SITE_URL}/archive.html">

  <!-- OpenGraph / Facebook -->
  <meta property="og:type" content="website">
  <meta property="og:url" content="{SITE_URL}/archive.html">
  <meta property="og:title" content="Complete A–Z Spaghetti Western Film Archive (560+ Titles)">
  <meta property="og:description" content="Browse the complete crawlable directory of 560+ Italian and European Westerns from 1961 to 1977.">
  <meta property="og:image" content="{SITE_URL}/1.jpg">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Complete A–Z Spaghetti Western Film Archive (560+ Titles)">
  <meta name="twitter:description" content="Browse the complete crawlable directory of 560+ Italian and European Westerns from 1961 to 1977.">
  <meta name="twitter:image" content="{SITE_URL}/1.jpg">

  <!-- Google Fonts Preconnect -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;900&family=Lora:ital,wght@0,400;0,600;1,400&family=Rye&display=swap" rel="stylesheet">

  <link rel="stylesheet" href="style.css">

  <!-- Schema.org Structured Data -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    "name": "Complete A–Z Spaghetti Western Film Archive",
    "url": "{SITE_URL}/archive.html",
    "description": "Comprehensive filmography directory indexing 560+ European and Italian Western films from 1961 to 1977.",
    "about": {{
      "@type": "Thing",
      "name": "Spaghetti Western Cinema"
    }},
    "numberOfItems": {len(movies)}
  }}
  </script>
</head>
<body>
  <div class="dust-overlay" aria-hidden="true"></div>

  <!-- Header Container -->
  <header class="site-header" id="top">
    <div class="header-inner">
      <div class="header-badge">
        <span class="badge-star">★</span>
        <span class="badge-text">560+ CULT TITLES INDEXED</span>
        <span class="badge-star">★</span>
      </div>
      <h1 class="site-title">
        <span class="title-sub">COMPLETE A–Z DIRECTORY</span>
        <span class="title-main">SPAGHETTI WESTERN ARCHIVE</span>
      </h1>
      <p class="site-tagline">
        Exhaustive crawlable filmography covering 560+ European Westerns produced between 1961 and 1977.
      </p>
      <div class="header-controls">
        <a href="/" class="back-btn">🎲 Return to Randomizer Game</a>
        <a href="https://flickfuture.com/flickfinder" target="_blank" rel="noopener noreferrer" class="flick-btn">🔍 Search on FlickFinder →</a>
      </div>
    </div>
  </header>

  <!-- Top Ad Slot (CLS Protected) -->
  <div class="ad-slot-container">
    <div class="ad-placeholder" id="ad-top-slot" aria-label="Advertisement Banner">
      <span class="ad-label">ADVERTISEMENT</span>
    </div>
  </div>

  <main class="main-content">
    <!-- Alphabetical Jump Bar -->
    <nav class="alpha-nav" aria-label="Alphabetical Jump Navigation">
      <div class="alpha-nav-title">JUMP TO LETTER:</div>
      <div class="alpha-pills">
        {jump_html}
      </div>
    </nav>

    <!-- Archive Film Directory Sections -->
    <div class="archive-directory">
      {"".join(sections_html)}
    </div>
  </main>

  <!-- Bottom Ad Slot (CLS Protected) -->
  <div class="ad-slot-container">
    <div class="ad-placeholder" id="ad-bottom-slot" aria-label="Advertisement Banner">
      <span class="ad-label">ADVERTISEMENT</span>
    </div>
  </div>

  <!-- Traffic Funnel Callout Card -->
  <section class="funnel-banner-wrapper">
    <div class="funnel-banner">
      <div class="funnel-icon">🏜️</div>
      <div class="funnel-text">
        <h3 class="funnel-title">Looking for deep actor filmographies or specific composers?</h3>
        <p class="funnel-description">
          Looking for a specific film, actor, or director? Search our complete 500+ title archive at FlickFinder →
        </p>
      </div>
      <a href="https://flickfuture.com/flickfinder" target="_blank" rel="noopener noreferrer" class="funnel-btn">
        SEARCH COMPLETE DATABASE AT FLICKFINDER →
      </a>
    </div>
  </section>

  <!-- Site Footer -->
  <footer class="site-footer">
    <div class="footer-inner">
      <p class="footer-copy">© 2025 Spaghetti Western Discovery. A curated archive of 560+ European Westerns (1961–1977).</p>
      <div class="footer-links">
        <a href="/">🎲 Random Discovery Machine</a>
        <span class="divider">•</span>
        <a href="archive.html">A–Z Complete Archive</a>
        <span class="divider">•</span>
        <a href="about.html">About</a>
        <span class="divider">•</span>
        <a href="privacy.html">Privacy Policy</a>
        <span class="divider">•</span>
        <a href="terms.html">Terms &amp; Conditions</a>
        <span class="divider">•</span>
        <a href="contact.html">Contact</a>
        <span class="divider">•</span>
        <a href="https://flickfuture.com/flickfinder" target="_blank" rel="noopener noreferrer">FlickFinder Complete Search</a>
      </div>
    </div>
  </footer>
</body>
</html>
"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(archive_content)
    print(f"Generated crawlable directory {output_file} ({len(movies)} films indexed).")

def main():
    csv_file = "Complete_Westerns.csv"
    json_file = "westerns.json"
    sitemap_file = "sitemap.xml"
    archive_file = "archive.html"

    print(f"Reading {csv_file}...")
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Found {len(rows)} rows in CSV.")

    movies = []
    slug_counts = {}

    for idx, r in enumerate(rows):
        title = (r.get("Title") or "").strip()
        year = (r.get("Year") or "").strip()
        alt_raw = (r.get("Alternative_Titles") or "").strip()
        director = (r.get("Director") or "").strip()
        lead_actor = (r.get("Lead_Actor") or "").strip()
        co_stars_raw = (r.get("Co_Stars") or "").strip()
        music = (r.get("Music") or "").strip()
        synopsis = (r.get("Synopsis_and_Notes") or "").strip()

        if not title:
            continue

        # Clean alternative titles list
        alt_titles = [a.strip() for a in alt_raw.split(";") if a.strip()] if alt_raw else []

        # Clean co-stars list
        co_stars = [c.strip() for c in co_stars_raw.split(",") if c.strip()] if co_stars_raw else []

        # Unique slug generation
        base_slug = make_slug(title, year)
        if not base_slug:
            base_slug = f"western-{idx+1}"

        if base_slug in slug_counts:
            slug_counts[base_slug] += 1
            slug = f"{base_slug}-{slug_counts[base_slug]}"
        else:
            slug_counts[base_slug] = 1
            slug = base_slug

        movie_data = {
            "id": idx + 1,
            "title": title,
            "year": year,
            "slug": slug,
            "alt_titles": alt_titles,
            "director": director,
            "lead_actor": lead_actor,
            "co_stars": co_stars,
            "music": music,
            "synopsis": synopsis,
        }

        movie_data["tags"] = classify_tags(r)
        movies.append(movie_data)

    print(f"Processed {len(movies)} movies.")

    # Export minified JSON
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(movies, f, ensure_ascii=False, separators=(",", ":"))
    print(f"Wrote minified {json_file} successfully.")

    # Generate static crawlable archive.html directory
    generate_archive_html(movies, archive_file)

    # Generate sitemap.xml for SEO
    today = datetime.now().strftime("%Y-%m-%d")
    sitemap_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]

    # Home page
    sitemap_lines.append(f"""  <url>
    <loc>{SITE_URL}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>""")

    # Archive Directory Page
    sitemap_lines.append(f"""  <url>
    <loc>{SITE_URL}/archive.html</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>""")

    # Compliance & Trust pages
    for page in ["about.html", "privacy.html", "terms.html", "contact.html"]:
        sitemap_lines.append(f"""  <url>
    <loc>{SITE_URL}/{page}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>""")

    # Deep links for each film
    for m in movies:
        sitemap_lines.append(f"""  <url>
    <loc>{SITE_URL}/?film={m['slug']}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""")

    sitemap_lines.append("</urlset>\n")

    with open(sitemap_file, "w", encoding="utf-8") as f:
        f.write("\n".join(sitemap_lines))
    print(f"Generated {sitemap_file} with {len(movies) + 6} URLs.")

if __name__ == "__main__":
    main()
