from app.music.services.artists.service import ArtistService
from app.music.services.channels.service import ChannelService


class ChannelArtistsPresenter:

    @staticmethod
    def page(cursor, channel_id: int):
        channel = ChannelService.get_by_id(
            cursor=cursor,
            channel_id=channel_id,
        )

        channels = ArtistService.get_channels()

        statistics = ArtistService.statistics(
            channel_id=channel_id,
        )

        return {
            "title": f"Artists - {channel.name}",
            "subtitle": f"Daftar artist milik {channel.name}",
            "page": "artists",
            "view": "list",
            "channel": channel,
            "channels": channels,
            "statistics": statistics,
        }