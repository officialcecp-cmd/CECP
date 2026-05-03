import os

def remove_from_file(filepath, strings_to_remove):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False
    for old_str in strings_to_remove:
        if old_str in content:
            content = content.replace(old_str, "")
            modified = True
            
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Patched {filepath}")
    else:
        print(f"No match in {filepath}")

# For index.html
index_path = 'landing/templates/landing/index.html'
index_strs = [
    '<span class="w-1 h-1 rounded-full bg-cyan-600"></span>\n                                        <span>{{ blog.read_time|default:"5 min read" }}</span>'
]
remove_from_file(index_path, index_strs)

# For blog_detail.html
blog_path = 'landing/templates/landing/blog_detail.html'
blog_strs = [
    '<span class="w-1.5 h-1.5 rounded-full bg-cyan-600"></span>\n            <span>{{ blog.read_time|default:"5 min read" }}</span>'
]
remove_from_file(blog_path, blog_strs)
