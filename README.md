# aiida-ddec plugin

=======
[![Build Status](https://dev.azure.com/shoppingkj/aiida_ddec/_apis/build/status/kjappelbaum.aiida-ddec?branchName=aiida1)](https://dev.azure.com/shoppingkj/aiida_ddec/_build/latest?definitionId=1&branchName=aiida1)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/85523701e2f943d0b285516b9bc03c5c)](https://www.codacy.com/app/kjappelbaum/aiida-ddec?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=kjappelbaum/aiida-ddec&amp;utm_campaign=Badge_Grade)

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
