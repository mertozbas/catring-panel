# Basak Yemek - Deploy / Yayinlama Rehberi

## Onemli Not: Neden Cloudflare Pages Uygun Degil?

Bu uygulama **statik bir site degil**. Cloudflare Pages sadece HTML/CSS/JS dosyalarini sunar (statik hosting). Bizim uygulamamiz:

- **Python/Flask backend** calistiriyor (sunucu tarafinda kod)
- **SQLite veritabani** kullaniyor (dosya sistemi gerektiriyor)
- **Session yonetimi** yapiyor (sunucu tarafinda)
- **Google Maps API cagrilari** yapiyor (sunucu tarafinda geocoding)

Bu nedenle bir **sunucu (VPS)** veya **PaaS platformu** gerekiyor.

---

## Yontem 1: Railway.app (EN KOLAY - Ucretsiz Baslangic)

Railway, Python uygulamalarini dogrudan GitHub'dan deploy eder. Kredi karti gerekmez (baslangicta).

### Adimlar

**1. GitHub'a yukle:**
```bash
cd basak-yemek
git init
git add .
git commit -m "Initial commit"
```
GitHub'da yeni repo olustur ve push et:
```bash
git remote add origin https://github.com/KULLANICI/basak-yemek.git
git branch -M main
git push -u origin main
```

**2. Railway hesabi ac:**
- https://railway.app adresine git
- GitHub hesabinla giris yap

**3. Yeni proje olustur:**
- "New Project" > "Deploy from GitHub repo"
- basak-yemek reposunu sec
- Railway otomatik olarak Python uygulamasini algilar

**4. Ortam degiskenleri ayarla:**
Railway dashboard'da "Variables" sekmesine git:
```
SECRET_KEY=production-icin-guclu-bir-anahtar-olusturun
GOOGLE_MAPS_API_KEY=AIzaSy...
PORT=5050
```

**5. Baslangic komutu ayarla:**
Railway "Settings" > "Start Command":
```
python database/migrate.py && python app.py
```

**6. Procfile olustur** (proje kokune):
```
web: gunicorn app:create_app() --bind 0.0.0.0:$PORT
```

**7. gunicorn ekle:**
```bash
pip install gunicorn
pip freeze > requirements.txt
```

Railway otomatik deploy edecek. `basak-yemek-xxx.up.railway.app` gibi bir URL alirsiniz.

### Railway Ucretsiz Plan
- Aylik 5$ kredi (kucuk uygulamalar icin yeterli)
- Sleep yok (7/24 acik)
- Ozel domain baglayabilirsiniz

---

## Yontem 2: Render.com (UCRETSIZ - Demo Icin Ideal)

Render ucretsiz Python web servisi sunar.

### Adimlar

**1. GitHub'a yukle** (yukaridaki gibi)

**2. Render hesabi ac:**
- https://render.com adresine git
- GitHub ile giris yap

**3. Yeni Web Service olustur:**
- "New" > "Web Service"
- GitHub reposunu bagla
- Runtime: Python 3
- Build Command: `pip install -r requirements.txt && pip install gunicorn`
- Start Command: `python database/migrate.py && gunicorn app:create_app() --bind 0.0.0.0:$PORT`

**4. Ortam degiskenlerini ekle:**
```
SECRET_KEY=production-guclu-anahtar
GOOGLE_MAPS_API_KEY=AIzaSy...
```

**5. Deploy et**

`basak-yemek.onrender.com` gibi bir URL alirsiniz.

### Render Ucretsiz Plan Sinirlari
- 15 dakika istek gelmezse uyku moduna gecer (ilk istek ~30sn surer)
- Aylik 750 saat (tek servis icin yeterli)
- Demo/sunum icin gayet yeterli

---

## Yontem 3: VPS (Sunucu Kiralama - Production Icin)

Gercek production icin en iyi yontem. Tam kontrol.

### Onerilen VPS Saglayicilar

| Saglayici | En Ucuz Plan | Ozellik |
|-----------|-------------|---------|
| **Hetzner** | ~4 EUR/ay | Almanya/Finlandiya, cok ucuz, hizli |
| **DigitalOcean** | $6/ay | Kolay arayuz, iyi dokumantasyon |
| **Contabo** | ~4 EUR/ay | Ucuz, yuksek kaynak |
| **AWS Lightsail** | $3.50/ay | Amazon altyapisi |

### VPS Kurulum Adimlari (Ubuntu 22.04)

**1. Sunucuya baglan:**
```bash
ssh root@SUNUCU_IP
```

**2. Sistem guncelle ve gerekenleri kur:**
```bash
apt update && apt upgrade -y
apt install python3 python3-pip python3-venv nginx certbot python3-certbot-nginx -y
```

**3. Uygulama kullanicisi olustur:**
```bash
useradd -m -s /bin/bash basak
su - basak
```

