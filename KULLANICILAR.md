# Basak Yemek - Kullanici Hesaplari

## Varsayilan Kullanicilar

| Kullanici Adi | Sifre | Rol | Aciklama | Erisim |
|---------------|-------|-----|----------|--------|
| `admin` | `admin123` | Yonetici | Sistem yoneticisi | Tum moduller |
| `siparis` | `siparis123` | Siparis | Siparis sorumlusu | Dashboard, Siparisler, Musteriler |
| `mutfak` | `mutfak123` | Mutfak | Mutfak ekibi | Dashboard, Mutfak, Menu, Envanter |
| `diyetisyen` | `diyet123` | Diyetisyen | Diyetisyen | Dashboard, Diyetisyen, Menu, Envanter |
| `planlama` | `plan123` | Planlama | Planlama sorumlusu | Dashboard, Planlama, Satin Alma, Envanter |
| `muhasebe` | `muhasebe123` | Muhasebe | Muhasebe | Dashboard, ERP/Muhasebe |

## Sofor Hesaplari

| Kullanici Adi | Sifre | Sofor | Driver ID |
|---------------|-------|-------|-----------|
| `sofor1` | `sofor123` | Koray Bey | 1 |
| `sofor2` | `sofor123` | Fuat Bey | 2 |
| `sofor3` | `sofor123` | Kadir Bey | 3 |
| `sofor4` | `sofor123` | Gurkan Bey | 4 |

Sofor hesaplari sadece **Sofor Paneli**'ne erisebilir. Giris yapinca otomatik olarak kendi rotalari gorunur.

## Roller ve Yetkiler

| Rol | Erisebilecegi Moduller |
|-----|----------------------|
| **admin** | Tum moduller (sinirsiz erisim) |
| **siparis** | Dashboard, Siparisler, Musteriler |
| **mutfak** | Dashboard, Mutfak Paneli, Menu, Envanter |
| **diyetisyen** | Dashboard, Diyetisyen Modulu, Menu, Envanter |
| **sofor** | Sofor Paneli (sadece kendi rotalari) |
| **planlama** | Dashboard, Planlama, Satin Alma, Envanter |
| **muhasebe** | Dashboard, ERP/Muhasebe |

## Notlar

- Production ortaminda tum sifreleri degistirin
- `SECRET_KEY` ortam degiskenini mutlaka guncelleyin
- Sifreler werkzeug `scrypt` ile hashlenir
