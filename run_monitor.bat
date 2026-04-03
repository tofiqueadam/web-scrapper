@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
echo Starting NBE Monitor Task at %date% %time% >> scraper.log
python scraper.py
