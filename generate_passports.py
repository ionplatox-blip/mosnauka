import json
import html
import os
from pathlib import Path

def esc(text):
    """Escape text for safe HTML insertion."""
    if text is None:
        return ''
    return html.escape(str(text))

# Paths
DATA_DIR = Path("/Users/shakhgildyangy/COLAB_DATA/passports")
OUTPUT_DIR = Path("/Users/shakhgildyangy/mosnauka")
INDEX_JSON = DATA_DIR / "index.json"

# HTML Template for a Passport
PASSPORT_TEMPLATE = """<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8" />
    <meta content="width=device-width, initial-scale=1.0" name="viewport" />
    <title>МОСНАУКА — Паспорт: {name_short}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/@phosphor-icons/web"></script>
    <style>
      body {{ font-family: Inter, system-ui, sans-serif; background: #050505; color: white; }}
      .glass {{ background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); }}
      .mos-red {{ color: #ff003c; }}
      .mos-bg-red {{ background: #ff003c; }}
      .provenance-tag {{ font-size: 8px; font-weight: 900; text-transform: uppercase; letter-spacing: 0.1em; padding: 2px 6px; border-radius: 4px; }}
      .tag-egisu {{ background: rgba(0, 120, 255, 0.1); color: #40a0ff; border: 1px solid rgba(0, 120, 255, 0.2); }}
      .tag-colab {{ background: rgba(255, 0, 60, 0.1); color: #ff4070; border: 1px solid rgba(255, 0, 60, 0.2); }}
      .tag-org {{ background: rgba(255, 255, 255, 0.05); color: #aaa; border: 1px solid rgba(255, 255, 255, 0.1); }}
    </style>
  </head>
  <body>
    <div class="min-h-screen bg-[radial-gradient(circle_at_top_left,rgba(255,0,60,0.12),transparent_25%),radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_20%),linear-gradient(180deg,#050505,#0b0f16)]">
      
      <!-- Header -->
      <header class="sticky top-0 z-30 backdrop-blur-md border-b border-white/10 bg-black/40">
        <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <a class="text-2xl font-black italic tracking-tight uppercase hover:opacity-80 transition" href="index.html">
            МОС<span class="mos-red">НАУКА</span>
          </a>
          <div class="flex items-center gap-4">
            <span class="text-[10px] uppercase tracking-widest text-zinc-500 font-bold">Паспорт организации v1.0</span>
            <a href="catalog.html" class="text-xs font-bold uppercase hover:text-red-500 transition">Реестр</a>
          </div>
        </div>
      </header>

      <main class="max-w-7xl mx-auto px-6 py-10">
        <!-- Breadcrumbs & Action -->
        <div class="mb-10 flex items-center justify-between">
          <div class="flex items-center gap-2 text-[10px] uppercase font-bold tracking-widest text-zinc-500">
            <a href="index.html" class="hover:text-white">Главная</a>
            <span>/</span>
            <a href="catalog.html" class="hover:text-white">Реестр</a>
            <span>/</span>
            <span class="text-zinc-300">{name_short}</span>
          </div>
          <a href="catalog.html" class="px-5 py-2 border border-white/10 rounded-full text-[10px] font-black uppercase tracking-widest hover:bg-white/5 transition">
            ← К списку
          </a>
        </div>

        <!-- Hero Section -->
        <section class="grid lg:grid-cols-[1fr_350px] gap-8 mb-12">
          <div class="glass rounded-[2.5rem] p-10 flex flex-col justify-between relative overflow-hidden">
            <div class="absolute top-0 right-0 p-8 opacity-5 pointer-events-none">
                <img src="{logo_url}" class="w-64 h-64 grayscale invert" alt="">
            </div>
            
            <div class="relative z-10">
              <div class="flex items-center gap-4 mb-6">
                <div class="w-20 h-20 rounded-2xl bg-white p-2 flex items-center justify-center shrink-0">
                  <img src="{logo_url}" class="max-w-full max-h-full object-contain" alt="{name_short_escaped} logo">
                </div>
                <div>
                  <h1 class="text-3xl md:text-5xl font-black tracking-tight uppercase leading-tight mb-2">{name_short}</h1>
                  <p class="text-zinc-400 font-medium">{name_full}</p>
                </div>
              </div>

              <div class="flex flex-wrap gap-4 mt-8">
                <div class="flex items-center gap-2 text-zinc-400 text-sm italic">
                  <i class="ph ph-map-pin mos-red"></i>
                  <span>{address}</span>
                </div>
                <a href="{website}" target="_blank" class="flex items-center gap-2 text-zinc-300 text-sm hover:text-white transition">
                  <i class="ph ph-globe mos-red"></i>
                  <span>{website_short}</span>
                </a>
              </div>
            </div>

            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-12 relative z-10">
              <div class="p-4 rounded-2xl bg-white/5 border border-white/10">
                <div class="text-[9px] uppercase font-black text-zinc-500 mb-1">Лаборатории</div>
                <div class="text-3xl font-black italic">{metrics_labs}</div>
              </div>
              <div class="p-4 rounded-2xl bg-white/5 border border-white/10">
                <div class="text-[9px] uppercase font-black text-zinc-500 mb-1">Ученые</div>
                <div class="text-3xl font-black italic">{metrics_scientists}</div>
              </div>
              <div class="p-4 rounded-2xl bg-white/5 border border-white/10">
                <div class="text-[9px] uppercase font-black text-zinc-500 mb-1">Проекты НИОКР</div>
                <div class="text-3xl font-black italic">{metrics_projects}</div>
              </div>
              <div class="p-4 rounded-2xl bg-white/5 border border-white/10">
                <div class="text-[9px] uppercase font-black text-zinc-500 mb-1">РИД</div>
                <div class="text-3xl font-black italic">{metrics_rid}</div>
              </div>
            </div>
          </div>

          <div class="flex flex-col gap-6">
            <div class="glass rounded-[2rem] p-8 flex-1">
              <div class="flex justify-between items-center mb-6">
                <h3 class="text-xs font-black uppercase tracking-widest text-zinc-400">Ведущий коллектив</h3>
                <span class="provenance-tag tag-colab">CoLab Data</span>
              </div>
              <div class="space-y-4">
                {scientists_html}
              </div>
            </div>
            <div class="glass rounded-[2rem] p-8 bg-red-600/5 border-red-500/20">
               <h3 class="text-xs font-black uppercase tracking-widest text-red-400 mb-4">Статус центра</h3>
               <div class="flex items-center gap-3 mb-6">
                 <div class="w-3 h-3 rounded-full mos-bg-red animate-pulse"></div>
                 <span class="text-sm font-bold uppercase">Активен в экосистеме</span>
               </div>
               <button class="w-full py-4 bg-white text-black font-black uppercase text-[10px] tracking-widest rounded-xl hover:bg-zinc-200 transition shadow-xl">
                 Запросить НИОКР
               </button>
            </div>
          </div>
        </section>

        <!-- Main Content Tabs Like Structure -->
        <div class="grid lg:grid-cols-2 gap-8">
          
          <!-- LEFT: Technical Capacity (CoLab) -->
          <div class="space-y-8">
            <div class="flex items-center justify-between px-2">
              <h2 class="text-2xl font-black uppercase italic tracking-tight">Инфраструктура и компетенции</h2>
              <span class="provenance-tag tag-colab">Агрегированные данные CoLab.ws</span>
            </div>
            
            <div class="space-y-6">
              {laboratories_html}
            </div>
          </div>

          <!-- RIGHT: Official Activity (EGISU) -->
          <div class="space-y-8">
            <div class="flex items-center justify-between px-2">
              <h2 class="text-2xl font-black uppercase italic tracking-tight">Официальные результаты</h2>
              <span class="provenance-tag tag-egisu">Верифицировано ЕГИСУ</span>
            </div>

            <!-- EGISU Projects -->
            <div class="glass rounded-[2.5rem] p-8 overflow-hidden">
              <div class="flex items-center gap-3 mb-6 font-black uppercase text-[10px] tracking-widest text-blue-400">
                <i class="ph ph-briefcase-metal text-lg"></i>
                <span>Инвентаризация НИОКР</span>
              </div>
              <div class="space-y-6">
                {projects_html}
              </div>
            </div>

            <!-- EGISU RID -->
            <div class="glass rounded-[2.5rem] p-8">
              <div class="flex items-center gap-3 mb-6 font-black uppercase text-[10px] tracking-widest text-purple-400">
                 <i class="ph ph-certificate text-lg"></i>
                 <span>Интеллектуальная собственность</span>
              </div>
              <div class="space-y-4">
                {rid_html}
              </div>
            </div>

            <!-- Organization Editable Section Placeholder -->
            <div class="glass rounded-[2.5rem] p-8 border-dashed border-zinc-700 bg-transparent">
               <div class="flex items-center justify-between mb-6">
                 <div class="flex items-center gap-3 font-black uppercase text-[10px] tracking-widest text-zinc-500">
                    <i class="ph ph-note-pencil text-lg"></i>
                    <span>Дополнительно от организации</span>
                 </div>
                 <span class="provenance-tag tag-org">Ожидает заполнения</span>
               </div>
               <p class="text-xs text-zinc-600 italic">Секция для внесения уточнений, актуальных контактов и расширенного портфолио. Редактируется уполномоченным представителем организации.</p>
            </div>

          </div>
        </div>
      </main>

      <!-- Footer -->
      <footer class="py-20 border-t border-white/10 mt-20 bg-black/40">
        <div class="max-w-7xl mx-auto px-6 text-center">
          <div class="text-3xl font-black italic uppercase mb-8">МОС<span class="mos-red">НАУКА</span></div>
          <p class="text-zinc-500 text-sm max-w-2xl mx-auto italic mb-12">Единая экосистема технологического развития площадок и заказчиков в Москве.</p>
          <div class="text-white/20 text-[10px] uppercase font-bold tracking-[0.5em]">&copy; 2026 ЦИФРОВОЙ ПАСПОРТ ОБЪЕКТА</div>
        </div>
      </footer>
    </div>
  </body>
</html>
"""

