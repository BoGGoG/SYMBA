import sys
import os
from icecream import ic 
import numpy as np
import sympy as sp
from nltk.tree import Tree

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import sympy as sp
from source.ampl2tree import ampl_to_tree, rightmost_operator_pos, func_to_tree, tree_to_prefix, expand_tree, contract_tree


def test_func_to_tree():
    arr = ["gamma", "alpha1", "alpha2", "alpha3"]
    res = func_to_tree(arr)
    res_test = Tree("gamma", ["alpha1", "alpha2", "alpha3"])
    assert res == res_test
    arr = ["Prod", "a", "c"]
    res = func_to_tree(arr)
    res_test = Tree("Prod", ["a", "c"])
    assert res == res_test


def test_finished():
    arr = [Tree("gamma", ["alpha1", "alpha2", "alpha3"])]
    assert ampl_to_tree(arr) == arr[0]


def test_rightmost_operator_pos():
    arr = ["Prod(", "-1/2", "i", "Pow", "e", "2", ")"]
    res = rightmost_operator_pos(arr)
    assert res == 3
    arr = ["Sum(", "Pow", "m_e", "2","Prod", "-1", "s_13" ,"Prod", "1/2","reg_prop", ")"]
    res = rightmost_operator_pos(arr)
    assert res == 7


def test_hybrid():
    arr = ["Prod(", "-1/2", "a", "c", ")"]  # )
    res = ampl_to_tree(arr, remove_hybrid_parentheses=False)
    assert res == Tree("Prod(", ["-1/2", "a", "c"])  # )

    arr = ["Prod(", "-1/2", "a", "c", "Pow", "e", "2", ")"]  # )
    res = ampl_to_tree(arr, remove_hybrid_parentheses=False)
    assert res == Tree("Prod(", ["-1/2", "a", "c", Tree("Pow", ["e", "2"])])  # )

    arr = ["Prod(", "-1/2", "a", "c", ")"]  # )
    res = ampl_to_tree(arr, remove_hybrid_parentheses=True)
    assert res == Tree("Prod", ["-1/2", "a", "c"])  # )

    arr = ["Prod(", "-1/2", "a", "c", "Pow", "e", "2", ")"]  # )
    res = ampl_to_tree(arr, remove_hybrid_parentheses=True)
    assert res == Tree("Prod", ["-1/2", "a", "c", Tree("Pow", ["e", "2"])])  # )

    arr = ["Prod(", "-1/2", "a", "c", "Sum(", "1", "2", "3", ")", ")"]  # )
    res = ampl_to_tree(arr, remove_hybrid_parentheses=True)
    assert res == Tree("Prod", ["-1/2", "a", "c", Tree("Sum", ["1", "2", "3"])])  # )


def test_ampl_to_tree():
    arr = ["Prod", "-1/2", "Pow", "e", "2"]
    res = ampl_to_tree(arr)
    assert res == Tree("Prod", ["-1/2", Tree("Pow", ["e", "2"])])

    arr = ["Prod", "-1/2", "Sum", "e", "2"]
    res = ampl_to_tree(arr)
    assert res == Tree("Prod", ["-1/2", Tree("Sum", ["e", "2"])])

    arr = ["Prod", "-1/2", "Prod", "e", "2"]
    res = ampl_to_tree(arr)
    assert res == Tree("Prod", ["-1/2", Tree("Prod", ["e", "2"])])

    arr = ["Prod", "-1/2", "gamma", "alpha_1", "alpha_2", "alpha_3"]
    res = ampl_to_tree(arr)
    assert res == Tree("Prod", ["-1/2", Tree("gamma", ["alpha_1", "alpha_2", "alpha_3"])])

    arr = ["Prod", "Pow", "i", "-1/2", "gamma", "alpha_1", "alpha_2", "alpha_3"]
    res = ampl_to_tree(arr)
    # assert res == Tree("Prod", ["-1/2", Tree("gamma", ["alpha_1", "alpha_2", "alpha_3"])])


