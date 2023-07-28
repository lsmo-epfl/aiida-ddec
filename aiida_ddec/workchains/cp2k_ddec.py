# -*- coding: utf-8 -*-
"""DdecCp2kChargesWorkChain workchain of the AiiDA DDEC plugin"""

from __future__ import absolute_import

from aiida.common import AttributeDict
from aiida.engine import ToContext, WorkChain
from aiida.orm import Dict
from aiida.plugins import CalculationFactory, DataFactory, WorkflowFactory

from aiida_ddec.utils import extract_core_electrons, merge_Dict

Cp2kBaseWorkChain = WorkflowFactory("cp2k.base")  # pylint: disable=invalid-name
DdecCalculation = CalculationFactory("ddec")  # pylint: disable=invalid-name
CifData = DataFactory("core.cif")  # pylint: disable=invalid-name


class Cp2kDdecWorkChain(WorkChain):
    """A workchain that computes DDEC charges after a single-point
    DFT calculation using Cp2kBaseWorkChain
    """

    @classmethod
    def define(cls, spec):
        """Define workflow specification."""
        super(Cp2kDdecWorkChain, cls).define(spec)

        spec.expose_inputs(Cp2kBaseWorkChain, namespace="cp2k_base")
        spec.expose_inputs(DdecCalculation, namespace="ddec")

        spec.outline(cls.run_cp2k, cls.run_ddec, cls.return_results)

        spec.expose_outputs(Cp2kBaseWorkChain, include=["remote_folder"])
        spec.expose_outputs(DdecCalculation, include=["structure_ddec"])

        spec.exit_code(903, "ERROR_PARSING_CP2K_OUTPUT", "Error while parsing CP2K output")
        spec.exit_code(904, "ERROR_PARSING_DDEC_OUTPUT", "Error while parsing DDEC output")

    def run_cp2k(self):
        """Modify CP2K input to compute the charge density,
        and run the ENERGY calculation
        """

        param_modify = Dict(
            dict={
                "GLOBAL": {"RUN_TYPE": "ENERGY"},
                "FORCE_EVAL": {"DFT": {"PRINT": {"E_DENSITY_CUBE": {"_": "ON", "STRIDE": "1 1 1"}}}},
            }
        ).store()

        cp2k_base_inputs = AttributeDict(self.exposed_inputs(Cp2kBaseWorkChain, "cp2k_base"))
        cp2k_base_inputs["cp2k"]["parameters"] = merge_Dict(cp2k_base_inputs["cp2k"]["parameters"], param_modify)
        cp2k_base_inputs["metadata"]["label"] = "cp2k_energy"
        cp2k_base_inputs["metadata"]["call_link_label"] = "call_cp2k_energy"
        running = self.submit(Cp2kBaseWorkChain, **cp2k_base_inputs)
        self.report("Running Cp2kBaseWorkChain to compute the charge-density")
        return ToContext(cp2k_calc=running)

    def run_ddec(self):
        """Parse the CP2K ouputs (E_DENSITY_CUBE and core electrons),
        generate the DDEC input and submit DDEC calculation.
        """
        # extract number of core electrons from the cp2k output and prepare input
        try:
            core_e = extract_core_electrons(self.ctx.cp2k_calc.outputs.remote_folder)
            ddec_inputs = AttributeDict(self.exposed_inputs(DdecCalculation, "ddec"))
            ddec_inputs[
                "charge_density_folder"
            ] = self.ctx.cp2k_calc.outputs.remote_folder.creator.outputs.remote_folder
        except Exception as exc:  # pylint: disable=broad-except
            self.report(f'Encountered exception "{str(exc)}" while parsing CP2K output')
            return self.exit_codes.ERROR_PARSING_CP2K_OUTPUT  # pylint: disable=no-member

        ddec_inputs["parameters"] = merge_Dict(ddec_inputs["parameters"], core_e)
        ddec_inputs["metadata"]["call_link_label"] = "call_ddec_calc"

        # Create the calculation process and launch it
        running = self.submit(DdecCalculation, **ddec_inputs)
        self.report(f"Running DdecCalculation<{running.pk}> to compute point charges from the charge-density")
        return ToContext(ddec_calc=running)

    def return_results(self):
        """Return exposed outputs and print the pk of the CifData w/DDEC"""
        try:
            self.out_many(self.exposed_outputs(self.ctx.cp2k_calc, Cp2kBaseWorkChain))
            self.out_many(self.exposed_outputs(self.ctx.ddec_calc, DdecCalculation))
            self.report(f"DDEC charges computed: CifData<{self.outputs['structure_ddec'].pk}>")
        except KeyError:
            return self.exit_codes.ERROR_PARSING_DDEC_OUTPUT  # pylint: disable=no-member

        return 0