def format_scientist(s):
    name = esc(s.get('name', 'N/A'))
    h_index = esc(s.get('h_index', '—'))
    url = esc(s.get('url', '#'))
    return f'''
    <div class="flex items-center justify-between p-4 rounded-2xl bg-white/5 border border-white/10 group hover:border-red-500/30 transition">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-full bg-zinc-800 flex items-center justify-center text-zinc-500">
          <i class="ph ph-user"></i>
        </div>
        <div>
          <div class="text-sm font-bold">{name}</div>
          <div class="text-[10px] text-zinc-500 uppercase tracking-wider">h-index: {h_index}</div>
        </div>
      </div>
      <a href="{url}" target="_blank" class="text-zinc-500 hover:text-white transition">
        <i class="ph ph-arrow-square-out text-lg"></i>
      </a>
    </div>'''

def format_laboratory(l):
    tags = "".join([f'<span class="px-2 py-1 rounded-md bg-white/5 border border-white/10 text-[9px] uppercase font-bold text-zinc-400">{esc(t)}</span>' for t in l.get('tags', [])[:3]])
    equipment = esc(l.get('equipment', ''))
    if len(equipment) > 150: equipment = equipment[:147] + "..."
    name = esc(l.get('name', 'Laboratory'))
    desc = esc(l.get('description', '')[:200])
    url = esc(l.get('url', '#'))
    scientists_count = esc(l.get('scientists_count', '—'))
    
    return f'''
    <div class="glass rounded-[2rem] p-8 group hover:border-red-500/30 transition shadow-lg">
      <div class="flex flex-wrap gap-2 mb-4">{tags}</div>
      <h3 class="text-xl font-bold mb-3 group-hover:text-red-500 transition">{name}</h3>
      <p class="text-xs text-zinc-400 leading-relaxed mb-6">{desc}...</p>
      
      {f'<div class="p-4 rounded-xl bg-black/40 border border-white/5"><div class="text-[9px] uppercase font-black text-zinc-500 mb-2 italic">Комплекс оборудования</div><div class="text-[11px] text-zinc-300 leading-snug">{equipment}</div></div>' if equipment else ''}
      
      <div class="mt-6 flex items-center justify-between">
        <span class="text-[10px] font-black uppercase text-zinc-500">Штат: {scientists_count} чел.</span>
        <a href="{url}" target="_blank" class="text-[10px] font-black uppercase tracking-widest flex items-center gap-2 hover:text-red-500 transition">
          Подробнее <i class="ph ph-arrow-right"></i>
        </a>
      </div>
    </div>'''

