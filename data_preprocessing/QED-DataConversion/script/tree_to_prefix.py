import pickle
from nltk import Tree
from icecream import ic
import sys
import os
import sympy as sp
from multiprocessing import Pool

current = os.path.dirname(os.path.realpath(__file__))
parent_parent = os.path.dirname(os.path.dirname(current))
sys.path.append(parent_parent)

from converters.tree2other.tree2other import tree_to_prefix


n_cpu = 4
ampl_trees_file = "../../data.nosync/tree/QED_amplitudes_trees.pickle"
sqampl_trees_file = "../../data.nosync/tree/QED_sqamplitudes_trees.pickle"

with open(ampl_trees_file, "br") as f:
    ampl_trees = pickle.load(f)

with open(sqampl_trees_file, "br") as f:
    sqampl_trees = pickle.load(f)

assert len(ampl_trees) == len(sqampl_trees)
print("Loaded trees from")
print(ampl_trees_file)
print("and")
print(sqampl_trees_file)
ic(len(ampl_trees))

for ampls, sqampls in zip(ampl_trees, sqampl_trees):
    assert len(ampls) == len(sqampls)
    ic(len(ampls))


ampl_prefix = []
sqampl_prefix = []

for ampls in ampl_trees:
    print("converting amplitudes trees to prefix on", n_cpu, "cpus.")
    with Pool(n_cpu) as p:
        ampl_prefix_process = list(p.map(tree_to_prefix, ampls))
    ampl_prefix.append(ampl_prefix_process)

for sqampls in sqampl_trees:
    print("converting sqamplitudes trees to prefix on", n_cpu, "cpus.")
    with Pool(n_cpu) as p:
        sqampl_prefix_process = list(p.map(tree_to_prefix, sqampls))
    sqampl_prefix.append(sqampl_prefix_process)

assert len(ampl_prefix) == len(sqampl_prefix)
for a, sqa in zip(ampl_prefix, sqampl_prefix):
    assert len(a) == len(sqa)
