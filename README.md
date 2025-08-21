# Flappy Bird AI - Sebuah Eksperimen Kecerdasan Buatan

Selamat datang di proyek Flappy Bird AI! Ini bukan sekadar game Flappy Bird biasa. Di sini, Anda tidak akan bermain sebagai burungnya. Sebaliknya, Anda akan menyaksikan sekelompok burung yang dikendalikan oleh Kecerdasan Buatan (AI) belajar dari nol untuk menguasai permainan ini melalui proses evolusi digital.

## 🚀 Teknologi yang Digunakan

Proyek ini dibangun dengan dua komponen utama dari ekosistem Python:

- **Pygame**: Sebuah library fundamental untuk pengembangan game 2D, digunakan untuk membangun seluruh logika dan visualisasi dari game Flappy Bird.
- **NEAT (NeuroEvolution of Augmenting Topologies)**: Sebuah algoritma genetika canggih yang diimplementasikan melalui library `neat-python`. Algoritma ini bertanggung jawab untuk "melatih" otak para burung dari generasi ke generasi.

## 🧠 Cara Kerjanya

Program ini menggunakan algoritma NEAT untuk melatih jaringan saraf agar bisa bermain Flappy Bird. Prosesnya dapat diringkas sebagai berikut:

1.  **Inisialisasi**: Program memulai dengan populasi 50 burung. Setiap burung memiliki "otak" (jaringan saraf) yang acak dan tidak tahu cara bermain.
2.  **Simulasi**: Semua burung mencoba bermain secara bersamaan. Mereka menerima input dari lingkungan (posisi vertikal mereka dan jarak ke pipa berikutnya). Berdasarkan input ini, otak mereka memutuskan apakah akan melompat atau tidak.
3.  **Evaluasi (Fitness)**: Sebagian besar burung akan gagal dengan cepat. Burung yang berhasil terbang lebih jauh (bertahan hidup lebih lama) akan mendapatkan "skor kebugaran" (fitness) yang lebih tinggi.
4.  **Evolusi**: Setelah semua burung mati, algoritma NEAT akan memilih burung-burung dengan skor tertinggi. "Otak" mereka akan direproduksi (dikombinasikan dan sedikit dimutasi) untuk menciptakan generasi baru yang mewarisi sifat-sifat unggul dari orang tuanya.
5.  **Pengulangan**: Proses ini diulang untuk banyak generasi. Seiring waktu, Anda akan melihat populasi burung secara kolektif menjadi semakin pintar dan mahir dalam menghindari pipa.

## 🖼️ Aset yang Dibutuhkan

Versi baru ini menggunakan file gambar untuk tampilan visual. Kode ini dirancang untuk memuat aset dari folder `assets/`.

**PENTING:** Anda harus membuat folder `assets` di direktori utama proyek dan mengisinya dengan file-file gambar berikut:
- `bg.png` (Gambar latar belakang)
- `base.png` (Gambar lantai yang bergerak)
- `pipe.png` (Gambar pipa)
- `bird1.png` (Gambar burung dengan sayap di atas)
- `bird2.png` (Gambar burung dengan sayap di tengah)
- `bird3.png` (Gambar burung dengan sayap di bawah)

Program akan menampilkan pesan error jika file-file ini tidak dapat ditemukan. Anda bisa menggunakan aset dari repositori referensi yang Anda berikan atau menggunakan aset lain dengan nama file yang sama.

## 🛠️ Cara Menjalankan Program

Untuk menjalankan proyek ini di komputer Anda, ikuti langkah-langkah berikut:

1.  **Pastikan Anda memiliki Python 3 terinstal.**

2.  **Clone repositori ini (jika belum):**
    ```bash
    git clone <URL_REPOSITORI_INI>
    cd <NAMA_FOLDER_REPOSITORI>
    ```

3.  **Siapkan Aset:**
    Buat folder `assets` dan isi dengan file-file gambar yang disebutkan di atas.

4.  **Instal dependensi yang diperlukan:**
    Program ini membutuhkan `pygame` dan `neat-python`. Anda bisa menginstalnya menggunakan pip.
    ```bash
    pip install pygame neat-python
    ```

5.  **Jalankan program:**
    Setelah instalasi selesai, cukup jalankan file `flappy_ai.py`.
    ```bash
    python3 flappy_ai.py
    ```

Sebuah jendela Pygame akan muncul, dan Anda akan melihat proses pelatihan AI dimulai. Selamat menyaksikan evolusi!
