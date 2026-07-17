# @router.get("/songs/export/day/{day}")
# def export_txt_auto(
#     day: int,
#     target: int = Query(
#         default=140,
#         ge=1,
#         le=1000,
#         description="Jumlah output akhir",
#     ),
#     duplicate: int = Query(
#         default=2,
#         ge=1,
#         le=20,
#         description="Berapa kali tiap lagu diulang",
#     ),
# ):
#     # ==========================================================
#     # STEP 1
#     # Hitung jumlah lagu unik yang dibutuhkan.
#     #
#     # Contoh:
#     # target = 140
#     # duplicate = 2
#     #
#     # Maka cukup memilih:
#     # 70 lagu unik
#     # ==========================================================

#     target_unique = (target + duplicate - 1) // duplicate

#     with get_dict_cursor() as (cursor, conn):

#         # ==========================================================
#         # STEP 2
#         # Cek apakah hari ini sudah pernah dibuat.
#         # ==========================================================

#         cursor.execute(
#             """
#             SELECT COUNT(*) AS total
#             FROM song_usage
#             WHERE day=%s
#             """,
#             (day,),
#         )

#         existing = cursor.fetchone()["total"]

#         # ==========================================================
#         # STEP 3A
#         # Jika hari sudah pernah dibuat:
#         #
#         # - Ambil lagu yang sudah tersimpan.
#         # - Lagu TETAP sama.
#         # - Tetapi urutan diacak ulang setiap export.
#         # ==========================================================

#         if existing > 0:

#             cursor.execute(
#                 """
#                 SELECT
#                     s.id,
#                     s.title,
#                     a.name AS artist,
#                     c.name AS channel
#                 FROM song_usage u
#                 JOIN songs s
#                     ON u.song_id = s.id
#                 JOIN artists a
#                     ON s.artist_id = a.id
#                 JOIN channels c
#                     ON a.channel_id = c.id
#                 WHERE
#                     u.day = %s
#                     AND s.status='Live'
#                 ORDER BY u.id
#                 """,
#                 (day,),
#             )

#             selected = cursor.fetchall()

#             # ==========================================
#             # PERUBAHAN #3
#             #
#             # Lagu tetap sama.
#             # Hanya urutannya yang berubah.
#             # ==========================================

#             random.shuffle(selected)

#         # ==========================================================
#         # STEP 3B
#         # Jika hari BELUM pernah dibuat.
#         #
#         # Cari lagu yang belum pernah dipakai.
#         # ==========================================================

#         else:

#             cursor.execute(
#                 """
#                 SELECT
#                     s.id,
#                     s.title,
#                     a.name AS artist,
#                     c.id AS channel_id,
#                     c.name AS channel
#                 FROM songs s
#                 JOIN artists a
#                     ON s.artist_id = a.id
#                 JOIN channels c
#                     ON a.channel_id = c.id
#                 LEFT JOIN song_usage u
#                     ON s.id=u.song_id
#                 WHERE
#                     u.song_id IS NULL
#                     AND s.status='Live'
#                 ORDER BY RANDOM()
#                 """
#             )

#             rows = cursor.fetchall()

#             # ======================================================
#             # STEP 4
#             # Kelompokkan lagu berdasarkan Channel.
#             # ======================================================

#             grouped = defaultdict(list)

#             for row in rows:
#                 grouped[row["channel_id"]].append(row)

#             # ======================================================
#             # STEP 5
#             # Round Robin.
#             #
#             # Ambil satu lagu dari setiap channel
#             # agar distribusi lebih merata.
#             # ======================================================

#             selected = []

#             while len(selected) < target_unique:

#                 added = False

#                 for cid in grouped:

#                     if not grouped[cid]:
#                         continue

#                     selected.append(grouped[cid].pop(0))
#                     added = True

#                     if len(selected) >= target_unique:
#                         break

#                 if not added:
#                     break

#             # ======================================================
#             # STEP 6
#             # Simpan hasil pilihan ke song_usage.
#             #
#             # Tujuannya supaya lagu tersebut
#             # tidak dipilih lagi pada hari lain.
#             # ======================================================

#             for song in selected:

#                 cursor.execute(
#                     """
#                     INSERT INTO song_usage
#                     (song_id, day)
#                     VALUES (%s, %s)
#                     """,
#                     (song["id"], day),
#                 )

#             conn.commit()

#     # ==========================================================
#     # STEP 7
#     # Duplicate lagu.
#     #
#     # A -> A A
#     # B -> B B
#     # ==========================================================

#     paired = []

#     for song in selected:
#         paired.extend([song] * duplicate)

#     paired = paired[:target]

#     # ==========================================================
#     # STEP 8
#     # Mapping label grup.
#     #
#     # PERUBAHAN #2
#     # ==========================================================

#     GROUP_LABELS = {
#         1: "AMR 1",
#         2: "AMR 2",
#         3: "AMR 3",
#         4: "AMR 4",
#         5: "MCL 1",
#         6: "MCL 2",
#         7: "MCL 3",
#         8: "MCL 4",
#         9: "FKR 1",
#         10: "FKR 2",
#         11: "FKR 3",
#         12: "FKR 4",
#         13: "SPX 1",
#         14: "SPX 2",
#     }

#     lines = []

#     # ==========================================================
#     # STEP 9
#     # Generate isi TXT.
#     # ==========================================================

#     for i, song in enumerate(paired, start=1):

#         num = ((i - 1) % 10) + 1

#         title = song["title"].strip().lower()
#         artist = song["artist"].strip().lower()

#         query = f"{title} {artist}".replace(" ", "+")

#         yt_url = (
#             "https://www.youtube.com/results"
#             f"?search_query={query}"
#         )

#         lines.append(
#             f"{num}. 🇺🇲 Judul: {title} {artist}\n"
#             f"{yt_url}"
#         )

#         # ======================================================
#         # STEP 10
#         # Setiap 10 lagu tambahkan label grup.
#         # ======================================================

#         if i % 10 == 0:

#             group = i // 10

#             label = GROUP_LABELS.get(
#                 group,
#                 f"GROUP {group}",
#             )

#             lines.append(
#                 f"NAMA ABSEN : {label}\n"
#                 f"================="
#             )

#     # ==========================================================
#     # STEP 11
#     # Gabungkan seluruh output menjadi text.
#     # ==========================================================

#     text = "\n\n".join(lines)

#     # ==========================================================
#     # STEP 12
#     # Return sebagai file TXT.
#     # ==========================================================

#     return Response(
#         content=text,
#         media_type="text/plain",
#         headers={
#             "Content-Disposition":
#             f"attachment; filename=day_{day}.txt"
#         },
#     )