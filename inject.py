import re

html_path = "/Users/shakhgildyangy/mosnauka/catalog.html"
cards_path = "/Users/shakhgildyangy/Downloads/RnD_MAP/catalog_cards.html"

with open(cards_path, "r", encoding="utf-8") as f:
    cards_html = f.read()

with open(html_path, "r", encoding="utf-8") as f:
    text = f.read()

# I will replace everything between `<div class="grid grid-cols-1 md:grid-cols-2 gap-6">`
# and `            </div>\n            <!-- Pagination -->`

pattern = r'(<div class="grid grid-cols-1 md:grid-cols-2 gap-6">)(.*?)(</div>\s*<!-- Pagination -->)'
replacement = r'\1\n' + cards_html + r'\n            \3'

new_text, count = re.subn(pattern, replacement, text, flags=re.DOTALL)

if count > 0:
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(new_text)
    print("Injection successful.")
else:
    print("Failed to find replacement target.")
