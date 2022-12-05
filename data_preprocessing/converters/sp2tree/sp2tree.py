from nltk.tree import Tree
import sympy as sp
from icecream import ic
# from sympy.core.traversal import walk
# from sympy import Min, Max
# from sympy.abc import y, a
# from sympy import srepr, pi

operators = {
    # Elementary functions
    sp.Add: 'Sum',
    sp.Mul: 'Prod',
    sp.Pow: 'Pow',
    sp.exp: 'exp',
    sp.log: 'ln',
    sp.Abs: 'abs',
    sp.sign: 'sign',
    # Trigonometric Functions
    sp.sin: 'sin',
    sp.cos: 'cos',
    sp.tan: 'tan',
    sp.cot: 'cot',
    sp.sec: 'sec',
    sp.csc: 'csc',
    # Trigonometric Inverses
    sp.asin: 'asin',
    sp.acos: 'acos',
    sp.atan: 'atan',
    sp.acot: 'acot',
    sp.asec: 'asec',
    sp.acsc: 'acsc',
    # Hyperbolic Functions
    sp.sinh: 'sinh',
    sp.cosh: 'cosh',
    sp.tanh: 'tanh',
    sp.coth: 'coth',
    sp.sech: 'sech',
    sp.csch: 'csch',
    # Hyperbolic Inverses
    sp.asinh: 'asinh',
    sp.acosh: 'acosh',
    sp.atanh: 'atanh',
    sp.acoth: 'acoth',
    sp.asech: 'asech',
    sp.acsch: 'acsch',
    # Derivative
    sp.Derivative: 'derivative',
}

operators_inv = {operators[key]: key for key in operators}

operators_nargs = {
    # Elementary functions
    'Prod(': -1,
    'Sum(': -1,
    'Sum': 2,
    'sub': 2,
    'Prod': 2,
    'div': 2,
    'Pow': 2,
    'rac': 2,
    'inv': 1,
    'Pow2': 1,
    'Pow3': 1,
    'Pow4': 1,
    'Pow5': 1,
    'sqrt': 1,
    'exp': 1,
    'ln': 1,
    'abs': 1,
    'sign': 1,
    # Trigonometric Functions
    'sin': 1,
    'cos': 1,
    'tan': 1,
    'cot': 1,
    'sec': 1,
    'csc': 1,
    # Trigonometric Inverses
    'asin': 1,
    'acos': 1,
    'atan': 1,
    'acot': 1,
    'asec': 1,
    'acsc': 1,
    # Hyperbolic Functions
    'sinh': 1,
    'cosh': 1,
    'tanh': 1,
    'coth': 1,
    'sech': 1,
    'csch': 1,
    # Hyperbolic Inverses
    'asinh': 1,
    'acosh': 1,
    'atanh': 1,
    'acoth': 1,
    'asech': 1,
    'acsch': 1,
    # Derivative
    'derivative': 2,
    # custom functions
    'f': 1,
    'g': 2,
    'h': 3,
}


def sympy_to_tree(expr):
    """convert sympy expression to nltk.Tree"""
    if isinstance(expr, type("asdf")):
        return expr
    if len(expr.args) > 0:
        op = expr.func
        op = operators[op]
        args = [sympy_to_tree(a) for a in expr.args]
        # return Tree(op, list(map(sympy_to_tree, expr.args)))
        return Tree(op, args)
    else:
        return expr


def tree_to_sympy(tree, expression=None):
    """convert nltk.Tree back to sympy expression"""
    if not isinstance(tree, type(Tree("asdf", [""]))):
        return tree
    else:
        node = tree._label
        op = operators_inv[node]
        # num_args = operators_nargs[node]
        # if num_args != len(tree):
        #     print("num args not len(tree):")
        #     ic(num_args)
        #     ic(len(tree))
        #     ic(tree)
        # assert num_args == len(tree)
        return op(*[tree_to_sympy(t) for t in tree])
    return 0


if __name__ == "__main__":
    print("-------- sympy_to_tree")
    expr = ic(sp.sympify("a+b*c"))
    sympy_to_tree(expr).pretty_print(unicodelines=True)
    expr = ic(sp.sympify("a+b+c*(d + exp(e))"))
    sympy_to_tree(expr).pretty_print(unicodelines=True)
    expr = ic(sp.sympify("exp(a+b*sin(c))"))
    sympy_to_tree(expr).pretty_print(unicodelines=True)

    print("-------- tree_to_sympy")
    expr = sp.sympify("exp(a+b*sin(c))")
    ic(expr)
    tree = sympy_to_tree(expr)
    tree.pretty_print(unicodelines=True)
    expr_back = ic(tree_to_sympy(tree))
    assert expr == expr_back
