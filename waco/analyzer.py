import numpy as np
import pandas as pd


def detection_time(
        trace: pd.DataFrame,
        sensibility: float = 1,
        non_detection_value: float = None,
) -> pd.DataFrame:
    """Compute, for each pair (node, injection node), the time contaminant needs to reach a concentration greater
    than `sensibility` in `node` if injected in `injection_node`.

    Args:
        trace: A pandas Dataframe containing the contaminant trace (percentage) for
            each injection points in each node. \n
            The Dataframe has the following columns: \n
            - `time`: Simulation time in seconds. \n
            - `node`: Node of the water network to which the trace refers. \n
            - `<node_id1>`, ..., `<node_idN>`: Nodes of the water network where the contaminant has been injected. \n
            This Dataframe can be obtained calling waco.sim.contamination.
        sensibility: The concentration (percentage) to consider a contaminant detected.
        non_detection_value: The value to use if the concentration of contaminat in a node does
            not exceed `sensibility` in the simulation horizon.

    Returns:
        A pandas Dataframe with the detection times for each pair (node, injection_node). \n
            The Dataframe has the following columns: \n
            - `node`: The "observer" node of the water network. \n
            - `inj_node`: The node of the water network where the contaminant has been injected. \n
            - `time`: The first simulation timestep when the contaminant concentration in `node` exceeds `sensibility`,
                when the contaminant has been injected in `inj_node`. \n
    """
    if non_detection_value is None:
        times = sorted(trace["time"].unique())
        non_detection_value = times[-1] + (times[-1] - times[-2])

    def first_T_greater_than(series):
        filtered_series = series[series > sensibility]
        return trace.loc[filtered_series.index[0], "time"] if not filtered_series.empty else None

    det_time = trace.groupby("node").agg(
        {col: first_T_greater_than for col in trace.columns
         if col not in ["time", "node"]}
    )
    det_time = det_time.fillna(non_detection_value).stack().reset_index()
    det_time.columns = ["node", "inj_node", "time"]
    return det_time


def contaminated_volume(
        trace: pd.DataFrame,
        demand: pd.DataFrame,
        det_time: pd.DataFrame,
) -> pd.DataFrame:
    """Compute, for each pair (node, injection node), the volume of contaminated water consumed prior to detection.

    Args:
        trace: A pandas Dataframe containing the contaminant trace (percentage) for
            each injection points in each node. \n
            The Dataframe has the following columns: \n
            - `time`: Simulation time in seconds. \n
            - `node`: Node of the water network to which the trace refers. \n
            - `<node_id1>`, ..., `<node_idN>`: Nodes of the water network where the contaminant has been injected. \n
            This Dataframe can be obtained calling `waco.sim.contamination`.
        demand: A pandas Dataframe with the demand at each node for each simulation timestep. \n
            The Dataframe has to have the following columns: \n
            - `time`: Simulation time in seconds. \n
            - `node`: Node of the water network. \n
            - `demand`: Demand at `node` in the simulation timestep identified by `time`. \n
            This Dataframe can be obtained calling waco.sim.demand.
        det_time: A pandas Dataframe with the detection times for each pair (node, injection_node). \n
            The Dataframe has to have the following columns: \n
            - `node`: The "observer" node of the water network. \n
            - `inj_node`: The node of the water network where the contaminant has been injected. \n
            - `time`: The first simulation timestep when the contaminant concentration in `node` exceeds `sensibility`,
                when the contaminant has been injected in `inj_node`. \n
            This Dataframe can be obtained calling waco.analyzer.contaminated_volume.

    Returns:
        A pandas Dataframe with the volume of contaminated water consumed prior detection for each pair
            (node, injection_node). \n
            The Dataframe has the following columns: \n
                - `node`: The "observer" node of the water network. \n
                - `inj_node`: The node of the water network where the contaminant has been injected. \n
                - `volume`: The contaminated water consumed prior detection.
    """
    max_sim_time = trace["time"].max()
    det_time["time"] = det_time["time"].astype(int)
    scenario_names = list(trace.columns)
    scenario_names.remove("time")
    scenario_names.remove("node")
    # Compute the volume of contaminated water consumed in the different scenarios for each simulation timestep
    contam_vol = trace[scenario_names].mul(0.01 * demand["demand"], axis=0)
    contam_vol["time"] = trace["time"]
    contam_vol = contam_vol.groupby(["time"]).sum().stack()
    # Compute the volume of contaminated water consumed prior detection
    idxs = det_time[["time", "inj_node"]].to_numpy()
    idxs[np.where(idxs[:, 0] > max_sim_time), 0] = max_sim_time
    contam_vol = contam_vol[pd.MultiIndex.from_tuples(idxs.tolist())]
    contam_vol = pd.DataFrame({"node": det_time["node"].tolist(),
                               "inj_node": det_time["inj_node"].tolist(),
                               "volume": contam_vol.tolist()})
    return contam_vol
