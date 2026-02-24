# Basak Yemek - Catering Yonetim Sistemi

Ankara merkezli, gunluk ~1000 porsiyon kapasiteli yemek catering operasyonunu uctan uca yoneten web uygulamasi.

## Ozellikler

### Siparis ve Musteri Yonetimi
- Musteri kaydi, iletisim bilgileri, varsayilan siparis tercihleri
- Gunluk siparis olusturma (porsiyon, cesit, kap tipi, ozel not, ekstra)
- Otomatik siparis tekrarlama

### Haftalik Menu Planlama
- Haftalik menu olusturma (5-6 gun, 4 cesit yemek/gun)
- Reçete yonetimi ve malzeme hesaplama
- Menu yazdirma (PDF)

### Mutfak Paneli
- Gunluk hazirlama listesi
- Siparis bazli uretim takibi
- Malzeme kontrolu

### Diyetisyen Modulu
- Tedarik mal kabul / red islemi
- Recete ve besin deger kontrolu
- Malzeme kalite denetimi

### Rota ve Teslimat
- 4 sofor, gunluk rota olusturma
- Google Maps ile rota optimizasyonu (en yakin komsuluk sirasi)
- Sofor paneli: detayli siparis kartlari, tek tusla gunluk rota navigasyonu
- Teslim edilenleri atlayarak kaldigi yerden devam
- Haritada canli rota gorunumu (yesil: teslim, kirmizi: bekleyen)

### Envanter ve Satin Alma
- Stok takibi, minimum stok uyarilari
- Tedarikci yonetimi
- Satin alma siparisleri ve maliyet takibi

### Planlama
- Haftalik uretim planlama
- Malzeme ihtiyac hesaplama (recetelerden otomatik)

### Muhasebe / ERP
- Fatura olusturma
- Gelir-gider takibi
- Temel mali raporlama

### Telegram Bot (AI Destekli)
- Musteri siparis sorgulama
- Menu bilgisi
- Dogal dil ile etkilesim

### Teknik Ozellikler
- PWA destegi (mobil cihazlarda uygulama gibi kullanim)
- Responsive tasarim (telefon, tablet, masaustu)
- Rol bazli erisim kontrolu (7 farkli rol)
- Google Maps entegrasyonu (geocoding, rota optimizasyonu, harita)
- Service Worker ile offline destek

## Teknoloji

| Katman | Teknoloji |
|--------|-----------|
| Backend | Python 3, Flask |
| Veritabani | SQLite |
| Frontend | HTML5, CSS3, JavaScript (vanilla) |
| Harita | Google Maps JavaScript API, Directions API, Geocoding API |
| AI Bot | Telegram Bot API + Ollama / OpenAI |
| PDF | ReportLab |
| PWA | Service Worker, Web App Manifest |

## Proje Yapisi

