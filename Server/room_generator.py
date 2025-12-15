import requests
import time
import random
import math
from datetime import datetime

SERVER_URL = "http://192.168.1.50:5000/receive_sensor" 
SIMULATION_INTERVAL = 180  # 3 menit

class RealisticSensor:
    def __init__(self):
        # State awal sensor (nilai terakhir)
        self.temperature = 23.0  # Suhu awal pagi hari
        self.humidity = 65.0     # Kelembaban awal
        self.air_quality = 0.4   # AQ awal (good)
        
        # Parameter pola harian
        self.temp_base = 23.5      # Suhu rata-rata
        self.temp_amplitude = 3.5  # Variasi harian (pagi-siang)
        self.hum_base = 65.0       # Kelembaban rata-rata
        self.hum_amplitude = 10.0  # Variasi harian
        
    def get_time_factor(self):  
        """Menghitung faktor waktu untuk pola sinusoidal harian"""
        now = datetime.now()
        hour = now.hour + now.minute / 60.0
        
        # Sinusoidal pattern: puncak di jam 14:00 (siang)
        # Terendah di jam 02:00 (dini hari)
        time_factor = math.sin(2 * math.pi * (hour - 6) / 24)
        return time_factor, hour
    
    def get_activity_level(self, hour):
        """Menghitung level aktivitas berdasarkan jam (untuk AQ)"""
        # Aktivitas tinggi = AQ naik (CO2, PM2.5 dari manusia/aktivitas)
        if 6 <= hour < 9:      # Pagi: bangun, mandi, sarapan
            return 2.0
        elif 9 <= hour < 17:   # Siang: ruangan kosong (kerja/sekolah)
            return 0.3
        elif 17 <= hour < 23:  # Sore-malam: pulang, masak, kumpul
            return 2.5
        else:                  # Malam: tidur
            return 0.5
    
    def update_temperature(self):
        """Update suhu dengan pola diurnal + noise + inertia"""
        time_factor, _ = self.get_time_factor()
        
        # Target suhu berdasarkan waktu
        target_temp = self.temp_base + (self.temp_amplitude * time_factor)
        
        # Perubahan gradual menuju target (inertia)
        change = (target_temp - self.temperature) * 0.15  # 15% dari selisih
        
        # Tambahkan noise kecil (fluktuasi natural)
        noise = random.uniform(-0.2, 0.2)
        
        # Update nilai
        self.temperature += change + noise
        self.temperature = round(self.temperature, 2)
        
    def update_humidity(self):
        """Update kelembaban dengan pola inverse terhadap suhu"""
        time_factor, _ = self.get_time_factor()
        
        # Kelembaban berbanding terbalik dengan suhu
        # Pagi (suhu rendah) = kelembaban tinggi
        # Siang (suhu tinggi) = kelembaban rendah
        target_hum = self.hum_base - (self.hum_amplitude * time_factor)
        
        # Perubahan gradual
        change = (target_hum - self.humidity) * 0.1
        noise = random.uniform(-0.5, 0.5)
        
        self.humidity += change + noise
        self.humidity = round(max(30, min(85, self.humidity)), 1)  # Batas 30-85%
        
    def update_air_quality(self):

        _, hour = self.get_time_factor()

        activity = self.get_activity_level(hour)

        base_aq = 0.25

        # Kontribusi aktivitas manusia (terbatas & realistis)
        activity_effect = activity * 0.12   # max ≈ 0.30

        # Target AQ (tidak pernah > 0.65 tanpa event)
        target_aq = base_aq + activity_effect

        # Inertia (perubahan gradual)
        change = (target_aq - self.air_quality) * 0.15

        # Event spike kecil (mis. masak, asap sesaat)
        if random.random() < 0.03:
            spike = random.uniform(0.05, 0.12)
        else:
            spike = 0.0

        # Noise sensor
        noise = random.uniform(-0.01, 0.01)

        self.air_quality += change + spike + noise

        # Hard limit sensor nyata
        self.air_quality = round(max(0.0, min(1.0, self.air_quality)), 2)


    def get_sensor_data(self):
        """Update semua sensor dan return data"""
        self.update_temperature()
        self.update_humidity()
        self.update_air_quality()
        
        return {
            "temperature": self.temperature,
            "humidity": self.humidity,
            "air_quality": self.air_quality
        }

def send_data(sensor):
    sensor_data = sensor.get_sensor_data()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"\n[{timestamp}] Mengirim data:")
    print(f"  🌡️  Suhu: {sensor_data['temperature']}°C")
    print(f"  💧 Kelembaban: {sensor_data['humidity']}%")
    print(f"  🌫️  Air Quality: {sensor_data['air_quality']}")
    
    try:
        response = requests.post(SERVER_URL, json=sensor_data, timeout=5)
        response.raise_for_status()
        
        print(f"  ✅ Status: {response.status_code}")
        
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Gagal koneksi: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🔬 REALISTIC IoT SENSOR SIMULATOR v2")
    print("=" * 60)
    print(f"📡 Target: {SERVER_URL}")
    print(f"⏱️  Interval: {SIMULATION_INTERVAL} detik")
    print(f"📊 Model:")
    print(f"   • Suhu: Diurnal pattern (puncak siang)")
    print(f"   • Kelembaban: Inverse suhu (tinggi pagi)")
    print(f"   • Air Quality: Activity-based (tinggi pagi/sore)")
    print("=" * 60)
    
    sensor = RealisticSensor()
    
    print("\n⚠️  Pastikan Flask server AKTIF!")
    print("🚀 Memulai simulasi...\n")
    
    while True:
        send_data(sensor)
        time.sleep(SIMULATION_INTERVAL)