import copy
import os
from typing import List, Union, Optional

import pandas as pd
import wntr


def contamination(
        wn: wntr.network.WaterNetworkModel,
        inj_nodes: Optional[List[Union[int, str]]] = None,
        duration: Optional[int] = 24 * 3600,
        timestep: Optional[int] = 3600,
        **kwargs: dict,
) -> pd.DataFrame:
    """Simulate the injection of contaminations in multiple nodes.

    The contaminant is injected at the beginning of the simulation.

    Args:
        wn: The WaterNetworkModel used in the simulations.
        inj_nodes: The list of nodes ids considered as injection points.
            If None, all the junctions are considered as injection points.
        duration: The simulation duration in seconds. By dafault, it is one day (86400 seconds).
        timestep: The timestep of the simulation in seconds. By dafault, it is one hour (3600 seconds).
        **kwargs: Additional arguments to pass to the Epanet simulator: \n
            - file_prefix (str): Default prefix is "temp". All files (.inp, .bin/.out, .hyd, .rpt) use this prefix. \n
            - use_hyd (bool): Will load hydraulics from ``file_prefix + '.hyd'`` or from file specified in
                `hydfile_name`. \n
            - save_hyd (bool): Will save hydraulics to ``file_prefix + '.hyd'``
                or to file specified in `hydfile_name`. \n
            - hydfile (str): Optionally specify a filename for the hydraulics file other than the `file_prefix`. \n
            - version (float): Optionally change the version of the EPANET toolkit libraries. Valid choices are
                either 2.2 (the default if no argument provided) or 2.0. \n
            - convergence_error (bool): If convergence_error is True, an error will be raised if the
                simulation does not converge. If convergence_error is False, partial results are returned,
                a warning will be issued, and results.error_code will be set to 0
                if the simulation does not converge. Default is False. \n

    Returns:
        A pandas Dataframe containing the contaminant trace (percentage) for each injection points in each node. \n
            The Dataframe has the following columns: \n
            - `time`: Simulation time in seconds. \n
            - `node`: Node of the water network to which the trace refers. \n
            - `<node_id1>`, ..., `<node_idN>`: Nodes of the water network where the contaminant has been injected.
    """
    wn = _set_config(copy.deepcopy(wn), duration=duration, timestep=timestep)
    sim = wntr.sim.EpanetSimulator(wn)
    wn.options.quality.parameter = "TRACE"
    # If no injection nodes is specified, use the entire list of junctions
    inj_nodes = wn.junction_name_list if inj_nodes is None else inj_nodes
    trace = []
    for i, node in enumerate(inj_nodes):
        wn.options.quality.trace_node = node
        sim_results = sim.run_sim(**kwargs)
        curr_trace = sim_results.node["quality"]
        curr_trace = curr_trace.stack()
        trace.append(curr_trace)
    trace = pd.DataFrame(trace).T.reset_index()
    trace.columns = ["time", "node"] + inj_nodes
    _clean_tmp(kwargs.get("file_prefix", "temp"))
    return trace


def water_demand(
        wn: wntr.network.WaterNetworkModel,
        duration: Optional[int] = 24 * 3600,
        timestep: Optional[int] = 3600,
        **kwargs: dict,
) -> pd.DataFrame:
    """Run a simulation to extract the demand at each node.

    Args:
        wn: The WaterNetworkModel used in the simulation.
        duration: The simulation duration in seconds. By dafault, it is one day (86400 seconds).
        timestep: The timestep of the simulation in seconds. By dafault, it is one hour (3600 seconds).
        **kwargs: Additional arguments to pass to the Epanet simulator: \n
            - file_prefix (str): Default prefix is "temp". All files (.inp, .bin/.out, .hyd, .rpt) use this prefix. \n
            - use_hyd (bool): Will load hydraulics from ``file_prefix + '.hyd'`` or from file specified in
                `hydfile_name`. \n
            - save_hyd (bool): Will save hydraulics to ``file_prefix + '.hyd'``
                or to file specified in `hydfile_name`. \n
            - hydfile (str): Optionally specify a filename for the hydraulics file other than the `file_prefix`. \n
            - version (float): Optionally change the version of the EPANET toolkit libraries. Valid choices are
                either 2.2 (the default if no argument provided) or 2.0. \n
            - convergence_error (bool): If convergence_error is True, an error will be raised if the
                simulation does not converge. If convergence_error is False, partial results are returned,
                a warning will be issued, and results.error_code will be set to 0
                if the simulation does not converge. Default is False. \n

    Returns:
        A pandas Dataframe with the demand at each node for each simulation timestep. \n
            The Dataframe has the following columns: \n
            - `time`: Simulation time in seconds. \n
            - `node`: Node of the water network. \n
            - `demand`: Demand at `node` in the simulation timestep identified by `time`.
    """
    wn = _set_config(copy.deepcopy(wn), duration=duration, timestep=timestep)
    sim = wntr.sim.EpanetSimulator(wn)
    sim_results = sim.run_sim(**kwargs)
    _clean_tmp(kwargs.get("file_prefix", "temp"))
    demand = sim_results.node["demand"].stack().reset_index()
    demand.columns = ["time", "node", "demand"]
    return demand


def _set_config(
        wn: wntr.network.WaterNetworkModel,
        duration: int = 24 * 3600,
        timestep: int = 3600
) -> wntr.network.WaterNetworkModel:
    r"""Set the time configuration and hydraulic options of the given water network.

    Args:
        wn: The WaterNetworkModel to set up.
        duration: The simulation duration in seconds. By dafault, it is one day (86400 seconds).
        timestep: The timestep of the simulation in seconds. By dafault, it is one hour (3600 seconds).

    Returns:
        The WaterNetworkModel configured accordingly to the given attributes.
    """
    wn.options.time.duration = duration
    wn.options.time.hydraulic_timestep = timestep
    wn.options.time.quality_timestep = timestep
    wn.options.time.report_timestep = timestep
    wn.options.hydraulic.demand_model = "DDA"
    wn.options.hydraulic.headloss = "H-W"
    return wn


def _clean_tmp(file_prefix: str = "temp") -> None:
    r"""Delete all simulation temp files (.inp, .bin/.out, .hyd, .rpt).

    Args:
        file_prefix: Default prefix is "temp". All simulation temp files (.inp, .bin/.out, .hyd, .rpt)
            use this prefix.
    """
    for extension in [".inp", ".bin", ".hyd", ".rpt"]:
        try:
            os.remove(file_prefix + extension)
        except OSError:
            continue
