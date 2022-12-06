"""
This package contains all kinds of functions to transform from a tree to other formats.
"""
from nltk import Tree
import copy
from icecream import ic
import sympy as sp

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


def expand_tree(tree_input):
    """
    If the tree has Prod or Sum nodes with more than 2 arguments
    --> expand them to only have 2
    """
    tree = copy.deepcopy(tree_input)  # is there a better way to not mutate tree?
    if not isinstance(tree, Tree):
        return tree
    node = tree.label()
    nodes_considered = ["Sum", "Sum(", "Prod", "Prod("]  # ))
    if node[-1] == "(":  # )
        node = node[:-1]
        tree.set_label(node)
    if (node in nodes_considered) and (len(tree) > 2):
        leaves = [expand_tree(t) for t in tree[1:]]
        tree[0] = expand_tree(tree[0])
        tree[1] = expand_tree(Tree(node, leaves))
        del tree[2:]
    else:
        tree[0:] = [expand_tree(t) for t in tree[0:]]
    return tree


def contract_tree(tree_input, runs=0, add_opening_bracket=True):
    """inverse of `expand_tree`, not fully tested.

    Note: This implementation is not fully tested and probably not working 100%.
    One problem was that it didn't work at all depths.
    Right now my workaround is that I just run it three times and hope all
    cases are caught, but I don't think so.
    """

    tree = copy.deepcopy(tree_input)  # don't mutate tree

    if runs>2:
        return tree
    if not isinstance(tree, Tree):
        return tree
    node = tree.label()
    nodes_considered = ["Sum", "Sum(", "Prod", "Prod("]  # ))
    if (node in nodes_considered) and (isinstance(tree[1], Tree)) and (tree[1].label() == node):
        if add_opening_bracket:
            node = node + "("  # )
        tree.set_label(node)
        subtree = contract_tree(tree[1], add_opening_bracket=add_opening_bracket)
        # del[tree[1:]]
        tree[0:] = tree[0:1] + subtree[0:]
    else:
        tree[0:] = [contract_tree(t, add_opening_bracket=add_opening_bracket) for t in tree[0:]]
    return contract_tree(tree, runs=runs+1, add_opening_bracket=add_opening_bracket)


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


def tree_to_prefix(tree_input, hybrid=False):
    """converts a tree to an array in prefix notation.
    Automatically detects hybrid prefix if an operator is like `Prod(` )
    If operators don't have parentheses, you can still go to hybrid prefix with
    `hybrid=True`. Default is `False`
    """
    tree = copy.deepcopy(tree_input)
    if not hybrid:
        tree = expand_tree(tree)
    if hybrid:
        tree = contract_tree(tree)
    arr = []
    node = tree.label()
    if hybrid and (node in ["Sum", "Prod"]) and (len(tree)>2):
        node = node + "("  # )
    arr.append(node)
    for i in range(len(tree)):
        if isinstance(tree[i], Tree):
            arr = arr + tree_to_prefix(tree[i], hybrid=hybrid)
        else:
            arr.append(str(tree[i]))

    if node[-1] == "(":  # )
        arr.append(")")
    return arr
