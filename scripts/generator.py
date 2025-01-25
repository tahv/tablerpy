# /// script
# dependencies = []
# ///
from __future__ import annotations

import argparse
import logging
import shutil
import tempfile
import time
import urllib.request
import zipfile
from collections import deque
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Iterator, Sequence
from urllib.error import HTTPError

if TYPE_CHECKING:
    from _typeshed import StrPath


logger = logging.getLogger("tablerpy-generator")


def main(args: Sequence[str] | None = None) -> None:
    """Command line entry-point."""
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(name)s :: %(message)s",
        datefmt="%H:%M:%S",
        level=logging.DEBUG,
    )

    namespace = parse_args(args)
    version: str = namespace.version
    package: Path = namespace.package
    packs = [
        IconPack(
            icons_archive_dir=Path("svg/filled"),
            icons_extract_dir=package / "icons" / "filled",
            enum_name="FilledIcon",
            enum_py=package / "filled.py",
        ),
        IconPack(
            icons_archive_dir=Path("svg/outline"),
            icons_extract_dir=package / "icons" / "outline",
            enum_name="OutlineIcon",
            enum_py=package / "outline.py",
        ),
    ]

    download_tabler_icons(version=version, packs=packs)

    for pack in packs:
        logger.info("Writing enum file '%s'", pack.enum_py)
        pack.enum_py.parent.mkdir(parents=True, exist_ok=True)
        with pack.enum_py.open("wt") as f:
            f.write(f"import enum\n\n\nclass {pack.enum_name}(enum.Enum):\n")
            for svg in sorted(pack.icons_extract_dir.glob("*.svg")):
                key = svg.stem.upper().replace("-", "_")
                value = svg.name
                f.write(f'    {key} = "{value}"\n')


def parse_args(args: Sequence[str] | None) -> argparse.Namespace:  # noqa: D103
    parser = argparse.ArgumentParser(
        description=(
            "Download Tabler Icons release from github.com/tabler/tabler-icons "
            "and generate Python files."
        ),
    )
    parser.add_argument(
        "--version",
        required=True,
        help="Tabler Icons release version",
    )
    parser.add_argument(
        "--package",
        type=Path,
        default=Path(__file__).parent.parent / "src" / "tablerpy",
        help="Target package directory",
    )
    return parser.parse_args(args)


class TagNotFoundError(Exception):
    """Raised when a tag is requested but is not available."""


@dataclass(frozen=True)
class IconPack:
    """Icons pack information."""

    icons_archive_dir: Path
    """Relative path to icon directory in archive."""

    icons_extract_dir: Path
    """Extraction destination directory."""

    enum_name: str
    """Class name for generated `enum.Enum`."""

    enum_py: Path
    """Python file to write generated enum."""


def download_tabler_icons(version: str, packs: list[IconPack]) -> None:
    """Download tabler-icons ``version`` and extract ``packs``."""
    github_api = "https://github.com/{owner}/{repo}/releases/download/{tag}/{asset}"
    url = github_api.format(
        owner="tabler",
        repo="tabler-icons",
        tag=f"v{version}",
        asset=f"tabler-icons-{version}.zip",
    )

    with tempfile.TemporaryDirectory(prefix="tabler-") as tmpdir:
        try:
            archive = download(
                url=url,
                directory=tmpdir,
                filename="tabler-icons.zip",
                overwrite=False,
            )
        except HTTPError as exc:
            if exc.code == 404:  # noqa: PLR2004
                raise TagNotFoundError(version) from exc
            raise

        unzip(archive=archive, directory=tmpdir, overwrite=True)

        for pack in packs:
            src = Path(tmpdir) / pack.icons_archive_dir
            dst = pack.icons_extract_dir

            if dst.exists():
                shutil.rmtree(dst)

            logger.info("Moving '%s' to '%s'", src, dst)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(src, dst)


def download(
    url: str,
    directory: StrPath,
    filename: str | None = None,
    *,
    overwrite: bool = True,
    progression: Callable[[int, int], None] | None = None,
) -> Path:
    """Download file at ``url`` to ``directory``.

    Args:
        url: File to download.
        directory: Destination directory.
        filename: Optional name for downloaded file. Default to name from url.
        overwrite: Overwrite existing file. Default to `True`.
        progression: Optional callback for progression report.
            Callback takes 2 `int` arguments for ``current`` and ``total``
            downloaded bytes.

    Raises:
        FileExistsError: File already exists. Only raised if ``overwrite`` is `True`.

    Returns:
        Path to downloaded file.
    """
    filename = filename or url.split("/")[-1]
    filepath = Path(directory) / filename

    if not overwrite and filepath.exists():
        raise FileExistsError(filepath)

    iterator = _download_iterator(url, filepath)
    if progression:
        for current, total in iterator:
            progression(current, total)
    else:
        deque(iterator, maxlen=0)  # consume iterator

    return filepath


def _download_iterator(url: str, filepath: Path) -> Iterator[tuple[int, int]]:
    chunk_size = 1024 * 32

    logger.debug("Downloading '%s'", url)
    start_time = time.time()

    with urllib.request.urlopen(url) as response, filepath.open("wb") as file:  # noqa: S310
        # TODO: check status
        total_bytes = int(response.headers.get("Content-Length", 0))
        downloaded_bytes = 0

        for data in iter(partial(response.read, chunk_size), b""):
            file.write(data)
            downloaded_bytes += len(data)
            yield (downloaded_bytes, total_bytes)

    elapsed_time = time.time() - start_time
    logger.debug("Downloaded '%s' in %.2f seconds", filepath.name, elapsed_time)


def unzip(
    archive: StrPath,
    directory: StrPath,
    *,
    key: Callable[[zipfile.ZipInfo], bool] | None = None,
    overwrite: bool = True,
    progression: Callable[[int, int], None] | None = None,
) -> Path:
    """Extract the content of ``archive`` archive to ``destination``.

    Args:
        archive: Zip archive to extract.
        directory: Destination directory.
        key: Optional filtering function.
            Takes one argument of type `zipfile.ZipInfo` and must return a bool.
        overwrite: Overwrite existing ``directory``. Default to `True`.
        progression: Optional callback for progression report.
            Callback takes 2 `int` arguments for ``current`` and ``total``
            extracted bytes.

    Raises:
        FileExistsError: ``directory`` already exists.
            Only raised if ``overwrite`` is `True`.

    Return:
        Path to ``directory``.
    """
    destination = Path(directory)
    if not overwrite and destination.exists():
        raise FileExistsError(destination)

    iterator = _unzip_iterator(archive, str(destination), key)
    if progression:
        for current, total in iterator:
            progression(current, total)
    else:
        deque(iterator, maxlen=0)  # consume iterator

    return destination


def _unzip_iterator(
    zip_path: StrPath,
    destination: StrPath,
    key: Callable[[zipfile.ZipInfo], bool] | None = None,
) -> Iterator[tuple[int, int]]:
    logger.info("Extracting '%s'", zip_path)
    start_time = time.time()

    with zipfile.ZipFile(zip_path) as openzip:
        content = [info for info in openzip.infolist() if not key or key(info)]
        total_bytes = sum(zinfo.file_size for zinfo in content)
        extracted_bytes = 0

        for zip_info in content:
            openzip.extract(zip_info.filename, destination)
            extracted_bytes += zip_info.file_size
            yield (extracted_bytes, total_bytes)

    elapsed_time = time.time() - start_time
    logger.debug(
        "Extracted to '%s' in %.2f seconds",
        Path(destination).name,
        elapsed_time,
    )


if __name__ == "__main__":
    main()
