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
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f8f9fa, stop:1 #e9ecef);
                font-family: 'Segoe UI', Arial;
            }
            QLabel {
                color: #22223b;
                font-size: 16px;
                font-weight: 500;
                margin-bottom: 4px;
            }
            QRadioButton {
                font-size: 14px;
                color: #4a4e69;
                padding: 5px;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QRadioButton::indicator:unchecked {
                background-color: #ffffff;
                border: 2px solid #d1d1d1;
                border-radius: 9px;
            }
            QRadioButton::indicator:checked {
                background-color: #6c63ff;
                border: 2px solid #6c63ff;
                border-radius: 9px;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTAgM0w1LjUgOC41TDIuNSA2IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPjwvc3ZnPg==);
            }
            QRadioButton:hover {
                color: #6c63ff;
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

        # Format seçim kısmı güzelleştirme
        format_layout = QtWidgets.QHBoxLayout()
        format_group_box = QtWidgets.QGroupBox("İndirme Formatı")
        format_group_box.setStyleSheet('''
            QGroupBox {
                font-size: 14px;
                color: #22223b;
                font-weight: 500;
                border: 1px solid #d1d1d1;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 16px;
                background-color: rgba(255, 255, 255, 0.6);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
            }
        ''')
        
        format_box_layout = QtWidgets.QHBoxLayout()
        format_box_layout.setContentsMargins(15, 5, 15, 5)
        
        self.format_group = QtWidgets.QButtonGroup(self)
        self.mp4_radio = QtWidgets.QRadioButton('MP4 (Video)')
        self.mp3_radio = QtWidgets.QRadioButton('MP3 (Ses)')
        self.mp4_radio.setChecked(True)
        self.format_group.addButton(self.mp4_radio)
        self.format_group.addButton(self.mp3_radio)
        
        format_box_layout.addWidget(self.mp4_radio)
        format_box_layout.addWidget(self.mp3_radio)
        format_box_layout.addStretch()
        format_group_box.setLayout(format_box_layout)
        
        layout.addWidget(format_group_box)

        self.download_btn = AnimatedButton('İndir')
        self.download_btn.setStyleSheet('''
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4a4e69, stop:1 #9a8c98);
                color: #fff;
                border: none;
                border-radius: 12px;
                padding: 12px 0;
                font-size: 17px;
                font-weight: bold;
                margin-top: 10px;
                min-height: 38px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #22223b, stop:1 #4a4e69);
            }
        ''')
        self.download_btn.clicked.connect(self.download)
        layout.addWidget(self.download_btn)

        # Klasörü Aç butonu ekleniyor
        self.open_folder_btn = AnimatedButton('İndirme Klasörünü Aç')
        self.open_folder_btn.setStyleSheet('''
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #9a8c98, stop:1 #22223b);
                color: #fff;
                border: none;
                border-radius: 12px;
                padding: 10px 0;
                font-size: 16px;
                font-weight: bold;
                margin-top: 5px;
                min-height: 34px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4a4e69, stop:1 #22223b);
            }
        ''')
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

        if self.mp4_radio.isChecked():
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
