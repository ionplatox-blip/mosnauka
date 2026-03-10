import re

def main():
    with open('/Users/shakhgildyangy/mosnauka/tax-support.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Move Route section
    route_pattern = re.compile(r'(<!-- Service Formula \(Route\) -->.*?\s+)<!-- Artifacts for Business -->', re.DOTALL)
    route_match = route_pattern.search(html)

    if route_match:
        route_block = route_match.group(1)
        html = html.replace(route_block, '')
        
        split_target = '<!-- Problem Intro -->'
        if split_target in html:
            parts = html.split(split_target)
            html = parts[0] + route_block + split_target + parts[1]
            print("Successfully moved Route section")
        else:
            print("Target 'Problem Intro' not found")
    else:
        print("Route section not found")

    # 2. Fix Modules Grid Layout
    # Find the <!-- 7 Modules List --> and replace the following <div class="space-y-6">
    grid_target = '<!-- 7 Modules List -->\n        <div class="space-y-6">'
    if grid_target in html:
        html = html.replace(grid_target, '<!-- 7 Modules List -->\n        <div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">')
        print("Successfully updated modules container to grid")
    elif '<!-- 7 Modules List -->\n      <div class="space-y-6">' in html:
        # Prettier formats it with 6 spaces sometimes
        html = html.replace('<!-- 7 Modules List -->\n      <div class="space-y-6">', '<!-- 7 Modules List -->\n      <div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">')
        print("Successfully updated modules container to grid (6 spaces)")

    # 3. Change module cards from flex-row to flex-col to fit grid better
    # Original: class="glass p-8 md:p-10 rounded-[2.5rem] flex flex-col md:flex-row gap-8 items-start group hover:border-red-500/50 transition-all duration-500"
    html = html.replace('flex flex-col md:flex-row gap-8 items-start', 'flex flex-col gap-6 items-start h-full')

    with open('/Users/shakhgildyangy/mosnauka/tax-support.html', 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == '__main__':
    main()
