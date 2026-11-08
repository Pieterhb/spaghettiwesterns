#!/usr/bin/env python3
"""
IndexNow URL Submission Script — Admin/Backend Use Only
=======================================================
Submits updated URLs to Bing IndexNow API via HTTP POST.

DO NOT run this from client-side JavaScript or on visitor page loads.
This is a one-off or scheduled admin trigger only.

Usage:
    python tools/indexnow_submit.py

Requirements:
    pip install requests  (or use built-in urllib — no deps required by default)

Docs: https://www.indexnow.org/documentation
"""

import json
import urllib.request
import urllib.error
import urllib.parse
import sys

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
API_KEY = "98ebccc16ff84c2f8ec6a9411bb3d39d"
KEY_LOCATION = "https://spaghetti-westerns.softcoverbooks.co.za/98ebccc16ff84c2f8ec6a9411bb3d39d.txt"
HOST = "spaghetti-westerns.softcoverbooks.co.za"
INDEXNOW_ENDPOINT = "https://api.indexnow.org/IndexNow"

# All public URLs to submit (extend this list whenever you publish new content)
URLS_TO_SUBMIT = [
    "https://spaghetti-westerns.softcoverbooks.co.za/",
    "https://spaghetti-westerns.softcoverbooks.co.za/archive",
    "https://spaghetti-westerns.softcoverbooks.co.za/about",
    "https://spaghetti-westerns.softcoverbooks.co.za/contact",
    "https://spaghetti-westerns.softcoverbooks.co.za/privacy",
    "https://spaghetti-westerns.softcoverbooks.co.za/terms",
]

# ---------------------------------------------------------------------------
# Submit
# ---------------------------------------------------------------------------

def submit_indexnow() -> None:
    """Send a batch IndexNow POST request to Bing."""

    payload = {
        "host": HOST,
        "key": API_KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": URLS_TO_SUBMIT,
    }

    body = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        INDEXNOW_ENDPOINT,
        data=body,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "SpaghettiWesterns-IndexNow-Bot/1.0",
        },
        method="POST",
    )

    print(f"Submitting {len(URLS_TO_SUBMIT)} URLs to IndexNow …")
    print(f"  Endpoint : {INDEXNOW_ENDPOINT}")
    print(f"  Host     : {HOST}")
    print(f"  Key      : {API_KEY}")
    print(f"  URLs     :")
    for url in URLS_TO_SUBMIT:
        print(f"    - {url}")

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            status = response.status
            body_resp = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        status = exc.code
        body_resp = exc.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        print(f"\n[ERROR] Network error: {exc.reason}", file=sys.stderr)
        sys.exit(1)

    print(f"\nResponse status : {status}")
    if body_resp:
        print(f"Response body   : {body_resp}")

    # IndexNow returns 200 or 202 on success
    if status in (200, 202):
        print("\n✅  URLs successfully submitted to Bing IndexNow.")
    elif status == 400:
        print("\n❌  Bad request — check that all URLs belong to the declared host.", file=sys.stderr)
        sys.exit(1)
    elif status == 403:
        print(
            "\n❌  Forbidden — Bing could not verify the key file.\n"
            "   Make sure https://spaghetti-westerns.softcoverbooks.co.za/98ebccc16ff84c2f8ec6a9411bb3d39d.txt\n"
            "   returns HTTP 200 with the raw key as its body.\n"
            "   Also consider placing the key file on www.softcoverbooks.co.za for parent-domain verification.",
            file=sys.stderr,
        )
        sys.exit(1)
    elif status == 422:
        print("\n❌  Unprocessable entity — one or more URLs are invalid.", file=sys.stderr)
        sys.exit(1)
    elif status == 429:
        print("\n⚠️   Too many requests — you have been rate-limited. Try again later.", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"\n⚠️   Unexpected status {status}.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    submit_indexnow()
