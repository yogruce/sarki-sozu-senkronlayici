# -*- coding: utf-8 -*-
"""
Lyrics Synchronizer / Şarkı Sözü Senkronlayıcı
--------------------------------------------------
DistroKid tarzı pratik şarkı sözü senkronizasyon ve dışa aktarma aracı.
Practical lyric timing and synchronization tool (LRC / SRT / TXT export).

Features / Özellikler:
• Modern & Sleek CustomTkinter UI (Dark / Light themes)
• English & Turkish Language Support (Instant on-the-fly switching)
• Precise Spacebar Timing (Hold to sync line, release to finish)
• Step back 1 line and rewind 2 seconds on Backspace
• Export to TXT, LRC (Standard synced lyrics), and SRT (Subtitles)
• Adjustable Reaction Latency Compensation (ms)
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
import pygame

# Set default appearance and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Time formatting helpers
def fmt_lrc(t):
    """Format seconds into standard [mm:ss.xx] timestamp."""
    t = max(0.0, float(t))
    m = int(t // 60)
    s = t - (m * 60)
    return f"[{m:02d}:{s:05.2f}]"


def fmt_clock(t):
    """Format seconds into mm:ss.xx clock display."""
    t = max(0.0, float(t))
    m = int(t // 60)
    s = t - (m * 60)
    return f"{m:02d}:{s:05.2f}"


def fmt_srt(t):
    """Format seconds into SubRip SRT hh:mm:ss,ms timestamp."""
    ms = int(round(max(0.0, float(t)) * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


# Translations dictionary
I18N = {
    "tr": {
        "title": "Şarkı Sözü Senkronlayıcı",
        "audio_btn": "🎵 Şarkı Seç...",
        "audio_none": "(Henüz şarkı seçilmedi)",
        "lyrics_btn": "📄 Söz Dosyası Yükle (.txt)",
        "latency_lbl": "Tepki Telafisi:",
        "latency_unit": "ms",
        "play_btn": "▶ Senkrona Başla",
        "pause_btn": "⏸ Duraklat",
        "resume_btn": "▶ Devam Et",
        "pause_esc": "⏯ Duraklat / Devam (Esc)",
        "back_btn": "⏪ 1 Satır Geri (Backspace)",
        "restart_btn": "🔄 Baştan Başla (F5)",
        "reset_btn": "✏ Sözleri Düzenle / Sıfırla",
        "export_btn": "💾 Dışa Aktar (TXT + SRT + LRC)",
        "status_ready": "Şarkıyı ve sözleri yükleyin, ardından ▶ Senkrona Başla butonuna basın.",
        "status_playing": "▶ Çalıyor: Söz girince SPACE'e basılı tutun, satır bitince bırakın.",
        "status_paused": "⏸ Duraklatıldı. Devam etmek için Esc tuşuna veya butona basın.",
        "status_resumed": "▶ Şarkı çalmaya devam ediyor.",
        "status_step_back": "⏪ Bir satır geri alındı, şarkı 2 saniye öncesinden devam ediyor.",
        "status_finished": "✓ Tüm satırlar zamanlandı! Şarkı durdu. Dosyalarınızı kaydedebilirsiniz.",
        "status_song_ended": "Şarkı bitti.",
        "status_reset": "Sözler düzenleme modunda. Dilediğinizce değiştirip tekrar başlatabilirsiniz.",
        "missing_audio_title": "Şarkı Seçilmedi",
        "missing_audio_msg": "Lütfen önce bir ses dosyası (MP3, WAV, FLAC, OGG) seçin.",
        "missing_lyrics_title": "Sözler Boş",
        "missing_lyrics_msg": "Şarkı sözü alanı boş! Lütfen sözleri yazın veya bir .txt dosyası yükleyin.",
        "no_sync_title": "Kayıt Yok",
        "no_sync_msg": "Henüz dışa aktarılacak zamanlanmış satır bulunmuyor.",
        "export_title": "Kayıt Adı ve Konumu Seçin",
        "export_success_title": "Başarıyla Kaydedildi",
        "export_success_msg": "Aşağıdaki dosyalar başarıyla oluşturuldu:\n\n",
        "placeholder": "Şarkı sözlerini buraya yazın veya yapıştırın...\n(Boş satırlar otomatik atlanır, her satır ayrı zamanlanır.)",
        "sc_title": "Kısayollar:",
        "sc_space": "[SPACE] Basılı Tut: Satırı Zamanla",
        "sc_back": "[BACKSPACE] 1 Satır Geri (-2sn)",
        "sc_esc": "[ESC] Duraklat / Devam",
        "sc_f5": "[F5] Baştan Başlat",
        "theme_dark": "Koyu",
        "theme_light": "Açık",
        "audio_filter": "Ses Dosyaları (*.mp3, *.wav, *.ogg, *.flac)",
        "all_filter": "Tüm Dosyalar (*.*)",
        "txt_filter": "Metin Dosyaları (*.txt)",
        "counter_format": "İlerleme: {done}/{total} satır",
    },
    "en": {
        "title": "Lyrics Synchronizer",
        "audio_btn": "🎵 Select Audio...",
        "audio_none": "(No audio selected yet)",
        "lyrics_btn": "📄 Load Lyrics (.txt)",
        "latency_lbl": "Reaction Offset:",
        "latency_unit": "ms",
        "play_btn": "▶ Start Sync",
        "pause_btn": "⏸ Pause",
        "resume_btn": "▶ Resume",
        "pause_esc": "⏯ Pause / Resume (Esc)",
        "back_btn": "⏪ Step Back 1 Line (Backspace)",
        "restart_btn": "🔄 Restart Track (F5)",
        "reset_btn": "✏ Edit / Reset Lyrics",
        "export_btn": "💾 Export (TXT + SRT + LRC)",
        "status_ready": "Load audio track and lyrics, then click ▶ Start Sync.",
        "status_playing": "▶ Playing: HOLD [SPACE] while singing line, RELEASE when line finishes.",
        "status_paused": "⏸ Paused. Press [Esc] or click button to resume playback.",
        "status_resumed": "▶ Playback resumed.",
        "status_step_back": "⏪ Rewound 1 line, audio resumed 2 seconds prior.",
        "status_finished": "✓ All lines synchronized! Playback stopped. You can now export.",
        "status_song_ended": "Song playback ended.",
        "status_reset": "Lyrics are back in editing mode. Make adjustments and start again.",
        "missing_audio_title": "Audio Missing",
        "missing_audio_msg": "Please select an audio file (MP3, WAV, FLAC, OGG) first.",
        "missing_lyrics_title": "Lyrics Empty",
        "missing_lyrics_msg": "Lyrics field is empty! Please paste lyrics or load a .txt file.",
        "no_sync_title": "No Sync Data",
        "no_sync_msg": "No synchronized lines available to export.",
        "export_title": "Choose Filename & Destination",
        "export_success_title": "Export Completed",
        "export_success_msg": "The following files were created successfully:\n\n",
        "placeholder": "Type or paste lyrics here...\n(Empty lines are automatically skipped; each line is timed individually.)",
        "sc_title": "Shortcuts:",
        "sc_space": "[SPACE] Hold: Sync Line",
        "sc_back": "[BACKSPACE] Step Back (-2s)",
        "sc_esc": "[ESC] Pause / Resume",
        "sc_f5": "[F5] Restart Track",
        "theme_dark": "Dark",
        "theme_light": "Light",
        "audio_filter": "Audio Files (*.mp3, *.wav, *.ogg, *.flac)",
        "all_filter": "All Files (*.*)",
        "txt_filter": "Text Files (*.txt)",
        "counter_format": "Progress: {done}/{total} lines",
    },
}


class LyricsSyncApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Current language: 'tr' by default
        self.lang = "tr"
        self.t = I18N[self.lang]

        # Window Setup
        self.title(self.t["title"])
        self.geometry("980x740")
        self.minsize(800, 560)

        # Center window on screen
        self.update_idletasks()
        w = 980
        h = 740
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = max(0, int((sw - w) / 2))
        y = max(0, int((sh - h) / 2))
        self.geometry(f"{w}x{h}+{x}+{y}")

        # Audio Mixer initialization
        try:
            pygame.mixer.init()
        except Exception as e:
            print(f"Pygame mixer init warning: {e}")

        # State Variables
        self.audio_path = None
        self.audio_filename = None
        self.length = 0.0
        self.lines = []
        self.starts = []
        self.ends = []
        self.idx = 0
        self.syncing = False
        self.paused = False
        self.held = False
        self.offset = 0.0

        # Latency compensation variable (ms)
        self.latency_var = tk.IntVar(value=120)

        # Build Modern UI
        self.build_ui()

        # Keyboard Bindings
        self.bind_all("<KeyPress-space>", self.on_press)
        self.bind_all("<KeyRelease-space>", self.on_release)
        self.bind_all("<BackSpace>", self.on_back)
        self.bind_all("<Escape>", lambda e: self.toggle_pause())
        self.bind_all("<F5>", lambda e: self.restart())

        # Periodic tick loop for timer and progress update (50ms interval)
        self.after(50, self.tick)

    # ------------------ UI CREATION ------------------
    def build_ui(self):
        # 1. Top Header Bar (Title, Language Switch, Theme Switch)
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=16, pady=(12, 6))

        title_sub_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_sub_frame.pack(side="left")

        self.app_title_lbl = ctk.CTkLabel(
            title_sub_frame,
            text=f"🎙 {self.t['title']}",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.app_title_lbl.pack(side="left")

        settings_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        settings_frame.pack(side="right")

        # Theme Selector Segmented Button
        self.theme_seg = ctk.CTkSegmentedButton(
            settings_frame,
            values=["🌙 Dark", "☀️ Light"],
            command=self.on_theme_change,
            width=140,
            height=28,
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.theme_seg.set("🌙 Dark")
        self.theme_seg.pack(side="right", padx=(8, 0))

        # Language Selector Segmented Button
        self.lang_seg = ctk.CTkSegmentedButton(
            settings_frame,
            values=["TR", "EN"],
            command=self.on_lang_change,
            width=100,
            height=28,
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.lang_seg.set(self.lang.upper())
        self.lang_seg.pack(side="right")

        # 2. Audio & Timing Toolbar Card
        audio_card = ctk.CTkFrame(self, corner_radius=10)
        audio_card.pack(fill="x", padx=16, pady=6)

        # Audio Card Row 1: File selectors and file info
        row1 = ctk.CTkFrame(audio_card, fg_color="transparent")
        row1.pack(fill="x", padx=12, pady=(10, 6))

        self.pick_audio_btn = ctk.CTkButton(
            row1,
            text=self.t["audio_btn"],
            command=self.pick_audio,
            width=140,
            height=32,
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.pick_audio_btn.pack(side="left")

        self.audio_lbl = ctk.CTkLabel(
            row1,
            text=self.t["audio_none"],
            font=ctk.CTkFont(size=13),
            text_color=("gray30", "gray70"),
            anchor="w",
        )
        self.audio_lbl.pack(side="left", padx=12, fill="x", expand=True)

        self.load_lyrics_btn = ctk.CTkButton(
            row1,
            text=self.t["lyrics_btn"],
            command=self.load_lyrics,
            width=170,
            height=32,
            fg_color=("gray75", "gray30"),
            hover_color=("gray65", "gray40"),
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.load_lyrics_btn.pack(side="right")

        # Audio Card Row 2: Latency slider, Progress Bar & Live Clock
        row2 = ctk.CTkFrame(audio_card, fg_color="transparent")
        row2.pack(fill="x", padx=12, pady=(4, 10))

        # Latency slider & spinbox
        latency_box = ctk.CTkFrame(row2, fg_color="transparent")
        latency_box.pack(side="left")

        self.latency_lbl = ctk.CTkLabel(
            latency_box,
            text=self.t["latency_lbl"],
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.latency_lbl.pack(side="left", padx=(0, 4))

        self.latency_slider = ctk.CTkSlider(
            latency_box,
            from_=0,
            to=400,
            number_of_steps=40,
            width=120,
            height=16,
            variable=self.latency_var,
            command=self.on_latency_slider,
        )
        self.latency_slider.pack(side="left", padx=4)

        self.latency_val_lbl = ctk.CTkLabel(
            latency_box,
            text=f"{self.latency_var.get()} {self.t['latency_unit']}",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=55,
        )
        self.latency_val_lbl.pack(side="left")

        # Center / Right: Progress Bar & Timer Badge
        timer_box = ctk.CTkFrame(row2, fg_color="transparent")
        timer_box.pack(side="right", fill="x", expand=True, padx=(20, 0))

        self.time_lbl = ctk.CTkLabel(
            timer_box,
            text="00:00.00 / 00:00.00",
            font=ctk.CTkFont(family="Consolas", size=15, weight="bold"),
        )
        self.time_lbl.pack(side="right")

        self.progress_bar = ctk.CTkProgressBar(timer_box, height=8, corner_radius=4)
        self.progress_bar.set(0.0)
        self.progress_bar.pack(side="right", fill="x", expand=True, padx=(0, 14))

        # 3. Main Editor & Lyrics Area
        editor_container = ctk.CTkFrame(self, corner_radius=10)
        editor_container.pack(fill="both", expand=True, padx=16, pady=6)

        # CustomTkinter CTkTextbox for modern scrollbars and sleek border
        self.text = ctk.CTkTextbox(
            editor_container,
            font=ctk.CTkFont(family="Segoe UI", size=15),
            wrap="word",
            undo=True,
            corner_radius=8,
            border_spacing=8,
        )
        self.text.pack(fill="both", expand=True, padx=8, pady=8)

        # Configure highlighting tags for states
        self.setup_tags()

        # Insert helpful initial placeholder
        self.text.insert("1.0", self.t["placeholder"])

        # 4. Playback and Control Action Bar
        control_card = ctk.CTkFrame(self, corner_radius=10)
        control_card.pack(fill="x", padx=16, pady=6)

        ctrl_inner = ctk.CTkFrame(control_card, fg_color="transparent")
        ctrl_inner.pack(fill="x", padx=12, pady=10)

        # Primary Start / Sync Button
        self.play_btn = ctk.CTkButton(
            ctrl_inner,
            text=self.t["play_btn"],
            command=self.play,
            height=36,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.play_btn.pack(side="left", padx=(0, 6))

        # Pause / Resume Button
        self.pause_btn = ctk.CTkButton(
            ctrl_inner,
            text=self.t["pause_esc"],
            command=self.toggle_pause,
            height=36,
            fg_color=("gray75", "gray28"),
            hover_color=("gray65", "gray38"),
            font=ctk.CTkFont(size=13),
        )
        self.pause_btn.pack(side="left", padx=4)

        # Step Back Button
        self.back_btn = ctk.CTkButton(
            ctrl_inner,
            text=self.t["back_btn"],
            command=self.on_back_click,
            height=36,
            fg_color=("gray75", "gray28"),
            hover_color=("gray65", "gray38"),
            font=ctk.CTkFont(size=13),
        )
        self.back_btn.pack(side="left", padx=4)

        # Restart Button
        self.restart_btn = ctk.CTkButton(
            ctrl_inner,
            text=self.t["restart_btn"],
            command=self.restart,
            height=36,
            fg_color=("gray75", "gray28"),
            hover_color=("gray65", "gray38"),
            font=ctk.CTkFont(size=13),
        )
        self.restart_btn.pack(side="left", padx=4)

        # Reset / Edit Button
        self.reset_btn = ctk.CTkButton(
            ctrl_inner,
            text=self.t["reset_btn"],
            command=self.reset,
            height=36,
            fg_color=("gray75", "gray28"),
            hover_color=("gray65", "gray38"),
            font=ctk.CTkFont(size=13),
        )
        self.reset_btn.pack(side="left", padx=4)

        # Export Button (Highlighted emerald green, enabled when lines are synced)
        self.export_btn = ctk.CTkButton(
            ctrl_inner,
            text=self.t["export_btn"],
            command=self.export,
            state="disabled",
            height=36,
            fg_color="#16a34a",
            hover_color="#15803d",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.export_btn.pack(side="right", padx=(6, 0))

        # 5. Bottom Status Bar & Shortcuts Quick Reference
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=16, pady=(2, 10))

        status_row = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        status_row.pack(fill="x")

        self.status_lbl = ctk.CTkLabel(
            status_row,
            text=self.t["status_ready"],
            font=ctk.CTkFont(size=13),
            anchor="w",
        )
        self.status_lbl.pack(side="left", fill="x", expand=True)

        self.counter_lbl = ctk.CTkLabel(
            status_row,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("gray40", "gray60"),
        )
        self.counter_lbl.pack(side="right")

        # Shortcuts Pills Row
        self.shortcuts_row = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        self.shortcuts_row.pack(fill="x", pady=(4, 0))

        self.sc_lbl = ctk.CTkLabel(
            self.shortcuts_row,
            text=self.t["sc_title"],
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("gray45", "gray55"),
        )
        self.sc_lbl.pack(side="left", padx=(0, 4))

        self.sc_pills = []
        for key in ["sc_space", "sc_back", "sc_esc", "sc_f5"]:
            pill = ctk.CTkLabel(
                self.shortcuts_row,
                text=self.t[key],
                font=ctk.CTkFont(size=11),
                fg_color=("gray85", "gray22"),
                corner_radius=4,
                padx=6,
                pady=1,
            )
            pill.pack(side="left", padx=3)
            self.sc_pills.append((key, pill))

    def setup_tags(self):
        """Set up typography and highlight colors for lyric lines."""
        is_dark = ctk.get_appearance_mode() == "Dark"
        if is_dark:
            # Done: soft glowing emerald green
            self.text.tag_config("done", foreground="#4ade80", background="#064e3b")
            # Ready/Current: vibrant golden-yellow with subtle dark gold background
            self.text.tag_config("cur", foreground="#ffffff", background="#854d0e")
            # Space Pressed / Actively timing: energetic blazing orange highlight
            self.text.tag_config("held", foreground="#ffffff", background="#c2410c")
        else:
            # Light Mode styling
            self.text.tag_config("done", foreground="#15803d", background="#dcfce7")
            self.text.tag_config("cur", foreground="#78350f", background="#fef08a")
            self.text.tag_config("held", foreground="#ffffff", background="#ea580c")

    # ------------------ LANGUAGE & THEME ------------------
    def on_theme_change(self, value):
        mode = "Dark" if "Dark" in value else "Light"
        ctk.set_appearance_mode(mode)
        self.setup_tags()
        self.refresh()

    def on_lang_change(self, value):
        self.lang = value.lower()
        self.t = I18N[self.lang]
        self.update_texts()

    def update_texts(self):
        """Update all UI text widgets to the currently selected language."""
        self.title(self.t["title"])
        self.app_title_lbl.configure(text=f"🎙 {self.t['title']}")
        self.pick_audio_btn.configure(text=self.t["audio_btn"])
        if not self.audio_path:
            self.audio_lbl.configure(text=self.t["audio_none"])
        else:
            self.audio_lbl.configure(
                text=f"🎵 {self.audio_filename} ({fmt_clock(self.length)})"
            )
        self.load_lyrics_btn.configure(text=self.t["lyrics_btn"])
        self.latency_lbl.configure(text=self.t["latency_lbl"])
        self.latency_val_lbl.configure(
            text=f"{self.latency_var.get()} {self.t['latency_unit']}"
        )
        self.play_btn.configure(text=self.t["play_btn"])
        self.pause_btn.configure(
            text=self.t["resume_btn"] if self.paused else self.t["pause_esc"]
        )
        self.back_btn.configure(text=self.t["back_btn"])
        self.restart_btn.configure(text=self.t["restart_btn"])
        self.reset_btn.configure(text=self.t["reset_btn"])
        self.export_btn.configure(text=self.t["export_btn"])
        self.sc_lbl.configure(text=self.t["sc_title"])
        for key, pill in self.sc_pills:
            pill.configure(text=self.t[key])

        # Status text update based on current state
        if not self.syncing and not self.lines:
            self.status_lbl.configure(text=self.t["status_ready"])
        elif self.syncing:
            if self.paused:
                self.status_lbl.configure(text=self.t["status_paused"])
            else:
                self.status_lbl.configure(text=self.t["status_playing"])

        self.update_counter()

    def update_counter(self):
        if self.lines:
            done = sum(1 for s in self.starts if s is not None)
            total = len(self.lines)
            self.counter_lbl.configure(
                text=self.t["counter_format"].format(done=done, total=total)
            )
        else:
            self.counter_lbl.configure(text="")

    def on_latency_slider(self, val):
        self.latency_val_lbl.configure(text=f"{int(val)} {self.t['latency_unit']}")

    # ------------------ FILE OPERATIONS ------------------
    def pick_audio(self):
        types = [
            (self.t["audio_filter"], "*.mp3 *.wav *.ogg *.flac"),
            (self.t["all_filter"], "*.*"),
        ]
        p = filedialog.askopenfilename(filetypes=types, title=self.t["audio_btn"])
        if not p:
            return

        pygame.mixer.music.stop()
        self.syncing = False
        self.paused = False
        self.offset = 0.0

        try:
            self.length = pygame.mixer.Sound(p).get_length()
        except Exception:
            self.length = 0.0

        self.audio_path = p
        self.audio_filename = os.path.basename(p)
        dur_str = fmt_clock(self.length)
        self.audio_lbl.configure(
            text=f"🎵 {self.audio_filename} ({dur_str})",
            text_color=("black", "white"),
        )
        self.time_lbl.configure(text=f"00:00.00 / {dur_str}")
        self.progress_bar.set(0.0)

    def load_lyrics(self):
        if self.syncing:
            return

        types = [
            (self.t["txt_filter"], "*.txt"),
            (self.t["all_filter"], "*.*"),
        ]
        p = filedialog.askopenfilename(filetypes=types, title=self.t["lyrics_btn"])
        if not p:
            return

        data = ""
        for enc in ("utf-8-sig", "utf-8", "cp1254", "latin-1"):
            try:
                with open(p, "r", encoding=enc) as f:
                    data = f.read()
                break
            except Exception:
                continue

        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", data)
        self.status_lbl.configure(text=self.t["status_ready"])

    # ------------------ TIME & LATENCY HELPERS ------------------
    def pos(self):
        """Current track position in seconds, taking seek offset into account."""
        return self.offset + max(0, pygame.mixer.music.get_pos()) / 1000.0

    def lat(self):
        """Human reaction latency compensation in seconds."""
        try:
            return float(self.latency_var.get()) / 1000.0
        except Exception:
            return 0.12

    # ------------------ SYNCHRONIZATION ENGINE ------------------
    def play(self):
        if not self.audio_path:
            messagebox.showwarning(
                self.t["missing_audio_title"], self.t["missing_audio_msg"]
            )
            return

        pygame.mixer.music.stop()
        self.text.configure(state="normal")
        raw = self.text.get("1.0", "end").splitlines()
        self.lines = [l.strip() for l in raw if l.strip()]

        if not self.lines:
            messagebox.showwarning(
                self.t["missing_lyrics_title"], self.t["missing_lyrics_msg"]
            )
            return

        n = len(self.lines)
        self.text.delete("1.0", "end")
        self.text.insert("1.0", "\n".join(self.lines))
        # Lock editor while syncing
        self.text.configure(state="disabled")

        self.starts = [None] * n
        self.ends = [None] * n
        self.idx = 0
        self.held = False
        self.paused = False
        self.offset = 0.0

        try:
            pygame.mixer.music.load(self.audio_path)
            pygame.mixer.music.play()
        except Exception as e:
            messagebox.showerror("Error", f"Could not play audio:\n{e}")
            return

        self.syncing = True
        self.play_btn.configure(state="disabled")
        self.export_btn.configure(state="disabled")
        self.pause_btn.configure(text=self.t["pause_esc"])

        self.refresh()
        self.status_lbl.configure(text=self.t["status_playing"])
        self.update_counter()
        self.focus_set()

    def restart(self):
        if self.audio_path and self.lines:
            self.play()

    def refresh(self):
        """Refresh tag highlights across all lines."""
        for tag in ("done", "cur", "held"):
            self.text.tag_remove(tag, "1.0", "end")

        # Mark finished lines as done
        for i in range(min(self.idx, len(self.lines))):
            self.text.tag_add("done", f"{i+1}.0", f"{i+1}.end")

        # Mark current active line
        if self.idx < len(self.lines):
            active_tag = "held" if self.held else "cur"
            self.text.tag_add(active_tag, f"{self.idx+1}.0", f"{self.idx+1}.end")
            self.text.see(f"{self.idx+1}.0")

    def on_press(self, e):
        """SPACE key down: record line start timestamp."""
        if not self.syncing:
            return None
        if self.paused or self.held or self.idx >= len(self.lines):
            return "break"

        self.held = True
        self.starts[self.idx] = max(0.0, self.pos() - self.lat())
        self.refresh()
        self.update_counter()
        return "break"

    def on_release(self, e):
        """SPACE key up: record line end timestamp and advance to next line."""
        if not self.syncing:
            return None
        if not self.held:
            return "break"

        self.held = False
        t = self.pos() - self.lat()
        start_t = self.starts[self.idx] or 0.0
        self.ends[self.idx] = max(t, start_t + 0.1)

        self.idx += 1
        self.refresh()
        self.update_counter()

        if self.idx >= len(self.lines):
            self.finish(self.t["status_finished"])
        return "break"

    def on_back(self, e=None):
        """BACKSPACE key: step back 1 line, delete its timing, rewind 2 seconds."""
        if not self.syncing or self.held or self.idx == 0:
            return "break" if self.syncing else None

        self.idx -= 1
        back_to = self.starts[self.idx] or 0.0
        self.starts[self.idx] = None
        self.ends[self.idx] = None

        new_pos = max(0.0, back_to - 2.0)
        self.seek(new_pos)
        self.refresh()
        self.update_counter()
        self.status_lbl.configure(text=self.t["status_step_back"])
        return "break"

    def on_back_click(self):
        self.on_back(None)

    def seek(self, t):
        """Seek audio playback to a specific timestamp in seconds."""
        try:
            pygame.mixer.music.play(start=t)
            self.offset = t
            if self.paused:
                pygame.mixer.music.pause()
        except Exception as e:
            print(f"Seek error: {e}")

    def toggle_pause(self):
        """Toggle pause / resume playback."""
        if not self.syncing:
            return

        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
            self.pause_btn.configure(text=self.t["pause_esc"])
            self.status_lbl.configure(text=self.t["status_resumed"])
        else:
            pygame.mixer.music.pause()
            self.paused = True
            self.pause_btn.configure(text=self.t["resume_btn"])
            self.status_lbl.configure(text=self.t["status_paused"])

    def finish(self, msg):
        """Handle song or lyric completion."""
        pygame.mixer.music.stop()
        self.syncing = False
        self.held = False
        self.paused = False
        self.play_btn.configure(state="normal")

        done = sum(1 for s in self.starts if s is not None)
        self.export_btn.configure(state="normal" if done > 0 else "disabled")
        self.status_lbl.configure(text=msg)
        self.update_counter()

    def reset(self):
        """Reset synchronization and return editor to normal typing mode."""
        pygame.mixer.music.stop()
        self.syncing = False
        self.held = False
        self.paused = False
        self.lines, self.starts, self.ends = [], [], []
        self.play_btn.configure(state="normal")
        self.export_btn.configure(state="disabled")
        self.pause_btn.configure(text=self.t["pause_esc"])

        self.text.configure(state="normal")
        for tag in ("done", "cur", "held"):
            self.text.tag_remove(tag, "1.0", "end")

        dur_str = fmt_clock(self.length)
        self.time_lbl.configure(text=f"00:00.00 / {dur_str}")
        self.progress_bar.set(0.0)
        self.status_lbl.configure(text=self.t["status_reset"])
        self.counter_lbl.configure(text="")

    def tick(self):
        """Periodic clock update, progress bar refresh, and end-of-track detection."""
        if self.syncing:
            current_pos = self.pos()
            dur_str = fmt_clock(self.length)
            self.time_lbl.configure(text=f"{fmt_clock(current_pos)} / {dur_str}")

            if self.length > 0:
                self.progress_bar.set(min(1.0, current_pos / self.length))

            # Detect song finishing before user finishes lines
            if not self.paused and not pygame.mixer.music.get_busy():
                if self.held and self.idx < len(self.lines):
                    self.ends[self.idx] = self.length or current_pos
                    self.idx += 1
                    self.refresh()
                self.finish(self.t["status_song_ended"])

        self.after(50, self.tick)

    # ------------------ EXPORT FUNCTIONALITY ------------------
    def export(self):
        """Export synchronized lyrics to TXT, LRC, and SRT formats."""
        items = []
        n = len(self.lines)

        for i in range(n):
            s = self.starts[i]
            if s is None:
                continue
            e = self.ends[i]
            if e is None:
                nxt = self.starts[i + 1] if i + 1 < n else None
                e = nxt if nxt is not None else s + 3.0
            if e <= s:
                e = s + 0.5
            items.append((s, e, self.lines[i]))

        if not items:
            messagebox.showwarning(self.t["no_sync_title"], self.t["no_sync_msg"])
            return

        initial_name = "lyrics"
        if self.audio_path:
            initial_name = os.path.splitext(os.path.basename(self.audio_path))[0]

        base = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=initial_name,
            filetypes=[
                (self.t["txt_filter"], "*.txt"),
                ("LRC Lyrics (*.lrc)", "*.lrc"),
                ("SubRip Subtitle (*.srt)", "*.srt"),
                (self.t["all_filter"], "*.*"),
            ],
            title=self.t["export_title"],
        )
        if not base:
            return

        base = os.path.splitext(base)[0]
        txt_path = base + ".txt"
        lrc_path = base + ".lrc"
        srt_path = base + ".srt"

        # 1. Write TXT ([mm:ss.xx] line format)
        with open(txt_path, "w", encoding="utf-8") as f:
            for s, e, l in items:
                f.write(f"{fmt_lrc(s)} {l}\n")

        # 2. Write Standard LRC format
        with open(lrc_path, "w", encoding="utf-8") as f:
            for s, e, l in items:
                f.write(f"{fmt_lrc(s)} {l}\n")

        # 3. Write SubRip SRT format
        with open(srt_path, "w", encoding="utf-8") as f:
            for i, (s, e, l) in enumerate(items, 1):
                f.write(f"{i}\n{fmt_srt(s)} --> {fmt_srt(e)}\n{l}\n\n")

        messagebox.showinfo(
            self.t["export_success_title"],
            f"{self.t['export_success_msg']}• {os.path.basename(txt_path)}\n• {os.path.basename(lrc_path)}\n• {os.path.basename(srt_path)}\n\n📁 {os.path.dirname(txt_path)}",
        )


if __name__ == "__main__":
    app = LyricsSyncApp()
    app.mainloop()
