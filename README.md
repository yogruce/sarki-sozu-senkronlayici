# 🎙️ Şarkı Sözü Senkronlayıcı / Lyrics Synchronizer

<p align="center">
  <b>Modern, DistroKid tarzı pratik şarkı sözü senkronizasyonu ve LRC / SRT / TXT dışa aktarma aracı.</b><br>
  <i>Practical, DistroKid-style interactive lyrics synchronizer with LRC, SRT, and TXT multi-format export.</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/GUI-CustomTkinter-blueviolet" alt="CustomTkinter">
  <img src="https://img.shields.io/badge/Audio-Pygame--ce-success?logo=pygame" alt="Pygame">
  <img src="https://img.shields.io/badge/Language-TR%20%7C%20EN-orange" alt="Bilingual">
  <img src="https://img.shields.io/badge/License-MIT-lightgrey" alt="License">
</p>

---

## 🇹🇷 Türkçe Dokümantasyon

### ✨ Özellikler
- **Modern ve Şık Arayüz:** CustomTkinter ile tasarlanmış modern arayüz, göz yormayan **Koyu Tema (Dark)** ve ferah **Açık Tema (Light)** seçenekleri.
- **İki Dilli (TR / EN):** Arayüzün sağ üst köşesindeki butonla Türkçe ve İngilizce dilleri arasında tek tıkla anında geçiş yapabilme.
- **DistroKid Tarzı Spacebar Kontrolü:** 
  - Söz başladığında **SPACE** tuşuna basılı tutun (satır aktif vurgulanır).
  - Satır bittiğinde **SPACE** tuşunu bırakın (zaman damgası kaydedilir ve otomatik alt satıra geçer).
- **Geri Alma (Undo) Desteği:** Şarkı söylenirken hata yaparsanız **BACKSPACE** tuşuna basarak 1 satır geri dönebilirsiniz; program şarkıyı otomatik olarak 2 saniye öncesine sarar.
- **Tepki Telafisi (Latency Offset):** İnsan refleks gecikmesini telafi etmek için 0–400 ms arası ayarlanabilir hassas tepki gecikme kaydırıcısı (varsayılan: 120 ms).
- **Çoklu Dışa Aktarma Formatları:**
  - **`.lrc`** (Standart müzik çalar şarkı sözü formatı: `[01:23.45] Sözler`)
  - **`.srt`** (Video kurgu programları ve video oynatıcılar için SubRip altyazı formatı: `00:01:23,450 --> 00:01:27,100`)
  - **`.txt`** (Zaman damgalı metin dosyası)
- **Geniş Ses Formatı Desteği:** MP3, WAV, OGG, FLAC formatları ile sorunsuz çalışma.

---

### ⌨️ Kısayol Tuşları

| Kısayol | İşlev |
|---|---|
| **SPACE (Basılı Tut)** | Aktif satırın zamanlamasını başlatır (turuncu vurgu). |
| **SPACE (Bırak)** | Satırın bitiş zamanını kaydeder, tamamlandı olarak işaretler ve bir alt satıra geçer. |
| **BACKSPACE** | 1 satır geri alır, o satırın zamanlamasını siler ve şarkıyı 2 saniye geriye sarar. |
| **ESC** | Şarkıyı duraklatır / kaldığı yerden devam ettirir. |
| **F5** | Şarkıyı ve zamanlamayı en baştan başlatır. |

---

### 🚀 Kurulum ve Çalıştırma

1. **Depoyu klonlayın:**
   ```bash
   git clone https://github.com/yogruce/sarki-sozu-senkronlayici.git
   cd sarki-sozu-senkronlayici
   ```

2. **Gereksinimleri yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Uygulamayı başlatın:**
   ```bash
   python sarki_sozu_senkron.py
   ```

---

### 📦 EXE Olarak Derleme (Windows)

Uygulamayı Python yüklü olmayan bilgisayarlarda da çalıştırmak için tek tıkla çalıştırılabilir `.exe` oluşturabilirsiniz:
- Klasör içindeki **`build_exe.bat`** dosyasını çift tıklatarak çalıştırın.
- Derleme bittiğinde dosyanız **`dist\SarkiSozuSenkron\`** klasöründe hazır olacaktır.

---

<br>

---

## 🇬🇧 English Documentation

### ✨ Features
- **Modern & Sleek UI:** Built with CustomTkinter featuring clean cards, glowing highlights, and instant **Dark / Light mode** toggling.
- **Bilingual Support (TR / EN):** One-click dynamic switching between English and Turkish with real-time UI text refresh.
- **DistroKid-style Spacebar Workflow:**
  - **HOLD [SPACE]** when the lyric line starts being sung (vibrant orange highlight).
  - **RELEASE [SPACE]** when the line ends (line is timestamped, marked green, and cursor advances).
- **Quick Undo / Rewind:** Made a timing mistake? Simply press **BACKSPACE** to step back one line; the track automatically rewinds 2 seconds prior.
- **Latency Compensation (ms):** Fine-tune human reaction delay slider (0–400 ms, default: 120 ms) to keep synchronization razor-sharp.
- **Multi-Format Export:**
  - **`.lrc`** (Standard synchronized lyric format: `[01:23.45] Lyric text`)
  - **`.srt`** (SubRip subtitle format for video editors and media players: `00:01:23,450 --> 00:01:27,100`)
  - **`.txt`** (Timestamped text output)
- **Universal Audio Support:** Full compatibility with MP3, WAV, OGG, and FLAC audio files.

---

### ⌨️ Keyboard Shortcuts

| Shortcut | Description |
|---|---|
| **SPACE (Hold)** | Starts timing the current line (blazing orange highlight). |
| **SPACE (Release)** | Records end timestamp, marks line complete (green), and advances to the next line. |
| **BACKSPACE** | Steps back 1 line, clears that line's timing, and rewinds audio by 2 seconds. |
| **ESC** | Pauses or resumes playback. |
| **F5** | Restarts playback and synchronization from the very beginning. |

---

### 🚀 Installation & Quickstart

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yogruce/sarki-sozu-senkronlayici.git
   cd sarki-sozu-senkronlayici
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the application:**
   ```bash
   python sarki_sozu_senkron.py
   ```

---

### 📦 Building a Standalone EXE (Windows)

To distribute as a standalone Windows executable:
- Run the included **`build_exe.bat`** script.
- The compiled application will be generated in **`dist\SarkiSozuSenkron\`**.

---

### 📄 Output Sample / Örnek Çıktı

**LRC Format (`.lrc`):**
```text
[00:14.20] Is this the real life?
[00:17.50] Is this just fantasy?
[00:21.10] Caught in a landslide
[00:24.40] No escape from reality
```

**SRT Format (`.srt`):**
```text
1
00:00:14,200 --> 00:00:17,400
Is this the real life?

2
00:00:17,500 --> 00:00:21,000
Is this just fantasy?
```

---

### 📜 License
This project is licensed under the MIT License.
