from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import csv
import os
import fuzzy_logic
import json

app = Flask(__name__)

# State Global untuk menyimpan data terakhir dari sensor IoT
LAST_TEMPERATURE = 25
LAST_HUMIDITY = 30
LAST_AIRQUALITY = 20
LAST_IOT_TIMESTAMP = datetime.min

TIME_PROXIMITY_THRESHOLD = timedelta(minutes=5)
SMARTPHONE_DATA_RECEIVED = False

def format_hms(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours} jam {minutes} menit {secs} detik"

DATA_FOLDER = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)

@app.route('/receive_usage', methods=['POST'])
def receive_usage():
    global LAST_TEMPERATURE, LAST_HUMIDITY, LAST_AIRQUALITY, SMARTPHONE_DATA_RECEIVED, LAST_IOT_TIMESTAMP

    data = request.get_json(force=True)
    if not data:
        return jsonify({"status": "error", "message": "no json received"}), 400

    # Ambil ID unik handphone
    device_id = data.get("device_id", "unknown_device")

    DEVICE_FOLDER = os.path.join(DATA_FOLDER, f"device_{device_id}")
    os.makedirs(DEVICE_FOLDER, exist_ok=True)

    if not SMARTPHONE_DATA_RECEIVED:
        SMARTPHONE_DATA_RECEIVED = True
        print(f"\n[INFO] Koneksi diterima dari perangkat: {device_id}")

    # --- KONFIGURASI FILE DINAMIS PER HP ---
    OVERALL_CSV = os.path.join(DEVICE_FOLDER, f"dataset_{device_id}.csv")
    DETAIL_CSV = os.path.join(DEVICE_FOLDER, f"detail_{device_id}.csv")
    
    overall_exists = os.path.isfile(OVERALL_CSV)
    detail_exists = os.path.isfile(DETAIL_CSV)

    # --- PROSES DATA ---
    total_sec_all = data.get("total_screen_time_s", 0)
    usage_list = data.get("usage_data", [])

    now_dt = datetime.now()
    now = now_dt.isoformat()
    formatted_total = format_hms(total_sec_all)
    total_hours = total_sec_all / 3600

    # Hitung Fuzzy Logic
    result = fuzzy_logic.calculate_stress(
        total_hours,
        LAST_TEMPERATURE,
        LAST_HUMIDITY,
        LAST_AIRQUALITY
    )

    level = result["category"]
    message = result["message"]

    # --- SIMPAN DATA OVERALL KE FOLDER PERANGKAT ---
    with open(OVERALL_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not overall_exists:
            writer.writerow(["timestamp", "source", "temperature", "humidity", "air_quality", "total_usage_time", "fuzzy_level", "message"])
        
        writer.writerow([now, "android_summary", LAST_TEMPERATURE, LAST_HUMIDITY, LAST_AIRQUALITY, formatted_total, level, message])

    # --- SIMPAN DATA DETAIL KE FOLDER PERANGKAT ---
    if usage_list:
        with open(DETAIL_CSV, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not detail_exists:
                writer.writerow(["timestamp_received", "package_name", "app_name", "foreground_time_s"])
            
            for usage_item in usage_list:
                writer.writerow([
                    now,
                    usage_item.get("package", "N/A"),
                    usage_item.get("app_name", "N/A"),
                    usage_item.get("foreground_time_s", 0)
                ])

    print(f"\n[{now}] === Data Android ({device_id}) ===")
    print(f"Total Screen Time: {formatted_total} → Level: {level}")
    print(f"Suhu dipakai: {LAST_TEMPERATURE}°C, Humid: {LAST_HUMIDITY}%, AQ: {LAST_AIRQUALITY} ppm")
    print(f"FUZZY MESSAGE: {message}")

    return jsonify({
        "status": "ok",
        "source": "android",
        "device": device_id,
        "folder": DEVICE_FOLDER,
        "message": message,
        "level": level
    }), 200

@app.route('/receive_sensor', methods=['POST'])
def receive_sensor():
    global LAST_TEMPERATURE, LAST_HUMIDITY, LAST_AIRQUALITY, LAST_IOT_TIMESTAMP

    data = request.get_json(force=True)
    if not data:
        return jsonify({"status": "error", "message": "no json received"}), 400

    LAST_TEMPERATURE = data.get("temperature", LAST_TEMPERATURE)
    LAST_HUMIDITY = data.get("humidity", LAST_HUMIDITY)
    LAST_AIRQUALITY = data.get("air_quality", LAST_AIRQUALITY)
    LAST_IOT_TIMESTAMP = datetime.now()

    print(f"\n[{LAST_IOT_TIMESTAMP.isoformat()}] === Data IoT ===")
    print(f"Suhu: {LAST_TEMPERATURE} °C | Humid: {LAST_HUMIDITY}% | AQ: {LAST_AIRQUALITY} ppm")

    return jsonify({"status": "ok", "message": "Sensor data updated"}), 200

if __name__ == "__main__":
    print("Server Flask aktif di http://0.0.0.0:5000 ...")
    app.run(host="0.0.0.0", port=5000, debug=True)