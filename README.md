# aiida-ddec plugin

[![Build Status](https://travis-ci.org/yakutovicha/aiida-ddec.svg?branch=develop)](https://travis-ci.org/yakutovicha/aiida-ddec)
[![PyPI version](https://badge.fury.io/py/aiida-ddec.svg)](https://badge.fury.io/py/aiida-ddec)

A [DDEC](https://sourceforge.net/projects/ddec/files/) plugin for AiiDA.

## Installation

```shell
pip install git+ https://github.com/yakutovicha/aiida-ddec
```

### (development mode with code checking)

```shell
pip install -e .['pre-commit','testing']
pre-commit install
```

## Usage

Examples in the `examples` folder:

-   `cp2k_ddec.py`: workchain that run an ENERGY calculation in cp2k printing the
    electron density cube file, and compute the DDEC charges from that

-   `cp2kmultistage_ddec.py`: combines the CP2K Multistage workflow (e.g., to relax
    the structure) and the previous workchain, to get the DDEC charges of the
    relaxed structure

## License

MIT

## Contact

aliaksandr.yakutovich@epfl.ch
