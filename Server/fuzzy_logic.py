import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


screen_universe = np.arange(0, 12, 1) # 0 hingga 12 jam
temp_universe = np.arange(0, 46, 1)  # 10 hingga 45 °C
stress_universe = np.arange(0, 101, 1) # 0 hingga 100
humid_universe = np.arange(0, 101, 1) # 0 hingga 100 %
aq_universe = np.arange(0, 5.1, 0.1)    # 0 hingga 5.0 ppm

screen = ctrl.Antecedent(screen_universe, "screen") 
temp = ctrl.Antecedent(temp_universe, "temperature")
humid = ctrl.Antecedent(humid_universe, "humidity")
airq = ctrl.Antecedent(aq_universe, "air_quality")

stress = ctrl.Consequent(stress_universe, "stress", defuzzify_method='centroid')

screen['rendah'] = fuzz.trimf(screen_universe, [0, 0, 4])
screen['sedang'] = fuzz.trimf(screen_universe, [3, 5.5, 8])
screen['tinggi'] = fuzz.trimf(screen_universe, [7, 12, 12.1]) 

temp['dingin'] = fuzz.trimf(temp_universe, [0, 8, 16])
temp['nyaman'] = fuzz.trimf(temp_universe, [16, 23, 30])
temp['panas'] = fuzz.trimf(temp_universe, [30, 46, 46.1])

stress['rendah'] = fuzz.trimf(stress_universe, [0, 20, 40])
stress['sedang'] = fuzz.trimf(stress_universe, [30, 50, 70])
stress['tinggi'] = fuzz.trimf(stress_universe, [60, 80, 100])

humid['kering'] = fuzz.trimf(humid_universe, [0, 0, 40])
humid['ideal'] = fuzz.trimf(humid_universe, [30, 55, 70]) 
humid['lembab'] = fuzz.trimf(humid_universe, [60, 100, 100.1])

airq['baik'] = fuzz.trimf(aq_universe, [0, 0, 0.25])     
airq['sedang'] = fuzz.trimf(aq_universe, [0.2, 0.4, 0.65]) 
airq['buruk'] = fuzz.trimf(aq_universe, [0.6, 5.0, 5.1])

