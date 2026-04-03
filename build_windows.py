import subprocess
import sys
import os

def build_exe():
    print("Checking for PyInstaller...")
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Build command
    # --onefile: single .exe
    # --noconsole: no popup window (runs in background)
    # --name: the filename
    # --clean: clean cache before building
    cmd = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--name", "NBEMonitor",
        "--clean",
        "scraper.py"
    ]

    print(f"Building executable: {' '.join(cmd)}")
    subprocess.check_call(cmd)

    print("\n" + "="*30)
    print("BUILD COMPLETE!")
    print("Your executable is in the 'dist' folder: dist\\NBEMonitor.exe")
    print("="*30)
    print("\nInstructions for your coworker:")
    print("1. Copy 'dist\\NBEMonitor.exe' and your '.env' file to her computer.")
    print("2. Put them in the same folder.")
    print("3. She just needs to double-click 'NBEMonitor.exe' once.")
    print("   - It will run immediately.")
    print("   - It will automatically schedule itself to run every day at 10:00 AM.")

if __name__ == "__main__":
    build_exe()
