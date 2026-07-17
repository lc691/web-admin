"""
Sidebar Definition
==================

Single source of truth
for all navigation.
"""

from .schemas import SidebarItem


SIDEBAR = [

    SidebarItem(
        title="Dashboard",
        icon="home",
        url="/",
    ),

    SidebarItem(
        title="Music",
        icon="music",
        children=[

            SidebarItem(
                title="Channels",
                icon="broadcast",
                url="/channels",
            ),

            SidebarItem(
                title="Artists",
                icon="users",
                url="/artists",
            ),

            SidebarItem(
                title="Songs",
                icon="disc",
                url="/songs",
            ),

        ],
    ),

    SidebarItem(
        title="Shows",
        icon="device-tv",

        children=[

            SidebarItem(
                title="Shows",
                icon="device-tv",
                url="/shows",
            ),

            SidebarItem(
                title="Files",
                icon="folder",
                url="/files",
            ),

            SidebarItem(
                title="Platforms",
                icon="world",
                url="/platform",
            ),

        ],
    ),

    SidebarItem(
        title="Notes",
        icon="notes",

        children=[

            SidebarItem(
                title="Joki",
                icon="user",
                url="/joki",
            ),

            SidebarItem(
                title="Kloter",
                icon="stack",
                url="/kloter",
            ),

            SidebarItem(
                title="Catatan",
                icon="notebook",
                url="/catatan",
            ),

        ],
    ),

    SidebarItem(
        title="Users",
        icon="users",

        children=[

            SidebarItem(
                title="All Users",
                icon="users",
                url="/users",
            ),

            SidebarItem(
                title="VIP",
                icon="crown",
                url="/users?filter=vip",
                badge="VIP",
            ),

        ],
    ),

    SidebarItem(
        title="Security",
        icon="shield-lock",

        children=[

            SidebarItem(
                title="Trusted IP",
                icon="shield",
                url="/trusted_ips",
            ),

        ],
    ),

    SidebarItem(
        title="Settings",
        icon="settings",
        url="/settings",
    ),

]