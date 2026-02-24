# Basak Yemek - Kullanim Kilavuzu

Bu belge, Basak Yemek Catering Yonetim Sistemi'ni kullanan tum personel icin hazirlanmistir.

---

## ICINDEKILER

1. [Giris ve Genel Bilgiler](#1-giris-ve-genel-bilgiler)
2. [Sisteme Giris](#2-sisteme-giris)
3. [Dashboard (Ana Panel)](#3-dashboard-ana-panel)
4. [Siparis Yonetimi](#4-siparis-yonetimi)
5. [Musteri Yonetimi](#5-musteri-yonetimi)
6. [Rota ve Teslimat](#6-rota-ve-teslimat)
7. [Sofor Paneli](#7-sofor-paneli)
8. [Mutfak Paneli](#8-mutfak-paneli)
9. [Menu Planlama](#9-menu-planlama)
10. [Diyetisyen Modulu](#10-diyetisyen-modulu)
11. [Envanter (Depo)](#11-envanter-depo)
12. [Malzeme Planlama](#12-malzeme-planlama)
13. [Satin Alma](#13-satin-alma)
14. [Muhasebe / ERP](#14-muhasebe--erp)
15. [Raporlar](#15-raporlar)
16. [Bildirimler](#16-bildirimler)
17. [Telegram Bot](#17-telegram-bot)
18. [Mobil Kullanim (PWA)](#18-mobil-kullanim-pwa)
19. [Sik Sorulan Sorular](#19-sik-sorulan-sorular)

---

## 1. Giris ve Genel Bilgiler

Basak Yemek Catering Yonetim Sistemi, gunluk ~1000 porsiyon yemek uretim ve dagitim surecini yoneten web tabanli bir uygulamadir.

**Sistem 7 farkli rol ile calisir:**

| Rol | Gorev | Erisebildigi Moduller |
|-----|-------|----------------------|
| Yonetici (admin) | Tum sistemi yonetir | Tum moduller |
| Siparis | Siparis ve musteri islemleri | Dashboard, Siparisler, Musteriler |
| Mutfak | Yemek hazirlama takibi | Dashboard, Mutfak, Menu, Envanter |
| Diyetisyen | Kalite kontrol, recete | Dashboard, Diyetisyen, Menu, Envanter |
| Planlama | Uretim planlama | Dashboard, Planlama, Satinalma, Envanter, Raporlar |
| Muhasebe | Mali islemler | Dashboard, Muhasebe/ERP, Raporlar |
| Sofor | Teslimat | Sofor Paneli |

---

## 2. Sisteme Giris

1. Tarayicinizda uygulamanin adresini acin
2. Kullanici adinizi ve sifrenizi girin
3. "Giris Yap" butonuna basin
4. Rolunuze gore ilgili sayfaya yonlendirilirsiniz

**Onemli:** Sifrenizi kimseyle paylasmayiniz. Cikis yapmak icin sag ustteki "Cikis" butonunu kullaniniz.

---

## 3. Dashboard (Ana Panel)

Giris yaptiginizda ilk gorunen sayfadir. Burada:

- **Bugunun Siparisleri:** Toplam siparis sayisi
- **Toplam Porsiyon:** Bugunku toplam porsiyon
- **Teslimat Durumu:** Teslim edilen / bekleyen / iptal dagilimi (renkli progress bar)
- **Dusuk Stok Uyarisi:** Minimum seviyenin altindaki malzeme sayisi
- **Rota Tamamlanma:** Aktif rotalarin durumu
- **Odenmemis Fatura:** Toplam alacak tutari
- **Bugunun Menusu:** Gunun yemek listesi
- **Haftalik Porsiyon Trendi:** Son 7 gunun porsiyon grafigi
- **Kap Tipi Dagilimi:** Sefer tasi, paket, kuvet vb. dagilim grafigi

---

## 4. Siparis Yonetimi

### Yeni Siparis Olusturma
1. Sol menuden "Siparisler"e tiklayin
2. "Yeni Siparis" butonuna basin
3. Formu doldurun:
   - **Musteri:** Listeden secin
   - **Tarih:** Siparis tarihi (varsayilan: bugun)
   - **Porsiyon Sayisi:** Kac kisilik yemek
   - **Cesit Sayisi:** Kac cesit yemek (genelde 4)
   - **Kap Tipi:** Sefer tasi / Paket / Kuvet / Tepsi / Poset
   - **Ozel Not:** Varsa musteriye ozel istekler
4. "Kaydet" butonuna basin

### Siparis Durumlarini Anlama
- **Bekliyor (pending):** Siparis alindi, henuz hazirlama baslamadi
- **Hazirlaniyor (preparing):** Mutfakta hazirlaniyor
- **Hazir (ready):** Hazirlandi, teslimat icin bekliyor
- **Rotada (on_route):** Sofor yolda
- **Teslim Edildi (delivered):** Basariyla teslim edildi
- **Iptal (cancelled):** Iptal edilmis siparis

### Siparis Duzenleme
1. Siparisler listesinde duzenlemek istediginiz siparisin satirindaki "Duzenle" butonuna basin
2. Acilan modalda bilgileri guncelleyin
3. "Kaydet" butonuna basin

### Toplu Islemler
1. Sol taraftaki checkbox'larla birden fazla siparis secin
2. Ustteki toolbar'dan istediginiz islemi secin (ornegin "Hazir Yap", "Iptal Et")
3. Secili tum siparislere islem uygulanir

### Filtreleme
- Ustteki toolbar'daki dropdown filtrelerle (musteri, durum, kap tipi, rota) siparisleri filtreleyebilirsiniz

---

## 5. Musteri Yonetimi

### Yeni Musteri Ekleme
1. Sol menuden "Musteriler"e tiklayin
2. "Yeni Musteri" butonuna basin
3. Bilgileri girin:
   - **Firma Adi:** Musterinin firma/kurum adi
   - **Yetkili Kisi:** Iletisim kurulacak kisi
   - **Telefon:** Cep telefonu
   - **Adres:** Tam adres (Google Maps ile otomatik konum bulunur)
   - **Varsayilan Kap Tipi:** En sik kullandigi kap
   - **Varsayilan Porsiyon:** Her siparis icin varsayilan kisi sayisi
   - **Varsayilan Cesit:** Kac cesit yemek istedigini
   - **Segment:** VIP / Normal / Yeni
   - **Birim Fiyat:** Porsiyon basi fiyat (TL)
4. "Kaydet" butonuna basin

### Toplu Musteri Import (CSV)
1. Musteriler sayfasinda "CSV Import" butonuna basin
2. Ornek CSV dosyasini indirmek icin "Template Indir" butonuna basin
3. CSV dosyasini doldurun
4. Dosyayi yukleyin

### Musteri Siparis Gecmisi
- Musteri listesinde herhangi bir musterinin uzerine tiklayarak detay sayfasina gidin
- Son 30 gunluk siparis gecmisini ve istatistikleri gorun

---

## 6. Rota ve Teslimat

### Rota Olusturma
1. Sol menuden "Rotalar"a tiklayin
2. Tarih secin (varsayilan: bugun)
3. "Rota Olustur" butonuna basin
4. Sofor secin ve siparisleri rotaya atayın
5. "Rotayi Optimize Et" ile Google Maps uzerinden en verimli sira hesaplanir
6. Tahmini mesafe (km) ve sure (dk) gosterilir

### Rota Haritasi
- Her rotanin yanindaki "Haritada Gor" butonuyla teslimat noktalarini harita uzerinde gorebilirsiniz
- Yesil: Teslim edilen
- Kirmizi: Bekleyen
- Mavi cizgi: Onerilen rota

---

## 7. Sofor Paneli

Sofor hesabiyla giris yaptiginizda otomatik olarak Sofor Paneli acilir.

### Gunluk Goruntusu
- Bugunku rotaniz ve teslimat kartlariniz listelenir
- Her kartta:
  - Musteri adi, sira numarasi
  - Porsiyon sayisi
  - Kap tipi (renkli badge)
  - Cesit sayisi
  - Adres
  - Varsa ozel not (sari uyari)

### Teslim Etme
1. Musteriye ulastiginizda kart uzerindeki **"Teslim Et"** butonuna basin
2. Acilan modalda:
   - Opsiyonel olarak not girin (ornegin "Resepsiyona teslim", "Kapida birakildi")
   - Veya hizli seceneklerden birine tiklayin
3. "Teslim Et" butonuna basin
4. Kart "Teslim Edildi" olarak isaretlenir

### Problem Bildirme
Eger teslimat yapilamiyorsa:
1. Kart uzerindeki **"Problem"** butonuna basin
2. Problem tipini secin:
   - Musteri yok / Kapali
   - Adres bulunamadi
   - Siparis reddedildi
   - Diger
3. Aciklama yazin (zorunlu degil)
4. "Problem Bildir" butonuna basin
5. Yonetim otomatik olarak bilgilendirilir

### Gunluk Rota Navigasyonu
- Sayfanin altindaki **"Rotayi Baslat"** butonuna basin
- Google Maps uygulamasi acilir ve tum kalan teslimat noktalari sirasiyla gosterilir
- Teslim ettiginiz musteriler atlanir, sadece kalanlara navigasyon yapilir

### Rotayi Tamamla
- Tum teslimatlar yapildiktan sonra **"Rotayi Tamamla"** butonuna basin
- Rota durumu "tamamlandi" olarak guncellenir

---

## 8. Mutfak Paneli

### Gunluk Hazirlama Listesi
1. Sol menuden "Mutfak"a tiklayin
2. Bugunku siparisler toplam porsiyon ve kap tipine gore listelenir
3. Her yemek cesidi icin gerekli malzeme miktarlari gosterilir

### Malzeme Eksik Uyarisi
- Stokta yetersiz malzeme varsa hazirlama listesinde **kirmizi uyari** gosterilir
- Boylece satin alma birimi onceden bilgilendirilir

### Yazdirma
- **"Yazdir"** butonuna basarak hazirlama listesini yazicidan cikarabilirsiniz
- Yazdirma dosyasi temiz formatlanmistir (gereksiz menü ve butonlar gizlenir)

---

## 9. Menu Planlama

### Haftalik Menu Olusturma
1. Sol menuden "Haftalik Menu"ye tiklayin
2. Haftayi secin
3. Her gun icin 4 yemek cesidi girin (corba, ana yemek, yan yemek, tatli vb.)
4. Her yemek icin kayitli recetelerden secim yapin
5. "Kaydet" butonuna basin

### Menu Yazdirma
- **"PDF Yazdir"** butonuyla haftanin menusunu temiz formatta PDF olarak indirebilirsiniz
- Bu PDF musterilere gonderilebilir

---

## 10. Diyetisyen Modulu

### Mal Kabul Islemi
1. Sol menuden "Diyetisyen"e tiklayin
2. Bekleyen tedarikler listelenir
3. Her tedarik icin:
   - Malzeme kalitesini kontrol edin
   - "Kabul Et" veya "Red" butonuna basin
   - Red durumunda sebebi yazin

### Recete Kontrolu
- Recete detaylarina girerek besin degerlerini inceleyin
- Malzeme miktarlarini guncelleyin

---

## 11. Envanter (Depo)

### Stok Takibi
1. Sol menuden "Depo"ya tiklayin
2. Tum malzemeler listelenir:
   - Malzeme adi, mevcut stok, minimum stok, birim
   - Dusuk stoklar **kirmizi** ile vurgulanir

### Stok Girisi/Cikisi
- Malzeme uzerine tiklayarak stok hareketlerini gorun
- "Stok Ekle" veya "Stok Cikar" ile manuel giris yapin

### Minimum Stok Seviyesi
- Her malzeme icin minimum stok seviyesi tanimlanabilir
- Stok bu seviyenin altina dustugunde otomatik uyari olusur

---

## 12. Malzeme Planlama

### Haftalik Ihtiyac Hesaplama
1. Sol menuden "Malzeme Planlama"ya tiklayin
2. Haftayi secin
3. O haftanin menusundeki receteler baz alinarak toplam malzeme ihtiyaci hesaplanir
4. Mevcut stok ile karsilastirilir
5. Eksik malzemeler listelenir

---

## 13. Satin Alma

### Satin Alma Siparisi Olusturma
1. Sol menuden "Satinalma"ya tiklayin
2. "Yeni Siparis" butonuna basin
3. Tedarikci secin
4. Malzemeleri ve miktarlarini girin
5. "Kaydet" butonuna basin

### Siparis Takibi
- Siparisler durumlarini takip edin: Bekliyor > Onaylandi > Teslim Alindi
- Teslim alinan malzemeler otomatik olarak envantere eklenir

---

## 14. Muhasebe / ERP

### Fatura Olusturma
1. Sol menuden "Muhasebe / ERP"ye tiklayin
2. "Faturalar" tabina gidin
3. "Yeni Fatura" butonuna basin
4. Musteri secin, donem secin
5. Sistem otomatik olarak hesaplar:
   - Porsiyon sayisi x Birim fiyat = Ara toplam
   - %10 KDV hesaplanir
   - Toplam tutar gosterilir
6. "Olustur" butonuna basin

### Fatura PDF
- Fatura listesinde **"PDF"** butonuna basarak profesyonel formatta PDF indirebilirsiniz
- PDF icerir: firma logosu, musteri bilgisi, donem detaylari, kalem listesi, KDV, toplam

### Odeme Kaydi
1. "Odemeler" tabina gidin
2. "Odeme Ekle" butonuna basin
3. Musteri, fatura, tutar, odeme yontemi (nakit/havale/eft/cek) secin
4. "Kaydet" butonuna basin

### Cari Hesap
- "Cari Hesap" tabinda musteri bazli borc/alacak/bakiye takibi yapabilirsiniz
- Her musterinin toplam borcu, yaptigi odemeler ve kalan bakiyesi gosterilir

### Gelir-Gider Takibi
- "Gelir/Gider" tabinda tum mali hareketleri gorun
- Yeni gelir veya gider kaydi ekleyin
- Kategoriler: personel, malzeme, kira, nakliye, enerji, vergi, bakim, pazarlama, sigorta, ekipman, yakit, diger

---

## 15. Raporlar

Sol menuden "Raporlar"a tiklayin. 5 farkli rapor tipi mevcuttur:

### Gunluk Rapor
- Tarih secin ve "Goster" butonuna basin
- **Gosterilen bilgiler:**
  - Toplam siparis, porsiyon, teslim edilen, bekleyen, iptal
  - Kap tipi dagilimi (pasta grafik)
  - Rota ozeti tablosu (sofor, porsiyon, teslim orani, durum)
  - Tum siparis detaylari tablosu
  - Problem kayitlari (varsa)
- **CSV Indir** butonuyla raporu Excel'e aktarabilirsiniz

### Haftalik Rapor
- Baslangic ve bitis tarihlerini secin
- **Gosterilen bilgiler:**
  - Toplam siparis, porsiyon, teslim, farkli musteri, gelir, gider
  - Gunluk porsiyon trendi (sutun grafik)
  - Kap tipi dagilimi (pasta grafik)
  - En cok siparis veren musteriler tablosu

### Musteri Raporu
- Dropdown'dan musteri secin, donem belirleyin
- **Gosterilen bilgiler:**
  - Siparis sayisi, porsiyon, ortalama porsiyon, teslim, bakiye
  - Porsiyon trendi (cizgi grafik)
  - Odeme gecmisi
  - Siparis gecmisi tablosu

### Stok Raporu
- **Gosterilen bilgiler:**
  - Dusuk stok uyarilari (kirmizi cerceveli)
  - Son 7 gun tuketim tablosu
  - Son 7 gun stok girisi tablosu
  - Tum stok durumu (44 kalem)

### Sofor Performansi
- Baslangic ve bitis tarihlerini secin
- **Gosterilen bilgiler:**
  - Sofor bazli performans tablosu (rota, siparis, teslim, iptal, porsiyon, km, tamamlama %)
  - Porsiyon karsilastirmasi (sutun grafik)
  - Problem istatistikleri
  - Gunluk rota detaylari

---

## 16. Bildirimler

Sag ust kosedeki **zil ikonu** ile bildirimlere ulasabilirsiniz.

- Kirmizi badge: Okunmamis bildirim sayisi
- Tiklayinca dropdown acilir
- Bildirim turleri:
  - **Dusuk Stok:** Bir malzeme minimum seviyenin altina dustu
  - **Odenmemis Fatura:** Vadesi gecmis fatura var
  - **Teslimat Tamamlandi:** Bir rota tamamlandi
  - **Yeni Siparis:** Yeni siparis olusturuldu
  - **Problem Bildirimi:** Sofor teslimat problemi bildirdi
- Bildirimler 30 saniyede bir otomatik kontrol edilir

---

## 17. Telegram Bot

Telegram uzerinden siparis almak ve sirket ici iletisim icin bot kullanilmaktadir.

### Musteri Olarak (Birebir Mesaj)

Musteriler bota dogrudan mesaj atarak:

- **Siparis vermek icin:** "Merhaba, ben Ahmet, Vi Teknik'ten. Yarin 15 kisilik yemek gonderin."
  - Bot musteriyi otomatik tanir ve siparis olusturur
- **Menu sormak icin:** "bugun menu ne?" veya /menu komutu
- **Siparis sorgulamak icin:** "siparisim ne?" veya "siparisim nerede?"
- **Gecmis siparisler:** "siparis gecmisim"
- **Siparis iptali:** "iptal" yazin, bot onay ister

### Sirket Ici Grup

Bot, belirlenen sirket grubuna otomatik bildirimler gonderir:
- Sabah: Gunun menusu
- Siparis alindikca: Toplam ozet
- Rota tamamlaninca: Sofor bilgisi
- Stok dusunce: Uyari mesaji

Grup icinde su komutlar kullanilabilir:
- **"ozet"** veya **"gunluk rapor"** - Gunluk siparis ozeti
- **"haftalik"** - Haftalik rapor
- **"rotalar"** - Rota durumlari
- **"stok"** - Dusuk stok uyarilari

---

## 18. Mobil Kullanim (PWA)

Sistem, Progressive Web App (PWA) olarak calismaktadir. Telefonunuzda uygulama gibi kullanmak icin:

### iPhone / Safari
1. Safari'de uygulamayi acin
2. Alt taraftaki "Paylas" ikonuna basin
3. "Ana Ekrana Ekle" secenegine basin
4. "Ekle" butonuna basin

### Android / Chrome
1. Chrome'da uygulamayi acin
2. Adres cubugunun yanindaki menu ikonuna basin (3 nokta)
3. "Ana Ekrana Ekle" secenegine basin
4. "Ekle" butonuna basin

Artik telefonunuzun ana ekranindan dogrudan uygulamayi acabilirsiniz.

**Not:** Ozellikle soforler icin mobil kullanim onerilmektedir. Sofor paneli mobil cihazlara optimize edilmistir.

---

## 19. Sik Sorulan Sorular

### Sifre mi unuttum?
Yonetici (admin) hesabindan sifrenizi sifirlatmaniz gerekmektedir.

### Siparis nasil iptal edilir?
Siparisler sayfasinda ilgili siparisin durumunu "Iptal" olarak degistirin. Teslim edilmis siparisler iptal edilemez.

### Musteri adresi haritada gorunmuyor
Google Maps API anahtarinin dogru ayarlandigini kontrol edin. Adres yeterince detayli yazilmamis olabilir - il, ilce, mahalle, sokak, bina no bilgilerini ekleyin.

### Rota optimize edilmiyor
Google Maps Directions API'nin etkin oldugunu kontrol edin. API anahtariniz icin ilgili API'lerin (Maps JavaScript, Directions, Geocoding) aktif olmasi gerekir.

### Stok uyarisi gelmiyor
Malzemenin minimum stok seviyesinin tanimli oldugundan emin olun. "Depo" sayfasindan ilgili malzemeyi duzenleyerek minimum stok seviyesi girin.

### Telegram bot cevap vermiyor
- `TELEGRAM_BOT_TOKEN` ortam degiskeninin dogru ayarlandigini kontrol edin
- `OPENAI_API_KEY` ortam degiskeninin tanimli oldugundan emin olun
- `python agent/bot.py` komutunun calistigindan emin olun
- Bot'a Telegram'dan /start komutu gonderin

### CSV dosyasinda Turkce karakterler bozuk
CSV dosyasi UTF-8-BOM formatiyla olusturulmaktadir. Excel'de acarken "Veri > Metinden" secenegi ile UTF-8 encoding secin. Alternatif olarak Google Sheets'te import edebilirsiniz.

### Sistem yavasti
- Veritabaninin boyutunu kontrol edin
- `python database/migrate.py` ile indexlerin olusturulduguna emin olun
- Tarayici cache'ini temizleyin

---

## Teknik Destek

Sistem ile ilgili sorunlariniz icin yonetici (admin) ile iletisime gecin.

---

*Bu kilavuz Basak Yemek Catering Yonetim Sistemi v2.0 icin hazirlanmistir.*
*Son guncelleme: Subat 2026*
