// ===== LIBRARY =====
#include <WiFi.h>            // Untuk koneksi WiFi
#include <HTTPClient.h>      // Untuk kirim data ke server lewat HTTP
#include <ArduinoJson.h>     // Untuk format data JSON
#include <OneWire.h>         // Untuk komunikasi 1 kabel dengan DS18B20
#include <DallasTemperature.h> // Untuk membaca suhu dari sensor DS18B20
#include <NTPClient.h>       // Untuk mendapatkan waktu dari internet
#include <WiFiUdp.h>         // Untuk membantu NTP
#include <ESP32Servo.h>      // Untuk mengendalikan motor servo
#include <Preferences.h>     // EEPROM Preferences


// ===== KONFIGURASI =====
const char* ssid = "OOO";             // Nama WiFi
const char* password = "12345678";      // Password WiFi

const char* API_SENSOR_URL = "https://flask-koi-production.up.railway.app/sensor";        // URL API untuk mengirim data sensor
const char* API_JADWAL_URL = "https://flask-koi-production.up.railway.app/jadwal_pakan";   // URL API untuk mengambil jadwal pakan
const char* API_BUKAAN_URL = "https://flask-koi-production.up.railway.app/get-jumlah-bukaan";


// Pin yang digunakan
const int pinRelay = 26;   // Relay untuk pompa
const int pinServo = 18;   // Servo untuk buka tutup pakan
const int pinTrig = 12;    // Ultrasonik TRIG
const int pinEcho = 14;    // Ultrasonik ECHO
const int pinOneWire = 4;  // Pin sensor suhu DS18B20
const int pHSense = 34; // Pin sensor pH

// ===== OBJEK SENSOR =====
OneWire oneWire(pinOneWire);           // Buat jalur OneWire
DallasTemperature sensors(&oneWire);   // Buat objek sensor suhu
Servo servo;                           // Buat objek motor servo

// Objek untuk ambil waktu internet
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 7 * 3600, 60000); // UTC +7 WIB

// objek preferences
Preferences preferences;

// ===== STRUKTUR DATA UNTUK JADWAL =====
struct Jadwal {
  int jam;
  int menit;
};

Jadwal jadwalList[10];     // List untuk menyimpan maksimal 10 jadwal pakan
int jumlahJadwal = 0;      // Banyaknya jadwal aktif
int jumlahBukaan = 3;  // Default, akan diupdate dari API


// ===== TIMER =====
unsigned long lastSuhuCheck = 0;
unsigned long lastPakanCheck = 0;
unsigned long lastTarikJadwal = 0;
unsigned long lastPHRead = 0;
float currentPH = 0.0;
int lastJamEksekusi = -1;
int lastMenitEksekusi = -1;

// ===== FUNGSI =====

// 1. Fungsi untuk koneksi ke WiFi
void konekWifi() {
  WiFi.begin(ssid, password);
  Serial.print("Menyambung ke WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected!");
}

// 2. Fungsi untuk baca suhu dari DS18B20
float bacaSuhu() {
  sensors.requestTemperatures();
  return sensors.getTempCByIndex(0); // Ambil suhu pertama
}

// 3. Fungsi untuk menggerakkan motor servo
void gerakServo(int angle) {
  int duty = map(angle, 0, 180, 544, 2400); // Konversi sudut ke pulsa servo
  servo.writeMicroseconds(duty);
}

// 4. Fungsi untuk buka tutup pakan beberapa kali
void bukaTutupPakan(int repetisi = 3) {
  for (int i = 0; i < repetisi; i++) {
    gerakServo(45);    // Buka pakan
    delay(700);       // Tunggu setengah detik
    gerakServo(0);     // Tutup pakan
    delay(700);       // Tunggu setengah detik
  }
}

// 5. Fungsi untuk baca jarak isi pakan
long jarakSensor() {
  digitalWrite(pinTrig, LOW);
  delayMicroseconds(2);
  digitalWrite(pinTrig, HIGH);
  delayMicroseconds(10);
  digitalWrite(pinTrig, LOW);

  long duration = pulseIn(pinEcho, HIGH, 10000); // Baca lama pantulan
  long distance = duration * 0.034 / 2; // Konversi ke cm
  return distance;
}

// 6. Fungsi untuk hitung persen isi pakan
int hitungPersenIsi(long jarakCm) {
  const int TINGGI_WADAH_CM = 10; // Tinggi wadah pakan
  const int JARAK_MIN_CM = 2;     // Batas jarak minimum jika penuh

  if (jarakCm > TINGGI_WADAH_CM) jarakCm = TINGGI_WADAH_CM;
  if (jarakCm < JARAK_MIN_CM) jarakCm = JARAK_MIN_CM;

  int tinggiIsi = TINGGI_WADAH_CM - jarakCm;
  int kapasitasMax = TINGGI_WADAH_CM - JARAK_MIN_CM;
  float persen = (tinggiIsi * 100.0) / kapasitasMax;

  return round(persen);
}


