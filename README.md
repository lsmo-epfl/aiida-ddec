[![Build Status](https://github.com/lsmo-epfl/aiida-ddec/workflows/ci/badge.svg)](https://github.com/lsmo-epfl/aiida-ddec/actions)
[![Coverage Status](https://codecov.io/gh/lsmo-epfl/aiida-ddec/branch/develop/graph/badge.svg)](https://codecov.io/gh/lsmo-epfl/aiida-ddec)
[![PyPI version](https://badge.fury.io/py/aiida-ddec.svg)](https://badge.fury.io/py/aiida-ddec)


# aiida-ddec plugin

A [DDEC](https://sourceforge.net/projects/ddec/files/) plugin for AiiDA.

## Installation

```shell
pip install aiida-ddec
```

## Usage

Examples in the `examples` folder:

-   `test_cp2k_ddec_h2o.py`: Run an ENERGY calculation, printing the
    electron density cube file, and compute the DDEC charges from that


### Run tests

```shell
git clone https://github.com/lsmo-epfl/aiida-ddec
cd aiida-ddec
pip install -e .['pre-commit','testing']
pytest
```

If you are changing the inputs of existing tests or need to regenerate test data, place an `.aiida-testing-config.yml` 
file in your repository that points to the required simulation codes:
```yaml
---
mock_code:
  # code-label: absolute path
  cp2k-7.1: /path/to/cp2k.sopt
  chargemol-09_26_2017: /path/to/Chargemol_09_02_2017_linux_serial
```

Note: You may also need to change the value of `DDEC_ATOMIC_DENSITIES_DIRECTORY` environment variable in 
`.github/workflows/ci.yml` in order for the CI tests to pass.

## License

MIT

## Contact

aliaksandr.yakutovich@epfl.ch
