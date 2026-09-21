#!/usr/bin/env python3
"""
build_data.py
Converts Complete_Westerns.csv into an optimized, minified westerns.json
and generates a sitemap.xml for Cloudflare Pages deployment.
"""

import csv
import json
import re
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
    # Replace non-alphanumeric characters with a hyphen
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

def main():
    csv_file = "Complete_Westerns.csv"
    json_file = "westerns.json"
    sitemap_file = "sitemap.xml"

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
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>""")

    # Deep links for each film
    for m in movies:
        sitemap_lines.append(f"""  <url>
    <loc>{SITE_URL}/?film={m['slug']}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>""")

    sitemap_lines.append("</urlset>\n")

    with open(sitemap_file, "w", encoding="utf-8") as f:
        f.write("\n".join(sitemap_lines))
    print(f"Generated {sitemap_file} with {len(movies) + 1} URLs.")

if __name__ == "__main__":
    main()
