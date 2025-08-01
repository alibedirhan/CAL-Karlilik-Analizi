import pandas as pd
import numpy as np
import os
import tempfile
import gc
from tkinter import simpledialog, filedialog, messagebox

class KarlilikAnalizi:
    def __init__(self, progress_callback=None, log_callback=None):
        """
        Karlılık analizi sınıfı
        
        Args:
            progress_callback: İlerleme güncellemesi için callback fonksiyonu
            log_callback: Log mesajları için callback fonksiyonu
        """
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        
    def update_progress(self, value, status):
        """İlerleme durumunu güncelle"""
        if self.progress_callback:
            self.progress_callback(value, status)
    
    def log_message(self, message):
        """Log mesajı gönder"""
        if self.log_callback:
            self.log_callback(message)
    
    def turkce_normalize(self, text):
        """Türkçe karakterleri normalize et"""
        if pd.isna(text):
            return ""
        text = str(text).lower().strip()
        replacements = {
            'ı': 'i', 'i̇': 'i', 'İ': 'i', 'I': 'i',
            'ş': 's', 'Ş': 's', 'ç': 'c', 'Ç': 'c',
            'ğ': 'g', 'Ğ': 'g', 'ü': 'u', 'Ü': 'u',
            'ö': 'o', 'Ö': 'o'
        }
        for tr_char, en_char in replacements.items():
            text = text.replace(tr_char, en_char)
        return text
    
    def clean_numeric(self, value):
        """Sayısal değerleri temizle"""
        if pd.isna(value):
            return 0.0
        try:
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                value = value.replace('₺', '').replace('TL', '').strip()
                
                if ',' in value and '.' in value:
                    if value.rfind(',') > value.rfind('.'):
                        value = value.replace('.', '').replace(',', '.')
                    else:
                        value = value.replace(',', '')
                elif ',' in value:
                    value = value.replace(',', '.')
                
                return float(value)
        except:
            return 0.0
    
    def find_header_row(self, file_path):
        """Excel dosyasında uygun header satırını bul"""
        for header_row in [0, 1, 2, 3, 4]:
            try:
                test_df = pd.read_excel(file_path, header=header_row)
                
                if test_df.empty:
                    continue
                    
                self.log_message(f"Header {header_row} test ediliyor...")
                
                sutun_isimleri = [str(col).lower().strip() for col in test_df.columns]
                
                has_stok_ismi = any('stok' in sutun and ('ismi' in sutun or 'isim' in sutun or 'kodu' in sutun) for sutun in sutun_isimleri)
                has_satis = any('satış' in sutun or 'satis' in sutun for sutun in sutun_isimleri)
                has_miktar = any('miktar' in sutun for sutun in sutun_isimleri)
                has_fiyat = any('fiyat' in sutun for sutun in sutun_isimleri)
                has_tutar = any('tutar' in sutun for sutun in sutun_isimleri)
                
                veri_sutunu_sayisi = sum([has_satis, has_miktar, has_fiyat, has_tutar])
                if has_stok_ismi and veri_sutunu_sayisi >= 2:
                    self.log_message(f"✓ Header satırı {header_row} olarak belirlendi!")
                    return header_row
                    
            except Exception as e:
                self.log_message(f"Header {header_row} hatası: {e}")
                continue
        
        self.log_message("Uygun header bulunamadı, header=1 ile deneniyor...")
        return 1
    
    def find_stok_column(self, df):
        """Stok sütununu otomatik bul"""
        stok_ismi_col = None
        
        # Önce "stok ismi" ara
        for col in df.columns:
            col_clean = self.turkce_normalize(col)
            if 'stok' in col_clean and 'ismi' in col_clean:
                stok_ismi_col = col
                break
        
        # Bulamazsa "stok kodu" ara        
        if not stok_ismi_col:
            for col in df.columns:
                col_clean = self.turkce_normalize(col)
                if 'stok' in col_clean and 'kodu' in col_clean:
                    stok_ismi_col = col
                    break
        
        # Manuel seçim gerekirse
        if not stok_ismi_col:
            self.log_message("Stok sütunu otomatik bulunamadı, manuel seçim gerekli...")
            
            columns = list(df.columns)
            sutun_secenekleri = "\n".join([f"{i}: {col}" for i, col in enumerate(columns)])
            
            secim_str = simpledialog.askstring(
                "Sütun Seçimi",
                f"Hangi sütun stok ismi/kodu?\n\n{sutun_secenekleri}\n\nSütun numarasını girin (0-{len(columns)-1}):"
            )
            
            if secim_str is None:
                self.log_message("✗ Stok sütunu seçilmedi, işlem iptal ediliyor")
                return None
            
            try:
                secim_index = int(secim_str)
                if 0 <= secim_index < len(columns):
                    stok_ismi_col = columns[secim_index]
                else:
                    self.log_message("✗ Geçersiz sütun numarası")
                    return None
            except ValueError:
                self.log_message("✗ Geçersiz giriş")
                return None
        
        return stok_ismi_col
    
    def find_iskonto_columns(self, df):
        """İskonto dosyasından fiyat ve stok sütunlarını bul"""
        columns = df.columns.tolist()
        
        # Fiyat sütunu bul
        fiyat_col = None
        for col in columns:
            col_str = self.turkce_normalize(col)
            if 'fiyat' in col_str and 'liste' not in col_str:
                fiyat_col = col
                break
        
        # İskonto stok sütunu bul
        iskonto_stok_col = None
        for col in columns:
            col_clean = self.turkce_normalize(col)
            if 'stok' in col_clean and ('isim' in col_clean or 'ismi' in col_clean):
                iskonto_stok_col = col
                break
        
        # Manuel seçimler
        if not fiyat_col:
            self.log_message("Fiyat sütunu manuel seçim gerekli...")
            sutun_secenekleri = "\n".join([f"{i}: {col}" for i, col in enumerate(columns)])
            
            secim_str = simpledialog.askstring(
                "Fiyat Sütunu Seçimi",
                f"Hangi sütun fiyat bilgisi?\n\n{sutun_secenekleri}\n\nSütun numarasını girin:"
            )
            
            if secim_str is None:
                return None, None
            
            try:
                secim_index = int(secim_str)
                if 0 <= secim_index < len(columns):
                    fiyat_col = columns[secim_index]
            except ValueError:
                return None, None
        
        if not iskonto_stok_col:
            self.log_message("İskonto stok sütunu manuel seçim gerekli...")
            sutun_secenekleri = "\n".join([f"{i}: {col}" for i, col in enumerate(columns)])
            
            secim_str = simpledialog.askstring(
                "Stok İsmi Sütunu Seçimi",
                f"Hangi sütun stok ismi?\n\n{sutun_secenekleri}\n\nSütun numarasını girin:"
            )
            
            if secim_str is None:
                return None, None
            
            try:
                secim_index = int(secim_str)
                if 0 <= secim_index < len(columns):
                    iskonto_stok_col = columns[secim_index]
            except ValueError:
                return None, None
        
        return fiyat_col, iskonto_stok_col
    
    def create_price_dictionary(self, iskonto_df, iskonto_stok_col, fiyat_col):
        """İskonto dosyasından fiyat sözlüğü oluştur"""
        fiyat_dict = {}
        baslik_sayisi = 0
        
        try:
            for idx, row in iskonto_df.iterrows():
                stok_adi = row[iskonto_stok_col]
                tarih = row.get('Tarih', '')
                depo = row.get('Depo', '')
                fiyat = row[fiyat_col]
                
                stok_bos = pd.isna(stok_adi) or str(stok_adi).lower() == 'nan'
                tarih_bos = pd.isna(tarih) or str(tarih).lower() == 'nan'
                
                if stok_bos and tarih_bos:
                    gercek_stok_adi = str(depo).strip()
                    
                    if (gercek_stok_adi != '' and 
                        gercek_stok_adi.lower() != 'nan' and
                        not gercek_stok_adi.startswith('İZMİR BÖLGE') and
                        fiyat > 0 and
                        gercek_stok_adi not in fiyat_dict):
                        
                        fiyat_dict[gercek_stok_adi] = round(fiyat, 2)
                        baslik_sayisi += 1
                        
                        if baslik_sayisi <= 5:
                            self.log_message(f"Fiyat eşleşmesi: {gercek_stok_adi} → {fiyat}")
        
        except Exception as e:
            self.log_message(f"Fiyat işleme hatası: {e}")
        
        return fiyat_dict
    
    def match_prices(self, karlilik_df, stok_ismi_col, fiyat_dict):
        """Fiyatları eşleştir"""
        eslesen_sayisi = 0
        eslesmeyenler = []
        
        for idx, row in karlilik_df.iterrows():
            stok_adi = row[stok_ismi_col]
            
            if stok_adi in fiyat_dict:
                karlilik_df.at[idx, 'Birim Maliyet'] = fiyat_dict[stok_adi]
                eslesen_sayisi += 1
            else:
                eslesmeyenler.append(stok_adi)
        
        return eslesen_sayisi, eslesmeyenler
    
    def calculate_profits(self, karlilik_df):
        """Kar hesaplamalarını yap"""
        # Birim Kar hesaplama
        ort_satis_fiyat_col = None
        for col in karlilik_df.columns:
            col_str = self.turkce_normalize(col)
            if 'ort' in col_str and 'satis' in col_str and 'fiyat' in col_str:
                ort_satis_fiyat_col = col
                break
        
        if not ort_satis_fiyat_col:
            alternatif_fiyat_sutunlari = ['Ort.Satış\nFiyat', 'Ort Satış Fiyat', 'Ortalama Fiyat']
            for alt_col in alternatif_fiyat_sutunlari:
                if alt_col in karlilik_df.columns:
                    ort_satis_fiyat_col = alt_col
                    break
        
        if ort_satis_fiyat_col and ort_satis_fiyat_col in karlilik_df.columns:
            karlilik_df.loc[:, ort_satis_fiyat_col] = karlilik_df[ort_satis_fiyat_col].apply(self.clean_numeric)
            karlilik_df['Birim Kar'] = karlilik_df[ort_satis_fiyat_col] - karlilik_df['Birim Maliyet']
            self.log_message("✓ Birim Kar hesaplandı")
        else:
            karlilik_df['Birim Kar'] = 0.0
            self.log_message("Ort.Satış Fiyat sütunu bulunamadı")
        
        # Net Kar hesaplama
        satis_miktar_col = None
        for col in karlilik_df.columns:
            col_str = self.turkce_normalize(col)
            if 'satis' in col_str and 'miktar' in col_str:
                satis_miktar_col = col
                break
        
        if not satis_miktar_col:
            alternatif_miktar_sutunlari = ['Satış\nMiktar', 'Satis Miktar', 'Miktar']
            for alt_col in alternatif_miktar_sutunlari:
                if alt_col in karlilik_df.columns:
                    satis_miktar_col = alt_col
                    break
        
        if satis_miktar_col and satis_miktar_col in karlilik_df.columns:
            karlilik_df.loc[:, satis_miktar_col] = karlilik_df[satis_miktar_col].apply(self.clean_numeric)
            karlilik_df['Net Kar'] = karlilik_df['Birim Kar'] * karlilik_df[satis_miktar_col]
            self.log_message("✓ Net Kar hesaplandı")
        else:
            karlilik_df['Net Kar'] = 0.0
            self.log_message("Satış Miktar sütunu bulunamadı")
    
    # karlilik.py dosyasındaki prepare_result_dataframe fonksiyonunu düzelt

    def prepare_result_dataframe(self, karlilik_df, stok_ismi_col):
        """Sonuç dataframe'ini hazırla - TÜM ürünleri dahil et"""
        # Sütun seçimi
        istenen_sutunlar = []
        
        if stok_ismi_col and stok_ismi_col in karlilik_df.columns:
            istenen_sutunlar.append(stok_ismi_col)
        
        diger_sutunlar = ['Satış Miktar', 'Ort.Satış Fiyat', 'Satış Tutar', 'Birim Maliyet', 'Birim Kar', 'Net Kar']
        for sutun in diger_sutunlar:
            if sutun in karlilik_df.columns:
                istenen_sutunlar.append(sutun)
        
        # Alternatif sütun isimleri
        alternatif_sutunlar = {
            'Satış Miktar': ['Satış\nMiktar', 'Satis Miktar', 'Miktar'],
            'Ort.Satış Fiyat': ['Ort.Satış\nFiyat', 'Ort Satış Fiyat', 'Ortalama Fiyat'],
            'Satış Tutar': ['Satış\nTutar', 'Satis Tutar', 'Tutar'],
            'Birim Maliyet': ['Birim\nMaliyet', 'Maliyet'],
            'Birim Kar': ['Birim\nKar', 'Kar'],
            'Net Kar': ['Net\nKar', 'Toplam Kar']
        }
        
        for standart_isim, alternatifler in alternatif_sutunlar.items():
            if standart_isim not in istenen_sutunlar:
                for alt_isim in alternatifler:
                    if alt_isim in karlilik_df.columns:
                        istenen_sutunlar.append(alt_isim)
                        break
        
        # BURADA FİLTRELEME OLMAMALI - TÜM ÜRÜNLER DAHİL EDİLMELİ
        sonuc_df = karlilik_df[istenen_sutunlar].copy()
        
        # ÖNEMLİ: Bu satırı arayın ve varsa silin!
        # sonuc_df = sonuc_df[sonuc_df['Birim Maliyet'] > 0]  # BU SATIR VARSA SİLİN!
        
        # Sıralama
        if 'Net Kar' in sonuc_df.columns and 'Birim Kar' in sonuc_df.columns:
            sonuc_df = sonuc_df.sort_values(['Net Kar', 'Birim Kar'], ascending=[False, False])
            self.log_message("✓ Veriler Net Kar'a göre sıralandı")
        elif 'Birim Kar' in sonuc_df.columns:
            sonuc_df = sonuc_df.sort_values('Birim Kar', ascending=False)
            self.log_message("✓ Veriler Birim Kar'a göre sıralandı")
        
        # LOG: Kaç ürün dahil edildiğini kontrol et
        self.log_message(f"✓ Sonuç DataFrame'i hazırlandı: {len(sonuc_df)} ürün")
        
        return sonuc_df
    
    def save_results(self, sonuc_df, eslesen_sayisi, eslesmeyenler):
        """Sonuçları Excel dosyası olarak kaydet"""
        output_path = filedialog.asksaveasfilename(
            title="Karlılık Analizi Sonuçlarını Kaydet",
            defaultextension=".xlsx",
            filetypes=[("Excel dosyaları", "*.xlsx")]
        )
        
        if not output_path:
            self.log_message("Dosya kaydetme iptal edildi")
            return False
        
        # Güvenli özet hesaplama
        total_net_kar = sonuc_df['Net Kar'].sum() if 'Net Kar' in sonuc_df.columns else 0
        
        avg_birim_maliyet = 0
        if 'Birim Maliyet' in sonuc_df.columns:
            maliyet_data = sonuc_df[sonuc_df['Birim Maliyet'] > 0]['Birim Maliyet']
            avg_birim_maliyet = maliyet_data.mean() if len(maliyet_data) > 0 else 0
        
        avg_birim_kar = 0
        if 'Birim Kar' in sonuc_df.columns:
            kar_data = sonuc_df['Birim Kar']
            avg_birim_kar = kar_data.mean() if len(kar_data) > 0 else 0
        
        doluluk_orani = (eslesen_sayisi / len(sonuc_df) * 100) if len(sonuc_df) > 0 else 0
        
        # Excel kaydetme
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            sonuc_df.to_excel(writer, sheet_name='Karlılık Analizi', index=False)
            
            # Özet sayfası
            ozet_data = {
                'Bilgi': ['Toplam Stok Sayısı', 'Eşleşen Stok Sayısı', 'Eşleşmeyen Stok Sayısı', 
                          'Doluluk Oranı (%)', 'Ortalama Birim Maliyet', 'Ortalama Birim Kar', 'Toplam Net Kar'],
                'Değer': [
                    len(sonuc_df),
                    eslesen_sayisi,
                    len(sonuc_df) - eslesen_sayisi,
                    f"{doluluk_orani:.1f}",
                    f"{avg_birim_maliyet:.2f}",
                    f"{avg_birim_kar:.2f}",
                    f"{total_net_kar:.2f}"
                ]
            }
            ozet_df = pd.DataFrame(ozet_data)
            ozet_df.to_excel(writer, sheet_name='Özet', index=False)
        
        self.log_message(f"✓ Sonuçlar kaydedildi: {os.path.basename(output_path)}")
        self.log_message(f"📊 Özet: {eslesen_sayisi} eşleşen / {len(eslesmeyenler)} eşleşmeyen")
        self.log_message(f"📈 Doluluk Oranı: %{doluluk_orani:.1f}")
        
        return True
    
    def analyze(self, karlilik_path, iskonto_path):
        """Ana analiz fonksiyonu - DataFrame döndürür"""
        temp_files = []
        
        try:
            self.update_progress(15, "İskonto raporu yükleniyor...")
            
            # İskonto raporunu oku
            iskonto_df = pd.read_excel(iskonto_path)
            
            if iskonto_df.empty:
                self.log_message("✗ İskonto raporu dosyası boş!")
                return None
                
            self.log_message(f"✓ İskonto Raporu: {len(iskonto_df)} satır yüklendi")
            
            self.update_progress(25, "Karlılık analizi dosyası işleniyor...")
            
            # Karlılık Analizi dosyasını oku - header bul
            header_row = self.find_header_row(karlilik_path)
            karlilik_df = pd.read_excel(karlilik_path, header=header_row)
                
            if karlilik_df is None or karlilik_df.empty:
                self.log_message("✗ Karlılık Analizi dosyası boş veya okunamadı!")
                return None
                
            self.log_message("✓ Karlılık Analizi dosyası başarıyla yüklendi")
            
            self.update_progress(40, "Sütunlar analiz ediliyor...")
            
            # Stok sütunu bul
            stok_ismi_col = self.find_stok_column(karlilik_df)
            if not stok_ismi_col:
                return None
            
            self.log_message(f"✓ Stok sütunu: {stok_ismi_col}")
            
            # İskonto dosyası sütunları
            fiyat_col, iskonto_stok_col = self.find_iskonto_columns(iskonto_df)
            if not fiyat_col or not iskonto_stok_col:
                return None
            
            self.log_message(f"✓ Bulunan sütunlar: Stok={stok_ismi_col}, Fiyat={fiyat_col}")
            
            # Sütun kontrolleri
            if stok_ismi_col not in karlilik_df.columns:
                self.log_message("✗ Stok sütunu bulunamadı!")
                return None
            if iskonto_stok_col not in iskonto_df.columns:
                self.log_message("✗ İskonto stok sütunu bulunamadı!")
                return None
            if fiyat_col not in iskonto_df.columns:
                self.log_message("✗ Fiyat sütunu bulunamadı!")
                return None
            
            self.update_progress(60, "Veriler temizleniyor...")
            
            # Birim Maliyet sütunu ekle
            if 'Birim Maliyet' not in karlilik_df.columns:
                karlilik_df['Birim Maliyet'] = 0.0
            
            # Veri temizleme
            karlilik_df = karlilik_df[karlilik_df[stok_ismi_col].notna()].copy()
            iskonto_df = iskonto_df[iskonto_df[iskonto_stok_col].notna()].copy()
            
            if karlilik_df.empty or iskonto_df.empty:
                self.log_message("✗ Veriler temizleme sonrası boş kaldı!")
                return None
            
            # String temizleme
            karlilik_df.loc[:, stok_ismi_col] = karlilik_df[stok_ismi_col].astype(str).str.strip().str.upper()
            iskonto_df.loc[:, iskonto_stok_col] = iskonto_df[iskonto_stok_col].astype(str).str.strip().str.upper()
            
            # TOPLAM satırlarını kaldır
            karlilik_df = karlilik_df[~karlilik_df[stok_ismi_col].str.contains('TOPLAM|TOTAL|GENEL', case=False, na=False)].copy()
            iskonto_df = iskonto_df[~iskonto_df[iskonto_stok_col].str.contains('TOPLAM|TOTAL|GENEL', case=False, na=False)].copy()
            
            self.update_progress(70, "Fiyat bilgileri işleniyor...")
            
            iskonto_df.loc[:, fiyat_col] = iskonto_df[fiyat_col].apply(self.clean_numeric)
            
            # CSV işleme
            try:
                with tempfile.NamedTemporaryFile(mode='w+', suffix='.csv', delete=False, encoding='utf-8') as temp_file:
                    csv_path = temp_file.name
                    temp_files.append(csv_path)
                
                temp_df = pd.read_excel(iskonto_path)
                temp_df.to_csv(csv_path, index=False, encoding='utf-8')
                csv_df = pd.read_csv(csv_path, encoding='utf-8')
                iskonto_df = csv_df.copy()
                
                del temp_df, csv_df
                gc.collect()
                
            except Exception as e:
                self.log_message(f"CSV çevirme hatası: {e}")
            
            self.update_progress(80, "Fiyat eşleştirme yapılıyor...")
            
            # Fiyat dictionary oluştur
            fiyat_dict = self.create_price_dictionary(iskonto_df, iskonto_stok_col, fiyat_col)
            self.log_message(f"✓ {len(fiyat_dict)} stok için fiyat bilgisi alındı")
            
            self.update_progress(85, "Stok eşleştirme yapılıyor...")
            
            # Eşleştirme işlemi
            eslesen_sayisi, eslesmeyenler = self.match_prices(karlilik_df, stok_ismi_col, fiyat_dict)
            
            # Birim Maliyet temizleme
            karlilik_df['Birim Maliyet'] = karlilik_df['Birim Maliyet'].apply(self.clean_numeric)
            
            self.update_progress(90, "Kar hesaplamaları yapılıyor...")
            
            # Kar hesaplamalarını yap
            self.calculate_profits(karlilik_df)
            
            self.log_message(f"✓ Eşleştirme tamamlandı: {eslesen_sayisi} eşleşen, {len(eslesmeyenler)} eşleşmeyen")
            
            self.update_progress(95, "Sonuçlar kaydediliyor...")
            
            # Sonuç dataframe'ini hazırla
            sonuc_df = self.prepare_result_dataframe(karlilik_df, stok_ismi_col)
            
            # Dosya kaydetme
            save_result = self.save_results(sonuc_df, eslesen_sayisi, eslesmeyenler)
            
            # Başarılı kayıt sonrası DataFrame'i döndür
            if save_result:
                return sonuc_df
            else:
                return None
                
        except Exception as e:
            self.log_message(f"✗ HATA: {str(e)}")
            return None
        finally:
            # Temizlik
            for temp_file in temp_files:
                try:
                    if temp_file and os.path.exists(temp_file):
                        os.unlink(temp_file)
                except:
                    pass
            gc.collect()