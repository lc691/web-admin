# Export Playlist Architecture (Final)

> **Status:** Locked
> Setelah dokumen ini disetujui, implementasi dilakukan sesuai struktur di bawah tanpa mengubah arsitektur.

---

# Project Structure

```text
app/
│
├── routes/
│   └── music/
│       └── songs/
│           ├── router.py
│           ├── presenter.py
│           └── constants.py
│
├── repositories/
│   └── export/
│       ├── __init__.py
│       ├── types.py
│       ├── songs.py
│       ├── usage.py
│       ├── batches.py
│       └── statistics.py
│
├── services/
│   └── export/
│       ├── __init__.py
│       ├── service.py
│       ├── selector.py
│       ├── formatter.py
│       ├── duplicate.py
│       ├── youtube.py
│       ├── labels.py
│       ├── blacklist.py
│       └── validator.py
│
├── models/
├── schemas/
├── templates/
├── static/
└── core/
```

---

# Database

```text
songs

artists

channels

channel_blacklists

song_usage

song_export_batches

song_export_batch_items
```

Database dinyatakan **final**.

---

# Repository Layer

Repository hanya bertanggung jawab terhadap query PostgreSQL.

## songs.py

```text
get_available_songs()

get_exported_songs()
```

---

## usage.py

```text
save_song_usage()

reset_song_usage()

get_remaining_song_count()
```

---

## batches.py

```text
create_export_batch()

create_export_batch_items()

get_export_batch()

get_export_batch_by_day()

get_export_batch_items()

delete_export_batch()
```

---

## statistics.py

```text
export_exists()

get_export_information()
```

---

## types.py

```text
ExportMode

SongRow

ExportBatch

ExportBatchItem

ExportInformation
```

---

# Service Layer

Service merupakan orchestration layer.

## service.py

```text
export()

build_export()

load_existing_batch()

create_new_batch()
```

---

## selector.py

Seluruh algoritma pemilihan lagu.

```text
group_by_channel()

select_round_robin()

fill_remaining()

select_songs()
```

---

## duplicate.py

```text
duplicate_songs()
```

---

## formatter.py

```text
build_txt()
```

---

## youtube.py

```text
build_youtube_url()
```

---

## labels.py

```text
GROUP_LABELS

get_group_label()
```

---

## blacklist.py

```text
build_mode_filter()
```

---

## validator.py

```text
validate_target()

validate_duplicate()

validate_export_request()
```

---

# Export Flow

```text
Router
        │
        ▼
ExportService.export()
        │
        ▼
export_exists()
        │
 ┌──────┴─────────┐
 │                │
 │                │
Batch Ada     Batch Belum Ada
 │                │
 ▼                ▼
get_batch()   get_available_songs()
 │                │
 ▼                ▼
shuffle()      selector.select()
 │                │
 │                ▼
 │         save_song_usage()
 │                │
 │                ▼
 │        create_export_batch()
 │                │
 │                ▼
 │      create_export_batch_items()
 └────────┬──────────────┘
          ▼
duplicate_songs()
          ▼
build_txt()
          ▼
Response
```

---

# Selector Algorithm

## Phase 1

Distribusi merata.

```text
Round Robin

↓

preferred_channel_limit

↓

Semua channel mendapat kesempatan yang sama
```

---

## Phase 2

Jika target belum terpenuhi.

```text
Masih kurang lagu

↓

Ambil lagi dari channel
yang masih memiliki lagu

↓

Target terpenuhi
```

---

# Export Mode

## normal

```text
Semua lagu Live

Termasuk channel blacklist
```

---

## clean

```text
Semua lagu Live

Tidak termasuk channel blacklist
```

---

## blacklist

```text
Hanya lagu Live

Yang berasal dari channel blacklist
```

---

# Song Usage

`song_usage` hanya berfungsi sebagai penanda bahwa sebuah lagu sudah pernah digunakan pada mode tertentu.

```text
UNIQUE(song_id, mode)
```

Jika jumlah lagu yang tersedia tidak mencukupi kebutuhan export:

```text
reset_song_usage(mode)

↓

Generate ulang
```

---

# Export Batch

## song_export_batches

Menyimpan metadata export.

```text
day

mode

target

duplicate

channel_limit

excluded_channels

selected_unique

status

created_at

completed_at
```

---

## song_export_batch_items

Menyimpan daftar lagu unik hasil seleksi.

```text
batch_id

song_id

order_index
```

Duplicate **tidak disimpan** ke database.

Duplicate dilakukan pada proses formatting.

---

# Export Ulang

Jika batch sudah ada.

```text
Ambil playlist dari batch

↓

Acak urutan lagu

↓

Duplicate

↓

Generate TXT
```

Lagu tetap sama.

Yang berubah hanya urutan.

---

# Business Rules

* Batch unik berdasarkan `(day, mode)`.
* `song_usage` hanya digunakan untuk tracking penggunaan lagu.
* `song_export_batches` adalah metadata export.
* `song_export_batch_items` adalah source of truth playlist.
* Duplicate dilakukan saat generate output.
* Selector menggunakan **2 Phase Algorithm**.
* Repository hanya berisi query database.
* Seluruh business logic berada pada Service Layer.

---

# Architecture Status

```text
STATUS : LOCKED

Database          ✅
Repository        ✅
Service           ✅
Export Flow       ✅
Selector          ✅
Business Rules    ✅
Folder Structure  ✅
```

Mulai tahap implementasi, perubahan dilakukan hanya jika terdapat kebutuhan bisnis baru yang benar-benar mengharuskan perubahan arsitektur.
