import sympy as sp
import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from source.ExpressionsTokensCombiner import shorten_expression


masses_strings = [
        "m_e",
        "m_u",
        "m_d",
        "m_s",
        "m_c",
        "m_b",
        "m_t",
        ]


masses = [sp.Symbol(x) for x in masses_strings]


def process_ampl_sqampl(ampl_sqampl):
    """
    Needed in extra file for multiprocessing
    Read in one amplitudes and one squared amplitude.
    The amplitude is simplified using sympy
    """

    ampl = ampl_sqampl[0]
    sqampl = ampl_sqampl[1]
    try:
        sqampl_sp = sp.sympify(sqampl)
    except:
        print("Squared amplitude not a valid sympy expression, I am just returning (None, None) in this case.")
        print("The squared amplitudes was:")
        print(sqampl)
        return (None, None)
    sqampl_simplified = sp.factor(sqampl_sp, masses)
    return (ampl, sqampl_simplified)


def shorten_expression_helper(ampl_sqampl):
    ampl = ampl_sqampl[0]
    sqampl = ampl_sqampl[1]
    try:
        sqampl_shortened = shorten_expression(sqampl)
    except:
        print("Problem shortening squared amplitudes. I don't know how this code every go reached. GLHF. Printing the sqampl in question:")
        print(sqampl)
        return (None, None)
    return (ampl, sqampl_shortened)
