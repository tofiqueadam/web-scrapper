import os
import sys
import json
import logging
import platform
import subprocess
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configuration — all 6 law categories on the real NBE site
CATEGORIES = {
    "directives":    os.getenv("NBE_DIRECTIVES_URL",    "https://nbe.gov.et/mandates/directives/"),
    "proclamations": os.getenv("NBE_PROCLAMATIONS_URL", "https://nbe.gov.et/mandates/proclamation/"),
    "regulations":   os.getenv("NBE_REGULATIONS_URL",   "https://nbe.gov.et/mandates/regulation/"),
    "guidelines":    os.getenv("NBE_GUIDELINES_URL",    "https://nbe.gov.et/mandates/guidelines/"),
    "public_notes":  os.getenv("NBE_PUBLIC_NOTES_URL",  "https://nbe.gov.et/public-notice-2/"),
    "forms":         os.getenv("NBE_FORMS_URL",         "https://nbe.gov.et/forms/"),
}

STATE_FILE = "seen_docs.json"
FORMSPREE_URL = os.getenv("FORMSPREE_URL")


def setup_windows_scheduler():
    """
    On Windows, ensures a scheduled task exists to run this script daily at 10:00 AM.
    Uses schtasks.exe to create the task pointing to the current executable.
    """
    if platform.system() != "Windows":
        return

    task_name = "NBE_Monitor"
    # sys.executable gives the path to the .exe when bundled by PyInstaller
    exe_path = os.path.abspath(sys.executable)
    
    logging.info("Checking Windows Task Scheduler...")
    
    try:
        # Check if task already exists
        check_task = subprocess.run(
            ["schtasks", "/query", "/tn", task_name],
            capture_output=True, text=True
        )
        
        if check_task.returncode == 0:
            logging.info(f"Scheduled task '{task_name}' already exists.")
            return

        # Create the task: Daily at 10:00 AM
        logging.info(f"Creating scheduled task '{task_name}' for 10:00 AM daily.")
        create_task = subprocess.run(
            [
                "schtasks", "/create", "/tn", task_name, 
                "/tr", f'"{exe_path}"', 
                "/sc", "daily", "/st", "10:00", "/f"
            ],
            capture_output=True, text=True
        )
        
        if create_task.returncode == 0:
            logging.info("Successfully scheduled the NBE Monitor for 10:00 AM daily.")
        else:
            logging.error(f"Failed to create scheduled task: {create_task.stderr}")

    except Exception as e:
        logging.error(f"Error managing Windows Task Scheduler: {e}")


def load_state():
    """Load previously seen documents from JSON to prevent duplicate alerts."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logging.error("Corrupt state file, starting fresh.")
    return {cat: [] for cat in CATEGORIES}


def save_state(state):
    """Save the updated list of seen documents."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)


def scrape_nbe_page(url):
    """
    Fetches and parses an NBE page to find document titles and links.
    The live NBE site uses an Elementor grid layout with h5 tags (not standard tables).
    Falls back to standard table parsing for custom/mock sites.
    """
    logging.info(f"Scraping {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    documents = []

    # ── Method 1: Elementor grid layout (live NBE site) ──────────────────────
    # Documents are wrapped in <a> tags, with the title in an <h5> child
    elementor_links = soup.select("a h5")
    if elementor_links:
        for h5 in elementor_links:
            parent_a = h5.find_parent("a", href=True)
            title = h5.get_text(strip=True)
            link = parent_a["href"] if parent_a else url
            if title and len(title) > 3:
                documents.append({"id": title, "title": title, "link": link})

    # ── Method 2: Standard HTML table (mock/test sites) ──────────────────────
    if not documents:
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows[1:]:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    title_td = cols[1] if len(cols) > 1 else cols[0]
                    link_tag = row.find("a", href=True)
                    title = title_td.get_text(strip=True)
                    link = link_tag["href"] if link_tag else url
                    if title and len(title) > 3:
                        documents.append({"id": title, "title": title, "link": link})

    # ── Method 3: Generic PDF/download link fallback ──────────────────────────
    if not documents:
        logging.info("No tables/grid found — falling back to generic link scraping.")
        for a in soup.find_all("a", href=True):
            href = a["href"].lower()
            text = a.get_text(strip=True)
            if any(kw in href for kw in ["pdf", "download", "directive", "proclamation", "regulation"]):
                title = text if text else os.path.basename(href)
                if title and len(title) > 3:
                    documents.append({"id": title, "title": title, "link": a["href"]})

    # Deduplicate by ID
    unique_docs = {doc["id"]: doc for doc in documents}
    return list(unique_docs.values())


def send_formspree_alert(combined_message):
    """Dispatches a single consolidated Formspree notification."""
    if not FORMSPREE_URL:
        logging.warning("FORMSPREE_URL not configured. Skipping Formspree dispatch.")
        return
    try:
        logging.info("Sending consolidated notification to Formspree...")
        response = requests.post(FORMSPREE_URL, json={
            "_subject": "NBE Document Updates",
            "message": combined_message
        }, timeout=10)
        response.raise_for_status()
        logging.info("Successfully sent consolidated Formspree alert.")
    except Exception as e:
        logging.error(f"Failed to send Formspree alert: {e}")


def main():
    logging.info("Starting NBE Monitor execution.")
    
    # Auto-schedule on Windows if not already done
    setup_windows_scheduler()

    state = load_state()
    state_updated = False
    summary_messages = []

    for category, url in CATEGORIES.items():
        current_docs = scrape_nbe_page(url)
        new_docs = []

        for doc in current_docs:
            if doc["id"] not in state.get(category, []):
                new_docs.append(doc)
                state.setdefault(category, []).append(doc["id"])

        if new_docs:
            label = category.upper().replace("_", " ")
            logging.info(f"*** Found {len(new_docs)} new {category}! ***")
            section = f"NEW {label}:\n" + "\n".join(
                [f"- {d['title']}\n  Link: {d['link']}" for d in new_docs]
            )
            summary_messages.append(section)
            state_updated = True
        else:
            logging.info(f"No new {category} found.")

    # Send ONE combined email only if there are any updates
    if state_updated:
        combined_body = (
            "The following new documents were detected on the National Bank of Ethiopia website:\n\n"
            + "\n\n".join(summary_messages)
        )
        send_formspree_alert(combined_body)
        save_state(state)
        logging.info("State file updated successfully.")

    logging.info("NBE Monitor execution finished.")


if __name__ == "__main__":
    main()
