import sys
import os
from icecream import ic 
import numpy as np
import sympy as sp

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import sympy as sp
from source.SympyPrefix import sympy_to_hybrid_prefix, hybrid_prefix_to_sympy, sympy_to_prefix


def test_examples():
    test_sqampls = ["8*g**4*(2*m**4 - m**2*s)",
            "8*g**4*(2*m**4 - m**2*(s+d))",
            "8*g**4*(2*m**4 - m**2*(s+d)**2)",
            "25*21*a**(b*c)",
            # "exp(3)" # not working yet, but not crucial for SYMBA. TODO
            # "sin(x)" # not working yet, but not crucial for SYMBA. TODO
            ]
    for test_sqampl in test_sqampls:
        test_sqampl_sp = sp.factor(sp.sympify(test_sqampl))
        test_sqampl_prefix = sympy_to_hybrid_prefix(test_sqampl_sp)
        rec = hybrid_prefix_to_sympy(test_sqampl_prefix)
        assert rec == test_sqampl_sp


def test_qcd():
    """
    read in amplitudes and test on a random sample of them.
    """
    sqampls_file = "data.nosync/QED_sqamplitudes_TreeLevel_UpTo2to2_simplified.txt"
    with open(sqampls_file) as f:
        sqampls = f.readlines()

    num_tests = 10
    for test_sqampl in np.random.choice(sqampls, num_tests):
        test_sqampl_sp = sp.factor(sp.sympify(test_sqampl))
        test_sqampl_prefix = sympy_to_hybrid_prefix(test_sqampl_sp)
        rec = hybrid_prefix_to_sympy(test_sqampl_prefix)
        assert rec == test_sqampl_sp


def test_sympy_to_prefix():
    ic("asdf")
    expr_arr = "mul( mul 4 pow 9 s- 1 pow e 2 add s_23 mul 2 m2d )".split(" ")
    print(expr_arr)
    expr_symp = hybrid_prefix_to_sympy(expr_arr)
    print(expr_symp)
    expr_prefix = sympy_to_prefix(expr_symp)
    print(expr_prefix)
    return 0
