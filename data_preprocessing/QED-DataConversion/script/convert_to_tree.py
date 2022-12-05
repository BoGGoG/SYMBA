"""
Convert the amplitudes and squared amplitudes from `data.nosync` to different formats.
- `nltk.Tree`: This is the base form
This happens parallelized
"""

from icecream import ic
import os
import sys
from tqdm import tqdm
from itertools import (takewhile,repeat)
import sympy as sp
from multiprocessing import Pool
import pickle


current = os.path.dirname(os.path.realpath(__file__))
parent_parent = os.path.dirname(os.path.dirname(current))
sys.path.append(parent_parent)
ic(os.listdir(parent_parent))

import sympy as sp
from converters.ampl2tree.source.ampl2tree import ampl_to_tree, raw_ampl_to_tree, raw_ampl_to_tree_nosplit
from converters.sp2tree.sp2tree import sympy_to_tree


def rawincount(filename):
    """count numer of lines in a file. 
    From https://stackoverflow.com/questions/845058/how-to-get-line-count-of-a-large-file-cheaply-in-python
    """
    f = open(filename, 'rb')
    bufgen = takewhile(lambda x: x, (f.raw.read(1024*1024) for _ in repeat(None)))
    return sum( buf.count(b'\n') for buf in bufgen )

def load_raw_amplitudes(filename, max_lines=-1):
    """
    Loading raw amplitudes from filename.
    
    Options:
        - `max_lines`: maximum number of lines to read
    """
    print("Loading amplitudes from "+ filename)
    if max_lines > 0:
        number_of_lines = max_lines
    else:
        number_of_lines = rawincount(filename)
        ic(number_of_lines)
    data = [0 for i in range(number_of_lines-1)]
    pbar = tqdm(total=number_of_lines)
    with open(filename) as f:
        line = f.readline()
        ctr = 0
        data[ctr] = line.replace("\n", "").split(";")
        while line:
            line = f.readline()
            if line != "":
                data[ctr] = line.replace("\n", "").split(";")
            pbar.update(1)
            ctr = ctr + 1
            if ctr >= number_of_lines:
                break
    pbar.close()
    return data


def load_squared_amplitudes(filename, max_lines=-1, n_cpu=4):
    """
    Loading squared amplitudes from filename and parsing into sympy.
    All squared amplitudes should be exportet from sympy and thus be readable
    without any preprocessing.

    Options:
        - `max_lines`: maximum number of lines to read

    Returns:
        list of squared amplitudes, each as a sympy expression
    """
    print("Loading squared amplitudes from "+ filename)
    if max_lines > 0:
        number_of_lines = max_lines
    else:
        number_of_lines = rawincount(filename)
        ic(number_of_lines)
    data = [0 for i in range(number_of_lines-1)]
    pbar = tqdm(total=number_of_lines)
    with open(filename) as f:
       line = f.readline()
       line_sp = sp.sympify(line.strip())
       ctr = 0
       data[ctr] = line_sp
       while line:
            line = f.readline()
            if line != "":
                line = line.strip()
                # line_sp = sp.sympify(line.strip())
                data[ctr] = line
            pbar.update(1)
            ctr = ctr + 1
            if ctr >= number_of_lines:
                break
    pbar.close()
    with Pool(n_cpu) as p:
        data = p.map(sp.sympify, data)
    return data

data_folder = "../../data.nosync/"
amplitudes_filename_start = "QED_amplitudes_TreeLevel_"
sqamplitudes_filename_start = "QED_sqamplitudes_TreeLevel_simplified_"
# processes = ["1to2", "2to1", "2to2", "2to3", "3to2"]
processes = ["1to2", "2to1", "2to2"]
max_lines = -1

amplitudes = []
sqamplitudes = []
ampl_trees = []
sqampl_trees = []
n_cpu = 4


for process in processes:
    ampl_f = data_folder + amplitudes_filename_start + process + ".txt"
    sqampl_f = data_folder + sqamplitudes_filename_start + process + ".txt"
    amplitudes_process = load_raw_amplitudes(ampl_f, max_lines=max_lines)
    sqamplitudes_process = load_squared_amplitudes(sqampl_f, max_lines=max_lines, n_cpu=n_cpu)
    amplitudes.append(amplitudes_process)
    sqamplitudes.append(sqamplitudes_process)
    with Pool(n_cpu) as p:
        ampl_trees_process = p.map(raw_ampl_to_tree_nosplit, amplitudes_process)
    ampl_trees.append(ampl_trees_process)

    with Pool(n_cpu) as p:
        sqampl_trees_process = p.map(sympy_to_tree, sqamplitudes_process)
    sqampl_trees.append(sqampl_trees_process)
    


with open("../../data.nosync/tree/QED_amplitudes_trees.pickle", "bw") as f:
    pickle.dump(ampl_trees, f)

with open("../../data.nosync/tree/QED_sqamplitudes_trees.pickle", "bw") as f:
    pickle.dump(sqampl_trees, f)
