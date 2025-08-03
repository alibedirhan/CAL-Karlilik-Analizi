import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
from datetime import datetime
from karlilik import KarlilikAnalizi

class BupilicKarlilikGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Bupiliç Karlılık Analizi - Modern Interface")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f8f9fa')
        self.root.resizable(True, True)
        
        # Thread-safe iletişim için queue
        self.result_queue = queue.Queue()
        self.is_processing = False
        
        # Modern stil
        self.setup_style()
        
        # Değişkenler
        self.karlilik_path = tk.StringVar()
        self.iskonto_path = tk.StringVar()
        self.progress_var = tk.DoubleVar()
        
        # Karlılık analizi objesi
        self.analiz = KarlilikAnalizi(
            progress_callback=self.thread_safe_update_progress,
            log_callback=self.thread_safe_log_message
        )
        
        # Dashboard için analiz sonucu
        self.analiz_sonucu = None
        
        # Dashboard referansı
        self.dashboard = None
        
        self.setup_ui()
        
        # Queue kontrol timer'ı başlat
        self.check_queue()
        
    def thread_safe_update_progress(self, value, status):
        """Thread-safe progress güncelleme"""
        self.result_queue.put(('progress', {'value': value, 'status': status}))
    
    def thread_safe_log_message(self, message, msg_type='info'):
        """Thread-safe log mesajı"""
        self.result_queue.put(('log', {'message': message, 'type': msg_type}))
        
    def check_queue(self):
        """Thread'den gelen mesajları kontrol et"""
        try:
            while True:
                message_type, data = self.result_queue.get_nowait()
                
                if message_type == 'analysis_complete':
                    self.on_analysis_complete(data)
                elif message_type == 'analysis_error':
                    self.on_analysis_error(data)
                elif message_type == 'analysis_cancelled':
                    self.on_analysis_cancelled()
                elif message_type == 'progress':
                    self.update_progress(data['value'], data['status'])
                elif message_type == 'log':
                    self.log_message(data['message'], data.get('type', 'info'))
                    
        except queue.Empty:
            pass
        except Exception as e:
            print(f"Queue kontrol hatası: {e}")
        
        # 100ms sonra tekrar kontrol et
        if not getattr(self, '_closing', False):
            self.root.after(100, self.check_queue)
    
    def on_analysis_complete(self, result_data):
        """Analiz tamamlandığında çağrılır"""
        self.is_processing = False
        self.analiz_sonucu = result_data
        
        self.log_message("✓ Karlılık analizi başarıyla tamamlandı!", 'success')
        
        # Dashboard sekmesini oluştur
        self.create_dashboard_tab()
        
        # Başarı mesajı
        self.root.after(0, lambda: messagebox.showinfo(
            "Başarılı! 🎉",
            "Karlılık analizi tamamlandı!\nSonuç dosyası başarıyla kaydedildi.\n\n📊 Dashboard sekmesinde detaylı analizi görebilirsiniz."
        ))
        
        # Buton aktive et
        self.reset_process_button()
    
    def on_analysis_error(self, error_msg):
        """Analiz hatası oluştuğunda çağrılır"""
        self.is_processing = False
        self.update_progress(0, f"Hata: {str(error_msg)}")
        self.log_message(f"✗ HATA: {str(error_msg)}", 'error')
        
        self.root.after(0, lambda: messagebox.showerror(
            "Hata",
            f"İşlem sırasında hata oluştu:\n{str(error_msg)}"
        ))
        
        # Buton aktive et
        self.reset_process_button()
    
    def on_analysis_cancelled(self):
        """Analiz iptal edildiğinde çağrılır"""
        self.is_processing = False
        self.update_progress(0, "İşlem iptal edildi")
        
        # Buton aktive et
        self.reset_process_button()
    
    def reset_process_button(self):
        """Process butonunu varsayılan haline getir"""
        try:
            self.process_btn.config(
                state='normal', 
                text="✨ Analizi Başlat",
                bg='#fd7e14',
                cursor='hand2'
            )
        except tk.TclError:
            # Widget yoksa veya destroy edilmişse
            pass
        
    def setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except tk.TclError:
            # Tema mevcut değilse varsayılanı kullan
            pass
        
        # Modern button style
        style.configure(
            'Modern.TButton',
            font=('Segoe UI', 11),
            relief='flat',
            borderwidth=0,
            focuscolor='none',
            background='#007acc',
            foreground='white'
        )
        
        style.map('Modern.TButton',
                 background=[('active', '#005a9e'),
                           ('pressed', '#004080')])
        
        # Progress bar style
        style.configure(
            'Modern.Horizontal.TProgressbar',
            background='#007acc',
            troughcolor='#e1e5e9',
            borderwidth=0,
            lightcolor='#007acc',
            darkcolor='#005a9e'
        )
        
        # Modern frame style
        style.configure(
            'Modern.TFrame',
            background='#ffffff',
            relief='flat',
            borderwidth=1
        )
        
    def setup_ui(self):
        # Ana container
        main_container = tk.Frame(self.root, bg='#f8f9fa')
        main_container.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Header
        self.create_header(main_container)
        
        # Sekmeli yapı oluştur
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill='both', expand=True, pady=(20, 0))
        
        # Ana işlemler sekmesi
        self.main_tab = tk.Frame(self.notebook, bg='#f8f9fa')
        self.notebook.add(self.main_tab, text="🔧 Ana İşlemler")
        
        # Ana sekme içeriği
        self.setup_main_tab()
        
    def create_header(self, parent):
        header_frame = tk.Frame(parent, bg='#f8f9fa')
        header_frame.pack(fill='x', pady=(0, 10))
        
        # Logo/Başlık alanı - gradient efekt için Canvas kullanıyoruz
        title_canvas = tk.Canvas(header_frame, height=100, bg='#f8f9fa', highlightthickness=0)
        title_canvas.pack(fill='x')
        
        def draw_header():
            try:
                title_canvas.delete("all")
                width = title_canvas.winfo_width()
                height = 100
                
                # Gradient background simulation
                title_canvas.create_rectangle(0, 0, width, height, fill='#007acc', outline='')
                title_canvas.create_rectangle(0, 0, width, height, fill='#005a9e', stipple='gray25', outline='')
                
                # Başlık text
                title_canvas.create_text(width//2, 30, text="🚀 Bupiliç Karlılık Analizi", 
                                        font=('Segoe UI', 20, 'bold'), fill='white', anchor='center')
                title_canvas.create_text(width//2, 60, text="Karlılık ve İskonto Raporları Eşleştirme Sistemi",
                                        font=('Segoe UI', 12), fill='#b3d9ff', anchor='center')
            except tk.TclError as e:
                print(f"Header çizim hatası: {e}")
        
        # Canvas boyutunu ayarla
        def resize_canvas(event):
            self.root.after_idle(draw_header)
        
        title_canvas.bind('<Configure>', resize_canvas)
        self.root.after(100, draw_header)
        
    def setup_main_tab(self):
        # Ana container
        content_frame = tk.Frame(self.main_tab, bg='#f8f9fa')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Sol panel - Dosya seçimi ve kontroller
        left_frame = tk.Frame(content_frame, bg='#ffffff', relief='solid', bd=1)
        left_frame.pack(side='left', fill='y', padx=(0, 15))
        left_frame.config(width=400)
        left_frame.pack_propagate(False)
        
        # Sağ panel - Sonuçlar
        right_frame = tk.Frame(content_frame, bg='#ffffff', relief='solid', bd=1)
        right_frame.pack(side='right', fill='both', expand=True)
        
        # Sol panel içeriği
        self.create_left_panel(left_frame)
        
        # Sağ panel içeriği
        self.create_right_panel(right_frame)
        
    def create_left_panel(self, parent):
        # Panel başlığı
        panel_header = tk.Frame(parent, bg='#007acc', height=50)
        panel_header.pack(fill='x')
        panel_header.pack_propagate(False)
        
        tk.Label(
            panel_header,
            text="📁 Dosya Seçimi ve İşlemler",
            font=('Segoe UI', 14, 'bold'),
            fg='white',
            bg='#007acc'
        ).pack(expand=True)
        
        # İçerik alanı
        content = tk.Frame(parent, bg='#ffffff')
        content.pack(fill='both', expand=True, padx=25, pady=25)
        
        # Dosya seçim bölümü
        self.create_file_section(content)
        
        # İşlem butonu
        self.create_action_button(content)
        
        # Progress bölümü
        self.create_progress_section(content)
        
    def create_file_section(self, parent):
        # Karlılık dosyası
        karlilik_section = tk.LabelFrame(
            parent, 
            text="📊 Karlılık Analizi Dosyası", 
            font=('Segoe UI', 11, 'bold'),
            fg='#2c3e50',
            bg='#ffffff',
            relief='groove',
            bd=2
        )
        karlilik_section.pack(fill='x', pady=(0, 20))
        
        # Dosya yolu gösterimi
        path_frame = tk.Frame(karlilik_section, bg='#ffffff')
        path_frame.pack(fill='x', padx=15, pady=15)
        
        self.karlilik_display = tk.Text(
            path_frame,
            height=3,
            font=('Segoe UI', 9),
            bg='#f8f9fa',
            fg='#555555',
            relief='solid',
            bd=1,
            wrap='word'
        )
        self.karlilik_display.pack(fill='x', pady=(0, 10))
        self.karlilik_display.insert('1.0', "Henüz dosya seçilmedi...")
        self.karlilik_display.config(state='disabled')
        
        # Dosya seçim butonu
        karlilik_btn = tk.Button(
            path_frame,
            text="📂 Karlılık Dosyası Seç",
            command=self.select_karlilik_file,
            bg='#007acc',
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            relief='flat',
            bd=0,
            cursor='hand2',
            padx=20,
            pady=10
        )
        karlilik_btn.pack(fill='x')
        
        # Hover efektleri
        def on_enter(e):
            karlilik_btn.config(bg='#005a9e')
        def on_leave(e):
            karlilik_btn.config(bg='#007acc')
        karlilik_btn.bind("<Enter>", on_enter)
        karlilik_btn.bind("<Leave>", on_leave)
        
        # İskonto dosyası
        iskonto_section = tk.LabelFrame(
            parent, 
            text="💰 Bupiliç İskonto Raporu", 
            font=('Segoe UI', 11, 'bold'),
            fg='#2c3e50',
            bg='#ffffff',
            relief='groove',
            bd=2
        )
        iskonto_section.pack(fill='x', pady=(0, 30))
        
        # Dosya yolu gösterimi
        path_frame2 = tk.Frame(iskonto_section, bg='#ffffff')
        path_frame2.pack(fill='x', padx=15, pady=15)
        
        self.iskonto_display = tk.Text(
            path_frame2,
            height=3,
            font=('Segoe UI', 9),
            bg='#f8f9fa',
            fg='#555555',
            relief='solid',
            bd=1,
            wrap='word'
        )
        self.iskonto_display.pack(fill='x', pady=(0, 10))
        self.iskonto_display.insert('1.0', "Henüz dosya seçilmedi...")
        self.iskonto_display.config(state='disabled')
        
        # Dosya seçim butonu
        iskonto_btn = tk.Button(
            path_frame2,
            text="📂 İskonto Dosyası Seç",
            command=self.select_iskonto_file,
            bg='#28a745',
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            relief='flat',
            bd=0,
            cursor='hand2',
            padx=20,
            pady=10
        )
        iskonto_btn.pack(fill='x')
        
        # Hover efektleri
        def on_enter2(e):
            iskonto_btn.config(bg='#218838')
        def on_leave2(e):
            iskonto_btn.config(bg='#28a745')
        iskonto_btn.bind("<Enter>", on_enter2)
        iskonto_btn.bind("<Leave>", on_leave2)
        
    def create_action_button(self, parent):
        button_frame = tk.Frame(parent, bg='#ffffff')
        button_frame.pack(fill='x', pady=(0, 30))
        
        self.process_btn = tk.Button(
            button_frame,
            text="✨ Analizi Başlat",
            command=self.start_analysis,
            bg='#fd7e14',
            fg='white',
            font=('Segoe UI', 14, 'bold'),
            relief='flat',
            bd=0,
            cursor='hand2',
            pady=15
        )
        self.process_btn.pack(fill='x')
        
        # Hover efektleri
        def on_enter_process(e):
            if not self.is_processing and self.process_btn['state'] != 'disabled':
                self.process_btn.config(bg='#e8630e')
        def on_leave_process(e):
            if not self.is_processing and self.process_btn['state'] != 'disabled':
                self.process_btn.config(bg='#fd7e14')
        
        self.process_btn.bind("<Enter>", on_enter_process)
        self.process_btn.bind("<Leave>", on_leave_process)
        
    def create_progress_section(self, parent):
        progress_frame = tk.LabelFrame(
            parent, 
            text="📈 İşlem Durumu", 
            font=('Segoe UI', 11, 'bold'),
            fg='#2c3e50',
            bg='#ffffff'
        )
        progress_frame.pack(fill='x')
        
        # Progress bar
        progress_container = tk.Frame(progress_frame, bg='#ffffff')
        progress_container.pack(fill='x', padx=15, pady=15)
        
        self.progress_bar = ttk.Progressbar(
            progress_container,
            variable=self.progress_var,
            maximum=100,
            mode='determinate',
            style='Modern.Horizontal.TProgressbar'
        )
        self.progress_bar.pack(fill='x', pady=(0, 10))
        
        self.status_label = tk.Label(
            progress_container,
            text="Hazır - Dosyaları seçin ve analizi başlatın",
            font=('Segoe UI', 10),
            fg='#666666',
            bg='#ffffff',
            anchor='w'
        )
        self.status_label.pack(anchor='w')
        
    def create_right_panel(self, parent):
        # Panel başlığı
        panel_header = tk.Frame(parent, bg='#007acc', height=50)
        panel_header.pack(fill='x')
        panel_header.pack_propagate(False)
        
        tk.Label(
            panel_header,
            text="📝 İşlem Sonuçları ve Loglar",
            font=('Segoe UI', 14, 'bold'),
            fg='white',
            bg='#007acc'
        ).pack(expand=True)
        
        # Log alanı
        log_frame = tk.Frame(parent, bg='#ffffff')
        log_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Scrollable text area
        text_container = tk.Frame(log_frame, bg='#ffffff')
        text_container.pack(fill='both', expand=True)
        
        self.result_text = tk.Text(
            text_container,
            font=('Consolas', 10),
            bg='#2c3e50',
            fg='#ecf0f1',
            relief='flat',
            bd=0,
            wrap='word',
            padx=15,
            pady=15
        )
        
        scrollbar = tk.Scrollbar(text_container, orient='vertical', command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Başlangıç mesajı
        welcome_msg = """🚀 Bupiliç Karlılık Analizi Sistemine Hoşgeldiniz!

✨ Bu sistem karlılık analizi ve iskonto raporlarınızı eşleştirerek:
   • Birim maliyetleri hesaplar
   • Kar marjlarını analiz eder  
   • En karlı ürünleri belirler
   • Detaylı Excel raporları oluşturur

📋 Kullanım Adımları:
   1. Sol panelden karlılık analizi Excel dosyasını seçin
   2. Bupiliç iskonto raporu dosyasını seçin
   3. "Analizi Başlat" butonuna tıklayın
   4. İşlem tamamlandığında sonuç dosyasını kaydedin

🎯 Sistem hazır. Dosyalarınızı seçerek başlayabilirsiniz.
"""

        self.result_text.insert('1.0', welcome_msg)
        self.result_text.config(state='disabled')
        
        # Text coloring tags
        self.result_text.tag_config('success', foreground='#2ecc71', font=('Consolas', 10, 'bold'))
        self.result_text.tag_config('error', foreground='#e74c3c', font=('Consolas', 10, 'bold'))
        self.result_text.tag_config('warning', foreground='#f39c12', font=('Consolas', 10, 'bold'))
        self.result_text.tag_config('info', foreground='#3498db', font=('Consolas', 10))
        
    def select_karlilik_file(self):
        filename = filedialog.askopenfilename(
            title="Karlılık Analizi Dosyasını Seçin",
            filetypes=[("Excel dosyaları", "*.xlsx *.xls"), ("Tüm dosyalar", "*.*")]
        )
        if filename:
            self.karlilik_path.set(filename)
            import os
            
            # Display dosya bilgilerini güncelle
            try:
                self.karlilik_display.config(state='normal')
                self.karlilik_display.delete('1.0', 'end')
                self.karlilik_display.insert('1.0', f"✅ Seçilen dosya:\n{os.path.basename(filename)}\n\n📍 Tam yol: {filename}")
                self.karlilik_display.config(state='disabled')
                
                self.log_message(f"✓ Karlılık dosyası seçildi: {os.path.basename(filename)}", 'success')
            except tk.TclError as e:
                print(f"Dosya görüntüleme hatası: {e}")
            
    def select_iskonto_file(self):
        filename = filedialog.askopenfilename(
            title="Bupiliç İskonto Raporu Dosyasını Seçin",
            filetypes=[("Excel dosyaları", "*.xlsx *.xls"), ("Tüm dosyalar", "*.*")]
        )
        if filename:
            self.iskonto_path.set(filename)
            import os
            
            # Display dosya bilgilerini güncelle
            try:
                self.iskonto_display.config(state='normal')
                self.iskonto_display.delete('1.0', 'end')
                self.iskonto_display.insert('1.0', f"✅ Seçilen dosya:\n{os.path.basename(filename)}\n\n📍 Tam yol: {filename}")
                self.iskonto_display.config(state='disabled')
                
                self.log_message(f"✓ İskonto dosyası seçildi: {os.path.basename(filename)}", 'success')
            except tk.TclError as e:
                print(f"Dosya görüntüleme hatası: {e}")
            
    def log_message(self, message, msg_type='info'):
        """Ana thread'de log mesajı"""
        try:
            self.result_text.config(state='normal')
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Icon mapping
            icons = {
                'success': '✅',
                'error': '❌', 
                'warning': '⚠️',
                'info': 'ℹ️'
            }
            
            icon = icons.get(msg_type, 'ℹ️')
            formatted_message = f"\n[{timestamp}] {icon} {message}"
            
            # Insert message
            start_pos = self.result_text.index('end-1c')
            self.result_text.insert('end', formatted_message)
            end_pos = self.result_text.index('end-1c')
            
            # Apply color tag
            self.result_text.tag_add(msg_type, start_pos, end_pos)
            
            self.result_text.see('end')
            self.result_text.config(state='disabled')
        except tk.TclError as e:
            print(f"Log mesajı hatası: {e}")
        
    def update_progress(self, value, status):
        """Ana thread'de progress güncelleme"""
        try:
            self.progress_var.set(value)
            self.status_label.config(text=status)
        except tk.TclError as e:
            print(f"Progress güncelleme hatası: {e}")
        
    def start_analysis(self):
        if self.is_processing:
            return  # Zaten işlem devam ediyor
            
        if not self.karlilik_path.get() or not self.iskonto_path.get():
            messagebox.showwarning(
                "Eksik Dosya",
                "Lütfen hem karlılık analizi hem de iskonto raporu dosyalarını seçin!"
            )
            return
        
        self.is_processing = True
        
        # Buton deaktive et
        try:
            self.process_btn.config(
                state='disabled', 
                text="⏳ İşlem Devam Ediyor...", 
                bg='#6c757d',
                cursor='arrow'
            )
        except tk.TclError:
            pass
        
        # Thread'de çalıştır
        thread = threading.Thread(target=self.run_analysis, daemon=True)
        thread.start()
        
    def run_analysis(self):
        """Thread-safe analiz fonksiyonu"""
        try:
            # Analiz sınıfını çağır - DataFrame döndürür
            analiz_sonucu = self.analiz.analyze(self.karlilik_path.get(), self.iskonto_path.get())
            
            if analiz_sonucu is not None:
                # Başarılı sonucu queue'ya gönder
                self.result_queue.put(('analysis_complete', analiz_sonucu))
            else:
                # İptal durumu
                self.result_queue.put(('analysis_cancelled', None))
                
        except Exception as e:
            # Hata durumunu queue'ya gönder
            self.result_queue.put(('analysis_error', str(e)))
    
    def create_dashboard_tab(self):
        """Dashboard sekmesini oluştur"""
        try:
            from analiz_dashboard import AnalyzDashboard
            
            # Eğer analiz sonucu yoksa çık
            if self.analiz_sonucu is None or self.analiz_sonucu.empty:
                self.log_message("✗ Dashboard için analiz sonucu bulunamadı!", 'error')
                return
            
            # Eğer bir önceki dashboard varsa kaldır
            if self.dashboard:
                try:
                    # Dashboard sekmesini bul ve kaldır - DÜZELTİLDİ
                    tab_list = self.notebook.tabs()
                    for tab_id in tab_list:
                        try:
                            if self.notebook.tab(tab_id, "text") == "📊 Analiz Dashboard":
                                self.notebook.forget(tab_id)
                                break
                        except tk.TclError:
                            continue
                except tk.TclError:
                    pass
            
            # Gerçek analiz sonucu ile dashboard oluştur
            self.dashboard = AnalyzDashboard(self.notebook, self.analiz_sonucu)
            
            # Sekmeyi ekle
            dashboard_frame = self.dashboard.get_frame()
            self.notebook.add(dashboard_frame, text="📊 Analiz Dashboard")
            
            # Dashboard sekmesine geç
            try:
                self.notebook.select(dashboard_frame)
            except tk.TclError:
                pass
            
            self.log_message("✓ Dashboard gerçek verilerle oluşturuldu!", 'success')
            self.log_message(f"📊 {len(self.analiz_sonucu)} ürün analiz edildi", 'info')
            
        except ImportError as e:
            self.log_message(f"✗ Dashboard modülü bulunamadı: {str(e)}", 'error')
        except Exception as e:
            self.log_message(f"✗ Dashboard oluşturma hatası: {str(e)}", 'error')
            print(f"Dashboard hatası: {e}")  # Debug için
    
    def run(self):
        # Pencere kapanırken temizlik yap
        def on_closing():
            try:
                self._closing = True
                self.is_processing = False
                self.root.quit()
                self.root.destroy()
            except Exception:
                pass
        
        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            on_closing()

if __name__ == "__main__":
    app = BupilicKarlilikGUI()
    app.run()