def test_full_ampls():
    arr = "Prod(,-1/2,i,Pow,e,2,Pow,Sum(,Pow,m_e,2,Prod,-1,s_13,Prod,1/2,reg_prop,),-1,gamma,alpha_4,alpha_2,alpha_0,gamma,alpha_4,alpha_3,alpha_1,ee,i_0,alpha_0,(p_1)_u,ee,i_2,alpha_1,(p_2)_u,ee^(*),i_3,alpha_2,(p_3)_u,ee^(*),i_1,alpha_3,(p_4)_u,)"
    arr = arr.split(",")
    res = ampl_to_tree(arr)

    arr = "Prod(,1/9,i,Pow,e,2,Pow,Sum(,Pow,m_b,2,Prod,-1,s_11,Prod,2,s_13,Prod,-1,s_33,Prod,-1,reg_prop,),-1,Sum(,Prod(,m_b,gamma,alpha_12,alpha_3,alpha_6,gamma,alpha_13,alpha_6,alpha_0,A,i_3,alpha_12,(p_3),A,i_1,alpha_13,(p_4),b^(*),i_0,alpha_3,(p_1)_u,b,i_2,alpha_0,(p_2)_v,),Prod(,p_1,alpha_11,gamma,alpha_11,alpha_7,alpha_8,gamma,alpha_12,alpha_4,alpha_7,gamma,alpha_13,alpha_8,alpha_1,A,i_3,alpha_12,(p_3),A,i_1,alpha_13,(p_4),b^(*),i_0,alpha_4,(p_1)_u,b,i_2,alpha_1,(p_2)_v,),Prod(,-1,p_3,alpha_11,gamma,alpha_11,alpha_9,alpha_10,gamma,alpha_12,alpha_5,alpha_9,gamma,alpha_13,alpha_10,alpha_2,A,i_3,alpha_12,(p_3),A,i_1,alpha_13,(p_4),b^(*),i_0,alpha_5,(p_1)_u,b,i_2,alpha_2,(p_2)_v,),),)"
    arr = arr.split(",")
    res = ampl_to_tree(arr)


def test_tree_to_prefix():
    arr = ["Prod", "-1/2", "Pow", "e", "2"]
    tree = ampl_to_tree(arr)
    round_trip = tree_to_prefix(tree)
    assert arr == round_trip

    arr = ["Prod", "-1/2", "gamma", "alpha_1", "alpha_2", "alpha_3"]
    tree = ampl_to_tree(arr)
    round_trip = tree_to_prefix(tree)
    assert arr == round_trip

    arr = ["Prod", "Pow", "i", "-1/2", "gamma", "alpha_1", "alpha_2", "alpha_3"]
    tree = ampl_to_tree(arr)
    round_trip = tree_to_prefix(tree)
    assert arr == round_trip


    arr = "Prod(,1/9,i,Pow,e,2,Pow,Sum(,Pow,m_b,2,Prod,-1,s_11,Prod,2,s_13,Prod,-1,s_33,Prod,-1,reg_prop,),-1,Sum(,Prod(,m_b,gamma,alpha_12,alpha_3,alpha_6,gamma,alpha_13,alpha_6,alpha_0,A,i_3,alpha_12,(p_3),A,i_1,alpha_13,(p_4),b^(*),i_0,alpha_3,(p_1)_u,b,i_2,alpha_0,(p_2)_v,),Prod(,p_1,alpha_11,gamma,alpha_11,alpha_7,alpha_8,gamma,alpha_12,alpha_4,alpha_7,gamma,alpha_13,alpha_8,alpha_1,A,i_3,alpha_12,(p_3),A,i_1,alpha_13,(p_4),b^(*),i_0,alpha_4,(p_1)_u,b,i_2,alpha_1,(p_2)_v,),Prod(,-1,p_3,alpha_11,gamma,alpha_11,alpha_9,alpha_10,gamma,alpha_12,alpha_5,alpha_9,gamma,alpha_13,alpha_10,alpha_2,A,i_3,alpha_12,(p_3),A,i_1,alpha_13,(p_4),b^(*),i_0,alpha_5,(p_1)_u,b,i_2,alpha_2,(p_2)_v,),),)"
    arr = arr.split(",")
    tree = ampl_to_tree(arr)
    round_trip = tree_to_prefix(tree, hybrid=True)
    assert arr == round_trip