# ====================================
# RULE BASE
# ====================================
rules = [
    # =========================================================================
    # Kategori 1: SCREEN RENDAH (0-4 jam)
    # =========================================================================

    # ------------------ HUMID KERING -------------------
    ctrl.Rule(screen['rendah'] & temp['dingin'] & humid['kering'] & airq['buruk'], stress['tinggi']),
    ctrl.Rule(screen['rendah'] & temp['dingin'] & humid['kering'] & airq['sedang'], stress['sedang']),
    ctrl.Rule(screen['rendah'] & temp['dingin'] & humid['kering'] & airq['baik'], stress['sedang']),

    ctrl.Rule(screen['rendah'] & temp['nyaman'] & humid['kering'] & airq['buruk'], stress['tinggi']),
    ctrl.Rule(screen['rendah'] & temp['nyaman'] & humid['kering'] & airq['sedang'], stress['sedang']),
    ctrl.Rule(screen['rendah'] & temp['nyaman'] & humid['kering'] & airq['baik'], stress['sedang']),

    ctrl.Rule(screen['rendah'] & temp['panas'] & humid['kering'] & airq['buruk'], stress['tinggi']),
    ctrl.Rule(screen['rendah'] & temp['panas'] & humid['kering'] & airq['sedang'], stress['sedang']),
    ctrl.Rule(screen['rendah'] & temp['panas'] & humid['kering'] & airq['baik'], stress['sedang']),
    
    # ------------------ HUMID IDEAL ----------------------------------------------
    ctrl.Rule(screen['rendah'] & temp['dingin'] & humid['ideal'] & airq['buruk'], stress['tinggi']),
    ctrl.Rule(screen['rendah'] & temp['dingin'] & humid['ideal'] & airq['sedang'], stress['rendah']),
    ctrl.Rule(screen['rendah'] & temp['dingin'] & humid['ideal'] & airq['baik'], stress['rendah']),

    ctrl.Rule(screen['rendah'] & temp['nyaman'] & humid['ideal'] & airq['buruk'], stress['tinggi']),
    ctrl.Rule(screen['rendah'] & temp['nyaman'] & humid['ideal'] & airq['sedang'], stress['rendah']),
    ctrl.Rule(screen['rendah'] & temp['nyaman'] & humid['ideal'] & airq['baik'], stress['rendah']),

    ctrl.Rule(screen['rendah'] & temp['panas'] & humid['ideal'] & airq['buruk'], stress['tinggi']),
    ctrl.Rule(screen['rendah'] & temp['panas'] & humid['ideal'] & airq['sedang'], stress['sedang']),
    ctrl.Rule(screen['rendah'] & temp['panas'] & humid['ideal'] & airq['baik'], stress['sedang']),
    
    # ------------------ HUMID LEMBAB -------------------
    ctrl.Rule(screen['rendah'] & temp['dingin'] & humid['lembab'] & airq['buruk'], stress['tinggi']),
    ctrl.Rule(screen['rendah'] & temp['dingin'] & humid['lembab'] & airq['sedang'], stress['sedang']),
    ctrl.Rule(screen['rendah'] & temp['dingin'] & humid['lembab'] & airq['baik'], stress['sedang']),

    ctrl.Rule(screen['rendah'] & temp['nyaman'] & humid['lembab'] & airq['buruk'], stress['tinggi']),
    ctrl.Rule(screen['rendah'] & temp['nyaman'] & humid['lembab'] & airq['sedang'], stress['sedang']),
    ctrl.Rule(screen['rendah'] & temp['nyaman'] & humid['lembab'] & airq['baik'], stress['sedang']),

    ctrl.Rule(screen['rendah'] & temp['panas'] & humid['lembab'] & airq['buruk'], stress['tinggi']),
    ctrl.Rule(screen['rendah'] & temp['panas'] & humid['lembab'] & airq['sedang'], stress['sedang']),
    ctrl.Rule(screen['rendah'] & temp['panas'] & humid['lembab'] & airq['baik'], stress['sedang']),


    # =========================================================================
    # Kategori 2: SCREEN SEDANG (3-8 jam)
    # =========================================================================

    # ------------------ HUMID KERING -------------------
    ctrl.Rule(screen['sedang'] & temp['dingin'] & humid['kering'] & airq['buruk'], stress['tinggi']),
    ctrl.Rule(screen['sedang'] & temp['dingin'] & humid['kering'] & airq['sedang'], stress['tinggi']),
    ctrl.Rule(screen['sedang'] & temp['dingin'] & humid['kering'] & airq['baik'], stress['tinggi']),

    ctrl.Rule(screen['sedang'] & temp['nyaman'] & humid['kering'] & airq['buruk'], stress['tinggi']),
    ctrl.Rule(screen['sedang'] & temp['nyaman'] & humid['kering'] & airq['sedang'], stress['tinggi']),
    ctrl.Rule(screen['sedang'] & temp['nyaman'] & humid['kering'] & airq['baik'], stress['tinggi']),

    ctrl.Rule(screen['sedang'] & temp['panas'] & humid['kering'] & airq['buruk'], stress['tinggi']),
    ctrl.Rule(screen['sedang'] & temp['panas'] & humid['kering'] & airq['sedang'], stress['tinggi']),
    ctrl.Rule(screen['sedang'] & temp['panas'] & humid['kering'] & airq['baik'], stress['tinggi']),
    
    # ------------------ HUMID IDEAL ----------------------------------------------
    ctrl.Rule(screen['sedang'] & temp['dingin'] & humid['ideal'] & airq['buruk'], stress['tinggi']),
    ctrl.Rule(screen['sedang'] & temp['dingin'] & humid['ideal'] & airq['sedang'], stress['tinggi']),
    ctrl.Rule(screen['sedang'] & temp['dingin'] & humid['ideal'] & airq['baik'], stress['sedang']),

    ctrl.Rule(screen['sedang'] & temp['nyaman'] & humid['ideal'] & airq['buruk'], stress['tinggi']),
    ctrl.Rule(screen['sedang'] & temp['nyaman'] & humid['ideal'] & airq['sedang'], stress['tinggi']),
    ctrl.Rule(screen['sedang'] & temp['nyaman'] & humid['ideal'] & airq['baik'], stress['sedang']),

    ctrl.Rule(screen['sedang'] & temp['panas'] & humid['ideal'] & airq['buruk'], stress['tinggi']),
    ctrl.Rule(screen['sedang'] & temp['panas'] & humid['ideal'] & airq['sedang'], stress['tinggi']),
    ctrl.Rule(screen['sedang'] & temp['panas'] & humid['ideal'] & airq['baik'], stress['tinggi']),
    
    # ------------------ HUMID LEMBAB -------------------
    ctrl.Rule(screen['sedang'] & temp['dingin'] & humid['lembab'] & airq['buruk'], stress['tinggi']),
    ctrl.Rule(screen['sedang'] & temp['dingin'] & humid['lembab'] & airq['sedang'], stress['tinggi']),
    ctrl.Rule(screen['sedang'] & temp['dingin'] & humid['lembab'] & airq['baik'], stress['tinggi']),

    ctrl.Rule(screen['sedang'] & temp['nyaman'] & humid['lembab'] & airq['buruk'], stress['tinggi']),
    ctrl.Rule(screen['sedang'] & temp['nyaman'] & humid['lembab'] & airq['sedang'], stress['tinggi']),
    ctrl.Rule(screen['sedang'] & temp['nyaman'] & humid['lembab'] & airq['baik'], stress['tinggi']),

    ctrl.Rule(screen['sedang'] & temp['panas'] & humid['lembab'] & airq['buruk'], stress['tinggi']),
    ctrl.Rule(screen['sedang'] & temp['panas'] & humid['lembab'] & airq['sedang'], stress['tinggi']),
    ctrl.Rule(screen['sedang'] & temp['panas'] & humid['lembab'] & airq['baik'], stress['tinggi']),


    # =========================================================================
    # Kategori 3: SCREEN TINGGI (7-12 jam)
    # =========================================================================

    # ------------------ HUMID KERING --------------------------------------------
    ctrl.Rule(screen['tinggi'] & temp['dingin'] & humid['kering'] & airq['buruk'], stress['tinggi']),
    ctrl.Rule(screen['tinggi'] & temp['dingin'] & humid['kering'] & airq['sedang'], stress['tinggi']),
    ctrl.Rule(screen['tinggi'] & temp['dingin'] & humid['kering'] & airq['baik'], stress['tinggi']),

    ctrl.Rule(screen['tinggi'] & temp['nyaman'] & humid['kering'] & airq['buruk'], stress['tinggi']),
    ctrl.Rule(screen['tinggi'] & temp['nyaman'] & humid['kering'] & airq['sedang'], stress['tinggi']),
    ctrl.Rule(screen['tinggi'] & temp['nyaman'] & humid['kering'] & airq['baik'], stress['tinggi']),

    ctrl.Rule(screen['tinggi'] & temp['panas'] & humid['kering'] & airq['buruk'], stress['tinggi']),
    ctrl.Rule(screen['tinggi'] & temp['panas'] & humid['kering'] & airq['sedang'], stress['tinggi']),
    ctrl.Rule(screen['tinggi'] & temp['panas'] & humid['kering'] & airq['baik'], stress['tinggi']),
    
    # ------------------ HUMID IDEAL ----------------------------------------------
    ctrl.Rule(screen['tinggi'] & temp['dingin'] & humid['ideal'] & airq['buruk'], stress['tinggi']),
    ctrl.Rule(screen['tinggi'] & temp['dingin'] & humid['ideal'] & airq['sedang'], stress['tinggi']),
    ctrl.Rule(screen['tinggi'] & temp['dingin'] & humid['ideal'] & airq['baik'], stress['tinggi']),

    ctrl.Rule(screen['tinggi'] & temp['nyaman'] & humid['ideal'] & airq['buruk'], stress['tinggi']),
    ctrl.Rule(screen['tinggi'] & temp['nyaman'] & humid['ideal'] & airq['sedang'], stress['tinggi']),
    ctrl.Rule(screen['tinggi'] & temp['nyaman'] & humid['ideal'] & airq['baik'], stress['tinggi']),

    ctrl.Rule(screen['tinggi'] & temp['panas'] & humid['ideal'] & airq['buruk'], stress['tinggi']),
    ctrl.Rule(screen['tinggi'] & temp['panas'] & humid['ideal'] & airq['sedang'], stress['tinggi']),
    ctrl.Rule(screen['tinggi'] & temp['panas'] & humid['ideal'] & airq['baik'], stress['tinggi']),
    
    # ------------------ HUMID LEMBAB --------------------------------------------
    ctrl.Rule(screen['tinggi'] & temp['dingin'] & humid['lembab'] & airq['buruk'], stress['tinggi']),
    ctrl.Rule(screen['tinggi'] & temp['dingin'] & humid['lembab'] & airq['sedang'], stress['tinggi']),
    ctrl.Rule(screen['tinggi'] & temp['dingin'] & humid['lembab'] & airq['baik'], stress['tinggi']),

    ctrl.Rule(screen['tinggi'] & temp['nyaman'] & humid['lembab'] & airq['buruk'], stress['tinggi']),
    ctrl.Rule(screen['tinggi'] & temp['nyaman'] & humid['lembab'] & airq['sedang'], stress['tinggi']),
    ctrl.Rule(screen['tinggi'] & temp['nyaman'] & humid['lembab'] & airq['baik'], stress['tinggi']),

    ctrl.Rule(screen['tinggi'] & temp['panas'] & humid['lembab'] & airq['buruk'], stress['tinggi']),
    ctrl.Rule(screen['tinggi'] & temp['panas'] & humid['lembab'] & airq['sedang'], stress['tinggi']),
    ctrl.Rule(screen['tinggi'] & temp['panas'] & humid['lembab'] & airq['baik'], stress['tinggi']),
]