```
basak-yemek/
├── app.py                    # Flask uygulama fabrikasi
├── config.py                 # Yapilandirma (DB, API anahtarlari, port)
├── requirements.txt          # Python bagimliliklari
│
├── blueprints/               # Flask Blueprint modulleri (15 adet)
│   ├── auth.py               # Giris/cikis, rol yonetimi
│   ├── dashboard.py          # Ana panel
│   ├── customers.py          # Musteri CRUD + geocoding
│   ├── orders.py             # Siparis yonetimi
│   ├── routes.py             # Rota olusturma + optimizasyon
│   ├── driver_ui.py          # Sofor paneli
│   ├── drivers.py            # Sofor CRUD
│   ├── kitchen.py            # Mutfak paneli
│   ├── menu.py               # Menu planlama
│   ├── dietitian.py          # Diyetisyen modulu
│   ├── inventory.py          # Envanter
│   ├── planning.py           # Uretim planlama
│   ├── purchasing.py         # Satin alma
│   ├── erp.py                # Muhasebe/ERP
│   └── api.py                # REST API
│
├── models/                   # Veritabani modelleri
│   ├── db.py                 # SQLite baglanti yonetimi
│   ├── customer.py, order.py, route.py, driver.py
│   ├── menu.py, recipe.py, inventory.py
│   ├── purchase.py, supplier.py, finance.py
│   └── user.py               # Kullanici/kimlik dogrulama
│
├── templates/                # Jinja2 HTML sablonlari (20 adet)
│   ├── base.html             # Ana layout (sidebar, topbar)
│   ├── login.html            # Giris sayfasi
│   ├── dashboard.html        # Ana panel
│   ├── driver.html           # Sofor paneli (detayli)
│   └── ...                   # Diger sayfa sablonlari
│
├── static/
│   ├── css/style.css         # Tum CSS (~1000 satir, responsive)
│   ├── js/app.js             # Genel JS + Service Worker kaydi
│   ├── sw.js                 # Service Worker (offline destek)
│   ├── manifest.json         # PWA manifest
│   └── img/                  # PWA ikonlari
│
├── database/
│   ├── schema.sql            # Veritabani semasi (14 tablo)
│   ├── seed.sql              # Ornek veri
│   ├── migrate.py            # Migrasyon scripti
│   └── basak_yemek.db        # SQLite veritabani dosyasi
│
├── utils/
│   ├── maps.py               # Google Maps (geocoding, rota optimizasyonu)
│   ├── helpers.py            # Yardimci fonksiyonlar
│   └── pdf_generator.py      # PDF olusturma (menu yazdirma)
│
└── agent/                    # Telegram AI Bot
    ├── bot.py                # Bot ana dosyasi
    ├── prompts/              # Sistem promptlari
    └── tools/                # Bot araclari (siparis, menu, musteri)
```

## Kurulum

### 1. Gereksinimler
- Python 3.10+
- pip

### 2. Bagimliliklari Yukle
```bash
cd basak-yemek
pip install -r requirements.txt
```

### 3. Ortam Degiskenleri (Opsiyonel)
```bash
# Google Maps (harita, rota, geocoding icin)
export GOOGLE_MAPS_API_KEY="AIzaSy..."

# Uygulama guvenlik anahtari (production icin degistirin)
export SECRET_KEY="sizin-gizli-anahtariniz"

# Telegram Bot (opsiyonel)
export TELEGRAM_BOT_TOKEN="bot-token"
```

### 4. Veritabani Olustur ve Migrate Et
```bash
python database/migrate.py
```
Bu komut:
- Tum tablolari olusturur
- Varsayilan kullanicilari ekler (7 rol)
- 4 sofor hesabi olusturur
- Mevcut musterileri geocode eder (API key varsa)

### 5. Uygulamayi Baslat
```bash
python app.py
```
Uygulama `http://localhost:5050` adresinde calisir.

### 6. Telegram Bot (Opsiyonel)
```bash
python agent/bot.py
```

## Kullanim

1. Tarayicida `http://localhost:5050` adresine gidin
2. Kullanici adi ve sifre ile giris yapin (kullanicilar icin `KULLANICILAR.md` dosyasina bakin)
3. Rol bazli erisim: her kullanici sadece yetkili oldugu modulleri gorur

### Sofor Paneli
- Sofor hesabiyla giris yapinca otomatik olarak kendi rotalari gorunur
- "Gunluk Rotayi Baslat" butonu ile Google Maps'te tum kalan teslimatlar acilir
- Teslim edildi butonuna basinca siparis teslim olarak isaretlenir
- Tekrar "Gunluk Rota" basinca teslim edilenler atlanir

## Google Maps API Kurulumu

1. [Google Cloud Console](https://console.cloud.google.com) 'a gidin
2. Yeni proje olusturun veya mevcut projeyi secin
3. API'leri etkinlestirin:
   - Maps JavaScript API
   - Directions API
   - Geocoding API
4. Kimlik bilgileri > API Anahtari olusturun
5. Anahtari ortam degiskeni olarak ayarlayin:
   ```bash
   export GOOGLE_MAPS_API_KEY="AIzaSy..."
   ```

## Lisans

Bu proje ozel kullanim icindir.