def test_tree_to_prefix_hybrid():
    arr = ["Prod(", "-1/2", "a", "c", ")"]  # )
    tree = ampl_to_tree(arr, remove_hybrid_parentheses=True)
    round_trip = tree_to_prefix(tree)
    round_trip = tree_to_prefix(tree, hybrid=True)
    assert round_trip == arr
    

def test_round_trips():
    arr = ["Prod(", "-1/2", "a", "c", "d", ")"]  # )
    tree = ampl_to_tree(arr, remove_hybrid_parentheses=True)
    round_trip = tree_to_prefix(tree, hybrid=True)
    assert round_trip == arr
    
    arr_2 = ["Prod", "-1/2", "Prod", "a", "Prod", "c", "d"]  # )
    tree_2 = ampl_to_tree(arr_2, remove_hybrid_parentheses=True)
    round_trip = tree_to_prefix(tree_2, hybrid=True)
    ic(arr)
    ic(arr_2)
    ic(round_trip)
    # assert round_trip == arr

def test_expand_tree():
    arr = ["Prod(", "-1/2", "a", "c", "d", ")"]  # )
    tree = ampl_to_tree(arr, remove_hybrid_parentheses=True)
    tree_1 = ampl_to_tree(arr, remove_hybrid_parentheses=False)
    print("tree")
    tree.pretty_print()
    expand_tree(tree).pretty_print()
    print("tree1")
    tree_1.pretty_print()
    expand_tree(tree_1).pretty_print()

    print("tree2")
    arr_2 = ["Prod", "-1/2","Prod", "a", "Prod", "c", "d"]  # )
    tree_2 = ampl_to_tree(arr_2, remove_hybrid_parentheses=True)
    ic(expand_tree(tree_2))
    tree_2.pretty_print()

    print("tree3")
    arr_3 = ["Prod(", "-1/2", "a", "c", "Sum(", "1", "2", "3", ")", ")"]  # )
    tree_3 = ampl_to_tree(arr_3, remove_hybrid_parentheses=True)
    tree_3.pretty_print()
    expand_tree(tree_3).pretty_print()

    arr_4 = "Prod(,1/9,i,Pow,e,2,Pow,Sum(,Pow,m_b,2,Prod,-1,s_11,Prod,2,s_13,Prod,-1,s_33,Prod,-1,reg_prop,),-1,Sum(,Prod(,m_b,gamma,alpha_12,alpha_3,alpha_6,gamma,alpha_13,alpha_6,alpha_0,A,i_3,alpha_12,(p_3),A,i_1,alpha_13,(p_4),b^(*),i_0,alpha_3,(p_1)_u,b,i_2,alpha_0,(p_2)_v,),Prod(,p_1,alpha_11,gamma,alpha_11,alpha_7,alpha_8,gamma,alpha_12,alpha_4,alpha_7,gamma,alpha_13,alpha_8,alpha_1,A,i_3,alpha_12,(p_3),A,i_1,alpha_13,(p_4),b^(*),i_0,alpha_4,(p_1)_u,b,i_2,alpha_1,(p_2)_v,),Prod(,-1,p_3,alpha_11,gamma,alpha_11,alpha_9,alpha_10,gamma,alpha_12,alpha_5,alpha_9,gamma,alpha_13,alpha_10,alpha_2,A,i_3,alpha_12,(p_3),A,i_1,alpha_13,(p_4),b^(*),i_0,alpha_5,(p_1)_u,b,i_2,alpha_2,(p_2)_v,),),)"
    arr_4 = arr_4.split(",")
    tree_4 = ampl_to_tree(arr_4)
    expand_tree(tree_4).pretty_print()


