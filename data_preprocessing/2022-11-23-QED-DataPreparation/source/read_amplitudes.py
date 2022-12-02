import os
import csv
import more_itertools
import re
from icecream import ic
import numpy as np

indices_roman = [
        "i",
        "j",
        "k",
        "l",
        ]

indices_greek = [
        "alpha",
        "beta",
        "gam",
        "del",
        "eta",
        "sigma",
        "tau",
        "rho",
        "lambda",
        "nu",
        "mu",
        "eps",
        ]

def read_amplitudes_and_squares(folder_ampl, folder_sqampl):
    files_ampl = os.listdir(folder_ampl) 
    files_sqampl = os.listdir(folder_sqampl) 
    assert len(files_ampl) == len(files_sqampl)
    # to check if order of files is correct
    skip = len("ampl")
    files_sqampl_generated = ["sq_ampl"+f[skip:] for f in files_ampl]
    assert files_sqampl == files_sqampl_generated

    ampls = []
    sqampls = []
    for file in files_ampl:
        with open(folder_ampl+file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                ampls.append(row[:-1])

    for file in files_sqampl:
        with open(folder_sqampl+file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                sqampls.append(row[:-1])

    return (ampls, sqampls)


def read_amplitudes_and_raw_squares(folder_ampl, folder_sqampl_raw):
    """
    Read amplitudes in prefix format, but squared amplitudes in raw marty format.
    This is good, becaues the squared amplitudes can be read by sympy and simplified.
    """
    files_ampl = os.listdir(folder_ampl) 
    files_sqampl = os.listdir(folder_sqampl_raw) 
    assert len(files_ampl) == len(files_sqampl)
    # to check if order of files is correct
    skip = len("ampl")
    files_sqampl_generated = ["sq_ampl_raw"+f[skip:] for f in files_ampl]
    assert files_sqampl == files_sqampl_generated

    ampls = []
    sqampls = []
    for file in files_ampl:
        with open(folder_ampl+file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                ampls.append(row[:-1])

    for file in files_sqampl:
        with open(folder_sqampl_raw+file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                sqampls.append(row[0])

    return (ampls, sqampls)


def read_amplitudes(folder):
    files = os.listdir(folder)
    ret = []
    for file in files:
        with open(folder+file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                ret.append(row[:-1])
    return ret


def fix_operator_num_args(tree_expression, op="Prod"):
    """Prod 1 2 3 --> Prod 1 Prod 2 3"""
    if (tree_expression[0] == op) and (len(tree_expression) > 3):
        return [op, fix_operator_num_args(tree_expression[1], op=op)] + fix_operator_num_args([[op] + fix_operator_num_args(tree_expression[2:], op=op)])
    elif type(tree_expression) == type([1234]):
        return [fix_operator_num_args(e, op=op) for e in tree_expression]
    else:
        return tree_expression

def fix_operator_num_args_hybrid(tree_expression, op="Prod"):
    """Prod 1 2 3 --> Prod( 1 2 3 )"""
    if (tree_expression[0] == op) and (len(tree_expression) > 3):
        # return [op+"(", fix_operator_num_args_hybrid(tree_expression[1:]), ")"]  # hybrid prefix
        return [op, fix_operator_num_args(tree_expression[1], op=op)] + fix_operator_num_args([[op] + fix_operator_num_args(tree_expression[2:], op=op)]) # prefix
    elif type(tree_expression) == type([1234]):
        return [fix_operator_num_args_hybrid(e, op=op) for e in tree_expression]
    else:
        return tree_expression


def get_tree(expression):
    last_open_bracket_idx = get_last_open_bracket(expression)
    while last_open_bracket_idx != -1:
        next_closing_bracket_idx = get_next_closing_bracket(expression, last_open_bracket_idx)
        sub_expr = expression[last_open_bracket_idx+1:next_closing_bracket_idx]
        sub_expr = [expression[last_open_bracket_idx-1]] + sub_expr  # add operator before ()
        expression[last_open_bracket_idx-1] = sub_expr
        del expression[last_open_bracket_idx:next_closing_bracket_idx+1]
        last_open_bracket_idx = get_last_open_bracket(expression)

    return expression[0]

def fix_tree(tree_expression, operators=["Sum", "Prod"]):
    for op in operators:
        tree_expression = fix_operator_num_args_hybrid(tree_expression, op=op)
        # tree_expression = fix_operator_num_args(tree_expression, op=op)
    # return tree_expression
    ret = list(more_itertools.collapse(tree_expression))
    # ret = [value for value in ret if value not in ["(", ")"]]
    return ret


def get_last_open_bracket(expression):
    for i in range(len(expression)):
        if expression[-i] == '(':
            return len(expression) - i
        else:
            pass
    return -1


def get_next_closing_bracket(expression, last_open_bracket_idx):
    for i in range(last_open_bracket_idx+1, len(expression)):
        if expression[i] == ")":
            return i
    return -1

def fix_subscripts(expression):
    """expression: flat array of strings"""
    indices = set([])
    for i, str in enumerate(expression):
        str_new, idxs = fix_subscript(str)
        expression[i] = str_new
        for idx in idxs:
            indices.add(idx)

    greek = set([])
    roman = set([])
    other = set([])
    for index in indices:
        ind_name = index.split("_")[0]
        if ind_name in indices_greek:
            greek.add(index)
        elif ind_name in indices_roman:
            roman.add(index)
        else:
            other.add(index)

    if other:
        print("found new indices!")
        print(other)


    ret = list(more_itertools.collapse(expression))

    greek_replacements = enumerate_indices(greek, "alpha")
    roman_replacements = enumerate_indices(roman, "i")
    # ic(greek_replacements)

    ret = replace_indices(ret, greek_replacements)
    ret = replace_indices(ret, roman_replacements)

    return ret

def replace_indices(expression, replacements):
    for key in replacements:
        for i, e in enumerate(expression):
            expression[i] = e.replace(key, replacements[key])
    return expression


def enumerate_indices(indices, basis_str="alpha"):
    replacements = dict()
    indices_sorted = np.sort(np.array(list(indices)))
    for i, ind in enumerate(indices_sorted):
        replacements[ind]=basis_str+"_"+str(i)
    return replacements
        
def fix_subscript(str):
    if not has_subscript(str):
        return str, []
    var, subscript = str.split("_", maxsplit=1)
    if var == "gamma":
        subscripts = format_gamma(subscript)
        return [list(more_itertools.collapse(["gamma", subscripts])), subscripts]
    elif var == "p":
        num, index = format_p(subscript)
        return [["p_"+num, index], [index]]
    else:
        new_str, subscripts = format_other_subscripts(var, subscript)
        new_str = list(more_itertools.collapse(new_str))
        return [new_str, subscripts]

def format_p(subs):
    subs = subs.replace("\\", "")
    subs = subs.replace("%", "")
    subs = subs.replace("+", "")
    num, index = subs.split("_", maxsplit=1)
    return [num, index]

def format_gamma(subscript):
    """
    input looks like: '{%\\sigma_49,%gam_44,%eta_12}'
    gamma alsways has 3 indices
    """
    ind1, ind2, ind3 = subscript[1:-1].split(",")
    ind1 = format_index(ind1)
    ind2 = format_index(ind2)
    ind3 = format_index(ind3)

    return [ind1, ind2, ind3]


def format_index(ind):
    ind = ind.replace("\\","")
    ind = ind.replace("%", "")
    ind = ind.replace("+", "")
    # # not really consistent in data, so I'll just leave the + out
    # if ind[0] == "+":
    #     position = "up"
    #     ind = ind[1:]
    # else:
    #     position = "down"
    return ind

def format_other_subscripts(var, subscript):
    subscript = subscript[1:]  # remove first "{"
    # subscript = subscript.replace("p", "|p|")
    subscript, other = subscript.split("}")
    var = var.replace("e", "ee")
    ind1, ind2 = subscript.split(",")
    ind1 = format_index(ind1)
    ind2 = format_index(ind2)

    other = other.split("^")

    if len(other) == 2:
        var = var+"^"+other[1]
    other = other[0]


    return [[var, ind1, ind2, other], [ind1, ind2]]

def has_subscript(str):
    ret = ("_" in str) and ("{" in str)
    ret = (ret or ("p_" in str))
    return ret
