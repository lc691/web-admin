# SONG Admin Coding Convention v1.0

> Dokumen ini adalah standar pengembangan SONG Admin.
>
> Seluruh source code HARUS mengikuti aturan di bawah ini.
> Setelah disepakati, aturan ini tidak boleh diubah selama proyek berlangsung.

---

# 1. Tujuan

Project harus memiliki karakter berikut.

- Enterprise
- Modular
- Konsisten
- Mudah dicari
- Mudah di-debug
- Mudah dikembangkan
- Mudah dipahami meskipun dibuka kembali beberapa bulan kemudian

Bukan membuat kode sesingkat mungkin.

Bukan membuat file sebanyak mungkin.

Tetapi membuat alur aplikasi jelas.

---

# 2. Architecture

Browser
    │
    ▼
Routes
    │
    ▼
Service
    │
    ▼
Repository
    │
    ▼
PostgreSQL

Seluruh request HARUS mengikuti alur tersebut.

Tidak boleh melompati layer.

---

# 3. Layer Responsibility

## Route

Tugas

- Endpoint
- HTTP Method
- Query Parameter
- Path Parameter
- Form
- Upload File
- TemplateResponse
- RedirectResponse
- JSONResponse

Tidak boleh

- SQL
- Business Logic

---

## Service

Tugas

- Business Logic
- Validasi
- Flow Aplikasi
- Memanggil Repository
- Menggabungkan Data
- Menentukan Response Data

Tidak boleh

- SQL

---

## Repository

Tugas

- SELECT
- INSERT
- UPDATE
- DELETE

Tidak boleh

- FastAPI
- HTML
- JSONResponse
- RedirectResponse
- TemplateResponse
- Business Logic

Repository hanya berisi PostgreSQL Query.

---

# 4. Dependency Rule

Diizinkan

Route
↓

Service

Service
↓

Repository

Service
↓

Shared

Repository
↓

Shared

Tidak Diizinkan

Repository
↓

Service

Repository
↓

Route

Route
↓

Repository

---

# 5. Folder Rule

Setiap Domain memiliki folder sendiri.

Contoh

services/

songs/

artists/

channels/

export/

usage/

shared/

Jangan mencampur domain.

---

# 6. File Rule

Setiap domain minimal memiliki

service.py

repository.py

types.py

Tambahan hanya jika memang diperlukan.

Contoh

export/

selector.py

formatter.py

blacklist.py

Karena memang algoritmanya besar.

Songs tidak perlu dibuat banyak file.

---

# 7. Function Naming

Mengambil Data

get_*

Contoh

get_song()

get_artist()

get_channel()

---

Membuat Data

create_*

---

Mengubah Data

update_*

---

Menghapus Data

delete_*

---

Menghitung

count_*

---

Mengecek

exists_*

has_*

---

Membangun Context

build_*

---

Export

export_*

---

Import

import_*

---

# 8. Variable Naming

Gunakan nama jelas.

Benar

song

songs

artist

artists

channel

channels

remaining

selected

total

Tidak menggunakan

x

tmp

obj

a

b

c

data1

data2

---

# 9. SQL Rule

Semua SQL berada di Repository.

Tidak boleh SQL berada di

Route

Service

HTML

JavaScript

---

# 10. Comment Rule

Gunakan separator.

==========================================================

LIST

==========================================================

DATATABLE

==========================================================

CRUD

==========================================================

BATCH

==========================================================

EXPORT

==========================================================

IMPORT

---

# 11. Docstring Rule

Gunakan format sederhana.

"""
Mengambil daftar lagu.
"""

Tidak perlu docstring panjang.

---

# 12. Import Rule

Standard Library

↓

Third Party

↓

Local Module

Contoh

from pathlib import Path

from fastapi import APIRouter

from app.services.songs.service import get_song_page

---

# 13. Function Order

Urutan fungsi dalam file HARUS konsisten.

LIST

↓

DETAIL

↓

CREATE

↓

UPDATE

↓

DELETE

↓

BATCH

↓

IMPORT

↓

EXPORT

↓

STATISTICS

Jangan berubah-ubah.

---

# 14. Error Handling

Gunakan Exception.

Tidak mengembalikan string error.

Tidak menggunakan print().

---

# 15. Constants

Konstanta menggunakan UPPER_CASE.

Contoh

MAX_TARGET

VALID_STATUS

DEFAULT_DUPLICATE

---

# 16. Types

Semua TypedDict

Literal

Enum

berada di

types.py

---

# 17. HTML

Tidak ada Business Logic.

HTML hanya View.

---

# 18. JavaScript

Tidak ada SQL.

Tidak ada Business Logic.

JavaScript hanya

- UI
- Ajax
- Event
- Validation Ringan

---

# 19. CSS

Satu file per halaman.

Gunakan class yang jelas.

---

# 20. Commit Rule

Satu commit

=

Satu tujuan.

Contoh

feat(export): add blacklist export

fix(usage): filter by mode

refactor(song): move sql to repository

---

# 21. Patch Rule

Seluruh pengembangan menggunakan Patch.

Contoh

PATCH 01

Folder

PATCH 02

Repository

PATCH 03

Service

PATCH 04

Route

PATCH 05

HTML

PATCH 06

JavaScript

Setiap Patch harus dapat dijalankan.

---

# 22. Refactor Rule

Tidak melakukan refactor sambil membuat fitur.

Refactor dilakukan hanya jika

- Bug
- Performa
- Keterbacaan

Bukan karena ingin mencoba struktur baru.

---

# 23. Testing Rule

Setiap Patch harus diuji.

Minimal

- Halaman terbuka
- CRUD berjalan
- Export berjalan
- Usage berjalan

Baru lanjut ke Patch berikutnya.

---

# 24. Final Principle

Architecture First

↓

Code Second

↓

Feature Third

Jangan mengubah Architecture ketika project sudah berjalan.

Semua ide baru masuk Backlog.

Blueprint tetap.