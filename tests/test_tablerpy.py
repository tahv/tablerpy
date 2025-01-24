from __future__ import annotations

from pathlib import Path

import pytest

from tablerpy import FilledIcon, OutlineIcon, get_icon


@pytest.mark.parametrize("icon", [FilledIcon.BRAND_GITHUB, OutlineIcon.BRAND_GITHUB])
def test_get_icon(icon: FilledIcon | OutlineIcon) -> None:
    icon_path = get_icon(icon)
    assert isinstance(icon_path, Path)
    assert icon_path.exists()
