"""
Convert trees to hybrid prefix.

Plan:
    - for amplitudes:
        - read in one batch
        - convert
        - export
        - same until EOFError
    - same for squared amplitudes
    - tests after going through all of them:
        - read in one batch of each at a time. Check that same amount of amplitudes and squared amplitudes
    - maybe needed:
        - way of saving progress
"""
import pickle
from nltk import Tree
from icecream import ic
import sys
import os
import sympy as sp
from multiprocessing import Pool
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
from time import sleep

current = os.path.dirname(os.path.realpath(__file__))
parent_parent = os.path.dirname(os.path.dirname(current))
sys.path.append(parent_parent)

from converters.tree2other.tree2other import tree_to_prefix

def tree_to_hybrid_prefix(tree):
    return tree_to_prefix(tree, hybrid=True)


n_cpu = 6
ampl_trees_file = "../../data.nosync/tree/QED_amplitudes_trees.pickle"
sqampl_trees_file = "../../data.nosync/tree/QED_sqamplitudes_trees.pickle"
ampl_prefix_export_file = "../../data.nosync/hybrid_prefix/QED_amplitudes_hybrid_prefix.pickle"
sqampl_prefix_export_file = "../../data.nosync/hybrid_prefix/QED_sqamplitudes_hybrid_prefix.pickle"



ctr_start_ampl = 0
ctr_start_sqampl = 0
sleep_s = 10   # how long to sleep after each round
chunksize = 100


# amplitudes
f_ampl_export = open(ampl_prefix_export_file, "ba")
ctr = 0
with open(ampl_trees_file, "br") as f:
    try:
        while True:
            if ctr_start_ampl < 0: break
            if ctr < ctr_start_ampl:
                ampl_trees = pickle.load(f)
                print("skipping amplitudes #{}".format(ctr))
                ctr = ctr + 1
                continue
            print("working on amplitudes {}".format(ctr))
            ampl_trees = pickle.load(f)
            print("converting amplitudes trees to prefix on", n_cpu, "cpus.")
            # with Pool(n_cpu) as p:
            #     ampls_prefix = list(p.map(tree_to_prefix, ampl_trees))
            ampls_prefix = process_map(tree_to_hybrid_prefix, ampl_trees, max_workers
                                       = n_cpu, chunksize=chunksize)
            pickle.dump(ampls_prefix, f_ampl_export)
            ctr = ctr + 1
            sleep(sleep_s)
    except EOFError:
        print("Finished with amplitudes")
        pass
f_ampl_export.close()


# sqamplitudes
f_sqampl_export = open(sqampl_prefix_export_file, "ba")
ctr = 0
with open(sqampl_trees_file, "br") as f:
    try:
        while True:
            if ctr_start_sqampl < 0: break
            if ctr < ctr_start_sqampl:
                sqampl_trees = pickle.load(f)
                print("skipping sqamplitudes #{}".format(ctr))
                ctr = ctr + 1
                continue
            print("working on sqamplitudes {}".format(ctr))
            sqampl_trees = pickle.load(f)
            print("converting sqamplitudes trees to prefix on", n_cpu, "cpus.")
            # with Pool(n_cpu) as p:
            #     sqampls_prefix = list(p.map(tree_to_prefix, sqampl_trees))
            sqampls_prefix = process_map(tree_to_hybrid_prefix, sqampl_trees, max_workers
                                       = n_cpu, chunksize=chunksize)
            pickle.dump(sqampls_prefix, f_sqampl_export)
            ctr = ctr + 1
            sleep(sleep_s)
    except EOFError:
        print("Finished with sqamplitudes")
        pass
f_sqampl_export.close()


#
# sqampl_trees = []
# with open(sqampl_trees_file, "br") as f:
#     try:
#         while True:
#             sqampl_trees.append(pickle.load(f))
#     except EOFError:
#         pass
#
# assert len(ampl_trees) == len(sqampl_trees)
# print("Loaded trees from")
# print(ampl_trees_file)
# print("and")
# print(sqampl_trees_file)
# ic(len(ampl_trees))
# ic(len(sqampl_trees))
#
# for ampls, sqampls in zip(ampl_trees, sqampl_trees):
#     assert len(ampls) == len(sqampls)
#     ic(len(ampls))
#
#
# ampl_prefix = []
# sqampl_prefix = []
#
# for ampls in tqdm(ampl_trees[3:]):
#     print("converting amplitudes trees to prefix on", n_cpu, "cpus.")
#     with Pool(n_cpu) as p:
#         ampl_prefix_process = list(p.map(tree_to_prefix, ampls))
#     ampl_prefix.append(ampl_prefix_process)
#
# for sqampls in tqdm(sqampl_trees[3:]):
#     print("converting sqamplitudes trees to prefix on", n_cpu, "cpus.")
#     with Pool(n_cpu) as p:
#         sqampl_prefix_process = list(p.map(tree_to_prefix, sqampls))
#     sqampl_prefix.append(sqampl_prefix_process)
#
# assert len(ampl_prefix) == len(sqampl_prefix)
# for a, sqa in zip(ampl_prefix, sqampl_prefix):
#     assert len(a) == len(sqa)
#
# with open(ampl_prefix_export_file, "ba") as f:
#     pickle.dump(ampl_prefix, f)
#     print("Saved amplitudes prefix to", ampl_prefix_export_file)
#
# with open(sqampl_prefix_export_file, "ba") as f:
#     pickle.dump(sqampl_prefix, f)
#     print("Saved squared amplitudes prefix to", sqampl_prefix_export_file)
