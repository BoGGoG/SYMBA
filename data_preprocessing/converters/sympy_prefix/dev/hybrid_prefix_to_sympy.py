import sys
import os
from icecream import ic 
import numpy as np
import sympy as sp
  
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import sympy as sp
from source.SympyPrefix import sympy_to_hybrid_prefix, hybrid_prefix_to_sympy

sqampls_file = "data.nosync/QED_sqamplitudes_TreeLevel_UpTo2to2_simplified.txt"

with open(sqampls_file) as f:
    sqampls = f.readlines()

ic(len(sqampls))

test_sqampls = [
        "a+b*c",
        # "8*g**4*(2*m**4 - m**2*s)",
        # "8*g**4*(2*m**4 - m**2*(s+d))",
        # "8*g**4*(2*m**4 - m**2*(s+d)**2)",
        # "25*21*a**(b*c)",
        # "exp(3)" # not working yet, but not crucial for SYMBA. TODO
        # "sin(x)" # not working yet, but not crucial for SYMBA. TODO
        ]
for test_sqampl in test_sqampls:
    test_sqampl_sp = sp.factor(sp.sympify(test_sqampl))
    test_sqampl_prefix = sympy_to_hybrid_prefix(test_sqampl_sp)
    rec = hybrid_prefix_to_sympy(test_sqampl_prefix)
    ic(test_sqampl_sp)
    ic(np.array(test_sqampl_prefix))
    ic(rec == test_sqampl_sp)

num_tests = 10
ctr = 0
for test_sqampl in np.random.choice(sqampls, num_tests):
    test_sqampl_sp = sp.factor(sp.sympify(test_sqampl))
    test_sqampl_prefix = sympy_to_hybrid_prefix(test_sqampl_sp)
    rec = hybrid_prefix_to_sympy(test_sqampl_prefix)
    # ic(test_sqampl)
    ic(test_sqampl_sp)
    ic(np.array(test_sqampl_prefix))
    ic(rec == test_sqampl_sp)
    ctr = ctr + 1
ic(ctr)