def format_project(p):
    keywords = "".join([f'<span class="p-1 px-2 rounded-md bg-blue-500/5 text-[9px] text-blue-300 border border-blue-500/10">#{esc(k)}</span>' for k in p.get('keyword_list', [])[:4]])
    reg_num = esc(p.get('registration_number', '—'))
    name = esc(p.get('name', 'N/A'))
    abstract = esc(p.get('abstract', '—'))
    return f'''
    <div class="p-5 rounded-2xl bg-white/5 border border-white/5 hover:border-blue-500/20 transition group">
      <div class="text-[9px] font-black text-zinc-500 mb-2 uppercase tracking-widest">{reg_num}</div>
      <h4 class="text-sm font-bold mb-3 leading-snug group-hover:text-blue-400 transition">{name}</h4>
      <p class="text-[10px] text-zinc-500 line-clamp-2 mb-4 italic">{abstract}</p>
      <div class="flex flex-wrap gap-2 mb-4">{keywords}</div>
      <div class="flex items-center justify-between pt-4 border-t border-white/5">
         <span class="text-[10px] font-bold text-blue-500/80 uppercase">Бюджет верифицирован</span>
         <span class="text-[10px] font-black text-zinc-400 italic">2024-2025</span>
      </div>
    </div>'''

def format_rid(r):
    name = esc(r.get('name', 'N/A'))
    rid_type = esc(r.get('rid_type', 'Patent/RID'))
    reg_num = esc(r.get('registration_number', '—'))
    return f'''
    <div class="flex items-start gap-3 p-4 rounded-xl bg-white/5 border border-white/5 text-xs">
      <div class="w-8 h-8 rounded-lg bg-purple-500/10 flex items-center justify-center shrink-0">
        <i class="ph ph-files text-purple-400"></i>
      </div>
      <div>
        <div class="font-bold text-zinc-300 mb-1 leading-tight">{name}</div>
        <div class="text-[9px] uppercase font-black text-zinc-600 tracking-wider font-mono">{rid_type} | {reg_num}</div>
      </div>
    </div>'''

