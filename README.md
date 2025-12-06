# 🤖 Sistem Deteksi Stress dengan Fuzzy berdasarkan Aktivitas Smartphone dan Rekayasa Ruangan

Proyek ini mengimplementasikan sistem untuk mendeteksi tingkat stres pengguna berdasarkan dua sumber data utama: **aktivitas penggunaan *smartphone*** dan **kondisi lingkungan ruangan** (*suhu, kelembaban, kualitas udara*). Deteksi stres dilakukan menggunakan **Logika Fuzzy Mamdani** yang mengombinasikan variabel-variabel tersebut untuk menghasilkan tingkat stres.

## 🌟 Fitur Utama

  * **Deteksi Stres Fuzzy:** Menggunakan *library* `scikit-fuzzy` di Python untuk sistem inferensi fuzzy yang menggabungkan 4 input (*Screen Time*, *Temperature*, *Humidity*, *Air Quality*).
  * **Integrasi Smartphone (Android):** Aplikasi Android secara periodik (*setiap 15 menit*) mengambil data total waktu penggunaan layar dan 10 aplikasi teratas, kemudian mengirimkannya ke *server*.
  * **Integrasi IoT/Lingkungan:** *Server* menerima data suhu, kelembaban, dan kualitas udara dari simulasi sensor (dapat diganti dengan perangkat IoT nyata).
  * **Notifikasi Real-time:** Pengguna Android menerima notifikasi langsung di perangkat mereka mengenai tingkat stres yang terdeteksi, lengkap dengan pesan saran.
  * **Pencatatan Data:** Semua data input dan output hasil perhitungan fuzzy disimpan ke dalam *file* CSV (`dataset_overall.csv`) untuk analisis lebih lanjut.
  * **Logika Proximity:** Data IoT yang masuk akan dicatat ke CSV jika berdekatan waktunya (*threshold* 5 menit) dengan data *smartphone*.

-----

## 🏗️ Arsitektur Sistem

Sistem ini terdiri dari tiga komponen utama:

1.  **Aplikasi Android (Klien):** Mengumpulkan data penggunaan layar dan mengirimkannya ke *Server*.
2.  **Server Flask (Backend):** Menerima data dari Android dan IoT, menjalankan Logika Fuzzy, dan menyimpan data.
3.  **Simulasi IoT (Generator Data):** Mensimulasikan data sensor lingkungan yang dikirim ke *Server*.

-----

## 🛠️ Persyaratan dan Persiapan

### 1\. Persyaratan Python (Server & Simulasi IoT)

Pastikan Anda telah menginstal Python (disarankan versi 3.x) dan *library* berikut:

```bash
pip install Flask scikit-fuzzy numpy requests
```

### 2\. Persyaratan Android (Klien)

  * **Android Studio**
  * Perangkat Android (fisik atau emulator) dengan **izin akses penggunaan** (`Usage Access`) diaktifkan untuk aplikasi.
  * Perangkat harus mengizinkan **pengabaian optimasi baterai** (`Ignore Battery Optimizations`) agar *Worker* dapat berjalan secara periodik.
  * Izin **Notifikasi** harus diberikan (jika menggunakan Android 13+).

### 3\. Konfigurasi Jaringan

Aplikasi Android dan Simulasi IoT harus dapat mengakses *Server* Flask.

1.  **Tentukan IP Lokal:** Temukan alamat IP lokal komputer yang menjalankan *Server* Flask (misalnya, `10.27.104.9`).
2.  **Konfigurasi Server URL:**
      * **Android:** Ubah `ServerConfig.BASE_URL` (dikelola melalui dialog di `MainActivity.kt`). Pastikan formatnya `http://<IP_ANDA>:5000`.
      * **Simulasi IoT (`room_generator.py`):** Ubah variabel `SERVER_URL` di baris atas.

-----

## ⚙️ Detail Komponen dan Cara Kerja

### 1\. `fuzzy_logic.py` (Inti Logika Fuzzy)

  * **Input (Antecedent):**
      * `screen` (Waktu Layar dalam jam, $\in [0, 12]$)
      * `temperature` (Suhu, $\in [10, 40]$ °C)
      * `humidity` (Kelembaban, $\in [0, 100]$ %)
      * `air_quality` (Kualitas Udara, $\in [0, 5]$ - diasumsikan skala PM2.5/semacamnya yang terbalik dengan kualitas)
  * **Output (Consequent):**
      * `stress` (Tingkat Stres, $\in [0, 100]$)
  * **Fungsi Keanggotaan (Membership Functions):** Menggunakan fungsi **Segitiga (`trimf`)** untuk semua variabel.
  * **Rule Base:** Total 81 aturan (3 `screen` $\times$ 3 `temp` $\times$ 3 `humid` $\times$ 3 `airq`).
      * **Contoh Rule:** `IF screen is rendah AND temp is nyaman AND humid is ideal AND airq is baik THEN stress is rendah`.
  * **Inference:** Mamdani.
  * **Defuzzifikasi:** Centroid.
  * **Fungsi `calculate_stress`:** Fungsi *wrapper* yang menerima 4 input, menjalankan inferensi fuzzy, dan mengembalikan nilai stres, kategori (`Rendah` \< 35, `Sedang` 35-65, `Tinggi` \> 65), dan pesan saran.

