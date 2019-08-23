# aiida-ddec plugin

AiiDA plugin for the DDEC code

# Installation

```shell
git clone https://github.com/yakutovicha/aiida-ddec
cd aiida-ddec
pip install -e .  # also installs aiida, if missing (but not postgres)
#pip install -e .[precommit,testing] # install extras for more features
verdi quicksetup  # better to set up a new profile
verdi calculation plugins  # should now show your calclulation plugins
```

# License

MIT

# Contact

aliaksandr.yakutovich@epfl.ch
