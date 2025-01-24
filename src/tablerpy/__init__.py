from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tablerpy.filled import FilledIcon
from tablerpy.outline import OutlineIcon

if TYPE_CHECKING:
    from importlib.abc import Traversable

if sys.version_info < (3, 10):
    import importlib_resources
else:
    import importlib.resources as importlib_resources

__all__ = ["FilledIcon", "OutlineIcon", "get_icon"]


def get_icon(icon: FilledIcon | OutlineIcon) -> Traversable:
    """Return ``icon`` path."""
    icon_dir: str
    if isinstance(icon, FilledIcon):
        icon_dir = "filled"
    elif isinstance(icon, OutlineIcon):
        icon_dir = "outline"
    else:  # pragma: no cover
        raise TypeError(type(icon))

    # https://github.com/python/importlib_resources/issues/257#issuecomment-1192863274
    return (
        importlib_resources.files("tablerpy.icons")
        .joinpath(icon_dir)
        .joinpath(icon.value)
    )
