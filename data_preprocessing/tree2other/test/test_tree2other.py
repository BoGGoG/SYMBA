import sys
import os
from icecream import ic 
import numpy as np
import sympy as sp
from sympy import sympify, pprint
from nltk import Tree

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
parent_parent = os.path.dirname(parent)
sys.path.append(parent)
sys.path.append(parent_parent)

import sympy as sp
from tree2other import expand_tree, contract_tree, tree_to_prefix, tree_to_sympy
from sp2tree.sp2tree import sympy_to_tree
from ampl2tree.source.ampl2tree import ampl_to_tree


def test_sympy():
    expressions_s = ["a+b", "a*b", "a**b", "a+b*c", "a+b+c", "a+b+c*d", "a+b+c**d", "a**b+c+d"]
    expressions = [sympify(s) for s in expressions_s]

    trees = [sympy_to_tree(s) for s in expressions]
    trees[-1].pretty_print()


def test_expand_tree():
    expressions_s = ["a+b", "a*b", "a**b", "a+b*c", "a+b+c", "a+b+c*d",
                     "a+b+c**d", "a**b+c+d", "a+(b*c*d*e)",
                     "a*b*(c+d+e+f)*exp(g)", "exp(a)*b*c*d"
                     ]
    expressions = [sympify(s) for s in expressions_s]

    trees = [sympy_to_tree(s) for s in expressions]
    for t in trees:
        expanded = expand_tree(t)
        print("normal")
        t.pretty_print(unicodelines=True)
        print("expanded")
        expanded.pretty_print(unicodelines=True)


def test_contract_tree():
    expressions_s = ["a+b", "a*b", "a**b", "a+b*c", "a+b+c", "a+b+c*d",
                     "a+b+c**d", "a**b+c+d", "a+(b*c*d*e)",
                     "a*b*(c+d+e+f)*exp(g)", "exp(a)*b*c*d"
                     ]
    expressions = [sympify(s) for s in expressions_s]

    trees = [sympy_to_tree(s) for s in expressions]
    for t in trees:
        expanded = expand_tree(t)
        contracted = contract_tree(expanded, add_opening_bracket=False)
        assert contracted == t


def test_tree_to_sympy_roundtrip():
    expressions_s = ["a+b", "a*b", "a**b", "a+b*c", "a+b+c", "a+b+c*d",
                     "a+b+c**d", "a**b+c+d", "a+(b*c*d*e)",
                     "a*b*(c+d+e+f)*exp(g)", "exp(a)*b*c*d"
                     ]
    expressions = [sympify(s) for s in expressions_s]

    trees = [sympy_to_tree(s) for s in expressions]
    roundtrips = [tree_to_sympy(t) for t in trees]
    for exp, roundtrip in zip(expressions, roundtrips):
        assert exp == roundtrip


def test_tree_to_prefix():
    expressions_s = ["a+b", "a*b", "a**b", "a+b*c", "a+b+c", "a+b+c*d",
                     "a+b+c**d", "a**b+c+d", "a+(b*c*d*e)",
                     "a*b*(c+d+e+f)*exp(g)", "exp(a)*b*c*d"
                     ]
    expressions = [sympify(s) for s in expressions_s]

    trees = [sympy_to_tree(s) for s in expressions]
    prefixes = [tree_to_prefix(t) for t in trees]
    [print(p) for p in prefixes]


def test_tree_to_prefix_round_trip():
    expressions_s = ["a+b", "a*b", "a**b", "a+b*c", "a+b+c", "a+b+c*d",
                     "a+b+c**d", "a**b+c+d", "a+(b*c*d*e)",
                     "a+b**c",
                     "a+b**(c+d)+e*f*g*h*i",
                     "4*e**2*(2*m2d+3)/9"
                     # "a*b*(c+d+e+f)*exp(g)", "exp(a)*b*c*d"
                     ]
    expressions = [sympify(s) for s in expressions_s]

    trees = [sympy_to_tree(s) for s in expressions]
    prefixes = [tree_to_prefix(t) for t in trees]
    round_trips = [ampl_to_tree(p) for p in prefixes]
    round_trips = [contract_tree(t, add_opening_bracket=False) for t in round_trips]
    print("")
    for i in range(len(expressions)):
        ic(i)
        ic(expressions[i])
        ic(trees[i])
        ic(prefixes[i])
        ic(round_trips[i])
        assert trees[i] == round_trips[i]


def test_special_cases():
    exp = "4*e**2*(2*m2d+3)/9"
    exp = sp.sympify(exp)
    ic(exp)
    ic(exp.args[0])
    tree = sympy_to_tree(exp)
    tree.pretty_print(unicodelines=True)
    tree_expanded = expand_tree(tree)
    tree_expanded.pretty_print(unicodelines=True)
    tree_round_trip = contract_tree(tree_expanded)
    tree_round_trip.pretty_print(unicodelines=True)
    prefix = tree_to_prefix(tree)
    hybrid_prefix = tree_to_prefix(tree_expanded, hybrid=True)
    ic(prefix)
    ic(hybrid_prefix)
    prefix_round_trip = ampl_to_tree(prefix)
    prefix_round_trip.pretty_print(unicodelines=True)
    assert prefix_round_trip == tree_expanded

    hybrid_prefix_round_trip = ampl_to_tree(hybrid_prefix, remove_hybrid_parentheses=True)
    hybrid_prefix_round_trip.pretty_print(unicodelines=True)
    assert hybrid_prefix_round_trip == tree

