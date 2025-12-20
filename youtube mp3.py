from PyQt5 import QtWidgets, QtCore, QtGui
from yt_dlp import YoutubeDL
import sys
import os
import re
import subprocess

class AnimatedButton(QtWidgets.QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=18, xOffset=0, yOffset=3, color=QtGui.QColor(74, 78, 105, 120)))
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.anim = QtCore.QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(120)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Enter:
            self.anim.stop()
            rect = self.geometry()
            self.anim.setStartValue(rect)
            self.anim.setEndValue(QtCore.QRect(rect.x()-2, rect.y()-2, rect.width()+4, rect.height()+4))
            self.anim.start()
        elif event.type() == QtCore.QEvent.Leave:
            self.anim.stop()
            rect = self.geometry()
            self.anim.setStartValue(rect)
            self.anim.setEndValue(QtCore.QRect(rect.x()+2, rect.y()+2, rect.width()-4, rect.height()-4))
            self.anim.start()
        return super().eventFilter(obj, event)

class AnimatedLineEdit(QtWidgets.QLineEdit):
    def __init__(self):
        super().__init__()
        # Daha yumuşak ve modern gölge efekti
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QtGui.QColor(100, 100, 100, 80))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        # Temel stiller
        self.setMinimumHeight(45)  # Daha büyük input alanı
        self.setFont(QtGui.QFont("Segoe UI", 10))  # Daha iyi font
        
        # URL ikonu ekle
        self.url_icon = QtGui.QIcon.fromTheme("edit-link", QtGui.QIcon.fromTheme("insert-link"))
        self.action = self.addAction(self.url_icon, QtWidgets.QLineEdit.LeadingPosition)
        
        # Ana stil ayarları
        self.setStyleSheet('''
            QLineEdit {
                background-color: #ffffff;
                border: 2px solid #d1d1d1;
                border-radius: 12px;
                padding: 8px 12px 8px 40px;  /* Sağdan/soldan ilave padding */
                font-size: 10pt;
                selection-background-color: #6c63ff;
                selection-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #6c63ff;
                background-color: #f9f9ff;
            }
        ''')
        
        # Animasyon hazırlık
        self.anim = QtCore.QPropertyAnimation(self, b"styleSheet")
        self.anim.setDuration(200)
        self.installEventFilter(self)
        
        # Temizleme düğmesi ekle
        self.setClearButtonEnabled(True)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.FocusIn:
            self.anim.stop()
            self.anim.setStartValue(self.styleSheet())
            self.anim.setEndValue('''
                QLineEdit {
                    background-color: #f9f9ff;
                    border: 2px solid #6c63ff;
                    border-radius: 12px;
                    padding: 8px 12px 8px 40px;
                    font-size: 10pt;
                    selection-background-color: #6c63ff;
                    selection-color: white;
                }
                QLineEdit:focus {
                    border: 2px solid #6c63ff;
                    background-color: #f9f9ff;
                }
            ''')
            self.anim.start()
        elif event.type() == QtCore.QEvent.FocusOut:
            self.anim.stop()
            self.anim.setStartValue(self.styleSheet())
            self.anim.setEndValue('''
                QLineEdit {
                    background-color: #ffffff;
                    border: 2px solid #d1d1d1;
                    border-radius: 12px;
                    padding: 8px 12px 8px 40px;
                    font-size: 10pt;
                    selection-background-color: #6c63ff;
                    selection-color: white;
                }
                QLineEdit:focus {
                    border: 2px solid #6c63ff;
                    background-color: #f9f9ff;
                }
            ''')
            self.anim.start()
        return super().eventFilter(obj, event)