# Rule Base
stress_ctrl = ctrl.ControlSystem(rules)
stress_sim = ctrl.ControlSystemSimulation(stress_ctrl)

# ====================================
# WRAPPER FUNCTION - IMPROVED ERROR HANDLING
# ====================================

def calculate_stress(screentime, temperature, humidity, air_quality):
    """
    Menghitung tingkat stress dengan fuzzy logic
    
    Parameters:
    - screentime: jam penggunaan layar (0-12)
    - temperature: suhu dalam Celsius (10-40)
    - humidity: kelembaban dalam % (0-100)
    - air_quality: kualitas udara (0-100, semakin tinggi semakin baik)
    
    Returns:
    - dict dengan stress_value, category, dan message
    """
    
    # Validasi dan normalisasi input
    screentime = float(max(0, min(screentime, 12)))
    temperature = float(max(10, min(temperature, 40)))
    humidity = float(max(0, min(humidity, 100)))
    air_quality = float(max(0, min(air_quality, 100)))
    
    # Debug log
    print(f"[FUZZY] Input - Screen: {screentime}h, Temp: {temperature}°C, Humid: {humidity}%, AQ: {air_quality}")
    
    try:
        # Reset simulation untuk menghindari state lama
        stress_sim.input['screen'] = screentime
        stress_sim.input['temperature'] = temperature
        stress_sim.input['humidity'] = humidity
        stress_sim.input['air_quality'] = air_quality

        # Komputasi fuzzy
        stress_sim.compute()
        
        # Cek apakah output berhasil dihitung
        if 'stress' not in stress_sim.output:
            raise KeyError("Output 'stress' tidak ditemukan setelah komputasi")
            
        value = float(stress_sim.output['stress'])
        print(f"[FUZZY] Output - Stress Value: {value}")
        
    except KeyError as e:
        print(f"[FUZZY ERROR] KeyError: {e}")
        print(f"[FUZZY ERROR] Available outputs: {stress_sim.output.keys() if hasattr(stress_sim, 'output') else 'None'}")
        print("[FUZZY ERROR] Menggunakan nilai default 50")
        value = 50.0
        
    except ValueError as e:
        print(f"[FUZZY ERROR] ValueError: {e}")
        print("[FUZZY ERROR] Kemungkinan tidak ada rule yang ter-trigger atau input di luar jangkauan")
        print("[FUZZY ERROR] Menggunakan nilai default 50")
        value = 50.0
        
    except Exception as e:
        print(f"[FUZZY ERROR] Unexpected error: {type(e).__name__}: {e}")
        print("[FUZZY ERROR] Menggunakan nilai default 50")
        value = 50.0

    # Kategorisasi
    if value < 35:
        category = "Rendah"
        message = "Kondisi kamu aman dan rileks 👍"
    elif value < 65:
        category = "Sedang"
        message = "Mulai perhatikan kondisi tubuh dan waktu layar 😊"
    else:
        category = "Tinggi"
        message = "Tingkat stres tinggi! Kurangi layar dan istirahat 😣"

    return {
        "stress_value": float(value),
        "category": category,
        "message": message
    }