// 7. Fungsi untuk kirim data sensor ke server
void kirimData(float suhu, int persenPakan, int statusPompa, float ph) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(API_SENSOR_URL);
    http.addHeader("Content-Type", "application/json");

    StaticJsonDocument<200> doc;
    doc["suhu"] = suhu;
    doc["pakan(%)"] = persenPakan;
    doc["pompa"] = statusPompa;
    doc["ph"] = ph;

    String body;
    serializeJson(doc, body);
    int httpResponseCode = http.POST(body);

    Serial.println("Kirim ke API, Response: " + String(httpResponseCode));
    http.end();
  }
}

// 8. Fungsi untuk ambil jadwal pakan dari server
// Fungsi untuk ambil jadwal pakan dari server
void tarikJadwalPakan() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(API_JADWAL_URL);

    int httpResponseCode = http.GET();
    if (httpResponseCode == 200) {
      String payload = http.getString();
      Serial.println("[INFO] Payload yang diterima:");
      Serial.println(payload);  // Tampilkan payload JSON

      StaticJsonDocument<512> doc;
      DeserializationError error = deserializeJson(doc, payload);

      if (!error) {
        // Mengambil array "jadwal" dari objek JSON
        JsonArray arr = doc["jadwal"].as<JsonArray>();
        Jadwal tempJadwal[10];
        int tempJumlah = 0;

        for (JsonArray item : arr) {
          if (item.size() >= 2 && tempJumlah < 10) {
            tempJadwal[tempJumlah].jam = item[0];
            tempJadwal[tempJumlah].menit = item[1];
            tempJumlah++;

            // Debug log
            Serial.printf("[DEBUG] Jadwal %d: %02d:%02d\n", tempJumlah, tempJadwal[tempJumlah - 1].jam, tempJadwal[tempJumlah - 1].menit);
          }
        }

        // Tampilkan jadwal yang baru ditarik
        Serial.println("[INFO] Jadwal yang baru ditarik:");
        for (int i = 0; i < tempJumlah; i++) {
          Serial.printf(" - Jadwal %d: %02d:%02d\n", i + 1, tempJadwal[i].jam, tempJadwal[i].menit);
        }

        if (isJadwalBerubah(tempJadwal, tempJumlah)) {
          jumlahJadwal = tempJumlah;
          for (int i = 0; i < tempJumlah; i++) {
            jadwalList[i] = tempJadwal[i];
          }
          simpanJadwalEEPROM();
          Serial.println("[INFO] Jadwal diperbarui dan disimpan ke EEPROM.");
        } else {
          Serial.println("[INFO] Jadwal dari API sama, tidak perlu simpan ulang.");
        }
      } else {
        Serial.println("[ERROR] Gagal mendeserialize JSON.");
      }
    } else {
      Serial.println("[ERROR] Gagal tarik jadwal. HTTP Response: " + String(httpResponseCode));
    }
    http.end();
  }
}



// 9. Fungsi untuk cek apakah sekarang waktunya memberi makan
bool cekJadwal(int jam, int menit) {
  for (int i = 0; i < jumlahJadwal; i++) {
    if (jadwalList[i].jam == jam && jadwalList[i].menit == menit) {
      return true;
    }
  }
  return false;
}

// 10. Fungsi simpan jadwal ke EEPROM
void simpanJadwalEEPROM() {
  preferences.begin("jadwal", false); // buka namespace "jadwal", mode read+write
  
  preferences.putInt("jumlah", jumlahJadwal); // Simpan jumlah jadwal

  // Simpan semua jadwal
  for (int i = 0; i < jumlahJadwal; i++) {
    String keyJam = "jam" + String(i);
    String keyMenit = "menit" + String(i);

    preferences.putInt(keyJam.c_str(), jadwalList[i].jam);
    preferences.putInt(keyMenit.c_str(), jadwalList[i].menit);
  }

  preferences.end(); // Tutup akses ke EEPROM
  Serial.println("Jadwal berhasil disimpan ke EEPROM.");
}

// 11. Fungsi load jadwal dari EEPROM
void loadJadwalEEPROM() {
  preferences.begin("jadwal", true); // buka namespace "jadwal", mode read-only

  jumlahJadwal = preferences.getInt("jumlah", 0); // Baca jumlah jadwal

  for (int i = 0; i < jumlahJadwal; i++) {
    String keyJam = "jam" + String(i);
    String keyMenit = "menit" + String(i);

    jadwalList[i].jam = preferences.getInt(keyJam.c_str(), 0);
    jadwalList[i].menit = preferences.getInt(keyMenit.c_str(), 0);
  }

  preferences.end(); // Tutup akses ke EEPROM
  Serial.println("Jadwal berhasil dimuat dari EEPROM.");
}

// 12. Fungsi cek jadwal EEPROM apakah sama dengan API
bool isJadwalBerubah(Jadwal* jadwalBaru, int jumlahBaru) {
  if (jumlahBaru != jumlahJadwal) {
    return true; // Kalau jumlah beda, pasti berubah
  }

  for (int i = 0; i < jumlahBaru; i++) {
    if (jadwalList[i].jam != jadwalBaru[i].jam || jadwalList[i].menit != jadwalBaru[i].menit) {
      return true; // Kalau ada yang beda, jadwal berubah
    }
  }
  
  return false; // Semua sama
}