class AnimatedStatusLabel(QtWidgets.QLabel):
    def __init__(self):
        super().__init__()
        # Modern stil
        self.setStyleSheet('''
            color: #6c63ff; 
            font-size: 16px; 
            font-weight: 600;
            padding: 10px;
            background-color: rgba(108, 99, 255, 0.15);
            border-radius: 8px;
            border: 1px solid rgba(108, 99, 255, 0.3);
        ''')
        
        # Gölge efekti
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QtGui.QColor(108, 99, 255, 70))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        # Animasyon
        self.anim = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(300)
        self.setWindowOpacity(1.0)
        
        # Başlangıçta görünmez
        self.setText("")
        self.setFixedHeight(0)
        self.setAlignment(QtCore.Qt.AlignCenter)

    def setText(self, text):
        self.anim.stop()
        
        if text:
            # Mesaj varsa göster
            self.setWindowOpacity(0.0)
            super().setText(text)
            self.setFixedHeight(45)  # Yüksekliği arttır
            self.anim.setStartValue(0.0)
            self.anim.setEndValue(1.0)
            self.anim.start()
        else:
            # Mesaj yoksa gizle
            self.setFixedHeight(0)
            super().setText("")

class ResolutionSelectionDialog(QtWidgets.QDialog):
    def __init__(self, resolutions, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Çözünürlük Seçin")
        self.setModal(True)
        self.setFixedSize(300, 400)
        self.selected_format = None
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial;
            }
            QRadioButton {
                font-size: 15px;
                padding: 8px;
                color: #22223b;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #6c63ff;
                border-radius: 10px;
            }
            QRadioButton::indicator:checked {
                background-color: #6c63ff;
                border: 2px solid #6c63ff;
            }
            QLabel {
                color: #22223b;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            QPushButton {
                background: #6c63ff;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #5753d0;
            }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        
        info_label = QtWidgets.QLabel("Lütfen indirmek istediğiniz\nkaliteyi seçin:")
        info_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(info_label)

        # Scroll area for resolutions if there are many
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll_content = QtWidgets.QWidget()
        self.resolutions_layout = QtWidgets.QVBoxLayout(scroll_content)
        
        self.radio_buttons = []
        for i, res in enumerate(resolutions):
            # res format: {'format_id': '...', 'height': 1080, 'ext': 'mp4', 'filesize': ...}
            size_str = ""
            if res.get('filesize'):
                size_mb = res['filesize'] / (1024 * 1024)
                size_str = f" (~{size_mb:.1f} MB)"
            elif res.get('filesize_approx'):
                size_mb = res['filesize_approx'] / (1024 * 1024)
                size_str = f" (~{size_mb:.1f} MB)"
            
            text = f"{res.get('height', 'Bilinmeyen')}p - {res.get('ext')}{size_str}"
            rb = QtWidgets.QRadioButton(text)
            rb.setProperty('format_id', res['format_id'])
            if i == 0:
                rb.setChecked(True)
            self.resolutions_layout.addWidget(rb)
            self.radio_buttons.append(rb)
            
        self.resolutions_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # Button box
        buttons_layout = QtWidgets.QHBoxLayout()
        ok_btn = QtWidgets.QPushButton("İndir")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QtWidgets.QPushButton("İptal")
        cancel_btn.setStyleSheet("background: #dc3545; margin-left: 10px;")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(ok_btn)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)

    def get_selected_format(self):
        for rb in self.radio_buttons:
            if rb.isChecked():
                return rb.property('format_id')
        return None

