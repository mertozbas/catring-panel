# Basak Yemek - Catering Yonetim Sistemi

Ankara merkezli, gunluk ~1000 porsiyon kapasiteli yemek catering operasyonunu uctan uca yoneten web uygulamasi. Siparis almadan mutfak uretimine, rota optimizasyonundan muhasebe takibine kadar tum surecleri tek platformda yonetir.

> **Canli Demo:** [Render uzerinde](https://catring-panel.onrender.com)

## Ekran Goruntuleri

| Dashboard | Sofor Paneli | Raporlar |
|-----------|-------------|----------|
| Siparis/porsiyon ozeti, teslimat durumu, grafikler | Mobil uyumlu teslimat kartlari, tek tusla navigasyon | 5 farkli rapor tipi, Chart.js grafikleri |

## Ozellikler

### Siparis ve Musteri Yonetimi
- Musteri kaydi, iletisim bilgileri, varsayilan siparis tercihleri (kap tipi, porsiyon, cesit)
- Musteri segmentasyonu (VIP/Normal/Yeni) ve birim fiyat tanimi
- Gunluk siparis olusturma (porsiyon, cesit, kap tipi, ozel not, ekstra)
- Toplu siparis islemleri (secim + toplu durum degistirme)
- Siparis duzenleme modal
- Siparis gecmisi takibi (order_history tablosu)
- CSV ile toplu musteri import

### Haftalik Menu Planlama
- Haftalik menu olusturma (5-6 gun, 4 cesit yemek/gun)
- Recete yonetimi ve malzeme hesaplama
- Menu yazdirma (PDF)

### Mutfak Paneli
- Gunluk hazirlama listesi
- Siparis bazli uretim takibi
- Malzeme kontrolu ve eksik stok uyarisi
- Yazdirma destegi (@media print)

### Diyetisyen Modulu
- Tedarik mal kabul / red islemi
- Recete ve besin deger kontrolu
- Malzeme kalite denetimi

### Rota ve Teslimat
- 4 sofor, gunluk rota olusturma
- Google Maps ile rota optimizasyonu (en yakin komsuluk sirasi)
- Sofor paneli: detayli siparis kartlari, tek tusla gunluk rota navigasyonu
- Teslimat onay modali (not ekleme: "Kapida birakildi", "Resepsiyona teslim")
- Problem bildirimi (Musteri yok, Adres bulunamadi, Siparis reddedildi, Diger)
- Haritada canli rota gorunumu (yesil: teslim, kirmizi: bekleyen)

### Envanter ve Satin Alma
- Stok takibi, minimum stok uyarilari
- Tedarikci yonetimi
- Satin alma siparisleri ve maliyet takibi

### Planlama
- Haftalik uretim planlama
- Malzeme ihtiyac hesaplama (recetelerden otomatik)

### Muhasebe / ERP
- Fatura olusturma (PDF export - ReportLab)
- Otomatik fatura hesaplama (musteri birim fiyati x porsiyon + %10 KDV)
- Cari hesap takibi (borc/alacak/bakiye)
- Gelir-gider takibi (12 kategori)
- Odeme kaydi girisi

### Raporlama Modulu (5 Tab)
- **Gunluk Rapor:** siparis/porsiyon ozeti, kap tipi dagilimi (doughnut chart), rota ozeti, siparis detaylari, problemler
- **Haftalik Rapor:** trend grafik (bar chart), kap tipi dagilimi, en cok siparis veren musteriler, finansal ozet
- **Musteri Raporu:** musteri bazli istatistikler, porsiyon trendi (line chart), odeme gecmisi, siparis gecmisi, bakiye
- **Stok Raporu:** dusuk stok uyarilari, son 7 gun tuketim/giris, tum stok durumu
- **Sofor Performansi:** tamamlama orani (progress bar), porsiyon karsilastirmasi (bar chart), problem istatistikleri
- Her raporda **CSV export** destegi

### Bildirim Sistemi
- Dashboard'da bildirim ikonu + dropdown
- Bildirim turleri: dusuk stok, odenmemis fatura, tamamlanan teslimat, yeni siparis, problem bildirimi
- 30 saniye periyodik kontrol
- Okunmamis badge sayaci

### Telegram Bot (AI Destekli)
- **Musteri Portali (DM):** siparis alma, menu sorgulama, siparis durumu, siparis gecmisi, iptal talebi
- **Sirket Ici Grup:** otomatik bildirimler (gunun menusu, siparis ozeti, rota tamamlama, dusuk stok)
- Inline keyboard destegi (siparis onay, menu secimi, musteri secimi)
- 14 arac: musteri arama, siparis olusturma, menu sorgulama, teslimat takibi, stok durumu, raporlama
- OpenAI GPT ile dogal dil anlama (Strands Agent SDK)

### Teknik Ozellikler
- PWA destegi (mobil cihazlarda uygulama gibi kullanim)
- Responsive tasarim (telefon, tablet, masaustu)
- Rol bazli erisim kontrolu (7 farkli rol)
- CSRF koruması (Flask-WTF)
- Google Maps entegrasyonu (geocoding, rota optimizasyonu, harita)
- Service Worker ile offline destek
- 12 veritabani indexi (performans optimizasyonu)
- Chart.js ile interaktif grafikler

## Teknoloji

| Katman | Teknoloji |
|--------|-----------|
| Backend | Python 3.10+, Flask 3.1 |
| Veritabani | SQLite |
| Frontend | HTML5, CSS3, JavaScript (vanilla), Chart.js |
| Harita | Google Maps JavaScript API, Directions API, Geocoding API |
| AI Bot | Telegram Bot API, Strands Agent SDK, OpenAI GPT |
| PDF | ReportLab |
| PWA | Service Worker, Web App Manifest |
| Guvenlik | Flask-WTF (CSRF), session-based auth |
| Deploy | Render.com, Gunicorn |

## Proje Yapisi

```
basak-yemek/
├── app.py                    # Flask uygulama fabrikasi
├── config.py                 # Yapilandirma (DB, API anahtarlari, port)
├── requirements.txt          # Python bagimliliklari
├── Procfile                  # Render deploy (gunicorn)
│
├── blueprints/               # Flask Blueprint modulleri (16 adet)
│   ├── auth.py               # Giris/cikis, rol yonetimi
│   ├── dashboard.py          # Ana panel (istatistikler, grafikler)
│   ├── customers.py          # Musteri CRUD + geocoding + CSV import
│   ├── orders.py             # Siparis yonetimi + toplu islemler
│   ├── routes.py             # Rota olusturma + optimizasyon
│   ├── driver_ui.py          # Sofor paneli + teslimat onay + problem bildir
│   ├── drivers.py            # Sofor CRUD
│   ├── kitchen.py            # Mutfak paneli
│   ├── menu.py               # Menu planlama
│   ├── dietitian.py          # Diyetisyen modulu
│   ├── inventory.py          # Envanter
│   ├── planning.py           # Uretim planlama
│   ├── purchasing.py         # Satin alma
│   ├── erp.py                # Muhasebe/ERP + fatura PDF
│   ├── reports.py            # Raporlama (5 tab + CSV export)
│   └── api.py                # REST API + bildirimler
│
├── models/                   # Veritabani modelleri
│   ├── db.py                 # SQLite baglanti yonetimi
│   ├── customer.py, order.py, route.py, driver.py
│   ├── menu.py, recipe.py, inventory.py
│   ├── purchase.py, supplier.py, finance.py
│   └── user.py               # Kullanici/kimlik dogrulama
│
├── templates/                # Jinja2 HTML sablonlari (22 adet)
│   ├── base.html             # Ana layout (sidebar, topbar, bildirimler)
│   ├── login.html            # Giris sayfasi
│   ├── dashboard.html        # Ana panel
│   ├── driver.html           # Sofor paneli (teslimat + problem modallari)
│   ├── reports.html          # Raporlama (5 tab, Chart.js)
│   └── ...                   # Diger sayfa sablonlari
│
├── static/
│   ├── css/style.css         # Tum CSS (responsive)
│   ├── js/app.js             # Genel JS + Service Worker kaydi
│   ├── sw.js                 # Service Worker (offline destek)
│   ├── manifest.json         # PWA manifest
│   └── img/                  # PWA ikonlari
│
├── database/
│   ├── schema.sql            # Veritabani semasi (16+ tablo, 12 index)
│   ├── seed.sql              # Ornek veri
│   ├── migrate.py            # Migrasyon scripti (14 adim)
│   └── basak_yemek.db        # SQLite veritabani dosyasi
│
├── utils/
│   ├── maps.py               # Google Maps (geocoding, rota optimizasyonu)
│   ├── helpers.py            # Yardimci fonksiyonlar
│   └── pdf_generator.py      # PDF olusturma (fatura, menu)
│
└── agent/                    # Telegram AI Bot
    ├── bot.py                # Bot ana dosyasi (grup + DM + inline keyboard)
    ├── prompts/
    │   └── system_prompt.txt # Bot sistem promptu
    └── tools/                # Bot araclari (7 adet)
        ├── customer_tools.py # Musteri arama, kayit
        ├── order_tools.py    # Siparis olusturma, sorgulama
        ├── menu_tools.py     # Menu sorgulama
        ├── route_tools.py    # Rota durumu, teslimat takibi
        ├── inventory_tools.py# Stok sorgulama
        ├── report_tools.py   # Gunluk/haftalik rapor
        └── notification_tools.py # Grup bildirimleri
```

## Kurulum

### 1. Gereksinimler
- Python 3.10+
- pip

### 2. Projeyi Klonla
```bash
git clone https://github.com/basak-yemek/basak-yemek.git
cd basak-yemek
```

### 3. Bagimliliklari Yukle
```bash
pip install -r requirements.txt
```

### 4. Ortam Degiskenleri
```bash
# Zorunlu (production icin degistirin)
export SECRET_KEY="sizin-gizli-anahtariniz"

# Google Maps (harita, rota, geocoding icin)
export GOOGLE_MAPS_API_KEY="AIzaSy..."

# Telegram Bot (opsiyonel)
export TELEGRAM_BOT_TOKEN="bot-token"
export TELEGRAM_GROUP_CHAT_ID="-100xxxxx"

# OpenAI (Telegram bot icin)
export OPENAI_API_KEY="sk-..."
```

### 5. Veritabani Olustur ve Migrate Et
```bash
python database/migrate.py
```
Bu komut:
- Tum tablolari ve indexleri olusturur
- Varsayilan kullanicilari ekler (10 kullanici, 7 rol)
- 4 sofor hesabi olusturur
- Mevcut musterileri geocode eder (API key varsa)

### 6. Uygulamayi Baslat
```bash
python app.py
```
Uygulama `http://localhost:5050` adresinde calisir.

### 7. Telegram Bot (Opsiyonel)
```bash
python agent/bot.py
```

## Varsayilan Kullanicilar

| Kullanici Adi | Sifre | Rol | Erisim Alani |
|---------------|-------|-----|-------------|
| admin | admin123 | Yonetici | Tum moduller |
| siparis | siparis123 | Siparis | Dashboard, Siparisler, Musteriler |
| mutfak | mutfak123 | Mutfak | Dashboard, Mutfak, Menu, Envanter |
| diyetisyen | diyetisyen123 | Diyetisyen | Dashboard, Diyetisyen, Menu, Envanter |
| planlama | planlama123 | Planlama | Dashboard, Planlama, Satinalma, Envanter, Raporlar |
| muhasebe | muhasebe123 | Muhasebe | Dashboard, Muhasebe/ERP, Raporlar |
| sofor1 | sofor123 | Sofor | Sofor Paneli (Koray Bey) |
| sofor2 | sofor123 | Sofor | Sofor Paneli (Fuat Bey) |
| sofor3 | sofor123 | Sofor | Sofor Paneli (Kadir Bey) |
| sofor4 | sofor123 | Sofor | Sofor Paneli (Gurkan Bey) |

## Google Maps API Kurulumu

1. [Google Cloud Console](https://console.cloud.google.com)'a gidin
2. Yeni proje olusturun veya mevcut projeyi secin
3. API'leri etkinlestirin:
   - Maps JavaScript API
   - Directions API
   - Geocoding API
4. Kimlik bilgileri > API Anahtari olusturun
5. Anahtari ortam degiskeni olarak ayarlayin

## Deploy (Render.com)

1. GitHub reposunu Render'a baglayin
2. Environment variables ekleyin (SECRET_KEY, GOOGLE_MAPS_API_KEY vb.)
3. Build command: `pip install -r requirements.txt && python database/migrate.py`
4. Start command: `gunicorn app:create_app() --bind 0.0.0.0:$PORT`

## Lisans

Bu proje ozel kullanim icindir.