# ====================================
# TESTING
# ====================================

if __name__ == '__main__':
    print("="*60)
    print("TESTING FUZZY LOGIC SYSTEM")
    print("="*60)
    
    # 1 — Kondisi paling stres (screen tinggi, panas, lembab, AQ bahaya)
    print("\n[TEST 1] Screen Tinggi + Panas + Lembab + AQ Bahaya (>0.6)")
    result1 = calculate_stress(10, 35, 85, 1.0)   # AQ = 1 ppm (bahaya)
    print(f"Result: {result1}\n")
    
    # 2 — Screen rendah tapi AQ bahaya
    print("[TEST 2] Screen Rendah + AQ Bahaya")
    result2 = calculate_stress(2, 25, 50, 0.8)
    print(f"Result: {result2}\n")
    
    # 3 — Screen rendah + humid lembab
    print("[TEST 3] Humid Sangat Lembab")
    result3 = calculate_stress(2, 25, 95, 0.1)    # AQ bagus
    print(f"Result: {result3}\n")
    
    # 4 — Kondisi optimal
    print("[TEST 4] Optimal (screen sedang, suhu nyaman, humid ideal, AQ rendah)")
    result4 = calculate_stress(3, 24, 50, 0.1)
    print(f"Result: {result4}\n")
    
    # 5 — Input minimum
    print("[TEST 5] Minimum Input")
    result5 = calculate_stress(0, 10, 0, 0.0)
    print(f"Result: {result5}\n")
    
    # 6 — Input maximum
    print("[TEST 6] Maximum Input")
    result6 = calculate_stress(12, 40, 100, 5.0)  # 5 ppm = sangat bahaya
    print(f"Result: {result6}\n")
    
    # 7 — Suhu dingin + AQ sedang
    print("[TEST 7] Suhu Dingin + AQ Sedang")
    result7 = calculate_stress(1, 15, 40, 0.4)
    print(f"Result: {result7}\n")
    
    # 8 — Suhu panas + AQ sedang
    print("[TEST 8] Suhu Panas + AQ Sedang")
    result8 = calculate_stress(5, 38, 50, 0.5)
    print(f"Result: {result8}\n")
    
    print("="*60)
    print("TESTING SELESAI")
    print("="*60)