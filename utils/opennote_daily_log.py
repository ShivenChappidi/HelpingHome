"""
Automate daily OpenNote log creation from sensor CSV.
"""

import os
import subprocess
from datetime import date

SENSOR_OUTPUT_DIR = "data/daily_logs"


def run_opennote_daily_log():
    today = date.today().isoformat()
    csv_path = os.path.join(SENSOR_OUTPUT_DIR, f"sensors_{today}.csv")
    if not os.path.exists(csv_path):
        print(f"Sensor data file not found: {csv_path}")
        return
    # Run the OpenNote daily_notes_from_csv script
    cmd = [
        "python", "-m", "opennote.daily_notes_from_csv",
        "--csv", csv_path,
        "--date", today
    ]
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    run_opennote_daily_log()
