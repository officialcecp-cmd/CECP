import ast

with open('landing/views.py', 'rb') as f:
    content = f.read().decode('latin-1')

tree = ast.parse(content)
func_code = ""
for node in tree.body:
    if isinstance(node, ast.FunctionDef) and node.name == 'submit_project':
        func_code = ast.unparse(node)

with open('func_dump.txt', 'w', encoding='utf-8') as f:
    f.write(func_code)
