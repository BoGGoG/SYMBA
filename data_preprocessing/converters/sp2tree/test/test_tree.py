import sys
import os
from icecream import ic 
import numpy as np
import sympy as sp
from sympy import sympify, pprint

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import sympy as sp
from sp2tree import sympy_to_tree, tree_to_sympy



def test_sp2tree():
    """
    Testing most basic functions.
    I think the `pretty_print` function reorders such that the plot looks the nicest.
    E.g. for "a**b+c+d" the tree looks like this:
            Sum
         ┌───┼───────┐
         │   │      Pow
         │   │   ┌───┴───┐
         c   d   a       b
    but I think it did not actually reorder the elements of the first sum, but rather only
    in the `pretty_print` function it prints them in a different order.
    """
    expressions_s = ["a+b", "a*b", "a**b", "a+b*c", "a+b+c", "a+b+c*d", "a+b+c**d", "a**b+c+d"]
    expressions = [sympify(s) for s in expressions_s]
    print("")
    [pprint(s) for s in expressions]

    for expr in expressions:
        tree = sympy_to_tree(expr)
        tree.pretty_print(unicodelines=True)



def test_sp2tree_realsqampls():
    sqampls_file = "../../data.nosync/QED_sqamplitudes_TreeLevel_2to2.txt"
    with open(sqampls_file) as f:
        sqampls = f.readlines(1000000)
        sqampls = [sympify(sqa) for sqa in sqampls]
    ic(len(sqampls))
    pprint(sqampls[0])
    tree = sympy_to_tree(sqampls[0])
    tree.pretty_print(unicodelines=True)

    # just test if any errors when converting to trees. This does not check if correct
    for sqa in sqampls:
        tree = sympy_to_tree(sqa)


def test_tree_to_sympy():
    """TODO"""
    return 0
