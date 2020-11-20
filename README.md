[![Build Status](https://github.com/lsmo-epfl/aiida-ddec/workflows/ci/badge.svg)](https://github.com/lsmo-epfl/aiida-ddec/actions)
[![Coverage Status](https://codecov.io/gh/lsmo-epfl/aiida-ddec/branch/develop/graph/badge.svg)](https://codecov.io/gh/lsmo-epfl/aiida-ddec)
[![PyPI version](https://badge.fury.io/py/aiida-ddec.svg)](https://badge.fury.io/py/aiida-ddec)


# aiida-ddec plugin

A [DDEC](https://sourceforge.net/projects/ddec/files/) plugin for AiiDA.

## Installation

```shell
pip install aiida-ddec
```

### (development mode with code checking)

```shell
git clone https://github.com/lsmo-epfl/aiida-ddec
cd aiida-ddec
pip install -e .['pre-commit','testing']
pre-commit install
```

## Usage

Examples in the `examples` folder:

-   `cp2k_ddec.py`: workchain that run an ENERGY calculation in cp2k printing the
    electron density cube file, and compute the DDEC charges from that

## License

MIT

## Contact

aliaksandr.yakutovich@epfl.ch
