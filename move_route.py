import re

with open('tax-support.html', 'r', encoding='utf-8') as f:
    html = f.read()

route_pattern = re.compile(r'(<!-- Service Formula \(Route\) -->.*?\s+)<!-- Artifacts for Business -->', re.DOTALL)
route_match = route_pattern.search(html)

if route_match:
    route_block = route_match.group(1)
    # Remove the route block from its original position
    html = html.replace(route_block, '')
    
    # Insert before <!-- Problem Intro -->
    split_target = '<!-- Problem Intro -->'
    if split_target in html:
        parts = html.split(split_target)
        new_html = parts[0] + route_block + split_target + parts[1]
        with open('tax-support.html', 'w', encoding='utf-8') as f:
            f.write(new_html)
        print("Successfully moved Route section")
    else:
        print("Target 'Problem Intro' not found")
else:
    print("Route section not found")