**4. Projeyi yukle:**
```bash
git clone https://github.com/KULLANICI/basak-yemek.git
cd basak-yemek
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

**5. Ortam degiskenleri:**
```bash
cat > .env << 'EOF'
SECRET_KEY=cok-guclu-rastgele-bir-anahtar-buraya
GOOGLE_MAPS_API_KEY=AIzaSy...
FLASK_DEBUG=False
EOF
```

**6. Migrate et:**
```bash
source .env
python database/migrate.py
```

**7. Systemd servisi olustur:**
```bash
sudo tee /etc/systemd/system/basak-yemek.service << 'EOF'
[Unit]
Description=Basak Yemek Catering
After=network.target

[Service]
User=basak
WorkingDirectory=/home/basak/basak-yemek
EnvironmentFile=/home/basak/basak-yemek/.env
ExecStart=/home/basak/basak-yemek/venv/bin/gunicorn app:create_app() --workers 3 --bind 127.0.0.1:5050
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable basak-yemek
sudo systemctl start basak-yemek
```

**8. Nginx yapilandirmasi:**
```bash
sudo tee /etc/nginx/sites-available/basak-yemek << 'EOF'
server {
    listen 80;
    server_name sizin-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5050;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/basak/basak-yemek/static;
        expires 30d;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/basak-yemek /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

**9. SSL sertifikasi (HTTPS):**
```bash
sudo certbot --nginx -d sizin-domain.com
```

**10. Kontrol:**
```bash
sudo systemctl status basak-yemek
curl http://localhost:5050/auth/login
```

---

## Yontem 4: Fly.io (Kolay + Ucretsiz Tier)

### Adimlar

**1. Fly CLI kur:**
```bash
# macOS
brew install flyctl

# Linux
curl -L https://fly.io/install.sh | sh
```

**2. Hesap olustur ve giris yap:**
```bash
fly auth signup
fly auth login
```

**3. Proje kokune `fly.toml` olustur:**
```toml
app = "basak-yemek"
primary_region = "ams"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "5050"

[http_service]
  internal_port = 5050
  force_https = true

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

**4. Procfile olustur:**
```
web: python database/migrate.py && gunicorn app:create_app() --bind 0.0.0.0:$PORT
```

**5. Deploy et:**
```bash
fly launch
fly secrets set SECRET_KEY="guclu-anahtar" GOOGLE_MAPS_API_KEY="AIzaSy..."
fly deploy
```

`basak-yemek.fly.dev` adresinden erisilir.

---

## Hizli Demo Icin Onerilerim

### En Hizli: ngrok (Yerel Makineden Paylasim)

Hicbir yere deploy etmeden, kendi bilgisayarinizdan demo yapabilirsiniz:

```bash
# 1. ngrok kur
brew install ngrok   # macOS
# veya https://ngrok.com/download

# 2. Uygulamayi baslat
python app.py

# 3. Baska terminalde ngrok baslat
ngrok http 5050
```

ngrok size `https://abc123.ngrok-free.app` gibi bir public URL verir. Bu URL'yi paylasarak herkes uygulamanizi gorebilir. Bilgisayariniz acik oldugu surece calisir.

### Demo Sunum Icin: Render.com

- Ucretsiz
- 5 dakikada deploy
- `basak-yemek.onrender.com` URL'si
- Uyku modundan uyanmasi 30sn surebilir (sunumdan once bir kez acin)

### Gercek Kullanim Icin: Hetzner VPS + Domain

- Aylik ~4 EUR
- 7/24 acik, hizli
- Kendi domaininiz (ornek: `basak.yemek.com.tr`)
- SSL sertifikasi (HTTPS)
- Tam kontrol

---

## Production Kontrol Listesi

Deploy oncesi yapilmasi gerekenler:

- [ ] `config.py` > `FLASK_DEBUG = False` yap
- [ ] `SECRET_KEY` ortam degiskeni guclu bir deger olsun (en az 32 karakter rastgele)
- [ ] Tum varsayilan sifreleri degistir (`admin123`, `sofor123` vb.)
- [ ] `GOOGLE_MAPS_API_KEY` icin domain kisitlamasi ekle (Google Cloud Console'da)
- [ ] HTTPS aktif olsun (SSL sertifikasi)
- [ ] SQLite yerine PostgreSQL dusunulebilir (cok kullanicili erisimde)
- [ ] Yedekleme plani olustur (veritabani icin gunluk backup)
- [ ] gunicorn kullan (Flask development server yerine)

## SQLite Hakkinda Not

SQLite tek dosya veritabanidir. Kucuk-orta olcekli uygulamalar icin gayet yeterlidir (~1000 porsiyon/gun). Ancak:
- Ayni anda cok fazla yazma islemi olursa yavaslar
- VPS'te veritabani dosyasini duzgun yedekleyin
- Cok buyurse PostgreSQL'e gecis dusunulebilir (models/db.py degisikligi yeterli)
