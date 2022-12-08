import os
import pickle
from icecream import ic
from nltk import Tree

amplitudes_export_file = "../../data.nosync/tree/QED_amplitudes_trees.pickle"
sqamplitudes_export_file = "../../data.nosync/tree/QED_sqamplitudes_trees.pickle"


amplitudes = []
sqamplitudes = []
with open(amplitudes_export_file, 'rb') as f:
    try:
        while True:
            amplitudes.append(pickle.load(f))
    except EOFError:
        pass

with open(sqamplitudes_export_file, 'rb') as f:
    try:
        while True:
            sqamplitudes.append(pickle.load(f))
    except EOFError:
        pass

ic(len(amplitudes))
ic(len(sqamplitudes))

for a, sqa in zip(amplitudes, sqamplitudes):
    ic(len(a))
    ic(len(sqa))
    assert len(a) == len(sqa)