def generate_catalog(orgs):
    cards_html = ""
    for org in orgs:
        cards_html += f'''
        <a href="passport-{org['slug']}.html" class="glass p-8 rounded-[2rem] hover:border-red-500/50 transition group flex flex-col justify-between">
          <div>
            <div class="w-16 h-16 bg-white rounded-xl p-2 mb-6 flex items-center justify-center">
              <img src="{org['logo_url']}" class="max-w-full max-h-full object-contain" alt="">
            </div>
            <h3 class="text-xl font-black uppercase mb-2 group-hover:text-red-500 transition">{esc(org['name_short'])}</h3>
            <p class="text-xs text-zinc-500 line-clamp-2 mb-6">{esc(org['name_full'])}</p>
          </div>
          <div class="grid grid-cols-3 gap-2 border-t border-white/10 pt-6">
            <div class="text-center">
                <div class="text-[8px] uppercase font-black text-zinc-600 mb-1">Лабы</div>
                <div class="font-black italic">{org['colab_labs']}</div>
            </div>
            <div class="text-center">
                <div class="text-[8px] uppercase font-black text-zinc-600 mb-1">НИОКР</div>
                <div class="font-black italic text-blue-400">{org['egisu_projects']}</div>
            </div>
            <div class="text-center">
                <div class="text-[8px] uppercase font-black text-zinc-600 mb-1">РИД</div>
                <div class="font-black italic text-purple-400">{org['egisu_rid']}</div>
            </div>
          </div>
        </a>'''
    
    html = f"""<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8" />
    <meta content="width=device-width, initial-scale=1.0" name="viewport" />
    <title>МОСНАУКА — Реестр паспортов</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
      body {{ font-family: Inter, system-ui, sans-serif; background: #050505; color: white; }}
      .glass {{ background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); }}
      .mos-red {{ color: #ff003c; }}
    </style>
  </head>
  <body>
    <div class="min-h-screen bg-[radial-gradient(circle_at_top_left,rgba(255,0,60,0.1),transparent_30%),linear-gradient(180deg,#050505,#0b0f16)]">
      <header class="sticky top-0 z-30 backdrop-blur-md border-b border-white/10 bg-black/40">
        <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <a class="text-2xl font-black italic tracking-tight uppercase" href="index.html">МОС<span class="mos-red">НАУКА</span></a>
        </div>
      </header>

      <main class="max-w-7xl mx-auto px-6 py-16">
        <div class="mb-16">
          <h1 class="text-5xl md:text-7xl font-black uppercase italic tracking-tighter mb-6">Реестр паспортов</h1>
          <p class="text-xl text-zinc-400 font-light max-w-2xl italic leading-relaxed">
            Цифровые профили ведущих научно-исследовательских центров Москвы с верифицированными данными ЕГИСУ и CoLab.
          </p>
        </div>

        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {cards_html}
        </div>
      </main>
    </div>
  </body>
</html>"""
    with open(OUTPUT_DIR / "catalog.html", "w") as f:
        f.write(html)

