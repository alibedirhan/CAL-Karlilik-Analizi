# 📊 Karlılık Analizi Uygulaması

Excel tabanlı karlılık ve iskonto raporu analiz uygulaması. İşletmelerin ürün bazlı kar analizlerini kolayca yapabilmelerini sağlar.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey.svg)

## 🎯 Özellikler

- ✨ **Modern Arayüz**: Tkinter tabanlı kullanıcı dostu arayüz
- 📊 **Dashboard**: Detaylı analiz sonuçları ve görselleştirme
- 🔍 **Akıllı Eşleştirme**: Karlılık ve iskonto verilerini otomatik eşleştirir
- 📈 **KPI Kartları**: Temel performans göstergelerini görüntüler
- 🔎 **Arama ve Filtreleme**: Ürün bazlı detaylı arama imkanı
- 📑 **Excel Çıktı**: Sonuçları Excel formatında kaydetme

## 🚀 Hızlı Başlangıç

### Gereksinimler

- Python 3.8 veya üzeri
- pip paket yöneticisi

### Kurulum

1. **Repository'yi klonlayın:**
```bash
git clone https://github.com/alibedirhan/CAL-Karlilik-Analizi.git
cd CAL-Karlilik-Analizi
```

2. **Gerekli paketleri yükleyin:**
```bash
pip install -r requirements.txt
```

3. **Uygulamayı çalıştırın:**
```bash
python gui.py
```

## 📦 Windows EXE İndirme

Windows kullanıcıları için hazır exe dosyası:

➡️ **[En Son Sürümü İndir](https://github.com/alibedirhan/CAL-Karlilik-Analizi/releases/latest)**

- İndirdiğiniz exe dosyasını çift tıklayarak çalıştırabilirsiniz
- Python kurulumuna gerek yoktur

## 📋 Kullanım Kılavuzu

### 1. Dosya Hazırlığı
- **Karlılık Analizi Dosyası**: Excel formatında ürün satış verileri
- **İskonto Raporu**: Bupiliç iskonto raporu Excel dosyası

### 2. Analiz Adımları
1. Uygulama açıldığında "Dosya Seçimi" bölümünden gerekli Excel dosyalarını seçin
2. "Analizi Başlat" butonuna tıklayın
3. İşlem tamamlandığında sonuç dosyasını kaydedin
4. Dashboard sekmesinden detaylı analizleri görüntüleyin

### 3. Dashboard Özellikleri
- **Performans Özeti**: Toplam kar, en karlı ürün gibi KPI'lar
- **Top Ürünler**: En karlı ve en çok satan ürün listeleri
- **Kar Dağılımı**: Ürünlerin kar kategorilerine göre dağılımı
- **Arama ve Filtreleme**: Ürün bazlı detaylı sorgulama

## 🖥️ Ekran Görüntüleri

### Ana Ekran
![Ana Ekran](docs/screenshots/ana-ekran.png)

### Dashboard
![Dashboard](docs/screenshots/dashboard.png)

## 🛠️ Geliştirme

### Proje Yapısı
```
├── gui.py                 # Ana arayüz
├── karlilik.py           # Karlılık analizi motoru
├── veri_analizi.py       # Veri analizi sınıfı
├── analiz_dashboard.py   # Dashboard arayüzü
├── dashboard_components.py # UI bileşenleri
├── requirements.txt      # Python bağımlılıkları
└── README.md            # Bu dosya
```

### Katkıda Bulunma
1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/YeniOzellik`)
3. Commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'e push edin (`git push origin feature/YeniOzellik`)
5. Pull Request açın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🐛 Hata Bildirimi

Hata bulduysanız veya öneriniz varsa [Issues](https://github.com/alibedirhan/CAL-Karlilik-Analizi/issues) sayfasından bildirebilirsiniz.

## 📞 İletişim

- GitHub: [@alibedirhan](https://github.com/alibedirhan)
- Email: alibedirhan.d@gmail.com

---

⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!
