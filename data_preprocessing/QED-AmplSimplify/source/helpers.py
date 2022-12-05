import sympy as sp


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

