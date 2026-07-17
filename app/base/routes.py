from app.utils.logger import log
from app.core.database import get_db_cursor


def get_dashboard_stats():
    stats = {
        "total_users": 0,
        "users_drac1n": 0,
        "users_utbk": 0,
        "new_users_today": 0,
        "new_users_week": 0,
        "new_users_month": 0,
        "total_vip": 0,
        "vip_drac1n": 0,
        "vip_utbk": 0,
        "active_vip": 0,
        "expired_vip_week": 0,
        "vip_percentage": 0,
        "total_shows": 0,
        "total_files": 0,
        "total_plays": 0,
        "total_genres": 0,
        "active_shows": 0,
        "recent_shows": 0,
        "total_amount": 0,
        "total_donasi": 0,
        "total_vip_donation": 0,
        "revenue_today": 0,
        "revenue_week": 0,
        "revenue_month": 0,
        "total_vouchers": 0,
        "active_vouchers": 0,
        "used_vouchers": 0,
        "total_admins": 0,
        "active_admins": 0,
        "conversion_rate": 0,
        "chart_labels": [],
        "chart_data": [],
        "revenue_distribution": [0, 0, 0],
        "recent_activities": [],
        "top_shows": [],
    }

    try:
        with get_db_cursor() as (cursor, _):
            # =========================
            # USERS + VIP (sama seperti sebelumnya)
            # =========================
            cursor.execute("""
                SELECT
                    COUNT(*) FILTER (WHERE source='drac1n'),
                    COUNT(*) FILTER (WHERE source='utbk'),
                    COUNT(*) FILTER (WHERE created_at >= CURRENT_DATE),
                    COUNT(*) FILTER (WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'),
                    COUNT(*) FILTER (WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'),
                    COUNT(*) FILTER (WHERE is_vip),
                    COUNT(*) FILTER (WHERE is_vip AND vip_expired > NOW()),
                    COUNT(*) FILTER (
                        WHERE vip_expired BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
                    )
                FROM (
                    SELECT 'drac1n' as source, created_at, is_vip, vip_expired FROM users
                    UNION ALL
                    SELECT 'utbk', created_at, is_vip, vip_expired FROM users_utbk
                ) u
            """)

            row = cursor.fetchone()
            stats["users_drac1n"] = row[0] or 0
            stats["users_utbk"] = row[1] or 0
            stats["new_users_today"] = row[2] or 0
            stats["new_users_week"] = row[3] or 0
            stats["new_users_month"] = row[4] or 0
            stats["total_vip"] = row[5] or 0
            stats["active_vip"] = row[6] or 0
            stats["expired_vip_week"] = row[7] or 0
            stats["total_users"] = stats["users_drac1n"] + stats["users_utbk"]

            if stats["total_users"] > 0:
                stats["vip_percentage"] = round(
                    stats["total_vip"] / stats["total_users"] * 100, 1
                )
                stats["conversion_rate"] = stats["vip_percentage"]

            # =========================
            # CONTENT
            # =========================
            cursor.execute("""
                SELECT
                    (SELECT COUNT(*) FROM shows),
                    (SELECT COUNT(*) FROM files),
                    (SELECT COALESCE(SUM(play_count), 0) FROM video_stats),
                    (SELECT COUNT(DISTINCT genre) FROM shows WHERE genre IS NOT NULL AND genre != ''),
                    (SELECT COUNT(*) FROM shows WHERE is_active = true),
                    (SELECT COUNT(*) FROM shows WHERE posted_at >= CURRENT_DATE - INTERVAL '30 days')
            """)

            row = cursor.fetchone()
            stats["total_shows"] = row[0] or 0
            stats["total_files"] = row[1] or 0
            stats["total_plays"] = row[2] or 0
            stats["total_genres"] = row[3] or 0
            stats["active_shows"] = row[4] or 0
            stats["recent_shows"] = row[5] or 0

            # =========================
            # DONATION
            # =========================
            cursor.execute("""
                SELECT
                    COALESCE(SUM(amount), 0),
                    COALESCE(SUM(amount) FILTER (WHERE type = 'donasi'), 0),
                    COALESCE(SUM(amount) FILTER (WHERE type = 'vip'), 0),
                    COALESCE(SUM(amount) FILTER (WHERE DATE(timestamp) = CURRENT_DATE), 0),
                    COALESCE(SUM(amount) FILTER (WHERE timestamp >= CURRENT_DATE - INTERVAL '7 days'), 0),
                    COALESCE(SUM(amount) FILTER (WHERE timestamp >= CURRENT_DATE - INTERVAL '30 days'), 0)
                FROM donation_log
            """)

            row = cursor.fetchone()
            stats["total_amount"] = row[0] or 0
            stats["total_donasi"] = row[1] or 0
            stats["total_vip_donation"] = row[2] or 0
            stats["revenue_today"] = row[3] or 0
            stats["revenue_week"] = row[4] or 0
            stats["revenue_month"] = row[5] or 0
            stats["revenue_distribution"] = [
                stats["total_vip_donation"],
                stats["total_donasi"],
                0,
            ]

            # =========================
            # VOUCHERS
            # =========================
            cursor.execute("""
                SELECT
                    COUNT(*),
                    COUNT(*) FILTER (WHERE is_used = FALSE AND (expires_at IS NULL OR expires_at > NOW())),
                    COUNT(*) FILTER (WHERE is_used = TRUE)
                FROM vip_vouchers
            """)

            row = cursor.fetchone()
            stats["total_vouchers"] = row[0] or 0
            stats["active_vouchers"] = row[1] or 0
            stats["used_vouchers"] = row[2] or 0

            # =========================
            # ADMINS
            # =========================
            cursor.execute("SELECT COUNT(*) FROM admins")
            row = cursor.fetchone()
            stats["total_admins"] = row[0] or 0
            stats["active_admins"] = row[0] or 0

            # =========================
            # TOP SHOWS (diperbaiki - join melalui files)
            # =========================
            cursor.execute("""
                SELECT 
                    s.id,
                    s.title,
                    s.genre,
                    s.thumbnail_url,
                    COALESCE(SUM(vs.play_count), 0) as total_plays
                FROM shows s
                LEFT JOIN files f ON s.id = f.show_id
                LEFT JOIN video_stats vs ON f.file_id = vs.file_id
                GROUP BY s.id, s.title, s.genre, s.thumbnail_url
                ORDER BY total_plays DESC
                LIMIT 5
            """)

            top_shows = cursor.fetchall()
            stats["top_shows"] = [
                {
                    "id": row[0],
                    "title": row[1] or "Untitled",
                    "genre": row[2] or "-",
                    "thumbnail_url": row[3] or "/static/img/default-thumb.png",
                    "views": row[4] or 0,
                }
                for row in top_shows
            ]

            # =========================
            # CHART DATA (VIP per day) - PERBAIKAN
            # =========================
            try:
                # Query untuk mengambil data VIP users per hari (30 hari terakhir)
                cursor.execute("""
                    SELECT 
                        DATE(created_at) as date,
                        COUNT(*) as vip_count
                    FROM users
                    WHERE is_vip = true 
                        AND created_at >= CURRENT_DATE - INTERVAL '30 days'
                    GROUP BY DATE(created_at)
                    ORDER BY date ASC
                """)

                chart_rows = cursor.fetchall()

                # Buat dictionary dari hasil query
                data_dict = {}
                for row in chart_rows:
                    if row[0]:  # pastikan date tidak NULL
                        data_dict[row[0]] = row[1]

                # Generate semua tanggal 30 hari terakhir (termasuk yang tidak ada data)
                from datetime import datetime, timedelta

                labels = []
                values = []
                today = datetime.now().date()

                for i in range(30, -1, -1):  # dari 30 hari lalu sampai hari ini
                    date = today - timedelta(days=i)
                    labels.append(date.strftime("%d %b"))
                    values.append(data_dict.get(date, 0))

                stats["chart_labels"] = labels
                stats["chart_data"] = values

                print(
                    f"CHART DATA: Generated {len(labels)} labels, total VIP count: {sum(values)}"
                )

            except Exception as e:
                log.error(f"Chart query error: {e}")
                stats["chart_labels"] = []
                stats["chart_data"] = []

            # =========================
            # RECENT ACTIVITIES
            # =========================
            activities = []

            # New users
            cursor.execute("""
                SELECT username, created_at, source 
                FROM (
                    SELECT username, created_at, 'drac1n' as source FROM users
                    UNION ALL
                    SELECT username, created_at, 'utbk' as source FROM users_utbk
                ) all_users
                ORDER BY created_at DESC 
                LIMIT 5
            """)

            for row in cursor.fetchall():
                activities.append(
                    {
                        "title": f"New user registered: {row[0]} ({row[2]})",
                        "time": (
                            row[1].strftime("%H:%M, %d %b") if row[1] else "Recently"
                        ),
                        "icon": "user-plus",
                        "color": "#10b981",
                        "bg_color": "rgba(16, 185, 129, 0.1)",
                        "link": "#",
                    }
                )

            # New shows
            cursor.execute("""
                SELECT title, posted_at 
                FROM shows 
                WHERE posted_at IS NOT NULL
                ORDER BY posted_at DESC 
                LIMIT 3
            """)

            for row in cursor.fetchall():
                activities.append(
                    {
                        "title": f"New show added: {row[0]}",
                        "time": (
                            row[1].strftime("%H:%M, %d %b") if row[1] else "Recently"
                        ),
                        "icon": "film",
                        "color": "#6366f1",
                        "bg_color": "rgba(99, 102, 241, 0.1)",
                        "link": "#",
                    }
                )

            # Recent donations
            cursor.execute("""
                SELECT amount, type, timestamp 
                FROM donation_log 
                ORDER BY timestamp DESC 
                LIMIT 3
            """)

            for row in cursor.fetchall():
                activities.append(
                    {
                        "title": f"Donation: Rp {row[0]:,.0f} ({row[1]})",
                        "time": (
                            row[2].strftime("%H:%M, %d %b") if row[2] else "Recently"
                        ),
                        "icon": "donate",
                        "color": "#f59e0b",
                        "bg_color": "rgba(245, 158, 11, 0.1)",
                        "link": "#",
                    }
                )

            stats["recent_activities"] = activities[:10]

        log.info(
            f"[Dashboard] Loaded Users={stats['total_users']} Shows={stats['total_shows']}"
        )
        return stats

    except Exception as e:
        log.error(f"[Dashboard] ERROR: {e}", exc_info=True)
        return stats
