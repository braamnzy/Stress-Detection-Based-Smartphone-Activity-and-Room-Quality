import requests
import time
import random
from datetime import datetime

# GANTI DENGAN URL NGROK/SERVER FLASK ANDA (Misal: http://1a2b3c4d.ngrok.io/receive_sensor)
SERVER_URL = "http://192.168.1.100:5000/receive_sensor" 
SIMULATION_INTERVAL = 900 # 📌 PERUBAHAN: Mengirim setiap 3 menit (180 detik)

def generate_sensor_data():
    """Menghasilkan data sensor simulasi."""
    data = {
        "temperature": round(random.uniform(25.0, 30.0), 2),
        "humidity": random.randint(50, 70),
        "air_quality": random.randint(30, 80)
    }
    return data

def send_data():
    sensor_data = generate_sensor_data()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Mengirim data simulasi: {sensor_data}")
    
    try:
        response = requests.post(SERVER_URL, json=sensor_data)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        
        print(f"Status Server: {response.status_code}")
        print(f"Respon Server: {response.json()}")
        
    except requests.exceptions.RequestException as e:
        print(f"Gagal koneksi ke server/Ngrok: {e}")

if __name__ == "__main__":
    print(f"Mock sensor aktif, mengirim data setiap {SIMULATION_INTERVAL} detik ke {SERVER_URL}")
    print("Pastikan Server Flask AKTIF dan data Smartphone sudah pernah masuk!")
    while True:
        send_data()
        time.sleep(SIMULATION_INTERVAL)