// 13. Funngsi cek WIFI RECCONECT
void cekWifi() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[WARNING] WiFi terputus! Mencoba reconnect...");

    WiFi.disconnect(); // Pastikan reset koneksi
    WiFi.begin(ssid, password);

    unsigned long startAttemptTime = millis();

    // Coba konek maksimal 10 detik
    while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < 10000) {
      delay(500);
      Serial.print(".");
    }

    if (WiFi.status() == WL_CONNECTED) {
      Serial.println("\n[INFO] WiFi reconnect berhasil!");
    } else {
      Serial.println("\n[ERROR] Gagal reconnect WiFi setelah 10 detik.");
    }
  }
}

// 14. Fungsi konversi nilai pH
float toPH(float voltage) {
  float m = (4.0 - 7.0) / (2.947 - 2.315);  // -3 / 0.632
  float b = 7.0 - (m * 2.315);
  return m * voltage + b;
}

void updateJumlahBukaan() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(API_BUKAAN_URL);
    int httpResponseCode = http.GET();

    if (httpResponseCode == 200) {
      String payload = http.getString();
      StaticJsonDocument<128> doc;
      DeserializationError error = deserializeJson(doc, payload);

      if (!error && doc.containsKey("jumlah_bukaan")) {
        jumlahBukaan = doc["jumlah_bukaan"];
        Serial.println("[INFO] Jumlah bukaan diupdate dari API: " + String(jumlahBukaan));
      } else {
        Serial.println("[WARNING] Gagal parsing JSON jumlah bukaan");
      }
    } else {
      Serial.println("[ERROR] Gagal ambil jumlah bukaan. HTTP Response: " + String(httpResponseCode));
    }

    http.end();
  }
}


// ===== SETUP =====
void setup() {
  Serial.begin(115200);

  pinMode(pinRelay, OUTPUT);
  pinMode(pinTrig, OUTPUT);
  pinMode(pinEcho, INPUT);

  servo.attach(pinServo);
  servo.write(0); // Servo di posisi tutup

  konekWifi();      // Sambung WiFi
  sensors.begin();  // Mulai sensor suhu
  timeClient.begin(); // Mulai NTP Client
  timeClient.update(); // Sinkronisasi jam pertama kali

  loadJadwalEEPROM(); // Cek jadwal di EEPROM
  tarikJadwalPakan(); // Tarik jadwal awal
  updateJumlahBukaan(); // Ambil jumlah bukaan dari API saat awal menyala

}

// ===== LOOP =====
void loop() {

  cekWifi(); // Cek WIFI terhubung atau tidak

  timeClient.update(); // Update jam internet
  int jam = timeClient.getHours();
  int menit = timeClient.getMinutes();

  unsigned long now = millis();

  // 1. Cek suhu tiap 5 detik
  if (now - lastSuhuCheck > 5000) {
    float suhu = bacaSuhu();
    Serial.println("Suhu: " + String(suhu) + " °C");

    // Kalau suhu > 32 derajat, nyalakan pompa (relay)
    if (suhu > 30) {
      digitalWrite(pinRelay, HIGH);
    } else {
      digitalWrite(pinRelay, LOW);
    }
    lastSuhuCheck = now;
  }

  // 2. Cek pH setiap 10 detik 
    if (now - lastPHRead >= 10000) {
    int rawPH = analogRead(pHSense);
    float voltagePH = rawPH * (3.3 / 4095.0);
    currentPH = toPH(voltagePH);
    Serial.print("pH: ");
    Serial.println(currentPH, 2);
    lastPHRead = now;
  }

  // 3. Cek isi pakan tiap 20 detik
  if (now - lastPakanCheck > 20000) {
    long jarak = jarakSensor();
    int persenPakan = hitungPersenIsi(jarak);
    Serial.println("Pakan tersisa: " + String(persenPakan) + "%");

    kirimData(bacaSuhu(), persenPakan, digitalRead(pinRelay), currentPH);

    lastPakanCheck = now;
  }

  // 4. Tarik ulang jadwal pakan tiap 1 menit
  if (now - lastTarikJadwal > 60000) {
    tarikJadwalPakan();
    lastTarikJadwal = now; 
  }

  // 5. Cek apakah sekarang waktunya memberi makan
  if (cekJadwal(jam, menit) && (jam != lastJamEksekusi || menit != lastMenitEksekusi)) {
    updateJumlahBukaan();          // Update dulu jumlah bukaan dari API
    Serial.println("Jumlah bukaan dari API: " + String(jumlahBukaan));  // <-- Tambahkan ini
    bukaTutupPakan(jumlahBukaan); // Pakai nilai dari API
    lastJamEksekusi = jam;
    lastMenitEksekusi = menit;
  }

  delay(1000); // Delay kecil supaya tidak terlalu berat kerja CPU
}