class DownloadProgressBar(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Layout oluştur
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)
        
        # Durum mesajı
        self.status_label = QtWidgets.QLabel("İndiriliyor...")
        self.status_label.setStyleSheet('''
            color: #ffffff;
            font-size: 16px;
            font-weight: bold;
            margin: 0;
        ''')
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        
        # İlerleme çubuğu
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)  # Metni görünür yap
        self.progress_bar.setFormat("%p%")      # Yüzde formatı
        self.progress_bar.setMinimumHeight(14)  # Daha kalın
        self.progress_bar.setMaximumHeight(14)
        self.progress_bar.setStyleSheet('''
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.3);
                border: none;
                border-radius: 7px;
                text-align: center;
                color: white;
                font-weight: bold;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background-color: #ffffff;
                border-radius: 7px;
            }
        ''')
        
        # Detay metni
        self.detail_label = QtWidgets.QLabel("")
        self.detail_label.setStyleSheet('''
            color: rgba(255, 255, 255, 0.9);
            font-size: 13px;
            font-weight: 500;
        ''')
        self.detail_label.setAlignment(QtCore.Qt.AlignCenter)
        
        # Bileşenleri ekle
        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.detail_label)
        
        # İlerleme animasyonu için timer
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.progress_value = 0
        self.is_indeterminate = True
        
        # Başlangıçta gizli
        self.hide()
        
    def start_progress(self, indeterminate=True):
        """İlerleme çubuğunu başlat"""
        self.is_indeterminate = indeterminate
        self.progress_value = 0
        self.progress_bar.setValue(0)
        if indeterminate:
            self.timer.start(50)
        self.show()
        
    def update_progress(self, value=None):
        """İlerleme çubuğunu güncelle"""
        if value is not None and not self.is_indeterminate:
            self.progress_value = value
            self.progress_bar.setValue(value)
        elif self.is_indeterminate:
            self.progress_value = (self.progress_value + 1) % 101
            self.progress_bar.setValue(self.progress_value)
    
    def set_status(self, text):
        """Durum metnini ayarla"""
        self.status_label.setText(text)
        
    def set_detail(self, text):
        """Detay metnini ayarla"""
        self.detail_label.setText(text)
        
    def finish(self, success=True):
        """İşlemi tamamla"""
        self.timer.stop()
        if success:
            self.progress_bar.setValue(100)
            self.set_status("İndirme tamamlandı!")
            self.set_detail("")
        else:
            self.set_status("İndirme başarısız oldu")
            
    def hide_progress(self):
        """İlerleme çubuğunu gizle"""
        self.timer.stop()
        self.hide()

