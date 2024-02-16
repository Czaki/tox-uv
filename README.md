# tox-uv

[![PyPI - Version](https://img.shields.io/pypi/v/tox-uv.svg)](https://pypi.org/project/tox-uv)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tox-uv.svg)](https://pypi.org/project/tox-uv)

-----

**Table of Contents**

- [Installation](#installation)
- [License](#license)

## Usage

```console
$ tox run -e env_spec --runner uv-virtualenv
```

Based on experiments there are problems with using `uv` to install sdist from a path.  So I suggest configuring 
tox to use the wheel for package installation.

```ini

[testenv]
package = wheel
```


## Installation

```console
pip install tox-uv
```

## License

`tox-uv` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
