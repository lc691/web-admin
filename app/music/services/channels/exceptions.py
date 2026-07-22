"""
Channel Exceptions
"""


class ChannelError(Exception):
    """
    Base exception untuk seluruh Channel.
    """


class ChannelNotFoundError(ChannelError):
    """
    Channel tidak ditemukan.
    """


class DuplicateChannelNameError(ChannelError):
    """
    Nama channel sudah digunakan.
    """


class DuplicateChannelEmailError(ChannelError):
    """
    Email channel sudah digunakan.
    """


class InvalidChannelNameError(ChannelError):
    """
    Nama channel tidak valid.
    """


class InvalidChannelEmailError(ChannelError):
    """
    Email channel tidak valid.
    """


class InvalidChannelPasswordError(ChannelError):
    """
    Password channel tidak valid.
    """


class InvalidChannelDataError(ChannelError):
    """
    Data channel tidak valid.
    """


class BulkChannelError(ChannelError):
    """
    Error operasi bulk.
    """