class DownloadThread(QtCore.QThread):
    progress_signal = QtCore.pyqtSignal(dict)
    finished_signal = QtCore.pyqtSignal()
    error_signal = QtCore.pyqtSignal(str)
    info_ready_signal = QtCore.pyqtSignal(dict)
    
    def __init__(self, url, download_folder, is_video=True, selected_format=None, is_playlist=False):
        super().__init__()
        self.url = url
        self.download_folder = download_folder
        self.is_video = is_video
        self.selected_format = selected_format
        self.is_playlist = is_playlist
        self.mode = 'extract_info' # 'extract_info' veya 'download'
        self.info = None

    def set_mode_download(self, selected_format, is_playlist=False):
        self.mode = 'download'
        self.selected_format = selected_format
        self.is_playlist = is_playlist

    def run(self):
        try:
            # Playlist başlığına göre klasör oluşturmak için güvenli isim fonksiyonu
            def get_safe_filename(title):
                return re.sub(r'[\\/:*?"<>|]', '', title)
                
            outtmpl = os.path.join(self.download_folder, '%(title)s.%(ext)s')
            
            if self.mode == 'extract_info':
                # Sadece bilgi çek
                with YoutubeDL({'quiet': True, 'no_warnings': True, 'extract_flat': 'in_playlist'}) as ydl:
                    self.info = ydl.extract_info(self.url, download=False)
                self.info_ready_signal.emit(self.info)
                
            elif self.mode == 'download':
                def my_hook(d):
                    if d['status'] == 'downloading':
                        self.progress_signal.emit(d)
                    elif d['status'] == 'finished':
                        d['progress_percent'] = 100
                        self.progress_signal.emit(d)

                # FFmpeg yolu (Kullanıcının belirttiği klasör)
                ffmpeg_dir = r"C:\ffmpeg"
                ffmpeg_path = os.path.join(ffmpeg_dir, "ffmpeg.exe")

                # FFmpeg kontrolü
                ffmpeg_available = False
                if os.path.exists(ffmpeg_path):
                    ffmpeg_available = True
                else:
                    # Sistem yolunda kontrol et
                    try:
                        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                        ffmpeg_available = True
                    except:
                        ffmpeg_available = False

                # Playlist ayarları
                ydl_opts = {
                    'ignoreerrors': True,
                    'progress_hooks': [my_hook],
                    'noplaylist': False if self.is_playlist else True,
                    'ffmpeg_location': ffmpeg_dir,
                }

                if self.is_playlist:
                     # Playlist ise alt klasöre indir
                     playlist_title = self.info.get('title', 'Playlist')
                     safe_title = get_safe_filename(playlist_title)
                     playlist_path = os.path.join(self.download_folder, safe_title)
                     if not os.path.exists(playlist_path):
                         os.makedirs(playlist_path)
                     # Dosya isminin başına sıra numarasını ekle (ör: 01 - Video Başlığı.mp4)
                     outtmpl = os.path.join(playlist_path, '%(playlist_index)s - %(title)s.%(ext)s')

                ydl_opts['outtmpl'] = outtmpl

                if self.is_video:
                    # Video
                    if self.is_playlist:
                        # Playlist için format seçimi
                        if ffmpeg_available:
                            # FFmpeg varsa: MP4 video (H.264 codec) + M4A ses
                            # [vcodec^=avc1] etiketi AV1 (av01) formatını engeller, H.264 (en uyumlu) seçer.
                            format_str = "bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]/best"
                        else:
                            # FFmpeg yoksa bile MP4 zorla
                            format_str = "best[ext=mp4]/best"
                    else:
                        # Tek video
                        if ffmpeg_available:
                            # Eğer kullanıcı özel format seçmediyse veya format seçimi geçersizse
                            if self.selected_format:
                                # Seçilen formatı MP4 stream ile birleştirmeyi dene (veya dönüştür)
                                format_str = f"{self.selected_format}+bestaudio[ext=m4a]/best[ext=mp4]/best"
                            else:
                                # Otomatik en iyi MP4 (H.264 Codec zorunlu)
                                format_str = "bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]/best"
                        else:
                            format_str = "best[ext=mp4]/best"
                    
                    ydl_opts.update({
                        'format': format_str,
                    })
                    
                    if ffmpeg_available:
                        ydl_opts['merge_output_format'] = 'mp4'
                        # Garanti olsun diye postprocessor ekle
                        ydl_opts['postprocessors'] = [{
                            'key': 'FFmpegVideoConvertor',
                            'preferedformat': 'mp4',
                        }]
                        
                else:
                    # Ses (MP3)
                    if ffmpeg_available:
                        ydl_opts.update({
                            'format': 'bestaudio/best',
                            'postprocessors': [{
                                'key': 'FFmpegExtractAudio',
                                'preferredcodec': 'mp3',
                                'preferredquality': '192',
                            }],
                        })
                    else:
                        # FFmpeg yoksa m4a/webm ses dosyasını olduğu gibi indir
                         ydl_opts.update({
                            'format': 'bestaudio/best',
                        })
                    
                # İndirme işlemini dene (Hata olursa basit formata geç)
                try:
                    with YoutubeDL(ydl_opts) as ydl:
                        ydl.download([self.url])
                except Exception as e:
                    error_msg = str(e)
                    # Eğer format hatası ise ve henüz fallback yapmadıysak
                    if 'Requested format is not available' in error_msg:
                        print("Karmaşık format başarısız oldu, 'best' formatı deneniyor...")
                        # Basit format ayarı
                        ydl_opts['format'] = 'best'
                        if 'merge_output_format' in ydl_opts:
                            del ydl_opts['merge_output_format']
                            
                        with YoutubeDL(ydl_opts) as ydl:
                            ydl.download([self.url])
                    else:
                        raise e  # Diğer hataları yukarı fırlat

                self.finished_signal.emit()
                
        except Exception as e:
            self.error_signal.emit(str(e))

