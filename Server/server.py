from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import csv
import os
import fuzzy_logic
import json

app = Flask(__name__)

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


CSV_OVERALL = "dataset_overall.csv"

if not os.path.exists(CSV_OVERALL):
    with open(CSV_OVERALL, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp", "source",
            "temperature", "humidity", "air_quality",
            "app_count", "total_usage_time", "fuzzy_level", "message",
            "usage_details"
        ])


# =======================
# ENDPOINT: ANDROID
# =======================
@app.route('/receive_usage', methods=['POST'])
def receive_usage():
    global LAST_TEMPERATURE, LAST_HUMIDITY, LAST_AIRQUALITY, SMARTPHONE_DATA_RECEIVED, LAST_IOT_TIMESTAMP

    data = request.get_json(force=True)
    if not data:
        return jsonify({"status": "error", "message": "no json received"}), 400

    if not SMARTPHONE_DATA_RECEIVED:
        SMARTPHONE_DATA_RECEIVED = True
        print("\n[INFO] Data Smartphone Pertama Diterima. Data IoT Sekarang Diizinkan Tampil dan Disimpan.")

    total_sec_all = data.get("total_screen_time_s", 0)
    usage_list = data.get("usage_data", [])

    now_dt = datetime.now()
    now = now_dt.isoformat()
    formatted_total = format_hms(total_sec_all)
    total_hours = total_sec_all / 3600

    # ==== FUZZY LOGIC ====
    result = fuzzy_logic.calculate_stress(
        total_hours,
        LAST_TEMPERATURE,
        LAST_HUMIDITY,
        LAST_AIRQUALITY
    )

    level = result["category"]
    message = result["message"]

    print(f"\n[{now}] === Android Usage Data ===")
    print(f"Total Screen Time: {formatted_total} → Level: {level}")
    print(f"Suhu dipakai: {LAST_TEMPERATURE}°C, Humid: {LAST_HUMIDITY}%, AQ: {LAST_AIRQUALITY}%")
    print(f"Jumlah Aplikasi: {len(usage_list)}")
    print(f"FUZZY MESSAGE: {message}")

    # Simpan usage_details apa adanya (tanpa package_map)
    try:
        usage_details_json_string = json.dumps(usage_list)
    except Exception as e:
        usage_details_json_string = f"Error serializing usage: {e}"

    # Tulis ke CSV
    with open(CSV_OVERALL, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow([
            now, "android_summary",
            LAST_TEMPERATURE, LAST_HUMIDITY, LAST_AIRQUALITY,
            len(usage_list), formatted_total, level, message,
            usage_details_json_string
        ])

        # PROXIMITY CHECK IOT
        time_difference = now_dt - LAST_IOT_TIMESTAMP

        if timedelta(seconds=0) <= time_difference <= TIME_PROXIMITY_THRESHOLD:
            iot_message = f"IoT data (T:{LAST_TEMPERATURE}) saved due to proximity rule."

            writer.writerow([
                LAST_IOT_TIMESTAMP.isoformat(), "iot_proximal",
                LAST_TEMPERATURE, LAST_HUMIDITY, LAST_AIRQUALITY,
                "", "", "", iot_message,
                ""
            ])
            print(f"[INFO] PROXIMITY LOGGED: Data IoT ({LAST_IOT_TIMESTAMP.strftime('%H:%M:%S')}) disimpan ke CSV.")
        else:
            print(f"[INFO] PROXIMITY CHECK: Data IoT terakhir ({LAST_IOT_TIMESTAMP.strftime('%H:%M:%S')}) terlalu jauh. Tidak disimpan.")

    return jsonify({
        "status": "ok",
        "source": "android",
        "message": message,
    }), 200


# =======================
# ENDPOINT: IoT
# =======================
@app.route('/receive_sensor', methods=['POST'])
def receive_sensor():
    global LAST_TEMPERATURE, LAST_HUMIDITY, LAST_AIRQUALITY, LAST_IOT_TIMESTAMP

    data = request.get_json(force=True)
    if not data:
        return jsonify({"status": "error", "message": "no json received"}), 400

    suhu = data.get("temperature")
    kelembapan = data.get("humidity")
    kualitas_udara = data.get("air_quality")

    LAST_TEMPERATURE = suhu
    LAST_HUMIDITY = kelembapan
    LAST_AIRQUALITY = kualitas_udara
    LAST_IOT_TIMESTAMP = datetime.now()

    now = datetime.now().isoformat()

    print(f"\n[{now}] === IoT Sensor Data ===")
    print(f"Suhu: {suhu} °C | Humid: {kelembapan}% | AQ: {kualitas_udara}%")

    return jsonify({
        "status": "ok",
        "source": "iot",
        "message": "Sensor data received.",
        "temperature": suhu,
        "humidity": kelembapan,
        "air_quality": kualitas_udara
    }), 200


# RUN SERVER
if __name__ == "__main__":
    print("Server Flask aktif di http://0.0.0.0:5000 ...")
    app.run(host="0.0.0.0", port=5000, debug=True)
