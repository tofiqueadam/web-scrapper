#!/bin/bash
cd /home/dell500/.gemini/antigravity/scratch/nbe_monitor

# Activate the virtual environment
source venv/bin/activate

# Optional: Add a timestamp to log when it started
echo "Starting NBE Monitor Cron Job at $(date)" >> scraper.log

# Run the python script
python3 scraper.py
