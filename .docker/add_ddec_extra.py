"""Add the required extra to the DDEC code."""

from aiida import orm

ddec_code = orm.load_code("ddec@localhost")
ddec_code.base.extras.set("DDEC_ATOMIC_DENSITIES_DIRECTORY", "/opt/code/chargemol_09_26_2017/atomic_densities")
