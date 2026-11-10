# ⚡ NekoBreaker: Cyber Overdrive

Game arcade modern Brick Breaker bertema **Cyberpunk Neon & Holographic Void** yang dikembangkan dengan arsitektur **Object-Oriented Programming (OOP)** penuh dalam **1 file Python tunggal (`main.py`)**. 

Dibuat & Disesuaikan oleh: **Heyden Alyas**

---

## 📸 Tangkapan Layar (Screenshots)

| Menu Utama & Navigasi | Gameplay, Ion Laser & Overdrive | Menu Pause Interaktif |
| :---: | :---: | :---: |
| ![Menu](assets/menu.png) | ![Gameplay](assets/gameplay.png) | ![Pause](assets/pause.png) |

---

## 🌟 Fitur Unggulan

1. **Arsitektur Mandiri 1 File (`main.py`)**:
   - Seluruh logika, grafis, partikel, audio synthesizer, dan sistem status terintegrasi dalam satu file tanpa dependensi aset eksternal.
2. **Menu Utama & Panduan Kontrol Interaktif**:
   - Menu utama dinamis dengan efek animasi teks berdenyut (*pulse glow*).
   - Layar panduan kontrol & informasi fungsi power-up (`[H]`).
   - Sistem penyimpanan dan pelacakan rekor nilai (*High Score*).
3. **Menu Pause Interaktif**:
   - Tekan `[P]` atau `[ESC]` kapan saja untuk menghentikan permainan sementara.
   - Pilihan melanjutkan (*Resume*), restart wave saat ini, atau kembali ke menu utama.
4. **Sistem Prosedural Sound FX (8-Bit Retro Sci-Fi)**:
   - Efek suara sintetis langsung dihasilkan oleh modul Python `wave` dan `io` tanpa memerlukan file `.wav`/`.mp3` eksternal.
   - Suara pantulan paddle, benturan bata, tembakan laser, perolehan power-up, dan aktivasi Overdrive.
   - Dapat di-*mute* kapan saja dengan tombol `[M]`.
5. **Mode Cyber Burst / Overdrive (`LEFT SHIFT`)**:
   - Benturan bola mengisi indikator energi *Burst Gauge*. Saat mencapai 100%, pemain dapat mengaktifkan Overdrive selama 6 detik di mana bola berubah menjadi plasma penembus matrix tanpa memantul balik (*piercing damage*).
6. **Kapsul Power-Up Jatuh**:
   - `WIDE`: Memperlebar paddle sebesar 45%.
   - `GUN`: Memasang sepasang meriam laser pada paddle (tekan `SPASI` untuk menembak).
   - `x2`: Menggandakan bola di arena (*Multi-Ball*).
   - `+1`: Menambah 1 HP nyawa paddle.
7. **Sistem Wave Berkelanjutan**:
   - Membersihkan seluruh matrix bata akan membuka wave berikutnya dengan kecepatan bola yang semakin menantang.
8. **Efek Visual Spektakuler**:
   - *Screen Shake* halus saat benturan besar.
   - Cincin gelombang kejut (*Shockwave*) saat bata hancur.
   - Jejak ekor neon (*Light Trail*) pada pergerakan bola.

---

## 🎮 Kontrol Permainan

| Tombol | Fungsi |
| :--- | :--- |
| **`A` / `D`** atau **`Panah Kiri` / `Kanan`** | Menggerakkan Cyber Paddle |
| **`SPASI`** | Menembakkan Laser (jika power-up `GUN` aktif) / Melanjutkan Game |
| **`LEFT SHIFT`** | Mengaktifkan **Cyber Overdrive** (saat Gauge 100%) |
| **`P` / `ESC`** | Membuka Menu Pause |
| **`M`** | Mengaktifkan / Menonaktifkan Audio SFX |
| **`H`** | Melihat Panduan & Kontrol di Menu Utama |

---

## 🚀 Cara Menjalankan

Cukup jalankan satu file ini menggunakan Python:

```powershell
python main.py
```
atau jika menggunakan virtual environment:
```powershell
.\.venv\Scripts\python.exe main.py
```
