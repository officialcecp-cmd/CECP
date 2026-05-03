import re

with open('landing/templates/landing/index.html', 'rb') as f:
    content = f.read()

# Replace the specific href="#" for the Read button inside the blog loop
old_button = b'<a href="#"\n                                            class="text-cyan-400 hover:text-cyan-300 text-sm font-semibold flex items-center gap-2 group/btn bg-cyan-400/10 hover:bg-cyan-400/20 px-4 py-2 rounded-lg transition-colors">\n                                            Read'

new_button = b'<a href="{% url \'landing:blog_detail\' blog.id %}"\n                                            class="text-cyan-400 hover:text-cyan-300 text-sm font-semibold flex items-center gap-2 group/btn bg-cyan-400/10 hover:bg-cyan-400/20 px-4 py-2 rounded-lg transition-colors">\n                                            Read'

if old_button in content:
    content = content.replace(old_button, new_button)
    print("Button replaced successfully!")
else:
    # Try replacing \r\n
    old_button_windows = b'<a href="#"\r\n                                            class="text-cyan-400 hover:text-cyan-300 text-sm font-semibold flex items-center gap-2 group/btn bg-cyan-400/10 hover:bg-cyan-400/20 px-4 py-2 rounded-lg transition-colors">\r\n                                            Read'
    new_button_windows = b'<a href="{% url \'landing:blog_detail\' blog.id %}"\r\n                                            class="text-cyan-400 hover:text-cyan-300 text-sm font-semibold flex items-center gap-2 group/btn bg-cyan-400/10 hover:bg-cyan-400/20 px-4 py-2 rounded-lg transition-colors">\r\n                                            Read'
    if old_button_windows in content:
        content = content.replace(old_button_windows, new_button_windows)
        print("Button replaced successfully (Windows line endings)!")
    else:
        print("Could not find the button to replace.")

with open('landing/templates/landing/index.html', 'wb') as f:
    f.write(content)
