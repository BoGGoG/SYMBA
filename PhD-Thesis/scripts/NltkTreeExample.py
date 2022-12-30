from nltk import Tree

tree = Tree("+", ["2", Tree("*", ["3", Tree("+", ["5", "2"])])])
tree.pretty_print()
