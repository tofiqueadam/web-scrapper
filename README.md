# NBE Document Monitor 🇪🇹

A Python script that monitors the [National Bank of Ethiopia](https://nbe.gov.et/) website for newly published legal documents and sends a **single consolidated email alert** via [Formspree](https://formspree.io/) when any updates are detected.

## What it monitors

Under the **Laws** navigation menu on nbe.gov.et:

| Category | URL |
|---|---|
| Directives | https://nbe.gov.et/mandates/directives/ |
| Proclamations | https://nbe.gov.et/mandates/proclamation/ |
| Regulations | https://nbe.gov.et/mandates/regulation/ |
| Guidelines | https://nbe.gov.et/mandates/guidelines/ |
| Public Notes | https://nbe.gov.et/public-notice-2/ |
| Forms | https://nbe.gov.et/forms/ |

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/tofiqueadam/web-scrapper.git
cd web-scrapper
```

### 2. Create a virtual environment and install dependencies
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure environment variables
Copy the template and fill in your details:
```bash
cp .env.template .env
```
Edit `.env`:
```env
FORMSPREE_URL=https://formspree.io/f/YOUR_FORM_ID
```
Get your free Formspree URL at [formspree.io](https://formspree.io/) — just create a form and verify your email.

### 4. Run manually
```bash
python scraper.py
```

## Scheduling (Windows Task Scheduler)
Use the included `run_monitor.bat` file. In Windows Task Scheduler:
- **Program:** Point to `run_monitor.bat` inside this folder
- **Trigger:** Daily at your preferred time (e.g. 10:00 AM)

This will silently run every day and only send an email if new documents appear.

## How it works
1. Scrapes all 6 NBE law categories
2. Compares new docs against `seen_docs.json` (state file, auto-created locally)
3. If any new documents are found → sends **one single email** summarising all updates
4. Updates `seen_docs.json` so you won't be re-notified about the same documents

## Files
| File | Purpose |
|---|---|
| `scraper.py` | Main scraper and email notification logic |
| `requirements.txt` | Python dependencies |
| `.env.template` | Environment variable template |
| `run_monitor.bat` | Windows scheduler launcher |
| `run_monitor.sh` | Linux/macOS cron launcher |
