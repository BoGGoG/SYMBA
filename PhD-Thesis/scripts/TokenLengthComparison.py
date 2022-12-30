import pickle
from nltk import Tree
from icecream import ic
import sys
import os
import sympy as sp
from collections import Counter
# from multiprocessing import Pool
#
# current = os.path.dirname(os.path.realpath(__file__))
# parent_parent = os.path.dirname(os.path.dirname(current))
# sys.path.append(parent_parent)

ampl_prefix_file = "../data.nosync/prefix/QED_amplitudes_prefix.pickle"
sqampl_prefix_file = "../data.nosync/prefix/QED_sqamplitudes_prefix.pickle"

amplitudes = []
sqamplitudes = []
with open(ampl_prefix_file, 'rb') as f:
    try:
        while True:
            amplitudes.append(pickle.load(f))
    except EOFError:
        pass

with open(sqampl_prefix_file, 'rb') as f:
    try:
        while True:
            sqamplitudes.append(pickle.load(f))
    except EOFError:
        pass




ic(len(amplitudes))
ic(len(sqamplitudes))

for ampl, sqampl in zip(amplitudes, sqamplitudes):
    ic(len(ampl))
    ic(len(sqampl))

# ic(len(amplitudes))
# for ampl in amplitudes:
#     ic(len(ampl))
#
#
# ic(len(amplitudes))
# for ampl in amplitudes:
#     ic(len(ampl))
#
# for ampl in amplitudes:
#     ctr = Counter(sum(ampl, []))
#     ic(ctr.most_common(5))
#
# for sqampl in sqamplitudes:
#     ctr = Counter(sum(sqampl, []))
#     ic(ctr.most_common(5))

