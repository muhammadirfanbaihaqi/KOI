from machine import Pin, PWM, RTC
import onewire, ds18x20
import network
import ntptime
from time import sleep, sleep_ms
import time
import urequests
import dht


# ======= KONFIGURASI WIFI DAN SERVER ======= #
SSID = "Gaji Guru Honorer"
PASSWORD = "kecilsemua"
API_SENSOR_URL = "http://192.168.1.5:5000/sensor"       # Ganti sesuai IP Flask
API_JADWAL_URL = "http://192.168.1.5:5000/jadwal_pakan" # Endpoint jadwal pakan

# Sensor suhu
sensor = dht.DHT11(Pin(5))

def get_current_time():
    """Mengembalikan timestamp dalam format YYYY-MM-DD HH:MM"""
    tm = time.localtime()  # Dapatkan waktu lokal ESP32
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}".format(tm[0], tm[1], tm[2], tm[3], tm[4])

def konek_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("📡 Menghubungkan WiFi...")
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            sleep(1)
    print("📶 WiFi Terhubung:", wlan.ifconfig())

def sync_waktu():
    try:
        print("⏳ Sinkronisasi waktu NTP...")
        ntptime.settime()
        print("⏱️ Waktu berhasil disinkronkan.")
    except:
        print("⚠️ Gagal sinkronisasi waktu!")

def kirim_data_ke_api(suhu, persen_pakan, status_pompa, pH):
    timestamp = get_current_time()
    data = {
        "suhu": suhu,
        "pakan(%)": persen_pakan,
        "pompa": status_pompa,
        "pH": pH,
        "timestamp": timestamp
    }
    try:
        response = urequests.post(API_SENSOR_URL, json=data)
        print("📤 Data dikirim ke API:", response.text)
        response.close()
    except Exception as e:
        print("⚠️ Gagal kirim data ke API:", e)

# Konek Wifi
konek_wifi(SSID, PASSWORD)
sync_waktu()

while True:
    sensor.measure()
    try:
        temperature = sensor.temperature()
        humidity = sensor.humidity()
        print(f"suhu : {temperature}, kelembapan : {humidity}")
        if temperature and humidity is not None:
            kirim_data_ke_api(humidity, 10, 1, 4)
        sleep(5)
    except Exception as e:
        print(f"Error: {e}")