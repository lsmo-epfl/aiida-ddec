# aiida-ddec plugin

=======
[![Build Status](https://dev.azure.com/shoppingkj/aiida_ddec/_apis/build/status/kjappelbaum.aiida-ddec?branchName=aiida1)](https://dev.azure.com/shoppingkj/aiida_ddec/_build/latest?definitionId=1&branchName=aiida1)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/85523701e2f943d0b285516b9bc03c5c)](https://www.codacy.com/app/kjappelbaum/aiida-ddec?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=kjappelbaum/aiida-ddec&amp;utm_campaign=Badge_Grade)

A [DDEC](https://sourceforge.net/projects/ddec/files/) plugin for AiiDA.

## Installation

```shell
pip install git+ https://github.com/yakutovicha/aiida-ddec
```

<<<<<<< HEAD
# License
=======
## Usage

Examples in the `examples` folder:

-   `cli.py`: DDEC calculation starting from a old CP2K calculation

-   `cp2k_relax_charges.py`: runs a workchain that first relaxes a structure using
     multistage CP2K workchains and then performs a DDEC calculation on the relaxed
    structure

-   `cp2k_sp_charges.py`: runs a workchain that first runs a CP2K single point
    calculation and then performs a DDEC calculation on the charge desnity

## License
>>>>>>> 2e440f7... [WIP] migration to AiiDA 1.0

MIT

## Contact

aliaksandr.yakutovich@epfl.ch
