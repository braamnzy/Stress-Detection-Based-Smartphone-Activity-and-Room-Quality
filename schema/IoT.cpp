#include <WiFi.h>    
#include <HTTPClient.h> 
#include <WiFiClient.h>
#include <DHT.h>

// --- KONFIGURASI WIFI ---
const char* ssid = "NAMA_WIFI_ANDA";
const char* password = "PASSWORD_WIFI_ANDA";

// --- KONFIGURASI SERVER ---
String serverURL = "http://192.168.1.105:5000/receive_sensor";

// --- KONFIGURASI SENSOR ---
#define DHTPIN D2          // Pin data sensor DHT ke D2 (GPIO4)
#define DHTTYPE DHT11      // Tipe sensor DHT11 atau DHT22
#define MQ135_PIN A0       // Pin analog MQ-135 ke A0

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  dht.begin();

  // Koneksi WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected!");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;

    // 1. Baca data dari sensor fisik
    float h = dht.readHumidity();
    float t = dht.readTemperature();
    int airRaw = analogRead(MQ135_PIN);
    
    // Konversi sederhana MQ-135 ke skala 0-5 PPM (sesuai universe fuzzy)
    float airQuality = (airRaw / 1024.0) * 5.0; 

    // Cek jika pembacaan gagal
    if (isnan(h) || isnan(t)) {
      Serial.println("Gagal baca sensor DHT!");
      return;
    }

    // 2. Bungkus data ke dalam JSON String
    String jsonPayload = "{";
    jsonPayload += "\"temperature\":" + String(t) + ",";
    jsonPayload += "\"humidity\":" + String(h) + ",";
    jsonPayload += "\"air_quality\":" + String(airQuality);
    jsonPayload += "}";

    // 3. Kirim HTTP POST ke Server Flask
    http.begin(client, serverURL);
    http.addHeader("Content-Type", "application/json");

    int httpResponseCode = http.POST(jsonPayload);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("HTTP Response code: " + String(httpResponseCode));
      Serial.println("Server Reply: " + response);
    } else {
      Serial.print("Error code: ");
      Serial.println(httpResponseCode);
    }

    http.end();
  }

  // Jeda pengiriman data sensor (misal: setiap 2 menit)
  delay(120000); 
}