class YouTubeDownloader(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        # İndirme klasörü için yol
        self.download_folder = os.path.join(os.path.expanduser('~'), 'Desktop', 'YouTubeIndirilenler')
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)
        
        # İndirme durumu için flag
        self.is_downloading = False
        self.download_thread = None

    def init_ui(self):
        # Pencere ayarları
        self.setWindowTitle('YouTube Video/Ses İndirici')
        self.setFixedSize(600, 600)  # Daha büyük pencere
        
        self.setStyleSheet('''
            QWidget {
                background: #f8f9fa;
                font-family: 'Segoe UI', Arial;
            }
            QLabel {
                color: #22223b;
                font-size: 16px;
                font-weight: 500;
                margin-bottom: 6px;
            }
        ''')

        # Ana layout - QGridLayout kullanacağız
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setSpacing(15)  
        main_layout.setContentsMargins(50, 40, 50, 40)  

        # 1. Başlık ve URL giriş alanı
        header_widget = QtWidgets.QWidget()
        header_layout = QtWidgets.QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)
        
        self.url_label = QtWidgets.QLabel('YouTube Video/Playlist URL:')
        self.url_label.setStyleSheet('font-size: 18px; font-weight: 600;')
        header_layout.addWidget(self.url_label)

        self.url_input = AnimatedLineEdit()
        self.url_input.setPlaceholderText('Video veya Playlist linkini buraya yapıştırın...')
        self.url_input.setMinimumHeight(50)
        header_layout.addWidget(self.url_input)
        
        main_layout.addWidget(header_widget)

        # 2. Format seçim kısmı
        format_widget = QtWidgets.QWidget()
        format_widget.setFixedHeight(120)  # Sabit yükseklik
        format_layout = QtWidgets.QVBoxLayout(format_widget)
        format_layout.setContentsMargins(0, 0, 0, 0)
        
        format_label = QtWidgets.QLabel("İndirme Formatı")
        format_label.setAlignment(QtCore.Qt.AlignCenter)
        format_label.setStyleSheet('font-size: 17px; margin-top: 5px;')
        format_layout.addWidget(format_label)
        
        # Format seçenekleri için butonlar
        format_button_container = QtWidgets.QWidget()
        format_button_layout = QtWidgets.QHBoxLayout(format_button_container)
        format_button_layout.setContentsMargins(0, 0, 0, 0)
        format_button_layout.setSpacing(20)
        
        # Format seçim butonları için stil
        format_button_style = '''
            QPushButton {
                background: #ffffff;
                color: #22223b;
                border: 2px solid #d1d1d1;
                border-radius: 12px;
                padding: 12px 0;
                font-size: 16px;
                font-weight: 500;
            }
            QPushButton:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                             stop:0 #6c63ff, stop:1 #5753d0);
                border: 2px solid #6c63ff;
                color: white;
            }
            QPushButton:hover:!checked {
                border: 2px solid #6c63ff;
                background-color: #f5f5ff;
            }
        '''
        
        # MP4 ve MP3 seçim butonları
        self.mp4_btn = QtWidgets.QPushButton("MP4 (Video)")
        self.mp4_btn.setCheckable(True)
        self.mp4_btn.setChecked(True)
        self.mp4_btn.setStyleSheet(format_button_style)
        self.mp4_btn.setFixedHeight(50)
        
        self.mp3_btn = QtWidgets.QPushButton("MP3 (Ses)")
        self.mp3_btn.setCheckable(True)
        self.mp3_btn.setStyleSheet(format_button_style)
        self.mp3_btn.setFixedHeight(50)
        
        # Buton grubuna ekle
        self.format_group = QtWidgets.QButtonGroup(self)
        self.format_group.addButton(self.mp4_btn, 1)
        self.format_group.addButton(self.mp3_btn, 2)
        self.format_group.setExclusive(True)
        
        # Layout'a butonları ekle
        format_button_layout.addWidget(self.mp4_btn)
        format_button_layout.addWidget(self.mp3_btn)
        
        format_layout.addWidget(format_button_container)
        main_layout.addWidget(format_widget)

        # 3. Butonlar ve durum bölgesi (sabit yükseklikte)
        actions_widget = QtWidgets.QWidget()
        actions_widget.setFixedHeight(235)  # Sabit yükseklik - boşluk için biraz daha arttırıldı
        actions_layout = QtWidgets.QVBoxLayout(actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(15)
        
        # Butonlar için ortak stil
        button_style = '''
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                             stop:0 #5c5f8a, stop:1 #4a4e69);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 15px 0;
                font-size: 17px;
                font-weight: bold;
                min-height: 55px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                             stop:0 #6c63ff, stop:1 #5753d0);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                             stop:0 #4f47c2, stop:1 #4641a7);
            }
            QPushButton:disabled {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                             stop:0 #9a9bac, stop:1 #8a8a9a);
                color: #d0d0d0;
            }
        '''

        # İndirme Butonları Grubu
        download_buttons_layout = QtWidgets.QHBoxLayout()
        download_buttons_layout.setSpacing(15)

        # Tek Video İndir butonu
        self.single_btn = AnimatedButton('Video İndir')
        self.single_btn.setStyleSheet('''
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                             stop:0 #5c5f8a, stop:1 #4a4e69);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 15px 0;
                font-size: 16px;
                font-weight: bold;
                min-height: 55px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                             stop:0 #6c63ff, stop:1 #5753d0);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:1, y1:0, x2:1, y2:0, 
                             stop:0 #4f47c2, stop:1 #4641a7);
            }
            QPushButton:disabled {
                background: qlineargradient(x1:1, y1:0, x2:1, y2:0, 
                             stop:0 #9a9bac, stop:1 #8a8a9a);
                color: #d0d0d0;
            }
        ''')
        self.single_btn.clicked.connect(lambda: self.start_info_fetch(playlist_mode=False))
        download_buttons_layout.addWidget(self.single_btn)

        # Playlist İndir butonu
        self.playlist_btn = AnimatedButton('Playlist İndir')
        self.playlist_btn.setStyleSheet('''
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                             stop:0 #2a9d8f, stop:1 #264653);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 15px 0;
                font-size: 16px;
                font-weight: bold;
                min-height: 55px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:1, y1:0, x2:1, y2:0, 
                             stop:0 #2ec4b6, stop:1 #2a9d8f);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:1, y1:0, x2:1, y2:0, 
                             stop:0 #264653, stop:1 #1d3557);
            }
            QPushButton:disabled {
                background: qlineargradient(x1:1, y1:0, x2:1, y2:0, 
                             stop:0 #9a9bac, stop:1 #8a8a9a);
                color: #d0d0d0;
            }
        ''')
        self.playlist_btn.clicked.connect(lambda: self.start_info_fetch(playlist_mode=True))
        download_buttons_layout.addWidget(self.playlist_btn)

        actions_layout.addLayout(download_buttons_layout)
        actions_layout.addSpacing(20)  # Butonlar arasına boşluk ekle

        # Klasörü Aç butonu
        self.open_folder_btn = AnimatedButton('İndirme Klasörünü Aç')
        self.open_folder_btn.setFixedHeight(50)
        self.open_folder_btn.setStyleSheet('''
            QPushButton {
                background: qlineargradient(x1:1, y1:0, x2:1, y2:0, 
                             stop:0 #6a6d8b, stop:1 #585b75);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 0;
                font-size: 17px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:1, y1:0, x2:1, y2:0, 
                             stop:0 #7a7d9b, stop:1 #686b85);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:1, y1:0, x2:1, y2:0, 
                             stop:0 #5a5d7b, stop:1 #484b65);
            }
            QPushButton:disabled {
                background: qlineargradient(x1:1, y1:0, x2:1, y2:0, 
                             stop:0 #8a8a9a, stop:1 #777788);
                color: #d0d0d0;
            }
        ''')
        self.open_folder_btn.clicked.connect(self.open_download_folder)
        actions_layout.addWidget(self.open_folder_btn)

        # Durum bildirimi için sabit alan
        self.status_container = QtWidgets.QWidget()
        self.status_container.setFixedHeight(60)  # Yüksekliği arttır
        status_container_layout = QtWidgets.QVBoxLayout(self.status_container)
        status_container_layout.setContentsMargins(0, 0, 0, 0)
        
        self.status_label = AnimatedStatusLabel()
        status_container_layout.addWidget(self.status_label)
        
        actions_layout.addWidget(self.status_container)
        main_layout.addWidget(actions_widget)

        # 4. İlerleme çubuğu bölgesi (her zaman sabit alan)
        progress_section = QtWidgets.QWidget()
        progress_section.setFixedHeight(100)  # Yüksekliği arttır
        progress_layout = QtWidgets.QVBoxLayout(progress_section)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setAlignment(QtCore.Qt.AlignCenter)  # Ortala
        
        self.progress_bar = DownloadProgressBar()
        self.progress_bar.setStyleSheet('''
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                         stop:0 #6c63ff, stop:1 #5753d0);
            border-radius: 12px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            padding: 15px;
        ''')
        self.progress_bar.setFixedHeight(80)
        progress_layout.addWidget(self.progress_bar)
        
        main_layout.addWidget(progress_section)
        
        # Boşluk doldurma
        spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        main_layout.addItem(spacer)

        self.setLayout(main_layout)

    def get_safe_filename(self, title):
        # Geçersiz karakterleri temizle
        return re.sub(r'[\\/:*?"<>|]', '', title)

    def open_download_folder(self):
        # İndirme klasörünü aç
        if os.path.exists(self.download_folder):
            if sys.platform == 'win32':
                os.startfile(self.download_folder)
            elif sys.platform == 'darwin':  # macOS
                subprocess.call(['open', self.download_folder])
            else:  # Linux
                subprocess.call(['xdg-open', self.download_folder])
        else:
            self.status_label.setText('İndirme klasörü bulunamadı!')

    def start_info_fetch(self, playlist_mode=False):
        if self.is_downloading:
            return
            
        url = self.url_input.text().strip()
        if not url:
            self.status_label.setText('Lütfen bir URL girin.')
            return

        # İndirme modu tercihi
        self.target_playlist_mode = playlist_mode

        # İndirme klasörünün var olduğundan emin ol
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)

        # UI Kilitle
        self.is_downloading = True
        self.single_btn.setEnabled(False)
        self.playlist_btn.setEnabled(False)
        self.mp3_btn.setEnabled(False)
        self.mp4_btn.setEnabled(False)
        self.status_label.setText("Bilgiler alınıyor...")
        self.progress_bar.start_progress(True)
        
        # Thread başlat - Playlist moduysa direkt playlist al, değilse noplaylist=True
        # Ancak info çekerken noplaylist=False yapmak daha güvenli, sonra karar veririz
        # fakat kullanıcı Video İndir dediyse playlist'i görmezden gelmeliyiz.
        # DownloadThread'e bu bilgiyi gönderelim mi? 
        # Şu anlık DownloadThread'de 'extract_flat': 'in_playlist' var.
        
        # Eğer kullanıcı "Video İndir" dediyse ve link playlist ise, sadece videoyu çekmek isteyebilir.
        # Ama DownloadThread init kısmında is_playlist yok, sonradan set ediliyor.
        # Şimdilik standart info çekelim, on_info_ready'de filtreleyelim.
        
        self.download_thread = DownloadThread(url, self.download_folder, self.mp4_btn.isChecked())
        self.download_thread.info_ready_signal.connect(self.on_info_ready)
        self.download_thread.error_signal.connect(self.on_error)
        self.download_thread.start()

    def on_info_ready(self, info):
        try:
            is_playlist_url = info.get('_type') == 'playlist' or 'entries' in info
            
            # Kullanıcı tercihi ile URL uyumu kontrolü
            if self.target_playlist_mode:
                # Playlist indirmek istendi
                if not is_playlist_url:
                    # Link playlist değil ama playlist butonu tıklandı -> Sorun yok, tek video iner
                    pass
                
                # Playlist ise soru sormadan indir
                self.start_actual_download(info)
                return
            else:
                # Tek video indirmek istendi
                if is_playlist_url:
                    # Link bir playlist ama kullanıcı "Video İndir" dedi.
                    # Bu durumda playlistin tamamını indirmemeliyiz.
                    # Eğer URL "watch?v=...&list=..." ise sadece videoyu indirmeliyiz.
                    # Eğer URL sadece "playlist?list=..." ise ve video ID yoksa ne yapmalı?
                    # yt-dlp 'noplaylist=True' ile bu işi halleder ama info çoktan çekildi.
                    
                    # Eğer info'da 'entries' varsa ve bu bir liste ise:
                    # 'Video İndir' dendiği için sadece İLK videoyu veya linkteki videoyu almalıyız. 
                    # Ancak info'yu 'extract_flat' ile çektik.
                    
                    # En doğrusu: İndirme aşamasına "noplaylist=True" bayrağı ile gitmek.
                    pass
                    
                self.start_actual_download(info, force_single=True)
                return

        except Exception as e:
            self.on_error(str(e))

    def start_actual_download(self, info, force_single=False):
        # Yardımcı fonksiyon: indirmeyi başlat
        is_playlist = (info.get('_type') == 'playlist' or 'entries' in info) and not force_single

        # Eğer force_single ise ve aslında playlist ise, playlist özelliğini kapatarak indirme yapmalıyız
        
        # Thread'i indirme moduna geçir
        self.download_thread.set_mode_download(self.download_thread.selected_format, is_playlist=is_playlist)
        self.download_thread.progress_signal.connect(self.update_progress_ui)
        self.download_thread.finished_signal.connect(self.download_finished)
        self.download_thread.start()

    # Eski kodun devamı için...
    # Aşağıdaki blok orijinal on_info_ready'nin yerini aldığı için orijinal kodu siliyoruz.
    # Ancak orijinal kodda 'start_actual_download' yoktu, her şeyi on_info_ready içinde yapıyordu.
    # Bu yüzden burayı temizleyip entegre etmemiz lazım.
    pass

    # NOT: Bu replacement ile 'on_info_ready' tamamen değişiyor.
    # Orijinal 'on_info_ready' fonksiyonunu tekrar yazıyorum, yeni mantığa göre.
    
    def update_progress_ui(self, d):
        # Playlist bilgisi
        prefix = ""
        if d.get('info_dict'):
            info = d.get('info_dict')
            if 'playlist_index' in info and 'n_entries' in info:
                prefix = f"Video {info['playlist_index']}/{info['n_entries']} - "

        if 'downloaded_bytes' in d and 'total_bytes' in d and d['total_bytes'] > 0:
            percent = d['downloaded_bytes'] / d['total_bytes'] * 100
            self.progress_bar.update_progress(int(percent))
            self.progress_bar.set_detail(f"{prefix}İndiriliyor: %{int(percent)}")
        elif 'downloaded_bytes' in d and 'total_bytes_estimate' in d and d['total_bytes_estimate'] > 0:
            percent = d['downloaded_bytes'] / d['total_bytes_estimate'] * 100
            self.progress_bar.update_progress(int(percent))
            self.progress_bar.set_detail(f"{prefix}İndiriliyor: %{int(percent)} (tahmini)")
        elif d.get('progress_percent') == 100:
             self.progress_bar.update_progress(100)
             if self.mp4_btn.isChecked():
                self.progress_bar.set_detail(f"{prefix}Tamamlandı / İşleniyor...")
             else:
                self.progress_bar.set_detail(f"{prefix}Dönüştürülüyor...")

    def download_finished(self):
        self.is_downloading = False
        self.single_btn.setEnabled(True)
        self.playlist_btn.setEnabled(True)
        self.mp3_btn.setEnabled(True)
        self.mp4_btn.setEnabled(True)
        self.progress_bar.finish(success=True)
        
        # 2 saniye sonra durumu temizle
        QtCore.QTimer.singleShot(2000, lambda: self.status_label.setText('İşlem tamamlandı!'))
        
        # Thread bağlantılarını temizle
        if self.download_thread:
            try:
                self.download_thread.progress_signal.disconnect()
                self.download_thread.finished_signal.disconnect()
            except:
                pass

    def on_error(self, error_message):
        self.is_downloading = False
        self.single_btn.setEnabled(True)
        self.playlist_btn.setEnabled(True)
        self.mp3_btn.setEnabled(True)
        self.mp4_btn.setEnabled(True)
        
        self.progress_bar.finish(False)
        self.status_label.setText("Hata oluştu!")
        
        error_str = str(error_message)
        if 'Requested format is not available' in error_str:
            self.progress_bar.set_detail('Seçilen formatta video bulunamadı.')
        else:
            self.progress_bar.set_detail(f'Hata: {error_str[:50]}...')
            
        QtWidgets.QMessageBox.critical(self, "Hata", f"Bir hata oluştu:\n{error_str}")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec_())
