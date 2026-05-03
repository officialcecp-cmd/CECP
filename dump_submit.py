import ast

with open('landing/views.py', 'rb') as f:
    content = f.read().decode('latin-1')

tree = ast.parse(content)
for node in tree.body:
    if isinstance(node, ast.FunctionDef) and node.name == 'submit_project':
        print(ast.unparse(node))
