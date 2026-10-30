# -*- coding: utf-8 -*-
"""
Şarkı Sözü Senkron Aracı (DistroKid tarzı)
1) Şarkıyı yükle, sözleri yaz/yapıştır/yükle
2) ▶ Play'e bas: şarkı çalar, sözler kilitlenir, SPACE modu aktif olur
3) Söz girince SPACE'i basılı tut (satır renklenir), satır bitince bırak (imleç alt satıra iner)
4) Son satır bitince şarkı otomatik durur
5) Kaydet: .txt ([dd:ss.ss] satır) ve .srt
Kısayollar: SPACE = zamanla | BACKSPACE = bir satır geri | ESC = duraklat/devam | F5 = baştan başla
"""
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import pygame

AUDIO_TYPES = [("Ses dosyaları", "*.mp3 *.wav *.ogg *.flac"), ("Tümü", "*.*")]


def fmt_lrc(t):
    t = max(0.0, t)
    m = int(t // 60)
    return f"[{m:02d}:{t - m * 60:05.2f}]"


def fmt_clock(t):
    t = max(0.0, t)
    m = int(t // 60)
    return f"{m:02d}:{t - m * 60:05.2f}"


def fmt_srt(t):
    ms = int(round(max(0.0, t) * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


class App:
    def __init__(self, root):
        self.root = root
        root.title("Şarkı Sözü Senkron Aracı")
        root.geometry("820x600")
        root.minsize(640, 420)
        pygame.mixer.init()

        self.audio_path = None
        self.length = 0.0
        self.lines = []
        self.starts = []
        self.ends = []
        self.idx = 0
        self.syncing = False
        self.paused = False
        self.held = False
        self.offset = 0.0

        self.build_ui()
        root.bind_all("<KeyPress-space>", self.on_press)
        root.bind_all("<KeyRelease-space>", self.on_release)
        root.bind_all("<BackSpace>", self.on_back)
        root.bind_all("<Escape>", lambda e: self.toggle_pause())
        root.bind_all("<F5>", lambda e: self.restart())
        root.after(50, self.tick)

    # ---------- arayüz ----------
    def build_ui(self):
        top = ttk.Frame(self.root, padding=8)
        top.pack(fill="x")
        ttk.Button(top, text="Şarkı Seç...", command=self.pick_audio, takefocus=False).pack(side="left")
        self.audio_lbl = ttk.Label(top, text="  (şarkı seçilmedi)")
        self.audio_lbl.pack(side="left")
        ttk.Button(top, text="Söz Dosyası Yükle (.txt)", command=self.load_lyrics, takefocus=False).pack(side="right")

        opt = ttk.Frame(self.root, padding=(8, 0))
        opt.pack(fill="x")
        ttk.Label(opt, text="Tepki telafisi (ms):").pack(side="left")
        self.latency = tk.IntVar(value=120)
        ttk.Spinbox(opt, from_=0, to=500, increment=10, width=5, textvariable=self.latency).pack(side="left", padx=4)
        self.time_lbl = ttk.Label(opt, text="00:00.00", font=("Consolas", 14))
        self.time_lbl.pack(side="right")

        self.text = tk.Text(self.root, font=("Segoe UI", 15), wrap="word", undo=True, spacing1=5, spacing3=5)
        self.text.tag_configure("done", foreground="#2e7d32")
        self.text.tag_configure("cur", background="#fff176", foreground="black")
        self.text.tag_configure("held", background="#ff8a65", foreground="black")
        self.text.insert("1.0", "Şarkı sözlerini buraya yapıştır veya yaz...\n(Boş satırlar atlanır, her satır ayrı zamanlanır.)")

        bot = ttk.Frame(self.root, padding=8)
        self.play_btn = ttk.Button(bot, text="▶ Play", command=self.play, takefocus=False)
        self.play_btn.pack(side="left")
        ttk.Button(bot, text="⏯ Duraklat/Devam (Esc)", command=self.toggle_pause, takefocus=False).pack(side="left", padx=6)
        ttk.Button(bot, text="🔄 Baştan Başla (F5)", command=self.restart, takefocus=False).pack(side="left")
        ttk.Button(bot, text="✏ Sıfırla / Sözleri Düzenle", command=self.reset, takefocus=False).pack(side="left", padx=6)
        self.export_btn = ttk.Button(bot, text="💾 Kaydet (TXT + SRT)", command=self.export, state="disabled", takefocus=False)
        self.export_btn.pack(side="right")
        self.status = ttk.Label(self.root, text="Şarkıyı ve sözleri yükle, sonra Play'e bas.", padding=(8, 0, 8, 8))
        # alt çubuklar önce paketlenir: pencere küçülse bile hep görünür
        self.status.pack(side="bottom", fill="x")
        bot.pack(side="bottom", fill="x")
        self.text.pack(fill="both", expand=True, padx=8, pady=8)

    # ---------- dosyalar ----------
    def pick_audio(self):
        p = filedialog.askopenfilename(filetypes=AUDIO_TYPES)
        if not p:
            return
        pygame.mixer.music.stop()
        self.syncing = False
        try:
            self.length = pygame.mixer.Sound(p).get_length()
        except Exception:
            self.length = 0.0
        self.audio_path = p
        self.audio_lbl.config(text="  " + os.path.basename(p))

    def load_lyrics(self):
        if self.syncing:
            return
        p = filedialog.askopenfilename(filetypes=[("Metin", "*.txt"), ("Tümü", "*.*")])
        if not p:
            return
        data = ""
        for enc in ("utf-8-sig", "cp1254", "latin-1"):
            try:
                with open(p, "r", encoding=enc) as f:
                    data = f.read()
                break
            except Exception:
                continue
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", data)

    # ---------- zaman ----------
    def pos(self):
        return self.offset + max(0, pygame.mixer.music.get_pos()) / 1000.0

    def lat(self):
        try:
            return int(self.latency.get()) / 1000.0
        except Exception:
            return 0.0

    # ---------- senkron ----------
    def play(self):
        if not self.audio_path:
            messagebox.showwarning("Eksik", "Önce bir şarkı seç.")
            return
        pygame.mixer.music.stop()
        self.text.config(state="normal")
        raw = self.text.get("1.0", "end").splitlines()
        self.lines = [l.strip() for l in raw if l.strip()]
        if not self.lines:
            messagebox.showwarning("Eksik", "Şarkı sözü boş.")
            return
        n = len(self.lines)
        self.text.delete("1.0", "end")
        self.text.insert("1.0", "\n".join(self.lines))
        self.text.config(state="disabled")  # şarkı çalarken sözler değiştirilemez
        self.starts = [None] * n
        self.ends = [None] * n
        self.idx = 0
        self.held = False
        self.paused = False
        self.offset = 0.0
        pygame.mixer.music.load(self.audio_path)
        pygame.mixer.music.play()
        self.syncing = True
        self.play_btn.config(state="disabled")
        self.export_btn.config(state="disabled")
        self.refresh()
        self.status.config(text="Çalıyor. Söz girince SPACE'i basılı tut, satır bitince bırak.")
        self.root.focus_set()

    def restart(self):
        if self.audio_path and self.lines:
            self.play()

    def refresh(self):
        for t in ("done", "cur", "held"):
            self.text.tag_remove(t, "1.0", "end")
        for i in range(min(self.idx, len(self.lines))):
            self.text.tag_add("done", f"{i+1}.0", f"{i+1}.end")
        if self.idx < len(self.lines):
            self.text.tag_add("held" if self.held else "cur", f"{self.idx+1}.0", f"{self.idx+1}.end")
            self.text.see(f"{self.idx+1}.0")

    def on_press(self, e):
        if not self.syncing:
            return None
        if self.paused or self.held or self.idx >= len(self.lines):
            return "break"
        self.held = True
        self.starts[self.idx] = max(0.0, self.pos() - self.lat())
        self.refresh()
        return "break"

    def on_release(self, e):
        if not self.syncing:
            return None
        if not self.held:
            return "break"
        self.held = False
        t = self.pos() - self.lat()
        self.ends[self.idx] = max(t, (self.starts[self.idx] or 0.0) + 0.1)
        self.idx += 1
        self.refresh()
        if self.idx >= len(self.lines):
            self.finish("Son satır bitti, şarkı durdu.")
        return "break"

    def finish(self, msg):
        pygame.mixer.music.stop()
        self.syncing = False
        self.held = False
        self.play_btn.config(state="normal")
        done = sum(1 for s in self.starts if s is not None)
        self.export_btn.config(state="normal" if done else "disabled")
        self.status.config(text=f"{msg} {done}/{len(self.lines)} satır zamanlandı. Kaydedebilirsin.")

    def on_back(self, e):
        if not self.syncing or self.held or self.idx == 0:
            return
        self.idx -= 1
        back_to = self.starts[self.idx] or 0.0
        self.starts[self.idx] = None
        self.ends[self.idx] = None
        self.seek(max(0.0, back_to - 2.0))
        self.refresh()
        self.status.config(text="Bir satır geri alındı, şarkı 2 sn öncesinden devam ediyor.")

    def seek(self, t):
        pygame.mixer.music.play(start=t)
        self.offset = t
        if self.paused:
            pygame.mixer.music.pause()

    def toggle_pause(self):
        if not self.syncing:
            return
        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
            self.status.config(text="Devam ediyor.")
        else:
            pygame.mixer.music.pause()
            self.paused = True
            self.status.config(text="Duraklatıldı (Esc ile devam).")

    def tick(self):
        if self.syncing:
            self.time_lbl.config(text=fmt_clock(self.pos()))
            if not self.paused and not pygame.mixer.music.get_busy():
                # şarkı sözler bitmeden bitti
                if self.held and self.idx < len(self.lines):
                    self.ends[self.idx] = self.length or self.pos()
                    self.idx += 1
                    self.refresh()
                self.finish("Şarkı bitti.")
        self.root.after(50, self.tick)

    def reset(self):
        pygame.mixer.music.stop()
        self.syncing = False
        self.held = False
        self.lines, self.starts, self.ends = [], [], []
        self.play_btn.config(state="normal")
        self.export_btn.config(state="disabled")
        self.text.config(state="normal")
        for t in ("done", "cur", "held"):
            self.text.tag_remove(t, "1.0", "end")
        self.time_lbl.config(text="00:00.00")
        self.status.config(text="Sıfırlandı. Sözleri düzenleyebilirsin.")

    # ---------- çıktı ----------
    def export(self):
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
            messagebox.showwarning("Boş", "Kaydedilecek zamanlanmış satır yok.")
            return
        base = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=os.path.splitext(os.path.basename(self.audio_path or "sarki"))[0],
            filetypes=[("Metin", "*.txt")],
            title="Dosya adını seç (TXT ve SRT birlikte kaydedilir)",
        )
        if not base:
            return
        base = os.path.splitext(base)[0]
        with open(base + ".txt", "w", encoding="utf-8") as f:
            for s, e, l in items:
                f.write(f"{fmt_lrc(s)} {l}\n")
        with open(base + ".srt", "w", encoding="utf-8") as f:
            for i, (s, e, l) in enumerate(items, 1):
                f.write(f"{i}\n{fmt_srt(s)} --> {fmt_srt(e)}\n{l}\n\n")
        messagebox.showinfo("Kaydedildi", f"{base}.txt\n{base}.srt")


if __name__ == "__main__":
    r = tk.Tk()
    App(r)
    r.mainloop()
