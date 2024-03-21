<img width="550" src="https://raw.githubusercontent.com/andreaponti5/waco/1051a60fe33bb7cf123186b926f503dc50e0ca0d/docs/img/logo_title.svg" alt="WaCo Logo" title="WaCo">
<hr />

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

WaCo is a library for simulating contaminations in water networks built on-top of the [WNTR](https://github.com/USEPA/WNTR) library.

# Installation
The only requirement is the [WNTR](https://github.com/USEPA/WNTR) library that is used for the hydraulic simulations:

* Python >= 3.9
* wntr >= 1.1.0

The latest release of WaCo can be easily installed via `pip`.

```shell
pip install waco
```

You can also install the latest developement version directly from GitHub.

```shell
pip install --upgrade git+https://github.com/andreaponti5/waco
```

## Getting Started
WaCo is composed by two modules:

* `sim`: contains the functionalities to perform hydraulic simulations for extracting the demands and the contaminant diffusion in water networks. It mainly acts as a wrapper around the WNTR library.
* `analyzer`: contains the functionalities to extract the detection times and the volumes of contaminated water from the simulations.

> **Note:** Refer to the [API Reference]() for more details about the two modules.

To extract the detection times you need to simulate the diffusion of contaminant with the `sim` and then use the `analyzer` module.

```python
import waco
import wntr

wn = wntr.network.WaterNetworkModel("examples/networks/Anytown.inp")
trace = waco.sim.contamination(wn=wn)
det_time = waco.analyzer.detection_time(trace)
```

The detection times are returned in a Dataframe containing the time when the contaminant exceeds a given threshold in a node considering a specific injection point.

| **node** | **inj_node** | **time** |
|----------|:------------:|:--------:|
| 1        |      1       |    0     |
| 1        |      2       |  18900   |
| ...      |     ...      |   ...    |
| 9        |      21      |  18900   |
| 9        |      22      |   5400   |

To extract the volume of contaminated water prior detection you also need to compute the demand at each node using the `sim` module.

```python
demand = waco.sim.water_demand(wn)
contam_vol = waco.analyzer.contaminated_volume(trace=trace,
                                               det_time=det_time,
                                               demand=demand)
```

The volumes are returned in a Dataframe containing the volume of contaminated water prior detection in each node considering a specific injection point.

| **node** | **inj_node** | **volume** |
|----------|:------------:|:----------:|
| 1        |      1       |  0.031545  |
| 1        |      2       |  0.116008  |
| ...      |     ...      |    ...     |
| 9        |      21      |  0.118453  |
| 9        |      22      |  0.102254  |
