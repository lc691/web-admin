from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class SidebarItem:
    title: str
    icon: str
    url: str | None = None

    children: list["SidebarItem"] = field(default_factory=list)

    badge: str | None = None

    permission: str | None = None

    active: bool = False

    expanded: bool = False