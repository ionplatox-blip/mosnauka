import re

paths = [
    "/Users/shakhgildyangy/mosnauka/catalog.html",
    "/Users/shakhgildyangy/mosnauka/index.html"
]

for fpath in paths:
    with open(fpath, "r", encoding="utf-8") as f:
        text = f.read()
    
    def replacer(m):
        inner = m.group(1).replace('"', '&quot;')
        return f'onclick="openProfileModal(\'{inner}\')"'
        
    new_text = re.sub(r'onclick="openProfileModal\(\'(.*?)\'\)"', replacer, text)
    
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(new_text)

print("Quotes fixed.")
