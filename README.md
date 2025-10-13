# Repository containing serial python drivers to control the experiments for the QUBITEKK quantum optics lab

Find the three different drivers in this repo

- motor driver for adjustable optical delay line
- digital photon coincidence counter
- bi-photon souce crystal temperature controller

# Student jupyter notebook

Students of ELEC4605 will have to run some experiments that are very time consuming to do manually.

The given ipynb contains scripts for labs 3-5 to automate those measurements.

# Installation

Navigate into this folder and run in your python environment:
```bash
pip install -e .
```

Alternatively using uv as environemnt manager:

```bash
uv sync
```

and then activate the just created environment:


```
.venv\Scripts\activate.ps1 (WINDOWS)
source .venv/bin/activate (LINUX)
```
