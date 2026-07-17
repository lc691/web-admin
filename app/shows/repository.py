from app.core.database import get_db_cursor, get_dict_cursor


class ShowRepository:
    """
    Repository layer for `shows` table.
    Handles CRUD operations and source label join.
    """

    # =====================================================
    # CONFIG
    # =====================================================
    TABLE_NAME = "shows"
    SOURCE_TABLE = "request_sources"

    ALLOWED_UPDATE_FIELDS = {
        "title",
        "sinopsis",
        "genre",
        "source_id",
        "hashtags",
        "thumbnail_url",
        "is_adult",
    }

    # =====================================================
    # INTERNAL HELPERS
    # =====================================================
    def _build_update_clause(self, data: dict) -> tuple[str, list]:
        """
        Build dynamic SET clause for UPDATE query.
        Returns:
            set_clause (str),
            values (list)
        """
        fields = []
        values = []

        for key, value in data.items():
            if key not in self.ALLOWED_UPDATE_FIELDS:
                continue

            fields.append(f"{key} = %s")
            values.append(value)

        if not fields:
            return "", []

        # auto updated_at
        fields.append("updated_at = NOW()")

        return ", ".join(fields), values

    # =====================================================
    # LIST ALL (DENGAN PAGINATION)
    # =====================================================

    def list_all(
        self,
        page: int = 1,
        per_page: int = 20,
        search: str | None = None,
    ) -> dict:
        """
        Get shows with pagination and search.
        
        Returns:
            {
                "data": list[dict],
                "total": int,
                "page": int,
                "per_page": int,
                "total_pages": int
            }
        """
        offset = (page - 1) * per_page
        
        # =====================================================
        # BUILD WHERE CLAUSE
        # =====================================================
        where_clause, params = self._build_search(search)
        
        # =====================================================
        # COUNT TOTAL
        # =====================================================
        count_query = f"""
            SELECT COUNT(*) AS total
            FROM {self.TABLE_NAME} s
            {where_clause}
        """
        
        with get_dict_cursor() as (cur, _):
            cur.execute(count_query, params)
            total = cur.fetchone()["total"]
        
        if total == 0:
            return {
                "data": [],
                "total": 0,
                "page": page,
                "per_page": per_page,
                "total_pages": 0
            }
        
        # =====================================================
        # MAIN QUERY
        # =====================================================
        query = f"""
            WITH file_stats AS (
                SELECT
                    f.show_id,
                    STRING_AGG(
                        DISTINCT f.channel_username,
                        ', '
                    ) FILTER (
                        WHERE f.channel_username IS NOT NULL
                    ) AS channel_username,
                    BOOL_OR(f.message_id IS NOT NULL) AS has_released,
                    COUNT(*) AS total_files
                FROM files f
                GROUP BY f.show_id
            )

            SELECT
                s.id,
                s.title,
                s.thumbnail_url,
                LEFT(s.sinopsis, 150) AS sinopsis,
                s.genre,
                s.hashtags,
                s.source_id,
                r.label AS source_label,
                s.is_adult,
                s.created_at,
                fs.channel_username,
                CASE
                    WHEN fs.total_files IS NULL THEN 'draft'
                    WHEN fs.has_released THEN 'released'
                    ELSE 'scheduled'
                END AS release_status

            FROM {self.TABLE_NAME} s
            LEFT JOIN {self.SOURCE_TABLE} r ON s.source_id = r.id
            LEFT JOIN file_stats fs ON fs.show_id = s.id
            {where_clause}
            ORDER BY s.id DESC
            LIMIT %s OFFSET %s
        """
        
        params.extend([per_page, offset])
        
        with get_dict_cursor() as (cur, _):
            cur.execute(query, params)
            data = cur.fetchall()
        
        return {
            "data": data,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }

    # =====================================================
    # LIST ALL SIMPLE (TANPA FILE STATS)
    # =====================================================

    def list_all_simple(
        self,
        page: int = 1,
        per_page: int = 20,
        search: str | None = None,
    ) -> dict:
        """
        Get shows WITHOUT file stats (lebih cepat).
        """
        offset = (page - 1) * per_page
        
        where_clause = ""
        params = []
        
        if search and len(search.strip()) >= 2:
            where_clause = "WHERE s.title ILIKE %s OR s.genre ILIKE %s"
            search_term = f"%{search.strip()}%"
            params = [search_term, search_term]
        
        # Count
        count_query = f"""
            SELECT COUNT(*) AS total
            FROM {self.TABLE_NAME} s
            {where_clause}
        """
        
        with get_dict_cursor() as (cur, _):
            cur.execute(count_query, params)
            total = cur.fetchone()["total"]
        
        if total == 0:
            return {
                "data": [],
                "total": 0,
                "page": page,
                "per_page": per_page,
                "total_pages": 0
            }
        
        # Main query (tanpa file_stats)
        query = f"""
            SELECT
                s.id,
                s.title,
                s.thumbnail_url,
                LEFT(s.sinopsis, 150) AS sinopsis,
                s.genre,
                s.hashtags,
                s.source_id,
                r.label AS source_label,
                s.is_adult,
                s.created_at
            FROM {self.TABLE_NAME} s
            LEFT JOIN {self.SOURCE_TABLE} r ON s.source_id = r.id
            {where_clause}
            ORDER BY s.id DESC
            LIMIT %s OFFSET %s
        """
        
        params.extend([per_page, offset])
        
        with get_dict_cursor() as (cur, _):
            cur.execute(query, params)
            data = cur.fetchall()
        
        return {
            "data": data,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }

    # =====================================================
    # GET BY ID
    # =====================================================
    def get_by_id(self, show_id: int) -> dict | None:
        if not isinstance(show_id, int) or show_id <= 0:
            return None

        query = f"""
            SELECT 
                s.*,
                r.label AS source_label
            FROM {self.TABLE_NAME} s
            LEFT JOIN {self.SOURCE_TABLE} r ON s.source_id = r.id
            WHERE s.id = %s
        """

        with get_dict_cursor() as (cur, _):
            cur.execute(query, (show_id,))
            return cur.fetchone()

    # =====================================================
    # INSERT
    # =====================================================
    def insert(self, data: dict) -> int:
        """
        Insert new show.
        Returns inserted rowcount (1 if success).
        """
        if "title" not in data or not data["title"]:
            raise ValueError("title is required")

        query = f"""
            INSERT INTO {self.TABLE_NAME} (
                title,
                sinopsis,
                genre,
                hashtags,
                source_id,
                thumbnail_url,
                is_adult,
                posted_at
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,NOW())
        """

        values = (
            data["title"],
            data.get("sinopsis"),
            data.get("genre"),
            data.get("hashtags"),
            data.get("source_id"),
            data.get("thumbnail_url"),
            data.get("is_adult", False),
        )

        with get_db_cursor(commit=True) as (cur, _):
            cur.execute(query, values)
            return cur.rowcount

    # =====================================================
    # UPDATE ONE
    # =====================================================
    def update_one(self, show_id: int, data: dict) -> int:
        """
        Update single show by id.
        Returns affected row count.
        """
        if not isinstance(show_id, int) or show_id <= 0:
            return 0

        set_clause, values = self._build_update_clause(data)
        if not set_clause:
            return 0

        query = f"""
            UPDATE {self.TABLE_NAME}
            SET {set_clause}
            WHERE id = %s
        """

        values.append(show_id)

        with get_db_cursor(commit=True) as (cur, _):
            cur.execute(query, tuple(values))
            return cur.rowcount

    # =====================================================
    # UPDATE BULK
    # =====================================================
    def update_bulk(self, ids: list[int], data: dict) -> int:
        """
        Update multiple shows by id list.
        Returns affected row count.
        """
        if not ids:
            return 0

        # Filter only valid ints
        ids = [i for i in ids if isinstance(i, int) and i > 0]
        if not ids:
            return 0

        set_clause, values = self._build_update_clause(data)
        if not set_clause:
            return 0

        placeholders = ",".join(["%s"] * len(ids))

        query = f"""
            UPDATE {self.TABLE_NAME}
            SET {set_clause}
            WHERE id IN ({placeholders})
        """

        values.extend(ids)

        with get_db_cursor(commit=True) as (cur, _):
            cur.execute(query, tuple(values))
            return cur.rowcount

    # =====================================================
    # DELETE
    # =====================================================
    def delete(self, show_id: int) -> int:
        """
        Delete show by id.
        Returns affected row count.
        """
        if not isinstance(show_id, int) or show_id <= 0:
            return 0

        query = f"DELETE FROM {self.TABLE_NAME} WHERE id = %s"

        with get_db_cursor(commit=True) as (cur, _):
            cur.execute(query, (show_id,))
            return cur.rowcount

    # =====================================================
    # SEARCH
    # =====================================================
    def search(self, keyword: str, limit: int = 50) -> list[dict]:
        """
        Search shows by title or genre.
        """
        query = f"""
            SELECT 
                s.id,
                s.title,
                s.genre,
                s.thumbnail_url,
                r.label AS source_label,
                s.is_adult
            FROM {self.TABLE_NAME} s
            LEFT JOIN {self.SOURCE_TABLE} r ON s.source_id = r.id
            WHERE s.title ILIKE %s
               OR s.genre ILIKE %s
            ORDER BY s.title ASC
            LIMIT %s
        """
        
        search_term = f"%{keyword}%"
        
        with get_dict_cursor() as (cur, _):
            cur.execute(query, (search_term, search_term, limit))
            return cur.fetchall()

    def _build_search(
        self,
        search: str | None,
    ) -> tuple[str, list]:
        where = ""
        params = []

        if search and len(search.strip()) >= 2:
            keyword = f"%{search.strip()}%"
            where = """
            WHERE
                s.title ILIKE %s
                OR s.genre ILIKE %s
            """
            params = [keyword, keyword]

        return where, params
    
    # =====================================================
    # STATS
    # =====================================================
    def get_stats(self) -> dict:
        """
        Get statistics for dashboard.
        """
        query = f"""
            SELECT
                COUNT(*) AS total_shows,
                COUNT(CASE WHEN is_adult = TRUE THEN 1 END) AS adult_shows,
                COUNT(CASE WHEN is_active = TRUE THEN 1 END) AS active_shows,
                COUNT(DISTINCT source_id) AS total_sources,
                COUNT(CASE WHEN thumbnail_url IS NOT NULL THEN 1 END) AS has_thumbnail
            FROM {self.TABLE_NAME}
        """
        
        with get_dict_cursor() as (cur, _):
            cur.execute(query)
            return cur.fetchone()