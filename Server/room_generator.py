import requests
import time
import random
import math
from datetime import datetime

SERVER_URL = "http://192.168.1.50:5000/receive_sensor" 
SIMULATION_INTERVAL = 180  

class RealisticSensor:
    def __init__(self):
        
        self.temperature = 23.0  
        self.humidity = 65.0     
        self.air_quality = 0.4   
        
        
        self.temp_base = 23.5     
        self.temp_amplitude = 3.5  
        self.hum_base = 65.0       
        self.hum_amplitude = 10.0  
        
    def get_time_factor(self):  
        
        now = datetime.now()
        hour = now.hour + now.minute / 60.0
        
        time_factor = math.sin(2 * math.pi * (hour - 6) / 24)
        return time_factor, hour
    
    def get_activity_level(self, hour):
        
        if 6 <= hour < 9:      
            return 2.0
        elif 9 <= hour < 17:   
            return 0.3
        elif 17 <= hour < 23:  
            return 2.5
        else:                  
            return 0.5
    
    def update_temperature(self):
        
        time_factor, _ = self.get_time_factor()
        
        target_temp = self.temp_base + (self.temp_amplitude * time_factor)
        
        change = (target_temp - self.temperature) * 0.15  
        
        noise = random.uniform(-0.2, 0.2)
      
        self.temperature += change + noise
        self.temperature = round(self.temperature, 2)
        
    def update_humidity(self):
        
        time_factor, _ = self.get_time_factor()
    
        target_hum = self.hum_base - (self.hum_amplitude * time_factor)
        
        change = (target_hum - self.humidity) * 0.1
        noise = random.uniform(-0.5, 0.5)
        
        self.humidity += change + noise
        self.humidity = round(max(30, min(85, self.humidity)), 1)  
        
    def update_air_quality(self):

        _, hour = self.get_time_factor()

        activity = self.get_activity_level(hour)

        base_aq = 0.25
        activity_effect = activity * 0.12  
        target_aq = base_aq + activity_effect
        change = (target_aq - self.air_quality) * 0.15

        
        if random.random() < 0.03:
            spike = random.uniform(0.05, 0.12)
        else:
            spike = 0.0

        noise = random.uniform(-0.01, 0.01)
        self.air_quality += change + spike + noise

        self.air_quality = round(max(0.0, min(1.0, self.air_quality)), 2)


    def get_sensor_data(self):

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