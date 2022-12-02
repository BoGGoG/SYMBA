import sys
import os
from icecream import ic 
import numpy as np
import sympy as sp

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import sympy as sp
from sympy_to_tree import sympy_to_tree, tree_to_sympy


def test_to_tree():
    sp_expr = sp.sympify("4*e**2*(2*m2d + s_23)/9")
    print("")
    sp.pprint(sp_expr)
    tree = sympy_to_tree(sp_expr)
    tree.pretty_print(unicodelines=True)
