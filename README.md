# RepEvol Simulator
This is the readme for the RepEvol simulator software.
This software was used to generate all data for the paper
_A House Divided: Cooperation, Polarization, and the Power of Reputation_.

## Dependencies and Requirements
The software is written in Python 3.
Aside from standard python packages coming with python, it requires the packages `numpy` and `matplotlib`.
It should work on any operating system that supports python 3 and these packages;
these packages are required by many other applications and python packages as well,
and are available for all well-known operating systems, such as Windows 11, Ubuntu Linux 23.04, variants of BSD and MacOS.
we have tested the software on Windows, Linux and MacOS Ventura 13.4.1.

## Downloading the software
Clone the repository to your local machine, using the command

```git clone [https://github.com/phillip-keldenich/reputation-simulator](https://github.com/phillip-keldenich/reputation-simulator)```

or an equivalent command in your git client.
Alternatively, download the repository as a zip file and unpack it.

## Installation
The software itself needs no installation and can be run directly from the repository directory.
To uninstall the software completely, simply delete the repository directory.

However, it requires Python 3 the python packages `numpy` and `matplotlib` to be installed.
In the following, we explain how to install these
on your system; if you are familiar with installing
python on your system, you can skip this section.
The installation process should take no more than a minute.

### Linux
Make sure you have a python 3 version installed on your system.
For example, if you are using Ubuntu, the package `python3` should be installed.
If not, you can install python using the package manager of your distribution.
For example, on Ubuntu, you can install python 3 using the command

```sudo apt install python3```.

For some distributions, the packages `numpy` and `matplotlib` are available from the package manager as well.
For example, on Ubuntu, you can install them using the command

```sudo apt install python3-numpy python3-matplotlib```.

If you do not want to or cannot use your package manager to install the dependencies,
but your python 3 version comes with the package manager `pip` (sometimes called `pip3`), a command-line tool to install python packages (which is the case for most python 3 installations, in particular on Linux and MacOS),
you can use it to install the dependencies (`numpy` and `matplotlib`) using one of the following commands:

```pip3 install numpy matplotlib```, or

```pip install numpy matplotlib```.

If you do not have `pip` installed, you can install it using the instructions on the [pip website](https://pip.pypa.io/en/stable/installing/).

### MacOS
Normally, MacOS comes with a pre-installed version of python3. If you would rather not use this version, you can use HomeBrew to install a newer version of python3. You can find instructions on how to install HomeBrew on the [HomeBrew website](https://brew.sh/). Once you have installed python3, you can install the dependencies using `pip` (see the instructions for Linux above).

### Other operating systems
If you are using another operating system, you can find instructions on how to install python 3 and the dependencies on the [python website](https://www.python.org/downloads/). In particular for Windows, you may also want to check out the [Anaconda distribution](https://www.anaconda.com/products/individual), which comes with python 3 and many useful packages pre-installed (including our dependencies).

## Running the software
The software is a simulator that can be run from the command line.
In the repository directory, run the command

```python3 main.py```.

Running the software should open a window showing the current state of the simulation (updated, by default, once every 1000 steps); it may take some time for the window contents to update.

Simultaneously, the simulator produces a directory
containing the data produced by the simulation.
Some parts of the data (the distribution of strategies, the reputation, ...) are saved as bitmaps in `.png` format, with one pixel per cell of the grid environment; the configuration of the simulation is stored as a text file and statistics are stored in `.csv` files.

The software takes a number of command-line arguments.
A full list of arguments together with a description can be obtained by running

```python3 main.py --help```.

### Important Command Line Arguments
In the following, we give a brief description of a few of the most important arguments.

Perhaps the most important parameter is the argument `-I` (or `--initial-strategies`), which controls how the initial state of the environment is generated, i.e., which strategy is assigned to each cell.
There is a whole host of possible values for this argument, choosing between different scenarios to be simulated.
We discuss a few possible values for this flag further below, in the examples section.

The argument `-U` controls the exploitation surplus parameter $U$; its default value is $0.6$.

The argument `-M` controls the number of steps to simulate; its default value is $10000001$.

The argument `-N` controls the side length $N$ of the lattice; its default value is $N = 80$. The total number of cells is $N^2$.

The argument `-r` controls how many iterations are between two _snapshots_ of the simulation, i.e., how often the state of the simulation is saved to disk and how often the GUI is updated; its default value is $1000$.

The arguments `--hell-prob` and `--heaven-prob` control the per-duel probability of contact with the global authorities (called `evil` and `virtue` in the paper).

## Examples
In the following, we give a few examples of how to run the software.



## License
The software and its documentation are available under the MIT open source license.