def main():
    with open(INDEX_JSON) as f:
        index_data = json.load(f)
    
    catalog_orgs = []

    for org_info in index_data['organizations']:
        print(f"Generating passport for {org_info['name_short']}...")
        org_json_path = DATA_DIR / org_info['file']
        with open(org_json_path) as f:
            org_data = json.load(f)
        
        identity = org_data['identity']
        sc = org_data['source_colab']['data']
        se = org_data['source_egisu']['data']
        metrics_sc = org_data['source_colab']['metrics']
        metrics_se = org_data['source_egisu']['metrics']

        # Format sections
        scientists_html = "".join([format_scientist(s) for s in sc.get('top3_scientists', [])])
        if not scientists_html:
            # Fallback to standalone if top3 empty
            scientists_html = "".join([format_scientist(s) for s in sc.get('standalone_researchers', [])[:3]])

        laboratories_html = "".join([format_laboratory(l) for l in sc.get('laboratories', [])[:6]])
        projects_html = "".join([format_project(p) for p in se.get('projects', [])[:5]])
        rid_html = "".join([format_rid(r) for r in se.get('rid', [])[:5]])

        # Create context
        context = {
            "name_short": esc(identity['name_short']),
            "name_short_escaped": esc(identity['name_short']),
            "name_full": esc(identity['name_full']),
            "logo_url": esc(identity['logo_url']),
            "address": esc(identity['address']),
            "website": esc(identity['website']),
            "website_short": esc(identity['website'].replace('https://', '').replace('http://', '').strip('/')),
            "metrics_labs": metrics_sc['total_laboratories'],
            "metrics_scientists": metrics_sc['total_scientists'],
            "metrics_projects": metrics_se['projects_ikrbs'],
            "metrics_rid": metrics_se['rid_count'],
            "scientists_html": scientists_html or '<p class="text-xs text-zinc-500 italic">Data pending</p>',
            "laboratories_html": laboratories_html or '<p class="text-xs text-zinc-500 italic">No public lab data found</p>',
            "projects_html": projects_html or '<p class="text-xs text-zinc-500 italic">No historical R&amp;D projects found in indexed period</p>',
            "rid_html": rid_html or '<p class="text-xs text-zinc-500 italic">No registered RID found in indexed period</p>'
        }

        passport_html = PASSPORT_TEMPLATE.format(**context)
        with open(OUTPUT_DIR / f"passport-{org_info['slug']}.html", "w") as f:
            f.write(passport_html)
        
        # Collect for catalog
        catalog_orgs.append({
            "slug": org_info['slug'],
            "name_short": org_info['name_short'],
            "name_full": org_info['name_full'],
            "logo_url": identity['logo_url'],
            "colab_labs": metrics_sc['total_laboratories'],
            "egisu_projects": metrics_se['projects_ikrbs'],
            "egisu_rid": metrics_se['rid_count']
        })

    print("Generating catalog...")
    generate_catalog(catalog_orgs)
    print("Done!")

if __name__ == "__main__":
    main()
