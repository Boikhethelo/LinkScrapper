# LinkedIn Profile Scraper

Scrapes LinkedIn profiles using Playwright (JS rendering) + BeautifulSoup (HTML parsing), with optional support for the official LinkedIn API.

---

## ⚠️ Legal Notice

LinkedIn's Terms of Service prohibit scraping. Use this only on profiles you are authorised to access, and for legitimate purposes. Consider using the official API wherever possible.

---

## Project Structure

```
LinkScraper/
├── config/
│   └── settings.py           # All config, loaded from .env
├── src/
│   ├── api/
│   │   └── linkedin_api.py   # Official LinkedIn OAuth2 API client
│   ├── scrapers/
│   │   ├── browser.py        # Playwright browser manager + login
│   │   └── profile_scraper.py# BeautifulSoup HTML parser
│   ├── models/
│   │   └── profile.py        # Pydantic data models
│   ├── storage/
│   │   └── database.py       # SQLite + CSV export
│   └── utils/
│       ├── logger.py         # Loguru logging (console + file)
│       └── rate_limiter.py   # Random delays between requests
├── data/output/              # Exported CSVs land here
├── logs/                     # scraper.log written here
├── .env.example              # Copy to .env and fill in values
├── requirements.txt
└── main.py                   # Entry point
```

---

## Setup

```bash
# 1. Clone / download the project
cd linkedin_scraper

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright's Chromium browser
playwright install chromium

# 5. Set up your credentials
cp .env .env
# Edit .env with your LinkedIn email, password, and API keys
```

---

## Usage

### Scrape profiles (browser + BeautifulSoup)

Edit `TARGET_PROFILES` in `main.py`, then:

```bash
python main.py scrape
# or just:
python main.py
```

Results are saved to `data/linkedin.db` and exported to `data/output/profiles.csv`.

### Official API demo (your own profile only)

```bash
python main.py api
```

---

## Configuration (.env)

| Variable              | Description                                      | Default                       |
|-----------------------|--------------------------------------------------|-------------------------------|
| `LINKEDIN_EMAIL`      | Your LinkedIn login email                        | —                             |
| `LINKEDIN_PASSWORD`   | Your LinkedIn login password                     | —                             |
| `LINKEDIN_CLIENT_ID`  | App client ID from LinkedIn Developers           | —                             |
| `LINKEDIN_CLIENT_SECRET` | App client secret                           | —                             |
| `MIN_DELAY`           | Minimum seconds between requests                 | `3.0`                         |
| `MAX_DELAY`           | Maximum seconds between requests                 | `8.0`                         |
| `HEADLESS`            | Run browser invisibly (`true`/`false`)           | `true`                        |
| `DB_PATH`             | SQLite database path                             | `data/linkedin.db`            |
| `OUTPUT_DIR`          | Directory for exported CSVs                      | `data/output`                 |

---

## Tips

- If you hit a CAPTCHA, set `HEADLESS=false` to solve it manually.
- LinkedIn's HTML class names change regularly — if parsing breaks, inspect the live page with DevTools and update `profile_scraper.py`.
- The `already_scraped()` check means re-running the script won't duplicate entries.
