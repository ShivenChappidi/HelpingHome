"""
Aggregate daily sensor data from all rooms and save as a CSV for OpenNote logging.
"""

import csv
import os
from datetime import date

ROOMS = [
    ("kitchen", "rooms/kitchen/kitchen.py"),
    ("laundry", "rooms/laundry/laundry.py"),
    ("bathroom", "rooms/bathroom/bathroom.py"),
]

SENSOR_OUTPUT_DIR = "data/daily_logs"

# Dummy function to simulate sensor data collection from each room
# Replace with actual sensor reading logic as needed
def collect_room_data(room_name):
    # Example: Replace with real sensor reading code
    if room_name == "kitchen":
        return {
            "room": "kitchen",
            "sound_db": 55,
            "light_lux": 60,
            "note": "Normal activity."
        }
    elif room_name == "laundry":
        return {
            "room": "laundry",
            "vibration": 1,
            "note": "Laundry finished."
        }
    elif room_name == "bathroom":
        return {
            "room": "bathroom",
            "noise_db": 70,
            "water_temp_c": 37,
            "note": "Shower used."
        }
    return {"room": room_name, "note": "No data."}

def aggregate_daily_sensor_data():
    os.makedirs(SENSOR_OUTPUT_DIR, exist_ok=True)
    today = date.today().isoformat()
    csv_path = os.path.join(SENSOR_OUTPUT_DIR, f"sensors_{today}.csv")
    fieldnames = ["date", "room", "note", "sound_db", "light_lux", "vibration", "noise_db", "water_temp_c"]
    rows = []
    for room, _ in ROOMS:
        data = collect_room_data(room)
        data_row = {k: data.get(k, "") for k in fieldnames}
        data_row["date"] = today
        rows.append(data_row)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"✅ Daily sensor data saved to {csv_path}")
    return csv_path

if __name__ == "__main__":
    aggregate_daily_sensor_data()
