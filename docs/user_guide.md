WaCo is built on top of [WNTR](https://github.com/USEPA/WNTR), that is a wrapper of [EPANET](https://github.com/USEPA/EPANET2.2).

```python
import waco
import wntr
```

## Read the water network
WaCo uses the `WaterNetworkModel` provided by [WNTR](https://github.com/USEPA/WNTR) to manage EPANET networks (with `.inp` extension).
Some example networks are provided in the `examples/networks` directory.

```python
# Read and plot the water network using wntr
wn = wntr.network.WaterNetworkModel("examples/networks/Anytown.inp")
wntr.graphics.plot_network(wn);
```

## Run simulations to analyze the diffusion of a contaminant
WaCo allows to simply analyze the diffusion of a contaminant in the network, considering different injection points, by using the `waco.sim.contamination` function. This function runs a [water quality simulation](https://usepa.github.io/WNTR/waterquality.html) for each injection points specified by the parameter `inj_nodes`; by default, all the junctions of the network are considered as injection points. For each simulation, the varying contaminant concentration (percentage) is tracked across the entire network.

```python
trace = waco.sim.contamination(wn=wn)
```

This results in a dataframe in which, each column represents an injection node (except for the "time" and "node" columns that are row ids) and each row represents the contaminant concentration in a node of the network at a specific simulation time for all the injection nodes.

| **time** | **node** | **1**      | **2**      | **...** | **21**    | **22**    |
|----------|----------|------------|------------|---------|-----------|-----------|
| 25200    | 6        | 32.408066  | 14.922180  | ...     | 34.149334 | 25.908562 |
| 25200    | 7        | 32.408066  | 14.922180  | ...     | 34.149334 | 25.908562 |
| 25200    | 8        | 32.408066  | 14.922180  | ...     | 34.149334 | 25.908562 |
| 25200    | 9        | 8.921225   | 0.914897   | ...     | 8.870847  | 65.627129 |
| 25200    | 10       | 12.547630  | 0.000000   | ...     | 0.000000  | 84.482864 |

Let's print some details:

```python
print(f"Columns: {list(trace.columns)}")
print(f"Simulation timesteps: {trace['time'].unique().tolist()}")
print(f"Water network nodes: {trace['node'].unique().tolist()}")
```

The output is:

```shell
Columns: ['time', 'node', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22']
Simulation timesteps: [0, 3600, 7200, 10800, 14400, 18000, 21600, 25200, 28800, 32400, 36000, 39600, 43200, 46800, 50400, 54000, 57600, 61200, 64800, 68400, 72000, 75600, 79200, 82800, 86400]
Water network nodes: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '40', '41', '42']
```

It is possible to change the injection nodes as well as the simulation duration and timestep (in seconds). 
In the following example, the injection points are limited to the nodes with ids `1`, `2`, `21` and `22`, the simulation duration is set to 5 hours and data are registered every 15 minutes.

```python
trace = waco.sim.contamination(wn=wn,
                               inj_nodes=["1", "2", "21", "22"],
                               duration=5 * 3600,  # 5 hours
                               timestep=15 * 60)   # 15 minutes
```

The result looks like the following:

| **time** | **node** |   **1**   | **2** | **21** | **22** |
|----------|:--------:|:---------:|-------|--------|--------|
| 0        |    1     |   100.0   | 0.0   | 0.0    | 0.0    |
| 0        |    2     |    0.0    | 100.0 | 0.0    | 0.0    |
| ...      |   ...    |    ...    | ...   | ...    | ...    |
| 18000    |    16    | 55.391529 | 0.0   | 9.2    | 21.9   |
| 18000    |    17    | 12.067455 | 0.0   | 0.0    | 85.5   |

## Compute the Detection Times
A useful insight is how long it takes to detect the contaminant at a specific location of the network (e.g., node). Considering that the contaminant is detected at a node when it exceeds a concentration percentage (`sensibility`), the function `waco.analyzer.detection_time` can be used to compute the detection times.

```python
det_time = waco.analyzer.detection_time(trace, sensibility=5)
```

The result is a Dataframe with the time the contaminant concentration reach the specified threshold (i.e., `sensibility`) in `node` when injected in `inj_node`.

| **node** | **inj_node** | **time** |
|----------|:------------:|:--------:|
| 1        |      1       |    0     |
| 1        |      2       |  18900   |
| ...      |     ...      |   ...    |
| 9        |      21      |  18900   |
| 9        |      22      |   5400   |

## Compute the Volumes of Contaminated Water
Another information that can be extracted from the simulations is the volume of contaminated water consumed prior to detection. First, the water demands at each node have to be computed using the `waco.sim.demand` function. Then, the `waco.analyzer.contaminated_volume` function can be used to compute the volume of contaminated water.

!!! note
    The same time granularity (`duration` and `timestep`) is required for both the `demand` and `trace` to be able to compute the volume of contaminated water.

```python
demand = waco.sim.water_demand(wn, 
                               duration=5 * 3600, # 5 hours
                               timestep=15 * 60)  # 15 minutes
contam_vol = waco.analyzer.contaminated_volume(trace=trace,
                                               det_time=det_time,
                                               demand=demand)
```

The demands are returned as a Dataframe with the water demand at each `node` and `time`.

| **time** | **node** | **demand** |
|----------|:--------:|:----------:|
| 0        |    1     |  0.031545  |
| 0        |    2     |  0.012618  |
| ...      |   ...    |    ...     |
| 18000    |    18    |  0.031545  |
| 18000    |    19    |  0.063090  |

Then, the volume of contaminated water is returned as a Dataframe with a structure similar to the detection times.

| **node** | **inj_node** | **volume** |
|----------|:------------:|:----------:|
| 1        |      1       |  0.031545  |
| 1        |      2       |  0.116008  |
| ...      |     ...      |    ...     |
| 9        |      21      |  0.118453  |
| 9        |      22      |  0.102254  |
