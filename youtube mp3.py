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

class YouTubeDownloader(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        # İndirme klasörü için yol
        self.download_folder = os.path.join(os.path.expanduser('~'), 'Desktop', 'YouTubeIndirilenler')
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)

    def init_ui(self):
        # Pencere ayarları
        self.setWindowTitle('YouTube Video/Ses İndirici')
        self.setFixedSize(480, 380)  # Biraz daha büyük pencere
        
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
                margin-bottom: 4px;
            }
        ''')

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(36, 28, 36, 28)

        self.url_label = QtWidgets.QLabel('YouTube Video URL:')
        layout.addWidget(self.url_label)

        self.url_input = AnimatedLineEdit()
        self.url_input.setPlaceholderText('Video URL\'sini buraya yapıştırın...')
        layout.addWidget(self.url_input)

        # Format seçim kısmı yeniden tasarlanıyor
        format_label = QtWidgets.QLabel("İndirme Formatı")
        format_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(format_label)
        
        # Format seçenekleri için widget ve layout
        format_widget = QtWidgets.QWidget()
        format_layout = QtWidgets.QHBoxLayout(format_widget)
        format_layout.setContentsMargins(0, 0, 0, 0)
        format_layout.setSpacing(10)
        
        # Butonlar için ortak stil
        button_style = '''
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                             stop:0 #5c5f8a, stop:1 #4a4e69);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 0;
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
                min-height: 45px;
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
        
        # Format seçim butonları için stil
        format_button_style = '''
            QPushButton {
                background: #ffffff;
                color: #22223b;
                border: 2px solid #d1d1d1;
                border-radius: 10px;
                padding: 8px 0;
                font-size: 15px;
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
        self.mp4_btn.setMinimumHeight(40)
        
        self.mp3_btn = QtWidgets.QPushButton("MP3 (Ses)")
        self.mp3_btn.setCheckable(True)
        self.mp3_btn.setStyleSheet(format_button_style)
        self.mp3_btn.setMinimumHeight(40)
        
        # Buton grubuna ekle
        self.format_group = QtWidgets.QButtonGroup(self)
        self.format_group.addButton(self.mp4_btn, 1)
        self.format_group.addButton(self.mp3_btn, 2)
        self.format_group.setExclusive(True)
        
        # Layout'a butonları ekle
        format_layout.addWidget(self.mp4_btn)
        format_layout.addWidget(self.mp3_btn)
        
        layout.addWidget(format_widget)

        self.download_btn = AnimatedButton('İndir')
        self.download_btn.setStyleSheet(button_style)
        self.download_btn.clicked.connect(self.download)
        layout.addWidget(self.download_btn)

        # Klasörü Aç butonu
        self.open_folder_btn = AnimatedButton('İndirme Klasörünü Aç')
        self.open_folder_btn.setStyleSheet(button_style)
        self.open_folder_btn.clicked.connect(self.open_download_folder)
        layout.addWidget(self.open_folder_btn)

        self.status_label = AnimatedStatusLabel()
        layout.addWidget(self.status_label)

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
        url = self.url_input.text().strip()
        if not url:
            self.status_label.setText('Lütfen bir URL girin.')
            return

        # İndirme klasörünün var olduğundan emin ol
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)

        self.status_label.setText('İndiriliyor...')
        QtWidgets.QApplication.processEvents()

        # outtmpl değerini doğrudan string olarak ver
        outtmpl = os.path.join(self.download_folder, '%(title)s.%(ext)s')

        if self.mp4_btn.isChecked():
            options = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/bestvideo+bestaudio/best',
                'outtmpl': outtmpl,
                'merge_output_format': 'mp4',
                'noplaylist': True,
                'ignoreerrors': True,
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
            }
        try:
            with YoutubeDL(options) as ydl:
                result = ydl.download([url])
            self.status_label.setText('İndirme tamamlandı!')
        except Exception as e:
            if 'Requested format is not available' in str(e):
                self.status_label.setText('Seçilen formatta video bulunamadı. Lütfen farklı bir video veya format deneyin.')
            else:
                self.status_label.setText(f'Hata: {str(e)}')

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec_())
