import re

html_path = "/Users/shakhgildyangy/mosnauka/index.html"
cards_path = "/Users/shakhgildyangy/Downloads/RnD_MAP/catalog_cards.html"

with open(cards_path, "r", encoding="utf-8") as f:
    cards_html = f.read()

# Extract the first 3 cards. Each card starts with `<div class="card-item `
card_blocks = re.split(r'(?=<div class="card-item )', cards_html)
card_blocks = [b for b in card_blocks if b.strip()]
top_3_cards = "".join(card_blocks[:3])

with open(html_path, "r", encoding="utf-8") as f:
    text = f.read()

pattern = r'(<div class="grid grid-cols-1 lg:grid-cols-3 gap-8">)(.*?)(</div>\s*</div>\s*</section>)'
replacement = r'\1\n' + top_3_cards + r'\n            \3'

new_text, count = re.subn(pattern, replacement, text, flags=re.DOTALL)

if count > 0:
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(new_text)
    print("Injection into index.html successful.")
else:
    print("Failed to find replacement target in index.html.")