### 2\. `server.py` (Server Backend - Flask)

Server ini menangani dua *endpoint* utama:

#### A. `/receive_usage` (dari Android)

1.  Menerima total waktu layar (`total_screen_time_s`) dan detail penggunaan aplikasi.
2.  Menggunakan data lingkungan **terakhir** yang disimpan (`LAST_TEMPERATURE`, dll.) bersama dengan waktu layar sebagai input ke `fuzzy_logic.calculate_stress()`.
3.  Mengirim hasil kategori stres dan pesan kembali ke Android.
4.  Mencatat data ke `dataset_overall.csv` dengan sumber `android_summary`.
5.  **Pencatatan IoT Proximity:** Jika data IoT terakhir diterima dalam batas waktu **5 menit** (`TIME_PROXIMITY_THRESHOLD`) dari data *smartphone*, data IoT tersebut juga dicatat dengan sumber `iot_proximal` untuk memastikan sinkronisasi data lingkungan dengan hasil perhitungan stres.

#### B. `/receive_sensor` (dari IoT/Simulasi)

1.  Menerima data sensor (`temperature`, `humidity`, `air_quality`).
2.  Memperbarui variabel global (`LAST_TEMPERATURE`, dll.) untuk digunakan dalam perhitungan fuzzy berikutnya.
3.  **Tidak melakukan perhitungan fuzzy atau penyimpanan ke CSV** di *endpoint* ini, karena perhitungan dan penyimpanan dipicu oleh data *smartphone* untuk memastikan pasangan data yang lengkap.

### 3\. `MainActivity.kt` & `UsageDataWorker.kt` (Aplikasi Android)

  * **`MainActivity.kt`:**
      * Meminta izin krusial (*Usage Access*, *Notification*, *Ignore Battery Optimization*).
      * Memiliki fungsi untuk menjadwalkan `UsageDataWorker` secara periodik.
      * Menyediakan dialog untuk mengubah alamat IP Server (`btnChangeIp`).
  * **`UsageDataWorker.kt`:**
      * Dieksekusi setiap **15 menit** oleh WorkManager.
      * Mengumpulkan **Top 10** aplikasi yang paling banyak digunakan dan total waktu layar 24 jam terakhir.
      * Mengirim data ke *Server* Flask melalui *endpoint* `/receive_usage`.
      * Jika respons dari *server* berisi pesan (`message`), menampilkan notifikasi kepada pengguna.

### 4\. `room_generator.py` (Simulasi IoT)

  * Simulasi sederhana yang menghasilkan data sensor acak.
  * Mengirim data ke *endpoint* `/receive_sensor` setiap **15 menit** (`SIMULATION_INTERVAL = 900`).

-----

## 🚀 Cara Menjalankan Sistem

### Langkah 1: Jalankan Server Flask

Buka terminal di direktori proyek dan jalankan *server*:

```bash
python server.py
```

> Server akan berjalan di `http://0.0.0.0:5000`.

### Langkah 2: Jalankan Aplikasi Android

1.  Buka proyek di Android Studio, *Build* dan *Run* aplikasi di perangkat/emulator.
2.  Di aplikasi, berikan **Semua Izin** yang diminta (*Usage Access*, *Notification*, *Ignore Battery Optimization*).
3.  Pastikan untuk **Mengubah IP Server** di aplikasi Android (`btnChangeIp`) sesuai dengan IP lokal Anda.
4.  Klik tombol **Get Usage & Schedule Monitoring** untuk menguji pengambilan data awal dan menjadwalkan *worker*.

### Langkah 3: Jalankan Simulasi Sensor IoT

Buka terminal **kedua** (sambil *Server* Flask tetap berjalan) dan jalankan simulasi sensor:

```bash
python room_generator.py
```

> Simulasi akan mengirim data sensor setiap 15 menit.

### Pemantauan

Lihat *output* konsol dari `server.py`. Setiap kali `UsageDataWorker` dari Android berjalan, Anda akan melihat log perhitungan fuzzy dan pesan stres yang terdeteksi. Data akan disimpan dalam `dataset_overall.csv`.

-----

## 📊 Output Data

Hasil perhitungan dan data input akan tersimpan di `dataset_overall.csv` dengan kolom:

| Kolom | Sumber Data | Deskripsi |
| :--- | :--- | :--- |
| `timestamp` | All | Waktu data dicatat. |
| `source` | All | `android_summary` atau `iot_proximal`. |
| `temperature` | All | Suhu (°C). |
| `humidity` | All | Kelembaban (%). |
| `air_quality` | All | Kualitas Udara (%). |
| `app_count` | Android | Jumlah aplikasi teratas yang dihitung. |
| `total_usage_time` | Android | Total waktu layar dalam format H:M:S. |
| `fuzzy_level` | Android | Kategori stres hasil Fuzzy (`Rendah`, `Sedang`, `Tinggi`). |
| `message` | Android | Pesan saran yang dikirim ke notifikasi. |
| `usage_details` | Android | Detail penggunaan aplikasi (*JSON string*). |
