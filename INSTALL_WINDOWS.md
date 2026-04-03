# Windows Installation Guide for NBE Monitor 🇪🇹

Follow these steps to set up the NBE Monitor on a new Windows computer.

## Step 1: Install Python
1. Go to [python.org/downloads](https://www.python.org/downloads/windows/).
2. Click the yellow **Download Python 3.x.x** button.
3. **CRITICAL:** When running the installer, check the box that says **"Add Python to PATH"** at the bottom.
4. Click **Install Now**.

## Step 2: Download the Code
1. If you don't have Git, download the repository as a ZIP file from GitHub.
2. Extract the ZIP folder to a safe place (e.g., `C:\NBE_Monitor`).

## Step 3: Set up the Environment
1. Open a terminal (Type `cmd` in the Start menu).
2. Go to the folder where you extracted the code:
   ```cmd
   cd C:\NBE_Monitor
   ```
3. Create a virtual environment:
   ```cmd
   python -m venv venv
   ```
4. Activate the virtual environment:
   ```cmd
   venv\Scripts\activate
   ```
5. Install the required libraries:
   ```cmd
   pip install -r requirements.txt
   ```

## Step 4: Configure Settings
1. In the folder, look for `.env.template`.
2. Rename it to `.env`.
3. Open it with Notepad and paste your Formspree URL:
   ```env
   FORMSPREE_URL=https://formspree.io/f/your_form_id
   ```

## Step 5: Test it
1. Run the script once manually to make sure it works:
   ```cmd
   python scraper.py
   ```
   *Note: If no new documents are found, it will say "No new documents found".*

## Step 6: Schedule Automatically
1. Open **Task Scheduler** from the Start menu.
2. Click **Create Basic Task...** on the right side.
3. **Name:** NBE Monitor
4. **Trigger:** Daily (Choose your time, e.g., 20:00).
5. **Action:** Start a Program.
6. **Program/script:** Browse to the `run_monitor.bat` file in your folder.
7. Click **Finish**.
8. **Pro Tip:** In Task Scheduler, double-click your new task, go to **Conditions**, and uncheck "Start the task only if the computer is on AC power" if you're on a laptop.
