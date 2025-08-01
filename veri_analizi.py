import pandas as pd
import numpy as np

class VeriAnalizi:
    def __init__(self, df):
        """
        Karlılık analizi sonuçlarını analiz eden sınıf
        
        Args:
            df: Pandas DataFrame - Karlılık analizi sonuç verisi
        """
        if df is None or df.empty:
            self.original_df = pd.DataFrame()
            self.df = pd.DataFrame()
        else:
            # Deep copy ile güvenli kopyalama
            self.original_df = df.copy(deep=True)
            self.df = self.original_df.copy(deep=True)
        
        self.clean_data()
    
    def clean_data(self):
        """Veriyi analiz için temizle - sadece çalışma kopyasında"""
        if self.df.empty:
            return
            
        try:
            # Sayısal sütunları temizle - çalışma kopyasında
            numeric_columns = ['Birim Maliyet', 'Birim Kar', 'Net Kar']
            for col in numeric_columns:
                if col in self.df.columns:
                    try:
                        # Güvenli numeric conversion
                        self.df.loc[:, col] = pd.to_numeric(self.df[col], errors='coerce')
                        # NaN değerleri 0 ile değiştir, ama sadece numeric olmayan değerler için
                        self.df.loc[:, col] = self.df[col].fillna(0)
                    except (KeyError, ValueError, TypeError) as e:
                        print(f"Sütun temizleme hatası {col}: {e}")
                        # Hata durumunda sütunu 0 ile doldur
                        self.df.loc[:, col] = 0
            
            # Miktar sütununu bul ve temizle
            miktar_cols = ['Satış Miktar', 'Satış\nMiktar', 'Satis Miktar', 'Miktar']
            for col in miktar_cols:
                if col in self.df.columns:
                    try:
                        self.df.loc[:, col] = pd.to_numeric(self.df[col], errors='coerce')
                        self.df.loc[:, col] = self.df[col].fillna(0)
                        break  # İlk bulunanı işle ve çık
                    except (KeyError, ValueError, TypeError) as e:
                        print(f"Miktar sütunu temizleme hatası {col}: {e}")
                        continue
                        
        except Exception as e:
            print(f"Genel veri temizleme hatası: {e}")
    
    def get_kpi_summary(self):
        """Temel KPI özetini döndür"""
        if self.df.empty:
            return self._get_empty_kpi()
        
        try:
            # Güvenli kar hesaplama
            net_kar_col = 'Net Kar'
            if net_kar_col not in self.df.columns:
                return self._get_empty_kpi()
            
            # Sadece sayısal değerleri al
            kar_series = pd.to_numeric(self.df[net_kar_col], errors='coerce')
            valid_kar_series = kar_series.dropna()
            
            # Toplam kar
            toplam_kar = float(valid_kar_series.sum()) if not valid_kar_series.empty else 0.0
            
            # En karlı ürün
            en_karli_urun = 'Veri Yok'
            en_karli_urun_kar = 0.0
            
            if not valid_kar_series.empty and len(self.df) > 0:
                try:
                    max_kar_idx = valid_kar_series.idxmax()
                    if pd.notna(max_kar_idx) and max_kar_idx in self.df.index:
                        # Stok ismi sütununu bul
                        stok_col = self.find_stok_column()
                        if stok_col and stok_col in self.df.columns:
                            product_name = self.df.loc[max_kar_idx, stok_col]
                            en_karli_urun = str(product_name) if pd.notna(product_name) else "Bilinmiyor"
                            en_karli_urun_kar = float(valid_kar_series.loc[max_kar_idx])
                except (KeyError, IndexError, ValueError, TypeError) as e:
                    print(f"En karlı ürün bulma hatası: {e}")
            
            # Ortalama kar
            ortalama_kar = float(valid_kar_series.mean()) if not valid_kar_series.empty else 0.0
            
            # Ürün sayıları - güvenli hesaplama
            toplam_urun = len(self.df)
            try:
                pozitif_kar_urun = len(valid_kar_series[valid_kar_series > 0])
                negatif_kar_urun = len(valid_kar_series[valid_kar_series < 0])
            except (KeyError, TypeError):
                pozitif_kar_urun = 0
                negatif_kar_urun = 0
            
            # Toplam satış miktarı
            toplam_satis_miktar = 0.0
            miktar_col = self.find_miktar_column()
            if miktar_col and miktar_col in self.df.columns:
                try:
                    miktar_series = pd.to_numeric(self.df[miktar_col], errors='coerce')
                    valid_miktar = miktar_series.dropna()
                    toplam_satis_miktar = float(valid_miktar.sum()) if not valid_miktar.empty else 0.0
                except (KeyError, TypeError, ValueError):
                    toplam_satis_miktar = 0.0
            
            return {
                'toplam_kar': round(toplam_kar, 2),
                'en_karli_urun': en_karli_urun,
                'en_karli_urun_kar': round(en_karli_urun_kar, 2),
                'ortalama_kar': round(ortalama_kar, 2),
                'toplam_urun': int(toplam_urun),
                'pozitif_kar_urun': int(pozitif_kar_urun),
                'negatif_kar_urun': int(negatif_kar_urun),
                'toplam_satis_miktar': round(toplam_satis_miktar, 0)
            }
            
        except Exception as e:
            print(f"KPI hesaplama hatası: {e}")
            return self._get_empty_kpi()
    
    def _get_empty_kpi(self):
        """Boş KPI yapısı döndür"""
        return {
            'toplam_kar': 0,
            'en_karli_urun': 'Veri Yok',
            'en_karli_urun_kar': 0,
            'ortalama_kar': 0,
            'toplam_urun': 0,
            'pozitif_kar_urun': 0,
            'negatif_kar_urun': 0,
            'toplam_satis_miktar': 0
        }
    
    def find_stok_column(self):
        """Stok ismi sütununu bul"""
        if self.df.empty:
            return None
            
        # Olasılık sırasına göre arama
        possible_patterns = [
            ['stok', 'ismi'],
            ['stok', 'isim'],
            ['stok', 'kodu'],
            ['stok', 'kod'],
            ['ürün', 'adı'],
            ['urun', 'adi'],
            ['ürün'],
            ['urun']
        ]
        
        # Önce tam eşleşme ara
        for col in self.df.columns:
            col_lower = str(col).lower().strip()
            for pattern in possible_patterns:
                if all(term in col_lower for term in pattern):
                    return col
        
        # Alternatif: İlk sütunu kullan
        return self.df.columns[0] if len(self.df.columns) > 0 else None
    
    def get_top_profitable_products(self, limit=10):
        """En karlı ürünleri döndür"""
        if self.df.empty or 'Net Kar' not in self.df.columns:
            return pd.DataFrame()
        
        try:
            stok_col = self.find_stok_column()
            if not stok_col or stok_col not in self.df.columns:
                return pd.DataFrame()
            
            # Numeric conversion ve güvenli filtreleme
            df_copy = self.df.copy()
            df_copy['Net Kar'] = pd.to_numeric(df_copy['Net Kar'], errors='coerce')
            
            # Geçerli kar değerleri olan satırları filtrele
            valid_df = df_copy.dropna(subset=['Net Kar'])
            if valid_df.empty:
                return pd.DataFrame()
            
            # Net kara göre sırala ve ilk N'i al
            top_df = valid_df.nlargest(limit, 'Net Kar')
            
            # Sadde gerekli sütunları al
            result_cols = [stok_col, 'Net Kar']
            if 'Birim Kar' in top_df.columns:
                result_cols.append('Birim Kar')
            
            # Miktar sütununu bul ve ekle
            miktar_col = self.find_miktar_column()
            if miktar_col and miktar_col in top_df.columns:
                result_cols.append(miktar_col)
            
            available_cols = [col for col in result_cols if col in top_df.columns]
            if not available_cols:
                return pd.DataFrame()
                
            return top_df[available_cols].reset_index(drop=True)
            
        except Exception as e:
            print(f"Top karlı ürünler hatası: {e}")
            return pd.DataFrame()
    
    def get_top_selling_products(self, limit=10):
        """En çok satan ürünleri döndür"""
        if self.df.empty:
            return pd.DataFrame()
        
        try:
            miktar_col = self.find_miktar_column()
            stok_col = self.find_stok_column()
            
            if not miktar_col or not stok_col or miktar_col not in self.df.columns or stok_col not in self.df.columns:
                return pd.DataFrame()
            
            # Numeric conversion ve güvenli filtreleme
            df_copy = self.df.copy()
            df_copy[miktar_col] = pd.to_numeric(df_copy[miktar_col], errors='coerce')
            
            # Geçerli miktar değerleri olan satırları filtrele
            valid_df = df_copy.dropna(subset=[miktar_col])
            if valid_df.empty:
                return pd.DataFrame()
            
            # Miktara göre sırala
            top_df = valid_df.nlargest(limit, miktar_col)
            
            # Gerekli sütunları al
            result_cols = [stok_col, miktar_col]
            if 'Net Kar' in top_df.columns:
                result_cols.append('Net Kar')
            if 'Birim Kar' in top_df.columns:
                result_cols.append('Birim Kar')
            
            available_cols = [col for col in result_cols if col in top_df.columns]
            if not available_cols:
                return pd.DataFrame()
                
            return top_df[available_cols].reset_index(drop=True)
            
        except Exception as e:
            print(f"Top satan ürünler hatası: {e}")
            return pd.DataFrame()
    
    def find_miktar_column(self):
        """Satış miktar sütununu bul"""
        if self.df.empty:
            return None
            
        # Öncelik sırasına göre arama
        possible_names = ['Satış Miktar', 'Satış\nMiktar', 'Satis Miktar', 'Miktar']
        
        # Tam eşleşme ara
        for col in self.df.columns:
            if col in possible_names:
                return col
        
        # Kısmi eşleşme ara
        for col in self.df.columns:
            try:
                col_lower = str(col).lower().strip()
                if 'miktar' in col_lower and ('satış' in col_lower or 'satis' in col_lower):
                    return col
            except (AttributeError, TypeError):
                continue
        
        # Sadece 'miktar' içeren sütun ara
        for col in self.df.columns:
            try:
                if 'miktar' in str(col).lower():
                    return col
            except (AttributeError, TypeError):
                continue
        
        return None
    
    def get_low_profit_products(self, limit=10):
        """En düşük karlı ürünleri döndür"""
        if self.df.empty or 'Net Kar' not in self.df.columns:
            return pd.DataFrame()
        
        try:
            stok_col = self.find_stok_column()
            if not stok_col or stok_col not in self.df.columns:
                return pd.DataFrame()
            
            # Numeric conversion ve güvenli filtreleme
            df_copy = self.df.copy()
            df_copy['Net Kar'] = pd.to_numeric(df_copy['Net Kar'], errors='coerce')
            
            # Geçerli kar değerleri olan satırları filtrele
            valid_df = df_copy.dropna(subset=['Net Kar'])
            if valid_df.empty:
                return pd.DataFrame()
            
            # Net kara göre artan sırala ve ilk N'i al
            low_df = valid_df.nsmallest(limit, 'Net Kar')
            
            # Gerekli sütunları al
            result_cols = [stok_col, 'Net Kar']
            if 'Birim Kar' in low_df.columns:
                result_cols.append('Birim Kar')
            
            miktar_col = self.find_miktar_column()
            if miktar_col and miktar_col in low_df.columns:
                result_cols.append(miktar_col)
            
            available_cols = [col for col in result_cols if col in low_df.columns]
            if not available_cols:
                return pd.DataFrame()
                
            return low_df[available_cols].reset_index(drop=True)
            
        except Exception as e:
            print(f"Düşük karlı ürünler hatası: {e}")
            return pd.DataFrame()
    
    def get_profit_distribution(self):
        """Kar dağılımı analizi"""
        if self.df.empty or 'Net Kar' not in self.df.columns:
            return {
                'cok_karli': 0,
                'orta_karli': 0,
                'dusuk_karli': 0,
                'zararda': 0
            }
        
        try:
            # Numeric conversion ve geçerli değerleri al
            kar_series = pd.to_numeric(self.df['Net Kar'], errors='coerce')
            kar_data = kar_series.dropna()
            
            if kar_data.empty:
                return {
                    'cok_karli': 0,
                    'orta_karli': 0,
                    'dusuk_karli': 0,
                    'zararda': 0
                }
            
            # Kar kategorileri - güvenli hesaplama
            zararda = len(kar_data[kar_data < 0])
            
            # Quantile hesaplama - güvenli
            try:
                # Sadece pozitif değerler için quantile
                pozitif_kar = kar_data[kar_data >= 0]
                if not pozitif_kar.empty and len(pozitif_kar) > 1:
                    q25 = pozitif_kar.quantile(0.25)
                    q75 = pozitif_kar.quantile(0.75)
                else:
                    q25 = 0
                    q75 = pozitif_kar.max() if not pozitif_kar.empty else 0
            except (ValueError, TypeError):
                q25 = 0
                q75 = kar_data.max() if not kar_data.empty else 0
            
            # Kategorilere ayır
            if q25 == q75:  # Tüm değerler aynı ise
                dusuk_karli = len(kar_data[(kar_data >= 0) & (kar_data < q75)]) if q75 > 0 else len(kar_data[kar_data >= 0])
                orta_karli = 0
                cok_karli = len(kar_data[kar_data >= q75]) if q75 > 0 else 0
            else:
                dusuk_karli = len(kar_data[(kar_data >= 0) & (kar_data < q25)])
                orta_karli = len(kar_data[(kar_data >= q25) & (kar_data < q75)])
                cok_karli = len(kar_data[kar_data >= q75])
            
            return {
                'cok_karli': int(cok_karli),
                'orta_karli': int(orta_karli),
                'dusuk_karli': int(dusuk_karli),
                'zararda': int(zararda)
            }
            
        except Exception as e:
            print(f"Kar dağılımı hatası: {e}")
            return {
                'cok_karli': 0,
                'orta_karli': 0,
                'dusuk_karli': 0,
                'zararda': 0
            }
    
    def search_product(self, search_term):
        """Ürün arama"""
        if self.df.empty or not search_term:
            return pd.DataFrame()
        
        try:
            stok_col = self.find_stok_column()
            if not stok_col or stok_col not in self.df.columns:
                return pd.DataFrame()
            
            # String tipine çevir ve güvenli arama yap
            search_series = self.df[stok_col].astype(str)
            
            # Büyük/küçük harf duyarsız arama - regex kapalı
            search_term_clean = str(search_term).strip()
            if not search_term_clean:
                return pd.DataFrame()
                
            try:
                mask = search_series.str.contains(search_term_clean, case=False, na=False, regex=False)
                result = self.df[mask]
                return result.reset_index(drop=True)
            except Exception as search_error:
                # Alternatif arama yöntemi
                print(f"String arama hatası, alternatif yöntem deneniyor: {search_error}")
                mask = search_series.str.lower().str.contains(search_term_clean.lower(), na=False)
                result = self.df[mask]
                return result.reset_index(drop=True)
            
        except Exception as e:
            print(f"Ürün arama hatası: {e}")
            return pd.DataFrame()
    
    def get_summary_stats(self):
        """Özet istatistikler"""
        if self.df.empty:
            return {}
        
        try:
            stats = {}
            
            # Net Kar istatistikleri
            if 'Net Kar' in self.df.columns:
                try:
                    net_kar_series = pd.to_numeric(self.df['Net Kar'], errors='coerce')
                    net_kar_data = net_kar_series.dropna()
                    
                    if not net_kar_data.empty:
                        stats['kar_toplam'] = float(net_kar_data.sum())
                        stats['kar_ortalama'] = float(net_kar_data.mean())
                        stats['kar_medyan'] = float(net_kar_data.median())
                        stats['kar_std'] = float(net_kar_data.std()) if len(net_kar_data) > 1 else 0.0
                except (ValueError, TypeError) as e:
                    print(f"Net kar istatistik hatası: {e}")
            
            # Birim Kar istatistikleri
            if 'Birim Kar' in self.df.columns:
                try:
                    birim_kar_series = pd.to_numeric(self.df['Birim Kar'], errors='coerce')
                    birim_kar_data = birim_kar_series.dropna()
                    
                    if not birim_kar_data.empty:
                        stats['birim_kar_ortalama'] = float(birim_kar_data.mean())
                        stats['birim_kar_medyan'] = float(birim_kar_data.median())
                except (ValueError, TypeError) as e:
                    print(f"Birim kar istatistik hatası: {e}")
            
            # Miktar istatistikleri
            miktar_col = self.find_miktar_column()
            if miktar_col and miktar_col in self.df.columns:
                try:
                    miktar_series = pd.to_numeric(self.df[miktar_col], errors='coerce')
                    miktar_data = miktar_series.dropna()
                    
                    if not miktar_data.empty:
                        stats['miktar_toplam'] = float(miktar_data.sum())
                        stats['miktar_ortalama'] = float(miktar_data.mean())
                except (ValueError, TypeError) as e:
                    print(f"Miktar istatistik hatası: {e}")
            
            return stats
            
        except Exception as e:
            print(f"İstatistik hesaplama hatası: {e}")
            return {}