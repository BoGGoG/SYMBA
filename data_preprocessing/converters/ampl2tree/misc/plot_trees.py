# print some random trees and their raw strings to file.

import sys
import os
from icecream import ic 
import numpy as np
import sympy as sp
from nltk.tree import Tree
from nltk.draw.tree import TreeView
from nltk.draw.util import CanvasFrame
from nltk.draw import TreeWidget

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import sympy as sp
from source.ampl2tree import ampl_to_tree, rightmost_operator_pos, func_to_tree, tree_to_prefix, expand_tree, contract_tree, get_tree, ampl_raw_tree_to_nltk
from source.ampl2tree import has_subscript, subscripts_to_subtree, is_basis_func, basis_function_to_subtree, nltk_tree_expand_subscripts, p_sub_to_tree
from source.ampl2tree import rename_indices, collect_indices, is_index, raw_ampl_to_tree, categorize_indices, get_index_replacements, nltk_tree_replace_leaves


ampls_raw_file = "../../data.nosync/QED_amplitudes_TreeLevel_2to3_raw.txt"
with open(ampls_raw_file) as f:
    ampls_raw = f.readlines()
    print("Loaded {} amplitudes.".format(len(ampls_raw)))
    ampls_raw = [a[:-1] for a in ampls_raw]


for i in np.random.choice(range(len(ampls_raw)), 10):
    exp = ampls_raw[i]
    tree = raw_ampl_to_tree(exp)
    tree = rename_indices(tree)
    cf = CanvasFrame()
    tc = TreeWidget(cf.canvas(),tree)
    cf.add_widget(tc,10,10) # (10,10) offsets

    folder = "trees_figures/"
    filename = '{}tree_{}'.format(folder, i)
    # TreeView(tree)._cframe.print_to_file(filename+".ps")
    cf.print_to_file(filename+".ps")
    os.system('ps2pdf -dEPSCrop {}.ps {}.pdf'.format(filename, filename))
    os.system('rm {}.ps'.format(filename))

    cf.destroy()

    with open(filename+".txt", "w") as f:
        f.write(exp)
