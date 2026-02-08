> [!WARNING]  
> tablerpy is now **archived** and will no longer receive updates.
> As of release `3.29.0`, Tabler Icons no longer provides zip archives in its releases
> See https://github.com/tabler/tabler-icons/issues/1371.

# tablerpy

[![PyPI - Version](https://img.shields.io/pypi/v/tablerpy?logo=pypi&label=PyPI&logoColor=white)](https://pypi.org/project/tablerpy/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tablerpy?logo=python&label=Python&logoColor=white)](https://pypi.org/project/tablerpy/)
[![License](https://img.shields.io/github/license/tahv/tablerpy?label=License)](https://github.com/tahv/tablerpy/blob/main/LICENSE)
[![CI - Tests](https://img.shields.io/github/actions/workflow/status/tahv/tablerpy/tests.yml?logo=github&logoColor=white&label=Tests)](https://github.com/tahv/tablerpy/actions/workflows/tests.yml)

[Tabler Icons](https://github.com/tabler/tabler-icons) library for Python.

> _Tabler Icons is a set of free MIT-licensed high-quality SVG icons.
> Each icon is designed on a 24x24 grid and a 2px stroke._
>
> _**[Browse at tabler.io/icons →](https://tabler.io/icons)**_

## Installation

```bash
pip install tablerpy
```

## Usage

The function `tablerpy.get_icon` accepts a `OutlineIcon | FilledIcon`
and return a `Traversable` (`pathlib.Path`) to the icon `.svg` file.

```python
from tablerpy import OutlineIcon, FilledIcon, get_icon

outline_icon_path = get_icon(OutlineIcon.BRAND_GITHUB)
filled_icon_path = get_icon(FilledIcon.BRAND_GITHUB)
```

Icon names match those on _tabler.io/icons_,
except they are uppercased and hyphens `-` are replaced with underscores `_`.
For example, [`brand-github`](https://tabler.io/icons/icon/brand-github)
becomes `BRAND_GITHUB`.

## Contributing

### Generating icons and enums

To keep up with Tabler Icons releases,
most of this package is generated using a script.

```console
$ python scripts/generator.py --help
usage: generator.py [-h] --version VERSION [--package PACKAGE]

Download Tabler Icons release from github.com/tabler/tabler-icons and generate Python files.

options:
  -h, --help         show this help message and exit
  --version VERSION  Tabler Icons release version
  --package PACKAGE  Target package directory
```

For instance, to generate files from Tabler Icons
[Release 3.29.0](https://github.com/tabler/tabler-icons/releases/tag/v3.29.0):

```bash
python scripts/generator.py --version 3.29.0
```

## Acknowledgements

- [pytablericons](https://github.com/niklashenning/pytablericons)
  for providing inspiration.
  The package include features for using icons with `Pillow`, `PyQt` or `PySide`.
