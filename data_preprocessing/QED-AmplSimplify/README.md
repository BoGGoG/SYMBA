# Description

In this folder the script does a few things:
	- The data comes from `../../data-generation-marty/QED/out`. The amplitudes are in the `ampl` folder and the squared amplitudes in `sq_ampl_raw`. Every in/out multiplicity has its own folder, so `QED/out/ampl/2to3/` will have lots of files for the 2to3 processes. Since every process is in a separate file, we read in all amplitudes and their respective squared amplitudes.
	- Then the squared amplitudes are simplified using SYMPY
	- The amplitudes and squared amplitudes are exported to `data.nosync`, still split into the different in/out multiplicities.
