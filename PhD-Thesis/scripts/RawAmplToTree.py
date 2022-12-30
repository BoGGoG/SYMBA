import sys
import os
from icecream import ic 
import numpy as np
import sympy as sp
from nltk.tree import Tree
from nltk.draw.tree import TreeView
from nltk.draw.util import CanvasFrame
from nltk.draw import TreeWidget
from nltk.draw.util import CanvasFrame

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
parent = os.path.dirname(parent)
parent = os.path.join(parent, "data_preprocessing", "converters")
sys.path.append(parent)

import sympy as sp
from ampl2tree.source.ampl2tree import ampl_to_tree, rightmost_operator_pos, func_to_tree, tree_to_prefix, expand_tree, contract_tree, get_tree, ampl_raw_tree_to_nltk
from ampl2tree.source.ampl2tree import has_subscript, subscripts_to_subtree, is_basis_func, basis_function_to_subtree, nltk_tree_expand_subscripts, p_sub_to_tree
from ampl2tree.source.ampl2tree import rename_indices, collect_indices, is_index, raw_ampl_to_tree, categorize_indices, get_index_replacements, nltk_tree_replace_leaves

expr = "Prod;(; -1;i;e;gamma_{%\sigma_111,%del_165,%del_166};A_{l_3,+%\sigma_111}(p_3)^(*);e_{i_3,%del_166}(p_1)_u;e_{k_3,%del_165}(p_2)_v^(*);)".split(";") #)
tree_raw = get_tree(expr)
tree = ampl_raw_tree_to_nltk(tree_raw)
print(tree_raw)                  
print("Tree after reading in")
tree.pretty_print(abbreviate=4, unicodelines=False)

print("Tree after expanding of subscripts")
tree = nltk_tree_expand_subscripts(tree)
tree.pretty_print(abbreviate=False, unicodelines=False)
tree.pretty_print(abbreviate=5, unicodelines=False)

tree.pretty_print(abbreviate=False, unicodelines=False)

tree = rename_indices(tree)
tree.pretty_print(abbreviate=False, unicodelines=False)


# cf = CanvasFrame()
# tc = TreeWidget(cf.canvas(),tree)
# tc['node_font'] = 'arial 14 bold'
# tc['leaf_font'] = 'arial 14'
# tc['node_color'] = '#005990'
# tc['leaf_color'] = '#3F8F57'
# tc['line_color'] = '#175252'
# # tc['abbreviate'] = True
# cf.add_widget(tc,10,10) # (10,10) offsets
# cf.print_to_file('figures/tree-ampl-in_electron_in_anti_electron_out_photon.pdf')
# cf.destroy()
