# analiz_dashboard.py - Ana Dashboard Sınıfı - HATASIZ VERSİYON

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import platform
from veri_analizi import VeriAnalizi
from dashboard_components import DashboardComponents

class AnalyzDashboard:
    def __init__(self, parent_notebook, df):
        """
        Modern Dashboard arayüzü - Refactored version
        """
        self.notebook = parent_notebook
        self.df = df.copy() if df is not None and not df.empty else pd.DataFrame()
        
        # Platform belirleme
        self.os_platform = platform.system()
        
        # VeriAnalizi nesnesini güvenli şekilde oluştur
        try:
            self.analiz = VeriAnalizi(self.df)
        except Exception as e:
            print(f"VeriAnalizi oluşturma hatası: {e}")
            self.analiz = None
        
        # Renk paletini components'ten al
        self.colors = DashboardComponents.COLORS
        
        # Dashboard frame'i oluştur
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.setup_dashboard()
        
    def get_frame(self):
        """Dashboard frame'ini döndür"""
        return self.dashboard_frame
    
    def setup_dashboard(self):
        """Modern Dashboard arayüzünü oluştur"""
        try:
            # Ana scroll frame
            self.create_enhanced_scrollable_frame()
            
            # Header
            self.create_modern_header()
            
            # KPI kartları
            self.create_enhanced_kpi_section()
            
            # Analiz sekmeleri
            self.create_analysis_tabs()
            
            # Arama bölümü
            self.create_enhanced_search_section()
        except Exception as e:
            print(f"Dashboard kurulum hatası: {e}")
    
    def create_enhanced_scrollable_frame(self):
        """GELİŞTİRİLMİŞ scroll edilebilir ana frame"""
        try:
            # Ana container
            main_container = tk.Frame(self.dashboard_frame, bg=self.colors['bg_primary'])
            main_container.pack(fill='both', expand=True)
            
            # Canvas ve scrollbar container
            scroll_container = tk.Frame(main_container, bg=self.colors['bg_primary'])
            scroll_container.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Canvas
            self.canvas = tk.Canvas(
                scroll_container, 
                bg=self.colors['bg_primary'], 
                highlightthickness=0,
                bd=0,
                relief='flat'
            )
            
            # Modern scrollbar
            scrollbar_style = ttk.Style()
            scrollbar_style.theme_use('clam')
            scrollbar_style.configure(
                'Custom.Vertical.TScrollbar',
                background=self.colors['bg_accent'],
                troughcolor=self.colors['bg_accent'],
                bordercolor=self.colors['border'],
                arrowcolor=self.colors['text_secondary'],
                darkcolor=self.colors['bg_accent'],
                lightcolor=self.colors['bg_secondary']
            )
            
            self.scrollbar = ttk.Scrollbar(
                scroll_container, 
                orient="vertical", 
                command=self.canvas.yview,
                style='Custom.Vertical.TScrollbar'
            )
            
            # Scrollable frame
            self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors['bg_primary'])
            
            # Scroll region güncellemesi
            def configure_scroll_region(event=None):
                """Canvas scroll region'ını güncelle"""
                try:
                    self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                except (tk.TclError, AttributeError):
                    pass
                    
            def configure_canvas_width(event=None):
                """Canvas genişliğini ayarla"""
                try:
                    canvas_width = self.canvas.winfo_width()
                    if canvas_width > 1 and hasattr(self, 'canvas_window'):
                        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
                except (tk.TclError, AttributeError):
                    pass
            
            # Event binding
            self.scrollable_frame.bind("<Configure>", configure_scroll_region)
            self.canvas.bind('<Configure>', configure_canvas_width)
            
            # Canvas window oluştur
            self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
            self.canvas.configure(yscrollcommand=self.scrollbar.set)
            
            # Mouse wheel scroll - Platform güvenli
            def on_mouse_wheel(event):
                """Platform bağımsız mouse wheel scroll"""
                try:
                    if not self.canvas.winfo_viewable():
                        return "break"
                        
                    delta = 0
                    if self.os_platform == "Windows":
                        delta = -1 * int(event.delta / 120)
                    elif self.os_platform == "Darwin":
                        delta = -1 * int(event.delta)
                    else:
                        if event.num == 4:
                            delta = -1
                        elif event.num == 5:
                            delta = 1
                        else:
                            return "break"
                    
                    self.canvas.yview_scroll(delta, "units")
                    return "break"
                    
                except (AttributeError, tk.TclError, ValueError, TypeError) as e:
                    print(f"Scroll event hatası: {e}")
                    return "break"
            
            def bind_mousewheel_events():
                """Platform bazlı mouse wheel event binding"""
                try:
                    if self.os_platform == "Windows":
                        self.canvas.bind("<MouseWheel>", on_mouse_wheel, add="+")
                        self.scrollable_frame.bind("<MouseWheel>", on_mouse_wheel, add="+")
                    elif self.os_platform == "Darwin":
                        self.canvas.bind("<MouseWheel>", on_mouse_wheel, add="+")
                        self.scrollable_frame.bind("<MouseWheel>", on_mouse_wheel, add="+")
                    else:
                        self.canvas.bind("<Button-4>", on_mouse_wheel, add="+")
                        self.canvas.bind("<Button-5>", on_mouse_wheel, add="+")
                        self.scrollable_frame.bind("<Button-4>", on_mouse_wheel, add="+")
                        self.scrollable_frame.bind("<Button-5>", on_mouse_wheel, add="+")
                except (tk.TclError, AttributeError) as e:
                    print(f"Mouse wheel binding hatası: {e}")
            
            def unbind_mousewheel_events():
                """Mouse wheel event binding'lerini kaldır"""
                try:
                    if self.os_platform in ["Windows", "Darwin"]:
                        self.canvas.unbind("<MouseWheel>")
                        try:
                            self.scrollable_frame.unbind("<MouseWheel>")
                        except tk.TclError:
                            pass
                    else:
                        self.canvas.unbind("<Button-4>")
                        self.canvas.unbind("<Button-5>")
                        try:
                            self.scrollable_frame.unbind("<Button-4>")
                            self.scrollable_frame.unbind("<Button-5>")
                        except tk.TclError:
                            pass
                except (tk.TclError, AttributeError):
                    pass
            
            def on_canvas_enter(event):
                try:
                    bind_mousewheel_events()
                except Exception as e:
                    print(f"Canvas enter hatası: {e}")
            
            def on_canvas_leave(event):
                try:
                    unbind_mousewheel_events()
                except Exception as e:
                    print(f"Canvas leave hatası: {e}")
            
            # Mouse enter/leave events
            try:
                self.canvas.bind('<Enter>', on_canvas_enter, add="+")
                self.canvas.bind('<Leave>', on_canvas_leave, add="+")
            except tk.TclError as e:
                print(f"Enter/Leave binding hatası: {e}")
            
            # Canvas ve scrollbar'ı pack et
            self.canvas.pack(side="left", fill="both", expand=True)
            self.scrollbar.pack(side="right", fill="y")
            
            # Ana içerik frame
            self.main_frame = tk.Frame(self.scrollable_frame, bg=self.colors['bg_primary'])
            self.main_frame.pack(fill='both', expand=True, padx=30, pady=30)
            
            # Temizlik fonksiyonu
            def cleanup_scroll():
                try:
                    unbind_mousewheel_events()
                except Exception:
                    pass
            
            self.canvas.bind('<Destroy>', lambda e: cleanup_scroll())
            
            def initial_focus_check():
                try:
                    if hasattr(self, 'canvas') and self.canvas.winfo_exists() and self.canvas.winfo_viewable():
                        bind_mousewheel_events()
                except (tk.TclError, AttributeError):
                    pass
            
            self.canvas.after(100, initial_focus_check)
            
        except Exception as e:
            print(f"Scrollable frame oluşturma hatası: {e}")
    
    def create_modern_header(self):
        """Modern gradient header"""
        try:
            header_frame = tk.Frame(self.main_frame, bg=self.colors['bg_primary'], height=120)
            header_frame.pack(fill='x', pady=(0, 30))
            header_frame.pack_propagate(False)
            
            # Gradient container
            gradient_frame = tk.Frame(header_frame, bg=self.colors['primary'])
            gradient_frame.pack(fill='both', expand=True)
            
            # Header içerik
            content_frame = tk.Frame(gradient_frame, bg=self.colors['primary'])
            content_frame.pack(expand=True, fill='both', padx=40, pady=30)
            
            # Ana başlık
            title_label = tk.Label(
                content_frame,
                text="📊 Karlılık Analizi Dashboard",
                font=('Segoe UI', 24, 'bold'),
                fg='white',
                bg=self.colors['primary']
            )
            title_label.pack(anchor='w')
            
            # Alt başlık - Güvenli uzunluk
            product_count = len(self.df) if not self.df.empty else 0
            subtitle_label = tk.Label(
                content_frame,
                text=f"Toplam {product_count} ürün detaylı analizi",
                font=('Segoe UI', 14),
                fg='#bfdbfe',
                bg=self.colors['primary']
            )
            subtitle_label.pack(anchor='w', pady=(5, 0))
            
            # Shadow efekti
            DashboardComponents.create_shadow_effect(header_frame, gradient_frame, 4)
            
        except Exception as e:
            print(f"Header oluşturma hatası: {e}")
    
    def create_enhanced_kpi_section(self):
        """Geliştirilmiş KPI kartları bölümü"""
        try:
            # Section başlığı
            DashboardComponents.create_section_title(self.main_frame, "🎯 Performans Özeti", "Ana performans metrikleri")
            
            # KPI verilerini al
            try:
                if self.analiz:
                    kpi_data = self.analiz.get_kpi_summary()
                else:
                    kpi_data = self.get_empty_kpi_data()
            except Exception as e:
                print(f"KPI verisi alma hatası: {e}")
                kpi_data = self.get_empty_kpi_data()
            
            # KPI kartları container
            kpi_container = tk.Frame(self.main_frame, bg=self.colors['bg_primary'])
            kpi_container.pack(fill='x', pady=(0, 40))
            
            # İlk satır KPI kartları
            kpi_row1 = tk.Frame(kpi_container, bg=self.colors['bg_primary'])
            kpi_row1.pack(fill='x', pady=(0, 20))
            
            # En karlı ürün adını güvenli şekilde kısalt
            en_karli_urun_text = str(kpi_data.get('en_karli_urun', 'Veri Yok'))
            if len(en_karli_urun_text) > 20:
                en_karli_urun_text = en_karli_urun_text[:20] + "..."
            
            # KPI kartlarını oluştur - Güvenli değerlerle
            DashboardComponents.create_modern_kpi_card(
                kpi_row1, "💰", "Toplam Net Kar", 
                f"₺{kpi_data.get('toplam_kar', 0):,.0f}", 
                self.colors['success'], 0
            )
            DashboardComponents.create_modern_kpi_card(
                kpi_row1, "🏆", "En Karlı Ürün", 
                en_karli_urun_text, 
                self.colors['primary'], 1
            )
            DashboardComponents.create_modern_kpi_card(
                kpi_row1, "📈", "Ortalama Kar", 
                f"₺{kpi_data.get('ortalama_kar', 0):,.0f}", 
                self.colors['warning'], 2
            )
            DashboardComponents.create_modern_kpi_card(
                kpi_row1, "📦", "Toplam Ürün", 
                f"{kpi_data.get('toplam_urun', 0)} adet", 
                self.colors['info'], 3
            )
            
            # İkinci satır KPI kartları
            kpi_row2 = tk.Frame(kpi_container, bg=self.colors['bg_primary'])
            kpi_row2.pack(fill='x')
            
            DashboardComponents.create_modern_kpi_card(
                kpi_row2, "✅", "Karlı Ürün", 
                f"{kpi_data.get('pozitif_kar_urun', 0)} adet", 
                self.colors['success'], 0
            )
            DashboardComponents.create_modern_kpi_card(
                kpi_row2, "❌", "Zararlı Ürün", 
                f"{kpi_data.get('negatif_kar_urun', 0)} adet", 
                self.colors['danger'], 1
            )
            DashboardComponents.create_modern_kpi_card(
                kpi_row2, "🎯", "En Yüksek Kar", 
                f"₺{kpi_data.get('en_karli_urun_kar', 0):,.0f}", 
                '#8b5cf6', 2
            )
            DashboardComponents.create_modern_kpi_card(
                kpi_row2, "📊", "Toplam Satış", 
                f"{kpi_data.get('toplam_satis_miktar', 0):,.0f} adet", 
                self.colors['info'], 3
            )
            
            # Grid konfigürasyonu
            for i in range(4):
                kpi_row1.grid_columnconfigure(i, weight=1)
                kpi_row2.grid_columnconfigure(i, weight=1)
                
        except Exception as e:
            print(f"KPI section oluşturma hatası: {e}")
    
    def get_empty_kpi_data(self):
        """Boş KPI verisi"""
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
    
    def create_analysis_tabs(self):
        """Modern analiz sekmeleri"""
        try:
            DashboardComponents.create_section_title(self.main_frame, "📊 Detaylı Analizler", "Ürün performans analizleri")
            
            # Tab container
            tab_container = tk.Frame(self.main_frame, bg=self.colors['bg_primary'])
            tab_container.pack(fill='x', pady=(0, 40))
            
            # Modern notebook style
            try:
                notebook_style = ttk.Style()
                notebook_style.configure(
                    'Modern.TNotebook',
                    background=self.colors['bg_primary'],
                    borderwidth=0
                )
                notebook_style.configure(
                    'Modern.TNotebook.Tab',
                    background=self.colors['bg_accent'],
                    foreground=self.colors['text_secondary'],
                    padding=[20, 12],
                    font=('Segoe UI', 10, 'bold')
                )
                notebook_style.map(
                    'Modern.TNotebook.Tab',
                    background=[('selected', self.colors['bg_secondary'])],
                    foreground=[('selected', self.colors['text_primary'])]
                )
            except Exception as e:
                print(f"Notebook style hatası: {e}")
            
            # Tab notebook
            self.analysis_notebook = ttk.Notebook(tab_container, style='Modern.TNotebook')
            self.analysis_notebook.pack(fill='both', expand=True)
            
            # Tab'ları oluştur
            self.create_performance_tab()
            self.create_profit_tab()
            self.create_distribution_tab()
            
        except Exception as e:
            print(f"Analysis tabs oluşturma hatası: {e}")
    
    def create_performance_tab(self):
        """Performans analizi sekmesi"""
        try:
            perf_frame = ttk.Frame(self.analysis_notebook)
            self.analysis_notebook.add(perf_frame, text="🏆 Performans")
            
            # Ana container
            main_container = tk.Frame(perf_frame, bg=self.colors['bg_secondary'])
            main_container.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Top products section
            top_section = tk.Frame(main_container, bg=self.colors['bg_secondary'])
            top_section.pack(fill='both', expand=True, pady=(0, 15))
            
            # Sol: En karlı ürünler
            left_container = tk.Frame(top_section, bg=self.colors['bg_secondary'])
            left_container.pack(side='left', fill='both', expand=True, padx=(0, 10))
            
            left_frame = tk.Frame(left_container, bg=self.colors['bg_secondary'], relief='flat')
            left_frame.pack(fill='both', expand=True)
            
            # Header
            left_header = tk.Frame(left_frame, bg=self.colors['primary'], height=40)
            left_header.pack(fill='x')
            left_header.pack_propagate(False)
            
            tk.Label(
                left_header,
                text="🔥 En Karlı Ürünler (Top 10)",
                font=('Segoe UI', 12, 'bold'),
                fg='white',
                bg=self.colors['primary']
            ).pack(expand=True)
            
            # Sağ: En çok satan ürünler
            right_container = tk.Frame(top_section, bg=self.colors['bg_secondary'])
            right_container.pack(side='right', fill='both', expand=True, padx=(10, 0))
            
            right_frame = tk.Frame(right_container, bg=self.colors['bg_secondary'], relief='flat')
            right_frame.pack(fill='both', expand=True)
            
            # Header
            right_header = tk.Frame(right_frame, bg=self.colors['info'], height=40)
            right_header.pack(fill='x')
            right_header.pack_propagate(False)
            
            tk.Label(
                right_header,
                text="📈 En Çok Satan Ürünler (Top 10)",
                font=('Segoe UI', 12, 'bold'),
                fg='white',
                bg=self.colors['info']
            ).pack(expand=True)
            
            # Shadow efektleri
            DashboardComponents.create_shadow_effect(left_container, left_frame, 3)
            DashboardComponents.create_shadow_effect(right_container, right_frame, 3)
            
            # Veri listelerini oluştur - Güvenli
            try:
                if self.analiz:
                    top_profitable = self.analiz.get_top_profitable_products(10)
                    top_selling = self.analiz.get_top_selling_products(10)
                    miktar_col = self.analiz.find_miktar_column()
                else:
                    top_profitable = pd.DataFrame()
                    top_selling = pd.DataFrame()
                    miktar_col = None
            except Exception as e:
                print(f"Top ürünler hatası: {e}")
                top_profitable = pd.DataFrame()
                top_selling = pd.DataFrame()
                miktar_col = None
            
            DashboardComponents.create_modern_product_list(
                left_frame, top_profitable, 'Net Kar', self.colors['success'], self.analiz
            )
            DashboardComponents.create_modern_product_list(
                right_frame, top_selling, miktar_col if miktar_col else 'Miktar', self.colors['info'], self.analiz
            )
            
        except Exception as e:
            print(f"Performance tab oluşturma hatası: {e}")
    
    def create_profit_tab(self):
        """Kar analizi sekmesi"""
        try:
            profit_frame = ttk.Frame(self.analysis_notebook)
            self.analysis_notebook.add(profit_frame, text="💰 Kar Analizi")
            
            main_container = tk.Frame(profit_frame, bg=self.colors['bg_secondary'])
            main_container.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Kar dağılımı - Güvenli veri alma
            try:
                if self.analiz:
                    dist_data = self.analiz.get_profit_distribution()
                else:
                    dist_data = {'cok_karli': 0, 'orta_karli': 0, 'dusuk_karli': 0, 'zararda': 0}
            except Exception as e:
                print(f"Kar dağılımı hatası: {e}")
                dist_data = {'cok_karli': 0, 'orta_karli': 0, 'dusuk_karli': 0, 'zararda': 0}
            
            # Kar dağılım başlığı
            dist_title = tk.Label(
                main_container,
                text="📊 Kar Dağılımı",
                font=('Segoe UI', 16, 'bold'),
                fg=self.colors['text_primary'],
                bg=self.colors['bg_secondary']
            )
            dist_title.pack(anchor='w', pady=(0, 20))
            
            # Kar dağılım kartları
            dist_frame = tk.Frame(main_container, bg=self.colors['bg_secondary'])
            dist_frame.pack(fill='x', pady=(0, 20))
            
            profit_colors = [self.colors['success'], self.colors['warning'], '#f97316', self.colors['danger']]
            profit_data = [
                ("📈", "Çok Karlı", dist_data.get('cok_karli', 0)),
                ("⚖️", "Orta Karlı", dist_data.get('orta_karli', 0)),
                ("📉", "Düşük Karlı", dist_data.get('dusuk_karli', 0)),
                ("❌", "Zararda", dist_data.get('zararda', 0))
            ]
            
            for i, ((icon, title, value), color) in enumerate(zip(profit_data, profit_colors)):
                DashboardComponents.create_profit_card(dist_frame, icon, title, value, color, i)
            
            # Grid konfigürasyonu
            for i in range(4):
                dist_frame.grid_columnconfigure(i, weight=1)
            
            # Düşük performanslı ürünler
            low_perf_container = tk.Frame(main_container, bg=self.colors['bg_secondary'])
            low_perf_container.pack(fill='x')
            
            low_perf_frame = tk.Frame(low_perf_container, bg=self.colors['bg_secondary'], relief='flat')
            low_perf_frame.pack(fill='both', expand=True)
            
            # Header
            low_perf_header = tk.Frame(low_perf_frame, bg=self.colors['danger'], height=40)
            low_perf_header.pack(fill='x')
            low_perf_header.pack_propagate(False)
            
            tk.Label(
                low_perf_header,
                text="⚠️ Dikkat Edilmesi Gereken Ürünler",
                font=('Segoe UI', 12, 'bold'),
                fg='white',
                bg=self.colors['danger']
            ).pack(expand=True)
            
            # Shadow efekti
            DashboardComponents.create_shadow_effect(low_perf_container, low_perf_frame, 3)
            
            # Düşük karlı ürünleri al - Güvenli
            try:
                if self.analiz:
                    low_profit_products = self.analiz.get_low_profit_products(10)
                else:
                    low_profit_products = pd.DataFrame()
            except Exception as e:
                print(f"Düşük karlı ürünler hatası: {e}")
                low_profit_products = pd.DataFrame()
            
            DashboardComponents.create_modern_product_list(
                low_perf_frame, low_profit_products, 'Net Kar', self.colors['danger'], self.analiz
            )
            
        except Exception as e:
            print(f"Profit tab oluşturma hatası: {e}")
    
    def create_distribution_tab(self):
        """Dağılım analizi sekmesi"""
        try:
            dist_frame = ttk.Frame(self.analysis_notebook)
            self.analysis_notebook.add(dist_frame, text="📊 Dağılım")
            
            main_container = tk.Frame(dist_frame, bg=self.colors['bg_secondary'])
            main_container.pack(fill='both', expand=True, padx=20, pady=20)
            
            # İstatistiksel özet - Güvenli veri alma
            try:
                if self.analiz:
                    stats = self.analiz.get_summary_stats()
                else:
                    stats = {}
            except Exception as e:
                print(f"İstatistik hatası: {e}")
                stats = {}
            
            stats_container = tk.Frame(main_container, bg=self.colors['bg_secondary'])
            stats_container.pack(fill='x')
            
            stats_frame = tk.Frame(stats_container, bg=self.colors['bg_secondary'], relief='flat')
            stats_frame.pack(fill='both', expand=True)
            
            # Header
            stats_header = tk.Frame(stats_frame, bg=self.colors['primary'], height=40)
            stats_header.pack(fill='x')
            stats_header.pack_propagate(False)
            
            tk.Label(
                stats_header,
                text="📈 İstatistiksel Özet",
                font=('Segoe UI', 12, 'bold'),
                fg='white',
                bg=self.colors['primary']
            ).pack(expand=True)
            
            # Shadow efekti
            DashboardComponents.create_shadow_effect(stats_container, stats_frame, 3)
            
            # İstatistik kartları - Güvenli
            if stats:
                stats_content = tk.Frame(stats_frame, bg=self.colors['bg_secondary'])
                stats_content.pack(fill='x', padx=20, pady=20)
                
                row = 0
                col = 0
                for key, value in stats.items():
                    if col >= 3:
                        col = 0
                        row += 1
                    
                    # Stat card container
                    stat_container = tk.Frame(stats_content, bg=self.colors['bg_secondary'])
                    stat_container.grid(row=row, column=col, padx=8, pady=8, sticky='ew')
                    
                    # Stat card
                    stat_card = tk.Frame(stat_container, bg='#f8fafc', relief='flat')
                    stat_card.pack(fill='both', expand=True)
                    
                    # İç padding
                    stat_inner = tk.Frame(stat_card, bg='#f8fafc')
                    stat_inner.pack(fill='both', expand=True, padx=20, pady=15)
                    
                    # Başlık
                    title_text = str(key).replace('_', ' ').title()
                    title_label = tk.Label(
                        stat_inner,
                        text=title_text,
                        font=('Segoe UI', 10, 'bold'),
                        fg=self.colors['text_secondary'],
                        bg='#f8fafc'
                    )
                    title_label.pack()
                    
                    # Değer - Güvenli formatlama
                    try:
                        if isinstance(value, float):
                            if 'kar' in str(key).lower():
                                value_text = f"₺{value:,.2f}"
                            else:
                                value_text = f"{value:,.2f}"
                        else:
                            value_text = f"{value:,}"
                    except (ValueError, TypeError):
                        value_text = str(value)
                        
                    value_label = tk.Label(
                        stat_inner,
                        text=value_text,
                        font=('Segoe UI', 14, 'bold'),
                        fg=self.colors['text_primary'],
                        bg='#f8fafc'
                    )
                    value_label.pack(pady=(5, 0))
                    
                    # Shadow efekti
                    DashboardComponents.create_shadow_effect(stat_container, stat_card, 2)
                    
                    col += 1
                
                # Grid ağırlıkları
                for i in range(3):
                    stats_content.grid_columnconfigure(i, weight=1)
            else:
                # Stats boşsa mesaj göster
                no_stats_label = tk.Label(
                    stats_frame,
                    text="📊 İstatistik verisi bulunamadı",
                    font=('Segoe UI', 12),
                    fg=self.colors['text_secondary'],
                    bg=self.colors['bg_secondary']
                )
                no_stats_label.pack(pady=30)
                
        except Exception as e:
            print(f"Distribution tab oluşturma hatası: {e}")
    
    def create_enhanced_search_section(self):
        """Gelişmiş arama bölümü"""
        try:
            DashboardComponents.create_section_title(self.main_frame, "🔍 Gelişmiş Ürün Arama", "Arama ve filtreleme araçları")
            
            # Arama container
            search_container = tk.Frame(self.main_frame, bg=self.colors['bg_primary'])
            search_container.pack(fill='x', pady=(0, 40))
            
            # Arama frame
            search_frame = tk.Frame(search_container, bg=self.colors['bg_secondary'], relief='flat')
            search_frame.pack(fill='x')
            
            # Shadow efekti
            DashboardComponents.create_shadow_effect(search_container, search_frame, 3)
            
            # Arama header
            search_header = tk.Frame(search_frame, bg=self.colors['primary'], height=50)
            search_header.pack(fill='x')
            search_header.pack_propagate(False)
            
            tk.Label(
                search_header,
                text="Arama ve Filtreleme",
                font=('Segoe UI', 14, 'bold'),
                fg='white',
                bg=self.colors['primary']
            ).pack(expand=True)
            
            # Arama kontrolleri
            controls_frame = tk.Frame(search_frame, bg=self.colors['bg_secondary'])
            controls_frame.pack(fill='x', padx=30, pady=25)
            
            # Arama kutusu satırı
            search_row = tk.Frame(controls_frame, bg=self.colors['bg_secondary'])
            search_row.pack(fill='x', pady=(0, 20))
            
            # Arama etiketi
            search_label = tk.Label(
                search_row,
                text="Ürün Adı:",
                font=('Segoe UI', 12, 'bold'),
                fg=self.colors['text_primary'],
                bg=self.colors['bg_secondary']
            )
            search_label.pack(side='left')
            
            # Arama kutusu
            self.search_var = tk.StringVar()
            search_entry_frame = tk.Frame(search_row, bg=self.colors['bg_secondary'])
            search_entry_frame.pack(side='left', padx=(15, 20))
            
            search_entry = tk.Entry(
                search_entry_frame,
                textvariable=self.search_var,
                font=('Segoe UI', 11),
                bg='#f8fafc',
                fg=self.colors['text_primary'],
                relief='solid',
                bd=1,
                width=35,
                insertbackground=self.colors['primary']
            )
            search_entry.pack(pady=3)
            
            # Buton grubu
            button_frame = tk.Frame(search_row, bg=self.colors['bg_secondary'])
            button_frame.pack(side='left')
            
            # Arama butonu
            search_btn = tk.Button(
                button_frame,
                text="🔍 Ara",
                command=self.search_product,
                bg=self.colors['primary'],
                fg='white',
                font=('Segoe UI', 11, 'bold'),
                relief='flat',
                bd=0,
                cursor='hand2',
                padx=25,
                pady=10
            )
            search_btn.pack(side='left', padx=(0, 10))
            
            # Temizle butonu
            clear_btn = tk.Button(
                button_frame,
                text="🗑️ Temizle",
                command=self.clear_search,
                bg=self.colors['text_secondary'],
                fg='white',
                font=('Segoe UI', 11),
                relief='flat',
                bd=0,
                cursor='hand2',
                padx=20,
                pady=10
            )
            clear_btn.pack(side='left')
            
            # Enter tuşu ile arama
            search_entry.bind('<Return>', lambda e: self.search_product())
            
            # Hover efektleri
            DashboardComponents.create_button_hover(search_btn, self.colors['primary'], self.colors['primary_dark'])
            DashboardComponents.create_button_hover(clear_btn, self.colors['text_secondary'], '#4b5563')
            
            # Hızlı filtreler
            filter_frame = tk.Frame(controls_frame, bg=self.colors['bg_secondary'])
            filter_frame.pack(fill='x')
            
            filter_label = tk.Label(
                filter_frame,
                text="Hızlı Filtreler:",
                font=('Segoe UI', 12, 'bold'),
                fg=self.colors['text_primary'],
                bg=self.colors['bg_secondary']
            )
            filter_label.pack(anchor='w', pady=(0, 10))
            
            # Filter buttons
            filter_buttons = tk.Frame(filter_frame, bg=self.colors['bg_secondary'])
            filter_buttons.pack(fill='x')
            
            filters = [
                ("Tümü", "all", self.colors['text_secondary']),
                ("Karlı", "profitable", self.colors['success']),
                ("Zararlı", "loss", self.colors['danger']),
                ("Yüksek Satış", "high_sales", self.colors['info'])
            ]
            
            for text, filter_type, color in filters:
                btn = tk.Button(
                    filter_buttons,
                    text=str(text),
                    command=lambda f=filter_type: self.apply_quick_filter(f),
                    bg=color,
                    fg='white',
                    font=('Segoe UI', 10, 'bold'),
                    relief='flat',
                    bd=0,
                    cursor='hand2',
                    padx=20,
                    pady=8
                )
                btn.pack(side='left', padx=(0, 12))
                
                # Hover efekti
                hover_colors = {
                    self.colors['text_secondary']: '#4b5563',
                    self.colors['success']: '#059669',
                    self.colors['danger']: '#dc2626',
                    self.colors['info']: '#0891b2'
                }
                hover_color = hover_colors.get(color, color)
                
                DashboardComponents.create_button_hover(btn, color, hover_color)
            
            # Sonuç alanı
            self.search_result_frame = tk.Frame(search_frame, bg=self.colors['bg_secondary'])
            self.search_result_frame.pack(fill='both', expand=True, padx=30, pady=(0, 30))
            
            # Başlangıç mesajı
            self.show_initial_search_message()
            
        except Exception as e:
            print(f"Search section oluşturma hatası: {e}")
    
    def show_initial_search_message(self):
        """Başlangıç arama mesajı"""
        try:
            DashboardComponents.show_initial_search_message(self.search_result_frame)
        except Exception as e:
            print(f"Initial search message hatası: {e}")
    
    def search_product(self):
        """Ürün arama işlemi"""
        try:
            search_term = self.search_var.get().strip()
            
            # Eski sonuçları temizle
            for widget in self.search_result_frame.winfo_children():
                try:
                    widget.destroy()
                except tk.TclError:
                    pass
            
            if not search_term:
                error_container = tk.Frame(self.search_result_frame, bg=self.colors['bg_secondary'])
                error_container.pack(fill='x', pady=10)
                
                error_frame = tk.Frame(error_container, bg='#fef2f2', relief='flat')
                error_frame.pack(fill='x')
                
                tk.Label(
                    error_frame,
                    text="⚠️ Lütfen arama terimi girin",
                    font=('Segoe UI', 12),
                    fg=self.colors['danger'],
                    bg='#fef2f2'
                ).pack(pady=15)
                
                DashboardComponents.create_shadow_effect(error_container, error_frame, 2)
                return
            
            # Arama yap - Güvenli
            try:
                if self.analiz:
                    results = self.analiz.search_product(search_term)
                else:
                    results = pd.DataFrame()
            except Exception as e:
                print(f"Arama hatası: {e}")
                results = pd.DataFrame()
            
            if results.empty:
                no_result_container = tk.Frame(self.search_result_frame, bg=self.colors['bg_secondary'])
                no_result_container.pack(fill='x', pady=10)
                
                no_result_frame = tk.Frame(no_result_container, bg='#fef2f2', relief='flat')
                no_result_frame.pack(fill='x')
                
                tk.Label(
                    no_result_frame,
                    text=f"❌ '{search_term}' için sonuç bulunamadı",
                    font=('Segoe UI', 12),
                    fg=self.colors['danger'],
                    bg='#fef2f2'
                ).pack(pady=15)
                
                DashboardComponents.create_shadow_effect(no_result_container, no_result_frame, 2)
                return
            
            # Sonuç başlığı
            result_header = tk.Frame(self.search_result_frame, bg=self.colors['bg_secondary'])
            result_header.pack(fill='x', pady=(0, 20))
            
            tk.Label(
                result_header,
                text=f"🎯 '{search_term}' için {len(results)} sonuç bulundu:",
                font=('Segoe UI', 14, 'bold'),
                fg=self.colors['success'],
                bg=self.colors['bg_secondary']
            ).pack(anchor='w')
            
            # Sonuç tablosu
            DashboardComponents.display_search_results(self.search_result_frame, results, self.analiz)
            
        except Exception as e:
            print(f"Search product hatası: {e}")
    
    def apply_quick_filter(self, filter_type):
        """Hızlı filtre uygula"""
        try:
            # Eski sonuçları temizle
            for widget in self.search_result_frame.winfo_children():
                try:
                    widget.destroy()
                except tk.TclError:
                    pass
            
            try:
                if filter_type == "all":
                    results = self.df.copy()
                elif filter_type == "profitable":
                    results = self.df[self.df['Net Kar'] > 0] if 'Net Kar' in self.df.columns else pd.DataFrame()
                elif filter_type == "loss":
                    results = self.df[self.df['Net Kar'] < 0] if 'Net Kar' in self.df.columns else pd.DataFrame()
                elif filter_type == "high_sales":
                    if self.analiz:
                        miktar_col = self.analiz.find_miktar_column()
                        if miktar_col and miktar_col in self.df.columns:
                            try:
                                # Pandas numeric conversion güvenli
                                miktar_series = pd.to_numeric(self.df[miktar_col], errors='coerce')
                                threshold = miktar_series.quantile(0.75)
                                mask = miktar_series >= threshold
                                results = self.df[mask]
                            except (ValueError, TypeError):
                                results = pd.DataFrame()
                        else:
                            results = pd.DataFrame()
                    else:
                        results = pd.DataFrame()
                else:
                    results = pd.DataFrame()
                    
            except Exception as e:
                print(f"Filtreleme hatası: {e}")
                results = pd.DataFrame()
            
            if results.empty:
                no_filter_container = tk.Frame(self.search_result_frame, bg=self.colors['bg_secondary'])
                no_filter_container.pack(fill='x', pady=10)
                
                no_filter_frame = tk.Frame(no_filter_container, bg='#fef2f2', relief='flat')
                no_filter_frame.pack(fill='x')
                
                tk.Label(
                    no_filter_frame,
                    text="❌ Bu filtre için sonuç bulunamadı",
                    font=('Segoe UI', 12),
                    fg=self.colors['danger'],
                    bg='#fef2f2'
                ).pack(pady=15)
                
                DashboardComponents.create_shadow_effect(no_filter_container, no_filter_frame, 2)
                return
            
            # Sonuç başlığı
            filter_names = {
                "all": "Tüm Ürünler",
                "profitable": "Karlı Ürünler",
                "loss": "Zararlı Ürünler", 
                "high_sales": "Yüksek Satışlı Ürünler"
            }
            
            result_header = tk.Frame(self.search_result_frame, bg=self.colors['bg_secondary'])
            result_header.pack(fill='x', pady=(0, 20))
            
            tk.Label(
                result_header,
                text=f"🎯 {filter_names.get(filter_type, 'Filtre')}: {len(results)} sonuç",
                font=('Segoe UI', 14, 'bold'),
                fg=self.colors['info'],
                bg=self.colors['bg_secondary']
            ).pack(anchor='w')
            
            # Sonuç tablosu - İlk 50 sonuç
            DashboardComponents.display_search_results(self.search_result_frame, results.head(50), self.analiz)
            
        except Exception as e:
            print(f"Quick filter hatası: {e}")
    
    def clear_search(self):
        """Arama sonuçlarını temizle"""
        try:
            self.search_var.set("")
            
            # Sonuç alanını temizle
            for widget in self.search_result_frame.winfo_children():
                try:
                    widget.destroy()
                except tk.TclError:
                    pass
            
            # Başlangıç mesajını göster
            self.show_initial_search_message()
            
        except Exception as e:
            print(f"Clear search hatası: {e}")