def test_contract_tree():
    print("---")
    arr = ["Prod(", "-1/2", "a", "c", "d", ")"]  # )
    tree = ampl_to_tree(arr, remove_hybrid_parentheses=True)
    tree.pretty_print()
    tree_expanded = expand_tree(tree)
    tree_expanded.pretty_print()
    tree_contracted = contract_tree(tree_expanded)
    tree_contracted.pretty_print()

    print("---")
    arr_2 = ["Prod", "-1/2","Prod", "a", "Prod", "c", "d"]  # )
    tree_2 = ampl_to_tree(arr_2, remove_hybrid_parentheses=True)
    tree_2.pretty_print()
    tree_2_contracted = contract_tree(tree_2)
    tree_2_contracted.pretty_print()

    print("---")
    arr_3 = ["Prod(", "-1/2", "a", "c", "Sum(", "1", "2", "3", ")", ")"]  # )
    tree_3 = ampl_to_tree(arr_3, remove_hybrid_parentheses=True)
    tree_3.pretty_print()
    tree_3_contracted = contract_tree(tree_3)
    tree_3_contracted.pretty_print()
    tree_3_round_trip = expand_tree(tree_3_contracted)
    tree_3_round_trip = contract_tree(tree_3_round_trip, add_opening_bracket=False)
    assert tree_3_round_trip == tree_3

    print("---")
    print("testing expand contract roundtrip")
    arr_4 = "Prod(,1/9,i,Pow,e,2,Pow,Sum(,Pow,m_b,2,Prod,-1,s_11,Prod,2,s_13,Prod,-1,s_33,Prod,-1,reg_prop,),-1,Sum(,Prod(,m_b,gamma,alpha_12,alpha_3,alpha_6,gamma,alpha_13,alpha_6,alpha_0,A,i_3,alpha_12,(p_3),A,i_1,alpha_13,(p_4),b^(*),i_0,alpha_3,(p_1)_u,b,i_2,alpha_0,(p_2)_v,),Prod(,p_1,alpha_11,gamma,alpha_11,alpha_7,alpha_8,gamma,alpha_12,alpha_4,alpha_7,gamma,alpha_13,alpha_8,alpha_1,A,i_3,alpha_12,(p_3),A,i_1,alpha_13,(p_4),b^(*),i_0,alpha_4,(p_1)_u,b,i_2,alpha_1,(p_2)_v,),Prod(,-1,p_3,alpha_11,gamma,alpha_11,alpha_9,alpha_10,gamma,alpha_12,alpha_5,alpha_9,gamma,alpha_13,alpha_10,alpha_2,A,i_3,alpha_12,(p_3),A,i_1,alpha_13,(p_4),b^(*),i_0,alpha_5,(p_1)_u,b,i_2,alpha_2,(p_2)_v,),),)"
    arr_4 = arr_4.split(",")
    print("base tree")
    tree_4 = ampl_to_tree(arr_4)
    tree_4.pretty_print(unicodelines=True)
    print("expanded tree")
    tree_4_expanded = expand_tree(tree_4)
    tree_4_expanded.pretty_print(unicodelines=True)
    print("roundtrip")
    tree_4_roundtrip = contract_tree(tree_4_expanded)
    tree_4_roundtrip.pretty_print(unicodelines=True)
    assert tree_4 == tree_4_roundtrip
    

def round_trip_expand_contract(ampl):
    """
    Check if the given amplitude (as array) is correctly round-trip encoded.
    Here round trip means expand and contract.
    The amplitude is first converted to a tree using `ampl_to_tree`.
    Since I'm too lazy to check if the amplitude is already in hybrid or in normal form,
    I expand, contract and expand again.

    """
    tree = ampl_to_tree(ampl)
    tree_expanded = expand_tree(tree)
    tree_contracted = contract_tree(tree_expanded, add_opening_bracket=True)
    tree_round_trip = expand_tree(tree_contracted)
    assert tree_expanded == tree_round_trip


def test_real_amplitudes_round_trips_expand_contract():
    ampls_file = "data.nosync/QED_amplitudes_TreeLevel_2to2.txt"
    with open(ampls_file) as f:
        ampls = f.readlines()
        ampls = [a[:-1] for a in ampls]  # remove new line character in each element

    # for i in range(len(ampls)):
    for i in [0, 20, 100, -1, -20, -100]:
        ampl = ampls[i].split(",")
        round_trip_expand_contract(ampl)


    ampls_file = "data.nosync/QED_amplitudes_TreeLevel_3to2.txt"
    with open(ampls_file) as f:
        ampls = f.readlines(1000000)  # how many bites, this is 1079 lines
        ampls = [a[:-1] for a in ampls]  # remove new line character in each element

    # for i in range(len(ampls)):
    for i in [0, 20, 100, -1, -20, -100]:
        ampl = ampls[i].split(",")
        round_trip_expand_contract(ampl)
