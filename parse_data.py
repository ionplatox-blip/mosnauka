import json

with open("/Users/shakhgildyangy/.gemini/antigravity/scratch/nioktr-map/map-app/src/data/map_data.json", "r") as f:
    data = json.load(f)

# Get top 20 centers based on project count
top_20 = sorted(data, key=lambda x: x['count'], reverse=True)[:20]

# Generate JS for index.html map
print("--- JS for index.html ---")
js_markers = "const centers = [\n"
for c in top_20:
    name = c['short_name'] if c.get('short_name') else c['name']
    name = name.replace('"', '\\"').replace('\n', ' ')
    js_markers += f"    {{ name: \"{name}\", lat: {c['lat']}, lng: {c['lng']}, count: {c['count']} }},\n"
js_markers += "];"
print(js_markers)

# Generate HTML for catalog.html
print("--- HTML for catalog.html ---")
html_cards = ""
for c in top_20:
    name = c['short_name'] if c.get('short_name') else c['name']
    name = name.replace('\n', ' ')
    city = c['city']
    count = c['count']
    html_cards += f"""
            <!-- Реальный центр -->
            <div class="bg-white/5 border border-white/10 rounded-3xl p-6 md:p-8 hover:bg-white/10 transition-colors group">
                <div class="flex flex-col md:flex-row gap-6 md:gap-8 cursor-pointer" onclick="window.location.href='profile-vuz.html'">
                    <!-- Логотип/Аватар -->
                    <div class="w-20 h-20 md:w-24 md:h-24 bg-gradient-to-br from-red-500/20 to-transparent rounded-2xl border border-red-500/30 flex items-center justify-center shrink-0 group-hover:border-red-500/60 transition-colors">
                        <i class="ph ph-buildings text-3xl md:text-4xl text-red-500"></i>
                    </div>
                    
                    <!-- Инфо -->
                    <div class="flex-1">
                        <div class="flex flex-wrap items-center gap-3 mb-3">
                            <span class="px-3 py-1 bg-red-500/20 text-red-400 border border-red-500/20 rounded-lg text-[10px] font-bold uppercase tracking-wider">НИИ / ВУЗ</span>
                            <span class="text-xs text-gray-400 flex items-center gap-1"><i class="ph ph-map-pin"></i> {city}</span>
                        </div>
                        
                        <h3 class="text-xl md:text-2xl font-bold mb-3 group-hover:text-red-400 transition-colors leading-tight">{name}</h3>
                        
                        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                            <div>
                                <div class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">НИОКТР</div>
                                <div class="text-lg font-bold text-white">{count}</div>
                            </div>
                            <div>
                                <div class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Компетенции</div>
                                <div class="text-lg font-bold text-white">-</div>
                            </div>
                            <div>
                                <div class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Оборудование</div>
                                <div class="text-lg font-bold text-white">-</div>
                            </div>
                            <div>
                                <div class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Рейтинг</div>
                                <div class="text-lg font-bold text-white flex items-center gap-1">
                                    <i class="ph-fill ph-star text-red-500 text-sm"></i>
                                    4.9
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
"""
print(html_cards)

