from typing import Dict, List, Optional

from app.core.database import get_clean_dict_cursor


class RequiredChannelRepository:
    TABLE_NAME = "required_channels"

    # =========================
    # CREATE
    # =========================
    def create(
        self,
        *,
        username: str,
        bot_username: str,
        added_by: Optional[str] = None,
        is_active: bool = True,
    ) -> Dict:
        """
        Create a new required channel.
        
        Args:
            username: Channel username (e.g., @channelname)
            bot_username: Bot username that requires this channel
            added_by: Who added this channel (optional)
            is_active: Whether this channel is active (default: True)
        
        Returns:
            Created channel dict
        """
        query = f"""
            INSERT INTO {self.TABLE_NAME}
                (username, bot_username, added_by, is_active)
            VALUES (%s, %s, %s, %s)
            RETURNING *
        """

        with get_clean_dict_cursor(commit=True) as cursor:
            cursor.execute(
                query,
                (username, bot_username, added_by, is_active),
            )
            return cursor.fetchone()

    # =========================
    # GET BY ID
    # =========================
    def get_by_id(self, channel_id: int) -> Optional[Dict]:
        """
        Get required channel by ID.
        
        Args:
            channel_id: Channel ID
        
        Returns:
            Channel dict or None if not found
        """
        query = f"""
            SELECT *
            FROM {self.TABLE_NAME}
            WHERE id = %s
        """

        with get_clean_dict_cursor() as cursor:
            cursor.execute(query, (channel_id,))
            return cursor.fetchone()

    # =========================
    # GET BY USERNAME
    # =========================
    def get_by_username(self, username: str, bot_username: Optional[str] = None) -> Optional[Dict]:
        """
        Get required channel by username.
        Optionally filter by bot_username.
        
        Args:
            username: Channel username
            bot_username: Bot username (optional)
        
        Returns:
            Channel dict or None if not found
        """
        query = f"""
            SELECT *
            FROM {self.TABLE_NAME}
            WHERE username = %s
        """
        params = [username]
        
        if bot_username:
            query += " AND bot_username = %s"
            params.append(bot_username)
        
        with get_clean_dict_cursor() as cursor:
            cursor.execute(query, tuple(params))
            return cursor.fetchone()

    # =========================
    # LIST
    # =========================
    def list_all(
        self,
        *,
        bot_username: Optional[str] = None,
        only_active: bool = False,
    ) -> List[Dict]:
        """
        List all required channels with optional filters.
        
        Args:
            bot_username: Filter by bot username
            only_active: Only return active channels
        
        Returns:
            List of channel dicts
        """
        conditions = []
        params = []

        if bot_username:
            conditions.append("bot_username = %s")
            params.append(bot_username)

        if only_active:
            conditions.append("is_active = true")

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        query = f"""
            SELECT *
            FROM {self.TABLE_NAME}
            {where_clause}
            ORDER BY added_at DESC
        """

        with get_clean_dict_cursor() as cursor:
            cursor.execute(query, tuple(params))
            return cursor.fetchall()

    # =========================
    # LIST BY BOT
    # =========================
    def list_by_bot(self, bot_username: str, only_active: bool = True) -> List[Dict]:
        """
        Get all required channels for a specific bot.
        
        Args:
            bot_username: Bot username
            only_active: Only return active channels
        
        Returns:
            List of channel dicts
        """
        return self.list_all(
            bot_username=bot_username,
            only_active=only_active,
        )

    # =========================
    # UPDATE
    # =========================
    def update(
        self,
        channel_id: int,
        *,
        username: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[Dict]:
        """
        Update a required channel.
        
        Args:
            channel_id: Channel ID
            username: New username (optional)
            is_active: New active status (optional)
        
        Returns:
            Updated channel dict or None if not found
        """
        fields = []
        params = []

        if username is not None:
            fields.append("username = %s")
            params.append(username)

        if is_active is not None:
            fields.append("is_active = %s")
            params.append(is_active)

        if not fields:
            return self.get_by_id(channel_id)

        params.append(channel_id)

        query = f"""
            UPDATE {self.TABLE_NAME}
            SET {', '.join(fields)}
            WHERE id = %s
            RETURNING *
        """

        with get_clean_dict_cursor(commit=True) as cursor:
            cursor.execute(query, tuple(params))
            return cursor.fetchone()

    # =========================
    # DELETE (HARD)
    # =========================
    def delete(self, channel_id: int) -> bool:
        """
        Permanently delete a required channel.
        
        Args:
            channel_id: Channel ID
        
        Returns:
            True if deleted, False if not found
        """
        query = f"""
            DELETE FROM {self.TABLE_NAME}
            WHERE id = %s
        """

        with get_clean_dict_cursor(commit=True) as cursor:
            cursor.execute(query, (channel_id,))
            return cursor.rowcount > 0

    # =========================
    # SOFT DELETE (DEACTIVATE)
    # =========================
    def deactivate(self, channel_id: int) -> Optional[Dict]:
        """
        Soft delete by setting is_active to False.
        
        Args:
            channel_id: Channel ID
        
        Returns:
            Updated channel dict or None if not found
        """
        return self.update(channel_id, is_active=False)

    # =========================
    # REACTIVATE
    # =========================
    def reactivate(self, channel_id: int) -> Optional[Dict]:
        """
        Reactivate a deactivated channel.
        
        Args:
            channel_id: Channel ID
        
        Returns:
            Updated channel dict or None if not found
        """
        return self.update(channel_id, is_active=True)

    # =========================
    # EXISTS
    # =========================
    def exists(self, username: str, bot_username: Optional[str] = None) -> bool:
        """
        Check if a required channel exists.
        
        Args:
            username: Channel username
            bot_username: Bot username (optional)
        
        Returns:
            True if exists, False otherwise
        """
        result = self.get_by_username(username, bot_username)
        return result is not None

    # =========================
    # GET ACTIVE COUNT
    # =========================
    def get_active_count(self, bot_username: Optional[str] = None) -> int:
        """
        Get count of active required channels.
        
        Args:
            bot_username: Filter by bot username (optional)
        
        Returns:
            Count of active channels
        """
        query = f"""
            SELECT COUNT(*) AS total
            FROM {self.TABLE_NAME}
            WHERE is_active = true
        """
        params = []
        
        if bot_username:
            query += " AND bot_username = %s"
            params.append(bot_username)
        
        with get_clean_dict_cursor() as cursor:
            cursor.execute(query, tuple(params))
            result = cursor.fetchone()
            return result["total"] if result else 0

    # =========================
    # BULK CREATE
    # =========================
    def bulk_create(
        self,
        channels: List[Dict],
    ) -> List[Dict]:
        """
        Bulk insert multiple required channels.
        
        Args:
            channels: List of dict with keys: 
                username, bot_username, added_by (optional), is_active (optional)
        
        Returns:
            List of created channel dicts
        """
        if not channels:
            return []
        
        query = f"""
            INSERT INTO {self.TABLE_NAME}
                (username, bot_username, added_by, is_active)
            VALUES (%s, %s, %s, %s)
            RETURNING *
        """
        
        results = []
        with get_clean_dict_cursor(commit=True) as cursor:
            for channel in channels:
                cursor.execute(
                    query,
                    (
                        channel["username"],
                        channel.get("bot_username"),
                        channel.get("added_by"),
                        channel.get("is_active", True),
                    ),
                )
                results.append(cursor.fetchone())
        
        return results