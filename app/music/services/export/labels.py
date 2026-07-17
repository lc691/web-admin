"""
Export Group Labels
===================

Group label untuk formatter export.
"""

from __future__ import annotations

# ==========================================================
# GROUP LABELS
# ==========================================================

GROUP_LABELS: dict[int, str] = {
    1: "AMR 1",
    2: "AMR 2",
    3: "AMR 3",
    4: "AMR 4",
    # 40 LAGU
    5: "MCL 1",
    6: "MCL 2",
    7: "MCL 3",
    8: "MCL 4",
    # 80 LAGU
    9: "FKR 1",
    10: "FKR 2",
    11: "FKR 3",
    12: "FKR 4",
    # 120 LAGU
    13: "ZAM 1",
    14: "ZAM 2",
    15: "ZAM 3",
    16: "ZAM 4",
    # 160 LAGU
    17: "SPX 1",
    18: "SPX 2",
    # 180 LAGU
}


# ==========================================================
# GROUP LABEL
# ==========================================================


def get_group_label(
    group: int,
) -> str:
    """
    Return group label.

    Unknown groups fall back to
    "GROUP <number>".
    """

    return GROUP_LABELS.get(
        group,
        f"GROUP {group}",
    )


# ==========================================================
# GROUP NUMBER
# ==========================================================


def get_group_number(
    index: int,
    *,
    group_size: int = 10,
) -> int:
    """
    Return group number based on item index.

    Example

        group_size = 10

        1..10   -> 1
        11..20  -> 2
        21..30  -> 3
    """

    return ((index - 1) // group_size) + 1


# ==========================================================
# IS GROUP END
# ==========================================================


def is_group_end(
    index: int,
    *,
    group_size: int = 10,
) -> bool:
    """
    Return True if current index is
    the last item of a group.
    """

    return index % group_size == 0


# ==========================================================
# BUILD GROUP SEPARATOR
# ==========================================================


def build_group_separator(
    group: int,
) -> str:
    """
    Build separator text.

    Example

        NAMA ABSEN : AMR 1
        =================
    """

    label = get_group_label(group)

    return (
        f"NAMA ABSEN : {label}\n"
        "================="
    )