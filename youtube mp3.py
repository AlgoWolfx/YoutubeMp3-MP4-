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
            font-size: 14px; 
            margin-top: 10px;
            font-weight: 500;
            padding: 8px;
            background-color: rgba(108, 99, 255, 0.1);
            border-radius: 8px;
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
            self.setFixedHeight(40)  # Yüksekliği ayarla
            self.anim.setStartValue(0.0)
            self.anim.setEndValue(1.0)
            self.anim.start()
        else:
            # Mesaj yoksa gizle
            self.setFixedHeight(0)
            super().setText("")

class DownloadProgressBar(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Layout oluştur
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)
        
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
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMinimumHeight(6)
        self.progress_bar.setMaximumHeight(6)
        self.progress_bar.setStyleSheet('''
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.3);
                border: none;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: #ffffff;
                border-radius: 3px;
            }
        ''')
        
        # Detay metni
        self.detail_label = QtWidgets.QLabel("")
        self.detail_label.setStyleSheet('''
            color: rgba(255, 255, 255, 0.8);
            font-size: 13px;
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

    def init_ui(self):
        # Pencere ayarları
        self.setWindowTitle('YouTube Video/Ses İndirici')
        self.setFixedSize(600, 520)  # Daha da büyük pencere boyutu
        
        # İkon ayarlarını kaldırıyoruz - dosya olmadığı için
        # Yerine basit bir stil tanımlıyoruz
        
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

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(20)  # Bileşenler arası boşluğu ayarla
        layout.setContentsMargins(50, 40, 50, 40)  # Kenar boşluklarını arttır

        # Başlık ve URL giriş alanı
        header_widget = QtWidgets.QWidget()
        header_layout = QtWidgets.QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)  # Başlık ve giriş kutusu arasındaki boşluk
        
        self.url_label = QtWidgets.QLabel('YouTube Video URL:')
        self.url_label.setStyleSheet('font-size: 18px; font-weight: 600;')  # Başlığı daha belirgin yap
        header_layout.addWidget(self.url_label)

        self.url_input = AnimatedLineEdit()
        self.url_input.setPlaceholderText('Video URL\'sini buraya yapıştırın...')
        self.url_input.setMinimumHeight(50)  # URL giriş kutusunu daha büyük yap
        header_layout.addWidget(self.url_input)
        
        layout.addWidget(header_widget)

        # Format seçim kısmı yeniden tasarlanıyor
        format_section = QtWidgets.QWidget()
        format_section_layout = QtWidgets.QVBoxLayout(format_section)
        format_section_layout.setContentsMargins(0, 0, 0, 0)
        format_section_layout.setSpacing(15)  # Başlık ve butonlar arası boşluğu arttır
        
        format_label = QtWidgets.QLabel("İndirme Formatı")
        format_label.setAlignment(QtCore.Qt.AlignCenter)
        format_label.setStyleSheet('font-size: 17px; margin-top: 5px;')
        format_section_layout.addWidget(format_label)
        
        # Format seçenekleri için widget ve layout
        format_widget = QtWidgets.QWidget()
        format_layout = QtWidgets.QHBoxLayout(format_widget)
        format_layout.setContentsMargins(0, 0, 0, 0)
        format_layout.setSpacing(20)  # Format butonları arası boşluğu arttır
        
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
        self.mp4_btn.setMinimumHeight(50)  # Format butonlarını daha büyük yap
        self.mp4_btn.setMinimumWidth(200)  # Minimum genişlik belirle
        
        self.mp3_btn = QtWidgets.QPushButton("MP3 (Ses)")
        self.mp3_btn.setCheckable(True)
        self.mp3_btn.setStyleSheet(format_button_style)
        self.mp3_btn.setMinimumHeight(50)  # Format butonlarını daha büyük yap
        self.mp3_btn.setMinimumWidth(200)  # Minimum genişlik belirle
        
        # Buton grubuna ekle
        self.format_group = QtWidgets.QButtonGroup(self)
        self.format_group.addButton(self.mp4_btn, 1)
        self.format_group.addButton(self.mp3_btn, 2)
        self.format_group.setExclusive(True)
        
        # Layout'a butonları ekle
        format_layout.addWidget(self.mp4_btn)
        format_layout.addWidget(self.mp3_btn)
        
        format_section_layout.addWidget(format_widget)
        layout.addWidget(format_section)

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
                margin-top: 5px;
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
        '''

        # İndir butonu ve progress bar için bir yığın
        self.button_stack = QtWidgets.QStackedWidget()
        self.button_stack.setMinimumHeight(65)  # Minimum yüksekliği ayarla
        
        # İndirme butonu widget
        download_btn_widget = QtWidgets.QWidget()
        download_btn_layout = QtWidgets.QVBoxLayout(download_btn_widget)
        download_btn_layout.setContentsMargins(0, 0, 0, 0)
        
        self.download_btn = AnimatedButton('İndir')
        self.download_btn.setStyleSheet(button_style)
        self.download_btn.setMinimumWidth(500)  # Minimum genişlik belirle
        self.download_btn.clicked.connect(self.download)
        download_btn_layout.addWidget(self.download_btn)
        
        # İlerleme çubuğu widget
        progress_widget = QtWidgets.QWidget()
        progress_layout = QtWidgets.QVBoxLayout(progress_widget)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        
        self.progress_bar = DownloadProgressBar()
        self.progress_bar.setStyleSheet('''
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                         stop:0 #6c63ff, stop:1 #5753d0);
            border-radius: 12px;
            padding: 15px;
        ''')
        self.progress_bar.setMinimumHeight(55)
        self.progress_bar.setMinimumWidth(500)  # Minimum genişlik belirle
        progress_layout.addWidget(self.progress_bar)
        
        # Yığın widget'a ekle
        self.button_stack.addWidget(download_btn_widget)
        self.button_stack.addWidget(progress_widget)
        
        layout.addWidget(self.button_stack)

        # Klasörü Aç butonu
        open_folder_section = QtWidgets.QWidget()
        open_folder_layout = QtWidgets.QVBoxLayout(open_folder_section)
        open_folder_layout.setContentsMargins(0, 0, 0, 0)
        
        self.open_folder_btn = AnimatedButton('İndirme Klasörünü Aç')
        self.open_folder_btn.setMinimumWidth(500)  # Minimum genişlik belirle
        self.open_folder_btn.setStyleSheet('''
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                             stop:0 #6a6d8b, stop:1 #585b75);
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
                             stop:0 #7a7d9b, stop:1 #686b85);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                             stop:0 #5a5d7b, stop:1 #484b65);
            }
        ''')
        self.open_folder_btn.clicked.connect(self.open_download_folder)
        open_folder_layout.addWidget(self.open_folder_btn)
        
        layout.addWidget(open_folder_section)

        self.status_label = AnimatedStatusLabel()
        layout.addWidget(self.status_label)
        
        # Boşluk ekle
        spacer = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        layout.addItem(spacer)

        self.setLayout(layout)

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

    def download(self):
        if self.is_downloading:
            return
            
        url = self.url_input.text().strip()
        if not url:
            self.status_label.setText('Lütfen bir URL girin.')
            return

        # İndirme klasörünün var olduğundan emin ol
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)
            
        # İndirme durumunu güncelle
        self.is_downloading = True
        
        # İlerleme çubuğunu göster
        self.button_stack.setCurrentIndex(1)
        self.progress_bar.start_progress()
        self.progress_bar.set_status("İndiriliyor...")
        
        if self.mp4_btn.isChecked():
            self.progress_bar.set_detail("Video indiriliyor ve işleniyor...")
        else:
            self.progress_bar.set_detail("Ses indiriliyor ve MP3'e dönüştürülüyor...")
            
        QtWidgets.QApplication.processEvents()

        # outtmpl değerini doğrudan string olarak ver
        outtmpl = os.path.join(self.download_folder, '%(title)s.%(ext)s')

        # İndirme ilerlemesini takip etmek için özel hooks tanımla
        def my_hook(d):
            if d['status'] == 'downloading':
                if 'downloaded_bytes' in d and 'total_bytes' in d and d['total_bytes'] > 0:
                    percent = d['downloaded_bytes'] / d['total_bytes'] * 100
                    self.progress_bar.update_progress(int(percent))
                    self.progress_bar.set_detail(f"İndiriliyor: %{int(percent)}")
                elif 'downloaded_bytes' in d and 'total_bytes_estimate' in d and d['total_bytes_estimate'] > 0:
                    percent = d['downloaded_bytes'] / d['total_bytes_estimate'] * 100
                    self.progress_bar.update_progress(int(percent))
                    self.progress_bar.set_detail(f"İndiriliyor: %{int(percent)} (tahmini)")
            elif d['status'] == 'finished':
                self.progress_bar.update_progress(100)
                if self.mp4_btn.isChecked():
                    self.progress_bar.set_detail("Video işleniyor...")
                else:
                    self.progress_bar.set_detail("MP3'e dönüştürülüyor...")
                QtWidgets.QApplication.processEvents()

        if self.mp4_btn.isChecked():
            options = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/bestvideo+bestaudio/best',
                'outtmpl': outtmpl,
                'merge_output_format': 'mp4',
                'noplaylist': True,
                'ignoreerrors': True,
                'progress_hooks': [my_hook],
            }
        else:
            options = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
                'outtmpl': outtmpl,
                'noplaylist': True,
                'ignoreerrors': True,
                'progress_hooks': [my_hook],
            }
            
        try:
            with YoutubeDL(options) as ydl:
                result = ydl.download([url])
            self.progress_bar.finish(True)
            QtWidgets.QApplication.processEvents()
            QtCore.QTimer.singleShot(2000, self.download_finished)
        except Exception as e:
            self.progress_bar.finish(False)
            if 'Requested format is not available' in str(e):
                self.progress_bar.set_detail('Seçilen formatta video bulunamadı.')
            else:
                self.progress_bar.set_detail(f'Hata: {str(e)}')
            QtCore.QTimer.singleShot(2000, self.download_failed)
            
    def download_finished(self):
        """İndirme başarıyla tamamlandığında çağrılır"""
        # İndirme durumunu güncelle
        self.is_downloading = False
        
        # Butonları göster
        self.button_stack.setCurrentIndex(0)
        
        # Durumu güncelle
        self.status_label.setText('İndirme tamamlandı!')
        
    def download_failed(self):
        """İndirme başarısız olduğunda çağrılır"""
        # İndirme durumunu güncelle
        self.is_downloading = False
        
        # Butonları göster
        self.button_stack.setCurrentIndex(0)
        
        # Durumu güncelle
        self.status_label.setText('İndirme başarısız oldu!')

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec_())
