from machine import Pin, PWM, RTC
import onewire, ds18x20
import network
import ntptime
from hcsr04 import HCSR04
from time import sleep, sleep_ms, time
import urequests

# ======= KONFIGURASI WIFI DAN SERVER ======= #
SSID = "abcd"
PASSWORD = "irfanbhq"
API_SENSOR_URL = "http://192.168.42.33:5000/sensor"       # Ganti sesuai IP Flask
API_JADWAL_URL = "http://192.168.42.33:5000/jadwal_pakan" # Endpoint jadwal pakan

# ----KONFIGURASI UBIDOTS ------
UBIDOTS_TOKEN = "BBUS-1yp1XSfykGjXkBO75BdEeMhS0Z6Al8"  # Token autentikasi Ubidots
UBIDOTS_DEVICE = "thekingsmercenaryUNI473stage3"  # Nama perangkat di Ubidots
UBIDOTS_URL = f"https://industrial.api.ubidots.com/api/v1.6/devices/{UBIDOTS_DEVICE}/"  # Endpoint API Ubidots

HEADERS_UBIDOTS = {
    "X-Auth-Token": UBIDOTS_TOKEN,
    "Content-Type": "application/json"
}


# ======= INISIALISASI SENSOR & PIN ======= #
ds_pin = Pin(4)
relay = Pin(26, Pin.OUT)
ow = onewire.OneWire(ds_pin)
ds_sensor = ds18x20.DS18X20(ow)

PIN_SERVO = 18
servo = PWM(Pin(PIN_SERVO), freq=50)

TRIGGER_PIN = 12
ECHO_PIN = 14
sensor = HCSR04(trigger_pin=TRIGGER_PIN, echo_pin=ECHO_PIN, echo_timeout_us=10000)

# ======= PARAMETER ======= #
BUKA_ANGLE = 90
TUTUP_ANGLE = 0
TINGGI_WADAH_CM = 10
JARAK_MIN_CM = 2

# ======= FUNGSI ======= #
def gerak_servo(angle):
    min_duty = 26
    max_duty = 128
    duty = int(min_duty + (angle / 180) * (max_duty - min_duty))
    servo.duty(duty)

def buka_tutup_pakan(repetisi=3):
    for i in range(repetisi):
        print(f"🔁 Pakan #{i+1} keluar...")
        gerak_servo(BUKA_ANGLE)
        sleep(2)
        gerak_servo(TUTUP_ANGLE)
        sleep(2)
    print("✅ Selesai memberi pakan.")

def hitung_persen_isi(jarak_cm):
    if jarak_cm > TINGGI_WADAH_CM:
        jarak_cm = TINGGI_WADAH_CM
    if jarak_cm < JARAK_MIN_CM:
        jarak_cm = JARAK_MIN_CM
    tinggi_isi = TINGGI_WADAH_CM - jarak_cm
    kapasitas_max = TINGGI_WADAH_CM - JARAK_MIN_CM
    persen = (tinggi_isi / kapasitas_max) * 100
    return round(persen)

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

def suhu():
    roms = ds_sensor.scan()
    if not roms:
        print('Sensor DS18B20 Tidak Ditemukan!')
        return None, None
    ds_sensor.convert_temp()
    sleep_ms(750)
    for rom in roms:
        suhu = ds_sensor.read_temp(rom)
        print("🌡️ Suhu: {:.2f}°C".format(suhu))
        if suhu > 32:
            print("🔥 Suhu > 32°C, Pompa HIDUP")
            relay.value(1)
            return suhu, 1
        else:
            print("❄️ Suhu <= 32°C, Pompa MATI")
            relay.value(0)
            return suhu, 0

def kirim_data_ke_api(suhu, persen_pakan, status_pompa):
    data = {
        "suhu": suhu,
        "pakan(%)": persen_pakan,
        "pompa": status_pompa
    }
    try:
        response = urequests.post(API_SENSOR_URL, json=data)
        print("📤 Data dikirim ke API:", response.text)
        response.close()
    except Exception as e:
        print("⚠️ Gagal kirim data ke API:", e)

def tarik_jadwal_pakan():
    try:
        response = urequests.get(API_JADWAL_URL)
        if response.status_code == 200:
            data = response.json()
            jadwal = data.get("jadwal", [])
            print("📥 Jadwal berhasil diambil:", jadwal)
            return jadwal
        else:
            print(f"❌ Gagal ambil jadwal: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Gagal terhubung ke server: {e}")
    return []

def cek_jadwal(jam, menit, jadwal_pakan):
    for j, m in jadwal_pakan:
        if jam == j and menit == m:
            return True
    return False


# *** Fungsi Mengirim Data ke Ubidots ***
def send_to_ubidots(suhu, pakan, pompa):
    """Mengirim data sensor ke Ubidots melalui HTTP POST"""
    payload = {
        "suhu": suhu,  # Suhu Air kolam
        "pakan": pakan,  # ketinggian pakan ikan
        "pompa": pompa  # status pompa
    }
    try:
        response = urequests.post(UBIDOTS_URL, json=payload, headers=HEADERS_UBIDOTS)
        print("Response Ubidots:", response.text)  # Cetak respons dari server Ubidots
        print(payload)
        response.close()
    except Exception as e:
        print("Error Ubidots:", e)  # Cetak error jika gagal mengirim data

# ======= PROGRAM UTAMA ======= #
konek_wifi(SSID, PASSWORD)
sync_waktu()
rtc = RTC()

last_suhu_check = 0
last_pakan_check = 0
last_jadwal_check = 0
last_jam_eksekusi = (-1, -1)

suhu_skrg = None
status_pompa = None
jadwal_pakan = []

while True:
    current_time = time()

    # Cek suhu setiap 5 detik
    if current_time - last_suhu_check >= 5:
        suhu_skrg, status_pompa = suhu()
        last_suhu_check = current_time

    # Cek level pakan dan kirim ke API setiap 10 detik
    if current_time - last_pakan_check >= 20:
        try:
            jarak = sensor.distance_cm()
            persen_pakan = hitung_persen_isi(jarak)
            print("📏 Jarak: {:.2f} cm | Sisa pakan: {}%".format(jarak, persen_pakan))
            if suhu_skrg is not None:
                kirim_data_ke_api(suhu_skrg, persen_pakan, status_pompa)
                # Kirim data ke Ubidots
                send_to_ubidots(suhu_skrg, persen_pakan, status_pompa)
        except Exception as e:
            print("⚠️ Gagal baca sensor ultrasonik:", e)
        last_pakan_check = current_time

    # Cek jadwal pakan dan eksekusi jika cocok
    if current_time - last_jadwal_check >= 2:
        jadwal_pakan = tarik_jadwal_pakan()
        now = rtc.datetime()
        jam = (now[4] + 7) % 24  # UTC -> WIB
        menit = now[5]
        print("🕒 Sekarang: {:02d}:{:02d}".format(jam, menit))

        if cek_jadwal(jam, menit, jadwal_pakan) and (jam, menit) != last_jam_eksekusi:
            buka_tutup_pakan()
            last_jam_eksekusi = (jam, menit)

        last_jadwal_check = current_time

    sleep(1)
