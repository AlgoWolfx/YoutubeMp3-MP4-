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
        self.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=12, xOffset=0, yOffset=2, color=QtGui.QColor(154, 140, 152, 80)))
        self.setStyleSheet('background: #fff; border: 2px solid #9a8c98; border-radius: 10px; padding: 8px; font-size: 15px;')
        self.setMinimumHeight(32)
        self.anim = QtCore.QPropertyAnimation(self, b"styleSheet")
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.FocusIn:
            self.setStyleSheet('background: #f8edeb; border: 2px solid #c9184a; border-radius: 10px; padding: 8px; font-size: 15px;')
        elif event.type() == QtCore.QEvent.FocusOut:
            self.setStyleSheet('background: #fff; border: 2px solid #9a8c98; border-radius: 10px; padding: 8px; font-size: 15px;')
        return super().eventFilter(obj, event)

class AnimatedStatusLabel(QtWidgets.QLabel):
    def __init__(self):
        super().__init__()
        self.setStyleSheet('color: #c9184a; font-size: 14px; margin-top: 10px;')
        self.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=8, xOffset=0, yOffset=1, color=QtGui.QColor(201, 24, 74, 80)))
        self.anim = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(300)
        self.setWindowOpacity(1.0)

    def setText(self, text):
        self.anim.stop()
        self.setWindowOpacity(0.0)
        super().setText(text)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.start()

class YouTubeDownloader(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        # İndirme klasörü için yol
        self.download_folder = os.path.join(os.path.expanduser('~'), 'Desktop', 'YouTubeIndirilenler')
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)

    def init_ui(self):
        self.setWindowTitle('YouTube Video/Ses İndirici')
        self.setFixedSize(460, 340)  # Yüksekliği artırdık
        self.setStyleSheet('''
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f4f6fb, stop:1 #e9ecef);
            }
            QLabel {
                color: #22223b;
                font-size: 15px;
                font-weight: 500;
            }
            QRadioButton {
                font-size: 14px;
                color: #4a4e69;
            }
        ''')

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(36, 28, 36, 28)

        self.url_label = QtWidgets.QLabel('YouTube URL:')
        layout.addWidget(self.url_label)

        self.url_input = AnimatedLineEdit()
        self.url_input.setPlaceholderText('https://www.youtube.com/watch?v=...')
        layout.addWidget(self.url_input)

        self.format_group = QtWidgets.QButtonGroup(self)
        self.mp4_radio = QtWidgets.QRadioButton('MP4 (Video)')
        self.mp3_radio = QtWidgets.QRadioButton('MP3 (Ses)')
        self.mp4_radio.setChecked(True)
        self.format_group.addButton(self.mp4_radio)
        self.format_group.addButton(self.mp3_radio)

        format_layout = QtWidgets.QHBoxLayout()
        format_layout.addWidget(self.mp4_radio)
        format_layout.addWidget(self.mp3_radio)
        format_layout.addStretch()
        layout.addLayout(format_layout)

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
