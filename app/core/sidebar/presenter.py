"""
Sidebar Presenter
=================

Prepare sidebar navigation for templates.
"""

from __future__ import annotations

from copy import deepcopy

from .menu import SIDEBAR
from .schemas import SidebarItem


class SidebarPresenter:
    """Prepare sidebar items."""

    @staticmethod
    def build(path: str) -> list[SidebarItem]:
        """
        Build sidebar.

        Args:
            path:
                Current request path.

        Returns:
            Sidebar items ready for rendering.
        """

        items = deepcopy(SIDEBAR)

        for item in items:
            SidebarPresenter._mark(item, path)

        return items

    @staticmethod
    def _mark(
        item: SidebarItem,
        path: str,
    ) -> bool:
        """
        Mark active & expanded state.

        Returns
        -------
        bool
            True if this item or one of its children is active.
        """

        matched = False

        if item.url:

            if item.url == "/":
                matched = path == "/"

            else:
                matched = path.startswith(item.url)

        child_active = False

        for child in item.children:

            if SidebarPresenter._mark(child, path):
                child_active = True

        item.active = matched

        item.expanded = child_active

        return matched or child_active