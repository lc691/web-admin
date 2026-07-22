"""
Channel Presenter
"""

from app.music.services.channels.service import ChannelService


class ChannelPresenter:
    """
    Presenter halaman Channel.
    """

    MODULE = "channels"
    ICON = "ti ti-brand-youtube"

    @classmethod
    def base(cls):
        """
        Context dasar semua halaman Channel.
        """
        return {
            "module": cls.MODULE,
            "icon": cls.ICON,
        }

    # =====================================================
    # INDEX
    # =====================================================

    @classmethod
    def index(cls):

        return {
            **cls.base(),

            "page": "index",

            "title": "Channels",

            "subtitle": "Kelola akun SoundOn Channel",
        }

    # =====================================================
    # CREATE
    # =====================================================

    @classmethod
    def create(cls):

        return {
            **cls.base(),

            "page": "form",

            "mode": "create",

            "title": "Tambah Channel",

            "subtitle": "Tambahkan channel baru.",

            "channel": None,
        }

    # =====================================================
    # EDIT
    # =====================================================

    @classmethod
    def edit(
        cls,
        cursor,
        channel_id: int,
    ):

        channel = ChannelService.detail(
            cursor,
            channel_id,
        )

        return {
            **cls.base(),

            "page": "form",

            "mode": "edit",

            "title": "Edit Channel",

            "subtitle": "Perbarui informasi channel.",

            "channel": channel,
        }

    # =====================================================
    # DETAIL
    # =====================================================

    @classmethod
    def detail(
        cls,
        cursor,
        channel_id: int,
    ):

        channel = ChannelService.detail(
            cursor,
            channel_id,
        )

        return {
            **cls.base(),

            "page": "detail",

            "title": channel["name"],

            "subtitle": "Informasi Channel",

            "channel": channel,
        }

    # =====================================================
    # STATISTICS
    # =====================================================

    @staticmethod
    def statistics(cursor):

        return ChannelService.statistics(cursor)