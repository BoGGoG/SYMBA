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
parent_0 = os.path.join(parent, "data_preprocessing")
parent_1 = os.path.join(parent, "data_preprocessing", "QED-AmplSimplify")
sys.path.append(parent_0)
sys.path.append(parent_1)

from source.helpers import process_ampl_sqampl, shorten_expression_helper
from converters.sp2tree.sp2tree import sympy_to_tree
import sympy as sp

sqampl = "4*e^2*(m_e^2 + 1/2*s_12)"
ic(sqampl)
_, sqampl = process_ampl_sqampl([0, sqampl])
ic(sqampl)
_, sqampl = shorten_expression_helper([0, sqampl])
ic(sqampl)
_, sqampl = process_ampl_sqampl([0, sqampl])
ic(sqampl)
_, sqampl = shorten_expression_helper([0, sqampl])
ic(sqampl)
tree = sympy_to_tree(sqampl)
tree.pretty_print()
