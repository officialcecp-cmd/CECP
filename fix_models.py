import os

filepath = os.path.join('landing', 'models.py')

try:
    with open(filepath, 'rb') as f:
        content = f.read()
    
    # \x97 is the byte that is causing the issue
    content = content.replace(b'\x97', b'-')
    
    with open(filepath, 'wb') as f:
        f.write(content)
        
    print("Successfully fixed models.py!")
except Exception as e:
    print(f"Error fixing file: {e}")
