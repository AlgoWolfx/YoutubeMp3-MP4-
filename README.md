# YouTube MP3/MP4 İndirici

Modern ve kullanıcı dostu bir YouTube video ve ses indirme uygulaması.

![YouTube İndirici Ekran Görüntüsü](screenshot.png)

## Özellikler

- YouTube videolarını MP4 formatında indirme
- YouTube videolarını MP3 (ses) formatında indirme
- Animasyonlu ve modern kullanıcı arayüzü
- İndirilen dosyalar için kolay erişim butonu
- Hata bildirimleri ve durum güncellemeleri

## Gereksinimler

- Python 3.6+
- PyQt5
- yt-dlp
- FFmpeg (MP3 dönüşümü için)

## Kurulum

1. Depoyu klonlayın:
   ```
   git clone https://github.com/KULLANICIADINIZ/youtube-mp3-mp4-indir.git
   cd youtube-mp3-mp4-indir
   ```

2. Gerekli kütüphaneleri yükleyin:
   ```
   pip install PyQt5 yt-dlp
   ```

3. FFmpeg'i yükleyin:
   - Windows: [FFmpeg İndirme Sayfası](https://ffmpeg.org/download.html)
   - Mac: `brew install ffmpeg`
   - Linux: `sudo apt-get install ffmpeg`

## Kullanım

1. Uygulamayı başlatın:
   ```
   python "youtube mp3.py"
   ```

2. YouTube video URL'sini girin
3. MP4 (video) veya MP3 (ses) formatını seçin
4. "İndir" butonuna tıklayın
5. İndirme tamamlandığında "İndirme Klasörünü Aç" butonuna tıklayarak dosyalara erişebilirsiniz

## İndirme Klasörü

İndirilen dosyalar masaüstündeki "YouTubeIndirilenler" klasörüne kaydedilir.

## Lisans

Bu proje açık kaynak olarak MIT lisansı altında yayınlanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakınız.

## Katkıda Bulunma

1. Bu depoyu fork edin
2. Kendi branch'inizi oluşturun (`git checkout -b yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik: açıklama'`)
4. Branch'inizi push edin (`git push origin yeni-ozellik`)
5. Bir Pull Request oluşturun 