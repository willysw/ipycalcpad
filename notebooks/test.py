%pdb on

from IPython.display import display, display_markdown
from ast import parse, dump, unparse
from rich.pretty import install
install()
from transform import UnitRegistry
u = UnitRegistry()

from ipycalcpad import ASTTransformer, PintTransformer, Node

def ps(ast_tree):
    print(dump(ast_tree, indent=2))

def md(text):
    display_markdown(text, raw=True)

def tex(node, subs:bool=False):
    md(f'$${node.get_tex(subs)}$$')

x = 3

atree = parse('1+2*-x**4')
ps(atree)

ptree = PintTransformer(namespace=locals()).visit(atree)
ps(ptree)

tree = ASTTransformer(namespace=locals(), arguments={}).visit(atree)[0]
display(tree)

display(tree.get_tex(subs=False))
tex(tree, False)

display(tree.get_tex(subs=True))
tex(tree, True)

display(tree.get_tex_result())
md(f'$${tree.get_tex_result()}$$')

display(tree.value)

