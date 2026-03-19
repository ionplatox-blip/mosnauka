#!/usr/bin/env python3
"""
МОСНАУКА — Passport Generator v2
Chunk 1: Skeleton, header, hero section with metrics (incl. R&D budget)
Chunk 2: About section with brief + detailed description
Chunk 3: Laboratories section (full-width grid, clickable cards)
Chunk 4: Scientists section (all scientists, photos, search/filter)
Chunk 5: Projects + RID + Footer
"""

import json
import html
import os
from pathlib import Path
from collections import Counter
import re

# ── Paths ──
DATA_DIR = Path("/Users/shakhgildyangy/COLAB_DATA/passports")
OUTPUT_DIR = Path("/Users/shakhgildyangy/mosnauka")
INDEX_JSON = DATA_DIR / "index.json"

def esc(text):
    """Escape text for safe HTML insertion."""
    if text is None:
        return ''
    return html.escape(str(text))


def calculate_total_budget(projects):
    """Sum all project budgets. Returns value in thousands of rubles."""
    total = 0
    for proj in projects:
        for b in proj.get('budgets', []):
            funds = b.get('funds')
            if funds and funds != 'None':
                try:
                    total += float(funds)
                except:
                    pass
    return total


def format_budget(total_thousands):
    """Format budget from thousands to human-readable string."""
    if total_thousands <= 0:
        return '—'
    mlrd = total_thousands / 1_000_000
    if mlrd >= 1:
        return f'{mlrd:.1f} млрд'
    mln = total_thousands / 1_000
    return f'{mln:.0f} млн'


def generate_summary(org):
    """Build natural human-readable org summary (brief + detailed)."""
    ident = org['identity']
    colab = org['source_colab']
    egisu = org['source_egisu']
    name = ident['name_short']

    labs_count = colab['metrics'].get('total_laboratories', 0)
    sci_count = colab['metrics'].get('total_scientists', 0)
    pubs_count = colab['metrics'].get('total_publications', 0)
    projs_count = egisu['metrics'].get('projects_ikrbs', 0)
    rid_count = egisu['metrics'].get('rid_count', 0)

    # Gather keywords from ALL projects + RIDs
    all_keywords = []
    for proj in egisu['data'].get('projects', []):
        all_keywords.extend([k.lower().strip() for k in proj.get('keyword_list', []) if k])
    for rid in egisu['data'].get('rid', []):
        all_keywords.extend([k.lower().strip() for k in rid.get('keyword_list', []) if k])
    kw_counts = Counter(all_keywords)

    # Top keywords (actual from data, not hardcoded)
    # Filter out very short or generic keywords
    top_kws = [kw for kw, cnt in kw_counts.most_common(30) if len(kw) > 3 and cnt >= 2][:12]

    # Thematic clusters (for grouping into research directions)
    clusters = {
        'наноматериалы и двумерные структуры': ['графен', 'двумерные материалы', 'наночастицы',
                               'дихалькогениды переходных металлов', 'наноструктуры', 'гетероструктуры',
                               'нанотехнологии', 'наноматериалы', 'тонкие плёнки'],
        'фотоника, оптика и спектроскопия': ['плазмоника', 'нанофотоника', 'фотоника',
                               'терагерцовое излучение', 'поляритоны', 'спектроскопия', 'лазер', 'оптика'],
        'искусственный интеллект и вычислительное моделирование': ['машинное обучение',
                               'искусственный интеллект', 'численное моделирование', 'нейронные сети',
                               'глубокое обучение', 'data science'],
        'космические технологии и навигация': ['нано-спутники', 'бортовая аппаратура', 'сейсморазведка',
                               'космос', 'навигация'],
        'биомедицина и биофизика': ['мембранные белки', 'компьютерная томография', 'биофизика',
                               'биоматериалы', 'геномика', 'биотехнология'],
        'химический синтез и катализ': ['катализ', 'органический синтез', 'полимеры', 'катализаторы',
                               'электрохимия', 'электрокатализ'],
        'материаловедение': ['сплавы', 'композиты', 'керамика', 'порошковая металлургия',
                               'аддитивные технологии', '3d-печать'],
    }
    active_dirs = []
    for cname, ckws in clusters.items():
        total = sum(kw_counts.get(kw, 0) for kw in ckws)
        if total >= 3:
            active_dirs.append(cname)

    # Key customers from projects
    cust_counter = Counter()
    for proj in egisu['data'].get('projects', []):
        cust = proj.get('customer', {})
        if cust:
            cust_short = cust.get('short_name', cust.get('name', ''))
            if cust_short:
                cust_counter[cust_short] += 1
    top_customers = cust_counter.most_common(5)

    # Total publications across projects
    total_pub_count = sum(proj.get('publication_count', 0) or 0 for proj in egisu['data'].get('projects', []))

    # Calculate budget
    total_budget = calculate_total_budget(egisu['data'].get('projects', []))
    budget_mln = total_budget / 1000

    # RID breakdown
    rid_types = Counter(r.get('rid_type', '?') for r in egisu['data'].get('rid', []))

    # ── Brief summary ──
    dirs_text = ', '.join(active_dirs[:3])
    if len(active_dirs) > 3:
        dirs_text += ' и другие'
    if not dirs_text:
        # Use top keywords instead
        dirs_text = ', '.join(top_kws[:5]) if top_kws else 'широкий спектр научных направлений'

    brief = esc(f'«{name}» — ведущий научно-исследовательский центр, объединяющий '
             f'{labs_count} лабораторий и {sci_count} учёных. '
             f'Исследовательский профиль охватывает {dirs_text}. '
             f'Опубликовано свыше {pubs_count} научных работ, '
             f'выполнено {projs_count} проектов НИОКТР и зарегистрировано {rid_count} результатов интеллектуальной деятельности.')

    # ── Detailed section ──
    detail = ''

    # Research profile (from clusters)
    if active_dirs:
        detail += '<h3 class="text-zinc-200 text-sm font-bold uppercase tracking-wide mb-3 mt-0">Исследовательский профиль</h3>'
        detail += '<p class="text-zinc-400 text-sm mb-2">Научная деятельность сосредоточена в нескольких ключевых направлениях:</p>'
        detail += '<ul class="text-zinc-400 text-sm space-y-1 ml-4 mb-6 list-disc">'
        for cname, ckws in clusters.items():
            matching = [kw for kw in ckws if kw_counts.get(kw, 0) > 0]
            total = sum(kw_counts.get(kw, 0) for kw in ckws)
            if total >= 3:
                topics = ', '.join(esc(m) for m in matching[:4])
                detail += f'<li><strong class="text-zinc-300">{esc(cname.capitalize())}</strong> — {topics}</li>'
        detail += '</ul>'

    # Top keywords cloud (actual from projects)
    if top_kws:
        detail += '<h3 class="text-zinc-200 text-sm font-bold uppercase tracking-wide mb-3">Ключевые компетенции (по данным ЕГИСУ)</h3>'
        detail += '<div style="display:flex;flex-wrap:wrap;gap:0.4rem;margin-bottom:1.5rem">'
        for kw in top_kws:
            cnt = kw_counts[kw]
            detail += f'<span style="padding:0.25rem 0.6rem;border:1px solid rgba(255,255,255,0.1);border-radius:999px;font-size:0.75rem;color:#a1a1aa">{esc(kw)} <span style="color:#52525b">({cnt})</span></span>'
        detail += '</div>'

    # Key labs
    top_labs = colab['data'].get('laboratories', [])[:6]
    if top_labs:
        detail += '<h3 class="text-zinc-200 text-sm font-bold uppercase tracking-wide mb-3">Ведущие лаборатории</h3>'
        detail += '<ul class="text-zinc-400 text-sm space-y-1 ml-4 mb-6 list-disc">'
        for lab in top_labs:
            lab_name = esc(lab.get('name', ''))
            sci_in_lab = len(lab.get('scientists', []))
            detail += f'<li>{lab_name} ({sci_in_lab} сотр.)</li>'
        if labs_count > 6:
            detail += f'<li class="text-zinc-600">...и ещё {labs_count - 6} лабораторий</li>'
        detail += '</ul>'

    # Key customers
    if top_customers:
        detail += '<h3 class="text-zinc-200 text-sm font-bold uppercase tracking-wide mb-3">Ключевые заказчики НИОКР</h3>'
        detail += '<ul class="text-zinc-400 text-sm space-y-1 ml-4 mb-6 list-disc">'
        for cust, cnt in top_customers:
            detail += f'<li><strong class="text-zinc-300">{esc(cust)}</strong> — {cnt} проектов</li>'
        detail += '</ul>'

    # IP
    if rid_types:
        detail += '<h3 class="text-zinc-200 text-sm font-bold uppercase tracking-wide mb-3">Интеллектуальная собственность</h3>'
        rid_parts = [f'{esc(t.lower())} — {c}' for t, c in rid_types.most_common()]
        detail += f'<p class="text-zinc-400 text-sm mb-6">Портфель из {rid_count} РИД: {", ".join(rid_parts)}.</p>'

    # Funding + publications
    funding_parts = []
    if total_budget > 0:
        funding_parts.append(f'Суммарный объём финансирования: <strong class="text-white">{budget_mln:,.1f} млн руб.</strong> ({projs_count} проектов, по данным ЕГИСУ НИОКТР).')
    if total_pub_count > 0:
        funding_parts.append(f'По итогам проектов опубликовано {total_pub_count} научных работ.')
    if funding_parts:
        detail += '<h3 class="text-zinc-200 text-sm font-bold uppercase tracking-wide mb-3">Финансирование и результаты</h3>'
        detail += f'<p class="text-zinc-400 text-sm">{" ".join(funding_parts)}</p>'

    return brief, detail


def generate_labs_html(laboratories, org_slug):
    """Generate HTML for all laboratory cards."""
    if not laboratories:
        return '<p class="text-sm text-zinc-500 italic">Нет данных о лабораториях</p>'

    cards = []
    for i, lab in enumerate(laboratories):
        name = esc(lab.get('name', 'Лаборатория'))
        desc = esc(lab.get('description', '')[:150])
        if len(lab.get('description', '')) > 150:
            desc += '...'
        url = f'{org_slug}/lab_{i:03d}.html'
        sci_count = len(lab.get('scientists', []))
        tags = lab.get('tags', [])[:3]
        tags_html = ''.join(
            f'<span class="px-2 py-1 rounded-md bg-white/5 border border-white/10 '
            f'text-[9px] uppercase font-bold text-zinc-400">{esc(t)}</span>'
            for t in tags
        )
        equipment = esc(lab.get('equipment', '')[:120])
        equip_html = ''
        if equipment:
            equip_html = f'''<div class="mt-4 p-3 rounded-xl bg-black/40 border border-white/5">
              <div class="text-[9px] uppercase font-black text-zinc-500 mb-1">Оборудование</div>
              <div class="text-[11px] text-zinc-400 leading-snug">{equipment}</div>
            </div>'''

        # Contacts
        contacts = lab.get('contacts', [])
        contact_html = ''
        if contacts:
            email = contacts[0] if contacts else ''
            contact_html = f'<span class="text-[10px] text-emerald-400 font-bold">✉ {esc(email)}</span>'

        card = f'''<div class="lab-item glass rounded-[2rem] p-8 hover:border-red-500/30 transition shadow-lg flex flex-col" data-idx="{i}" style="{"display:none" if i >= 3 else ""}">
          <div class="flex flex-wrap gap-2 mb-4">{tags_html}</div>
          <a href="{url}" class="group">
            <h3 class="text-lg font-bold mb-3 group-hover:text-red-400 transition leading-snug">{name}</h3>
          </a>
          <p class="text-xs text-zinc-500 leading-relaxed mb-4 flex-1">{desc}</p>
          {equip_html}
          <div class="mt-6 flex items-center justify-between pt-4 border-t border-white/5">
            <span class="text-[10px] font-black uppercase text-zinc-500">👥 {sci_count} сотрудников</span>
            {contact_html}
          </div>
          <div class="flex gap-2 mt-3">
            <a href="{url}" class="flex-1 text-center px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-[9px] font-bold uppercase tracking-wide text-zinc-400 hover:bg-white/10 transition">Подробнее</a>
            <a href="javascript:void(0)" onclick="openRequestModal('Связаться с лабораторией {name[:30]}')" class="flex-1 text-center px-3 py-2 rounded-xl bg-red-500/10 border border-red-500/30 text-[9px] font-bold uppercase tracking-wide text-red-400 hover:bg-red-500/20 transition cursor-pointer">📨 Связаться</a>
          </div>
        </div>'''
        cards.append(card)

    return '\n'.join(cards)


def collect_unique_scientists(laboratories, org_slug):
    """Deduplicate scientists across all labs, assign deterministic internal links.
    
    Uses the same dedup order as generate_site.py to ensure sci_{idx:03d}.html matches.
    """
    seen = set()
    unique = []
    idx = 0
    for lab in laboratories:
        lab_name = lab.get('name', '')
        for sci in lab.get('scientists', []):
            name = sci.get('name', '')
            if name and name not in seen:
                seen.add(name)
                entry = dict(sci)
                entry['_lab_name'] = lab_name
                entry['_internal_file'] = f'sci_{idx:03d}.html'
                unique.append(entry)
                idx += 1
    return unique


def generate_scientists_html(scientists, org_slug):
    """Generate HTML cards for all scientists."""
    if not scientists:
        return '<p class="text-sm text-zinc-500 italic">Нет данных об учёных</p>'

    cards = []
    for sci_idx, sci in enumerate(scientists):
        sci_name_raw = sci.get('name', '')
        name = esc(sci_name_raw)
        url = esc(sci.get('url', '#'))
        # Try internal page first
        internal_file = sci.get('_internal_file')
        if internal_file:
            url = f'{org_slug}/{internal_file}'
        photo = sci.get('photo_url', '')
        h_idx = sci.get('h_index')
        pubs = sci.get('publications', 0)
        lab_name = esc(sci.get('_lab_name', ''))

        # Research areas — first 4
        areas = sci.get('research_areas', [])
        if isinstance(areas, str):
            areas = [a.strip() for a in areas.split(',') if a.strip()]
        areas_display = areas[:4]
        areas_str = ', '.join(esc(a) for a in areas_display)
        if len(areas) > 4:
            areas_str += f' +{len(areas)-4}'
        # Data attribute for search
        search_areas = ' '.join(a.lower() for a in areas)

        # Photo or initials
        if photo:
            avatar = f'<img src="{esc(photo)}" class="w-full h-full object-cover" alt="{name}" loading="lazy">'
        else:
            parts = name.split()
            initials = ''.join(p[0] for p in parts[:2] if p)
            avatar = f'<div class="w-full h-full flex items-center justify-center bg-gradient-to-br from-red-600 to-red-900 text-white text-lg font-black">{initials}</div>'

        # h-index badge
        h_html = ''
        if h_idx and str(h_idx) != 'None':
            h_html = f'<span class="absolute -top-1 -right-1 px-1.5 py-0.5 bg-red-500 text-white text-[9px] font-bold rounded-full">h={h_idx}</span>'

        hidden = 'display:none' if sci_idx >= 3 else ''
        card = f'''<a href="{url}" target="_blank"
          class="sci-card glass rounded-2xl p-5 group hover:border-red-500/30 transition flex gap-4 items-start"
          data-name="{name.lower()}" data-areas="{esc(search_areas)}" data-idx="{sci_idx}" style="{hidden}">
          <div class="relative shrink-0">
            <div class="w-14 h-14 rounded-xl overflow-hidden border border-white/10">{avatar}</div>
            {h_html}
          </div>
          <div class="min-w-0 flex-1">
            <div class="text-sm font-bold group-hover:text-red-400 transition truncate">{name}</div>
            <div class="text-[10px] text-zinc-500 font-semibold mt-0.5 truncate">{lab_name}</div>
            <div class="text-[11px] text-zinc-400 mt-2 leading-snug line-clamp-2">{areas_str}</div>
            <div class="flex items-center gap-3 mt-2">
              <span class="text-[9px] text-zinc-600">📚 {pubs or 0} публ.</span>
            </div>
          </div>
        </a>'''
        cards.append(card)

    return '\n'.join(cards)


def generate_passport(org_file):
    """Generate passport page for any org given its JSON file path."""

    # Load data
    with open(org_file) as f:
        org = json.load(f)

    slug = org.get('slug', '')
    if not slug:
        print(f"⚠️ Skipping {org_file}: no slug")
        return

    identity = org['identity']
    colab = org['source_colab']
    egisu = org['source_egisu']
    sc = colab['data']
    se = egisu['data']
    m_colab = colab['metrics']
    m_egisu = egisu['metrics']

    # Calculate budget
    total_budget = calculate_total_budget(se.get('projects', []))
    budget_display = format_budget(total_budget)

    # Generate about section
    about_brief, about_detail = generate_summary(org)

    # Generate labs HTML
    laboratories = sc.get('laboratories', [])
    labs_html = generate_labs_html(laboratories, slug)

    # Generate scientists data (deterministic index-based linking)
    all_scientists = collect_unique_scientists(laboratories, slug)
    scientists_html = generate_scientists_html(all_scientists, slug)
    matched = len(all_scientists)  # all have internal links now

    # ── TOP-3 Labs (by scientist count) ──
    top_labs = sorted(enumerate(laboratories), key=lambda x: len(x[1].get('scientists',[])), reverse=True)[:3]
    top_labs_html = ''
    for idx, lab in top_labs:
        lname = esc(lab.get('name', ''))
        sci_count = len(lab.get('scientists', []))
        tags = lab.get('tags', [])[:2]
        tags_str = ' '.join(f'<span class="px-2 py-0.5 rounded bg-white/5 border border-white/10 text-[8px] uppercase font-bold text-zinc-500">{esc(t)}</span>' for t in tags)
        top_labs_html += f'''<a href="{slug}/lab_{idx:03d}.html" class="glass rounded-2xl p-5 group hover:border-red-500/30 transition flex flex-col">
          <div class="flex flex-wrap gap-1.5 mb-3">{tags_str}</div>
          <div class="text-sm font-bold group-hover:text-red-400 transition leading-snug mb-2">{lname}</div>
          <div class="text-[10px] text-zinc-500 font-bold mt-auto">👥 {sci_count} учёных</div>
        </a>\n'''

    # ── TOP-3 Scientists (by publications, deduplicated by surname) ──
    sci_by_pubs = sorted(all_scientists, key=lambda s: (s.get('publications',0) or 0), reverse=True)
    sci_sorted = []
    seen_surnames = set()
    for s in sci_by_pubs:
        parts = s.get('name', '').split()
        # Add both first and last word as possible surnames to catch both name orders
        keys = set()
        if parts:
            keys.add(parts[0].lower())
            keys.add(parts[-1].lower())
        if keys & seen_surnames:
            continue
        seen_surnames.update(keys)
        sci_sorted.append(s)
        if len(sci_sorted) == 3:
            break
    top_sci_html = ''
    for s in sci_sorted:
        s_name = esc(s.get('name', ''))
        s_pubs = s.get('publications', 0) or 0
        s_h = s.get('h_index')
        s_photo = s.get('photo_url', '')
        s_lab = esc(s.get('_lab_name', ''))
        s_file = s.get('_internal_file', '')
        s_url = f'{slug}/{s_file}' if s_file else esc(s.get('url', '#'))
        if s_photo:
            ava = f'<img src="{esc(s_photo)}" class="w-12 h-12 rounded-xl object-cover border border-white/10" loading="lazy">'
        else:
            parts = s_name.split()
            ini = ''.join(p[0] for p in parts[:2] if p)
            ava = f'<div class="w-12 h-12 rounded-xl flex items-center justify-center bg-gradient-to-br from-red-600 to-red-900 text-white font-bold text-sm">{ini}</div>'
        h_badge = f'<span class="px-1.5 py-0.5 bg-red-500 text-white text-[8px] font-bold rounded-full">h={s_h}</span>' if s_h and str(s_h) != 'None' else ''
        top_sci_html += f'''<a href="{s_url}" class="glass rounded-2xl p-5 group hover:border-red-500/30 transition flex gap-3 items-center">
          {ava}
          <div class="min-w-0 flex-1">
            <div class="text-sm font-bold group-hover:text-red-400 transition truncate">{s_name}</div>
            <div class="text-[10px] text-zinc-500 truncate">{s_lab}</div>
            <div class="flex items-center gap-2 mt-1">
              <span class="text-[9px] text-zinc-600">📚 {s_pubs} публ.</span> {h_badge}
            </div>
          </div>
        </a>\n'''

    # Projects and RID data
    projects = se.get('projects', [])
    rids = se.get('rid', [])

    # RID type breakdown — clickable cards linking to filtered list
    rid_types = Counter(r.get('rid_type', 'Неизвестно') for r in rids)
    rid_cards_html = ''
    type_icons = {'Программа для ЭВМ': '💻', 'База данных': '🗄️', 'Ноу-хау': '🔐',
                  'Полезная модель': '⚙️', 'Изобретение': '💡', 'Промышленный образец': '🏭'}
    # Also list individual RIDs
    rid_list_html = ''
    for i, r in enumerate(rids):
        rname = esc(r.get('name', '')[:100])
        rtype = esc(r.get('rid_type', ''))
        icon = type_icons.get(rtype, '📄')
        abstract = esc(r.get('abstract', '')[:80])
        if abstract and len(r.get('abstract', '')) > 80:
            abstract += '...'
        keywords = r.get('keyword_list', [])[:3]
        kw_html = ', '.join(esc(k) for k in keywords) if keywords else ''
        cust = r.get('customer', {})
        cust_short = esc(cust.get('short_name', '')) if cust else ''
        created = r.get('created_date', '')[:4]
        vis = 'block' if i < 5 else 'none'
        rid_list_html += f'''<a href="{slug}/rid_{i:04d}.html" class="rid-item block p-4 border-b border-white/5 hover:bg-white/5 transition group" style="display:{vis}" data-idx="{i}">
          <div class="flex items-start gap-3">
            <span class="text-lg mt-0.5">{icon}</span>
            <div class="min-w-0 flex-1">
              <div class="text-sm font-semibold group-hover:text-red-400 transition">{rname}</div>
              {"<div class='text-[11px] text-zinc-500 mt-1 line-clamp-1'>" + abstract + "</div>" if abstract else ""}
              <div class="flex items-center gap-3 mt-1.5 flex-wrap">
                <span class="text-[10px] text-zinc-600">{rtype}</span>
                {"<span class='text-[10px] text-zinc-600'>| " + kw_html + "</span>" if kw_html else ""}
                {"<span class='text-[10px] text-zinc-600'>| " + cust_short + "</span>" if cust_short else ""}
                {"<span class='text-[10px] text-zinc-700 ml-auto'>" + created + "</span>" if created else ""}
              </div>
            </div>
          </div>
        </a>\n'''

    for rtype, count in rid_types.most_common():
        icon = type_icons.get(rtype, '📄')
        rid_cards_html += f'''<div class="glass rounded-2xl p-5 text-center">
          <div class="text-2xl mb-2">{icon}</div>
          <div class="text-2xl font-black italic">{count}</div>
          <div class="text-[10px] uppercase font-bold text-zinc-500 mt-1">{esc(rtype)}</div>
        </div>\n'''

    # Projects — first 5 visible, rest hidden
    projects_html = ''
    for i, p in enumerate(projects[:30]):
        pname = esc(p.get('name', 'Без названия')[:120])
        proj_url = f'{slug}/proj_{i:04d}.html'
        keywords = p.get('keyword_list', [])[:5]
        kw_html = ', '.join(esc(k) for k in keywords) if keywords else ''
        budget_val = sum(float(b.get('funds', 0) or 0) for b in p.get('budgets', []))
        budget_str = f'{budget_val:,.0f} тыс. ₽' if budget_val > 0 else ''
        abstract = esc(p.get('abstract', '')[:100])
        if abstract and len(p.get('abstract', '')) > 100:
            abstract += '...'
        cust = p.get('customer', {})
        cust_short = esc(cust.get('short_name', '')) if cust else ''
        stage_start = p.get('stage_start_date', '')[:4]  # year only
        stage_end = p.get('stage_end_date', '')[:4]
        dates = f'{stage_start}–{stage_end}' if stage_start and stage_end and stage_start != stage_end else stage_start
        vis = 'block' if i < 5 else 'none'
        projects_html += f'''<a href="{proj_url}" class="proj-item block p-4 border-b border-white/5 hover:bg-white/5 transition group" style="display:{vis}" data-idx="{i}">
          <div class="text-sm font-semibold group-hover:text-red-400 transition">{pname}</div>
          {"<div class='text-[11px] text-zinc-500 mt-1 line-clamp-2'>" + abstract + "</div>" if abstract else ""}
          <div class="flex items-center gap-3 mt-2 flex-wrap">
            <span class="text-[10px] text-zinc-500">{kw_html}</span>
            {"<span class='text-[10px] text-zinc-600'>| " + cust_short + "</span>" if cust_short else ""}
            {"<span class='text-[10px] text-zinc-600'>| " + dates + "</span>" if dates else ""}
            <span class="text-[10px] text-zinc-600 ml-auto">{budget_str}</span>
          </div>
        </a>\n'''

    print(f"   Scientists: {len(all_scientists)} unique ({matched} with internal links)")

    # ── Build HTML ──
    page_html = f"""<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8" />
    <meta content="width=device-width, initial-scale=1.0" name="viewport" />
    <title>МОСНАУКА — Паспорт: {esc(identity['name_short'])}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/@phosphor-icons/web"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
      body {{ font-family: Inter, system-ui, sans-serif; background: #050505; color: white; }}
      .glass {{ background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.08); }}
      .mos-red {{ color: #ff003c; }}
      .mos-bg-red {{ background: #ff003c; }}
      .provenance-tag {{ font-size: 8px; font-weight: 900; text-transform: uppercase; letter-spacing: 0.1em; padding: 2px 8px; border-radius: 4px; }}
      .tag-egisu {{ background: rgba(0, 120, 255, 0.1); color: #40a0ff; border: 1px solid rgba(0, 120, 255, 0.2); }}
      .tag-colab {{ background: rgba(255, 0, 60, 0.1); color: #ff4070; border: 1px solid rgba(255, 0, 60, 0.2); }}
      .tag-org {{ background: rgba(255, 255, 255, 0.05); color: #aaa; border: 1px solid rgba(255, 255, 255, 0.1); }}

      /* Section titles */
      .section-header {{
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 0.5rem; margin-bottom: 1.5rem; margin-top: 3.5rem;
      }}
      .section-title {{
        font-size: 1.5rem; font-weight: 900; text-transform: uppercase;
        font-style: italic; letter-spacing: -0.02em;
      }}

      /* Chunk 3: Lab cards */
      .labs-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
        gap: 1.5rem;
      }}
      /* Chunk 4: Scientists */
      .sci-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
        gap: 1rem;
      }}
      .sci-card.hidden {{ display: none; }}
      .line-clamp-2 {{
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }}
      #sci-search {{
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 1rem;
        padding: 0.75rem 1.25rem 0.75rem 2.75rem;
        color: white;
        font-size: 0.875rem;
        width: 100%;
        outline: none;
        transition: border-color 0.2s;
      }}
      #sci-search:focus {{
        border-color: rgba(255,0,60,0.5);
      }}
      #sci-search::placeholder {{ color: rgba(255,255,255,0.25); }}
      /* Chunk 5: RID + Projects */
      .rid-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
        gap: 1rem;
      }}
    </style>
</head>
<body>
  <div class="min-h-screen bg-[radial-gradient(circle_at_top_left,rgba(255,0,60,0.12),transparent_25%),radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_20%),linear-gradient(180deg,#050505,#0b0f16)]">

    <!-- ═══ HEADER ═══ -->
    <header class="sticky top-0 z-30 backdrop-blur-md border-b border-white/10 bg-black/40">
      <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <a class="text-2xl font-black italic tracking-tight uppercase hover:opacity-80 transition" href="index.html">
          МОС<span class="mos-red">НАУКА</span>
        </a>
        <div class="flex items-center gap-4">
          <span class="text-[10px] uppercase tracking-widest text-zinc-500 font-bold">Паспорт организации v2.0</span>
          <a href="catalog.html" class="text-xs font-bold uppercase hover:text-red-500 transition">Реестр</a>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-6 py-10">

      <!-- ═══ BREADCRUMBS ═══ -->
      <div class="mb-10 flex items-center justify-between">
        <div class="flex items-center gap-2 text-[10px] uppercase font-bold tracking-widest text-zinc-500">
          <a href="index.html" class="hover:text-white">Главная</a>
          <span>/</span>
          <a href="catalog.html" class="hover:text-white">Реестр</a>
          <span>/</span>
          <span class="text-zinc-300">{esc(identity['name_short'])}</span>
        </div>
        <a href="catalog.html" class="px-5 py-2 border border-white/10 rounded-full text-[10px] font-black uppercase tracking-widest hover:bg-white/5 transition">
          ← К списку
        </a>
      </div>

      <!-- ═══ HERO SECTION ═══ -->
      <section class="glass rounded-[2.5rem] p-10 relative overflow-hidden mb-8">
        <!-- Bg watermark -->
        <div class="absolute top-0 right-0 p-8 opacity-5 pointer-events-none">
          <img src="{esc(identity['logo_url'])}" class="w-64 h-64 grayscale invert" alt="">
        </div>

        <div class="relative z-10">
          <!-- Identity -->
          <div class="flex items-center gap-5 mb-6">
            <div class="w-20 h-20 rounded-2xl bg-white p-2 flex items-center justify-center shrink-0">
              <img src="{esc(identity['logo_url'])}" class="max-w-full max-h-full object-contain" alt="{esc(identity['name_short'])} logo">
            </div>
            <div>
              <h1 class="text-3xl md:text-5xl font-black tracking-tight uppercase leading-tight mb-2">{esc(identity['name_short'])}</h1>
              <p class="text-zinc-400 font-medium">{esc(identity['name_full'])}</p>
            </div>
          </div>

          <!-- Contact row -->
          <div class="flex flex-wrap gap-6 mt-6">
            <div class="flex items-center gap-2 text-zinc-400 text-sm">
              <i class="ph ph-map-pin mos-red"></i>
              <span>{esc(identity['address'])}</span>
            </div>
            <a href="{esc(identity['website'])}" target="_blank" class="flex items-center gap-2 text-zinc-300 text-sm hover:text-white transition">
              <i class="ph ph-globe mos-red"></i>
              <span>{esc(identity['website'].replace('https://','').replace('http://','').strip('/'))}</span>
            </a>
          </div>

          <!-- Verified badge + Contact CTA -->
          <div class="mt-6 flex flex-wrap gap-3 items-center">
            <span class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-[11px] font-bold uppercase tracking-wide">
              <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>
              Верифицировано МОСНАУКОЙ
            </span>
          </div>
          <div class="mt-4 p-5 rounded-2xl bg-gradient-to-r from-red-500/20 to-red-500/5 border border-red-500/30 flex flex-wrap items-center justify-between gap-4">
            <div>
              <div class="text-sm font-bold">📨 Заинтересованы в сотрудничестве?</div>
              <div class="text-[11px] text-zinc-400 mt-1">Направьте запрос на НИОКР, консультацию или партнёрство</div>
            </div>
            <div class="flex gap-2">
              <a href="javascript:void(0)" onclick="openRequestModal('Запрос по {esc(identity['name_short'])}')" class="px-6 py-3 rounded-xl bg-red-500 text-white text-[11px] font-black uppercase tracking-wide hover:bg-red-600 transition inline-flex items-center gap-2 shadow-lg">
                <i class="ph ph-envelope-simple"></i> Направить запрос
              </a>
              <a href="{esc(identity['website'])}" target="_blank" class="px-5 py-3 rounded-xl bg-white/5 border border-white/10 text-[11px] font-bold uppercase text-zinc-400 hover:bg-white/10 transition inline-flex items-center gap-2">
                <i class="ph ph-globe"></i> Сайт
              </a>
            </div>
          </div>

          <!-- ═══ METRICS ROW ═══ -->
          <div class="grid grid-cols-2 md:grid-cols-5 gap-4 mt-10">
            <a href="#section-labs" class="p-4 rounded-2xl bg-white/5 border border-white/10 hover:border-white/30 transition cursor-pointer block">
              <div class="text-[9px] uppercase font-black text-zinc-500 mb-1">Лаборатории</div>
              <div class="text-3xl font-black italic">{m_colab['total_laboratories']}</div>
            </a>
            <a href="#section-scientists" class="p-4 rounded-2xl bg-white/5 border border-white/10 hover:border-white/30 transition cursor-pointer block">
              <div class="text-[9px] uppercase font-black text-zinc-500 mb-1">Учёные</div>
              <div class="text-3xl font-black italic">{m_colab['total_scientists']}</div>
            </a>
            <a href="#section-projects" class="p-4 rounded-2xl bg-white/5 border border-white/10 hover:border-white/30 transition cursor-pointer block">
              <div class="text-[9px] uppercase font-black text-zinc-500 mb-1">Проекты НИОКР</div>
              <div class="text-3xl font-black italic">{m_egisu['projects_ikrbs']}</div>
            </a>
            <a href="#section-rid" class="p-4 rounded-2xl bg-white/5 border border-white/10 hover:border-white/30 transition cursor-pointer block">
              <div class="text-[9px] uppercase font-black text-zinc-500 mb-1">РИД</div>
              <div class="text-3xl font-black italic">{m_egisu['rid_count']}</div>
            </a>
            <a href="#section-projects" class="p-4 rounded-2xl bg-red-500/5 border border-red-500/20 hover:border-red-500/40 transition cursor-pointer block">
              <div class="text-[9px] uppercase font-black text-red-400/70 mb-1">Объём НИОКР</div>
              <div class="text-3xl font-black italic mos-red">{budget_display} ₽</div>
            </a>
          </div>
        </div>
      </section>

      <!-- ═══ CHUNK 2: About section ═══ -->
      <section class="glass rounded-[2.5rem] p-10 mb-8">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-black uppercase italic tracking-tight">Об организации</h2>
        </div>
        <p class="text-[15px] text-zinc-300 leading-relaxed mb-6">{about_brief}</p>
        <details class="group">
          <summary class="cursor-pointer text-sm font-bold text-red-400 hover:text-red-300 transition select-none flex items-center gap-2">
            <i class="ph ph-caret-right text-xs transition-transform group-open:rotate-90"></i>
            Подробнее об исследовательской деятельности
          </summary>
          <div class="mt-6 pt-6 border-t border-white/10">
            {about_detail}
          </div>
        </details>
      </section>

      <!-- ═══ TOP-3 FEATURED ═══ -->
      <section class="glass rounded-[2.5rem] p-10 mb-8">
        <h2 class="text-lg font-black uppercase italic tracking-tight mb-6">⭐ Ведущие лаборатории и учёные</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <div class="text-[10px] uppercase font-black text-zinc-500 mb-3 tracking-widest">🏛️ Топ-3 лаборатории</div>
            <div class="flex flex-col gap-3">{top_labs_html}</div>
          </div>
          <div>
            <div class="text-[10px] uppercase font-black text-zinc-500 mb-3 tracking-widest">🏆 Топ-3 учёных</div>
            <div class="flex flex-col gap-3">{top_sci_html}</div>
          </div>
        </div>
      </section>

      <!-- ═══ TABS: Labs / Scientists ═══ -->
      <div class="glass rounded-2xl p-4 mb-4" style="border:1px solid rgba(56,189,248,0.15);background:rgba(56,189,248,0.03)">
        <div class="flex items-center gap-2 text-[10px] text-sky-400/70 font-bold uppercase">
          <i class="ph ph-info"></i>
          Показаны лаборатории и учёные, зарегистрированные на платформе CoLab. Фактическое число сотрудников может быть больше.
        </div>
      </div>
      <div class="section-header" id="section-labs">
        <div class="flex items-center gap-4">
          <button id="tab-labs" onclick="switchTab('labs')" class="section-title" style="background:none;border:none;color:white;cursor:pointer;padding:0">🔬 Лаборатории ({len(laboratories)})</button>
          <button id="tab-sci" onclick="switchTab('sci')" class="text-lg font-black uppercase italic tracking-tight opacity-30 hover:opacity-60 transition" style="background:none;border:none;color:white;cursor:pointer;padding:0" id="section-scientists">🎓 Учёные ({len(all_scientists)})</button>
        </div>
        <span class="provenance-tag tag-colab">CoLab Data</span>
      </div>

      <!-- Labs panel -->
      <div id="panel-labs">
        <div class="text-sm text-zinc-400 mb-3" id="lab-counter">Показаны 3 из {len(laboratories)}</div>
        <div class="labs-grid" id="labs-container">
          {labs_html}
        </div>
        <div class="mt-4 text-center">
          <button id="lab-more" onclick="showMore('lab-item', 'lab-more', 'lab-counter', {len(laboratories)}, 3)" class="px-6 py-2 rounded-full bg-white/5 border border-white/10 text-[10px] font-bold uppercase tracking-widest hover:bg-white/10 transition text-zinc-400">
            Показать ещё 3
          </button>
        </div>
      </div>

      <!-- Scientists panel (hidden by default) -->
      <div id="panel-sci" style="display:none">
        <div class="text-sm text-zinc-400 mb-3" id="sci-counter">Показаны 3 из {len(all_scientists)}</div>
        <div class="relative mb-6">
          <i class="ph ph-magnifying-glass absolute left-4 top-1/2 -translate-y-1/2 text-zinc-500"></i>
          <input id="sci-search" type="text" placeholder="Поиск по имени или области исследования...">
          <div id="sci-count" class="absolute right-4 top-1/2 -translate-y-1/2 text-[10px] text-zinc-500 font-bold">{len(all_scientists)} учёных</div>
        </div>
        <div class="sci-grid" id="sci-grid">
          {scientists_html}
        </div>
        <div class="mt-4 text-center">
          <button id="sci-more" onclick="showMore('sci-card', 'sci-more', 'sci-counter', {len(all_scientists)}, 3)" class="px-6 py-2 rounded-full bg-white/5 border border-white/10 text-[10px] font-bold uppercase tracking-widest hover:bg-white/10 transition text-zinc-400">
            Показать ещё 3
          </button>
        </div>
      </div>

      <script>
        // Tab switching
        function switchTab(tab) {{
          document.getElementById('panel-labs').style.display = tab === 'labs' ? '' : 'none';
          document.getElementById('panel-sci').style.display = tab === 'sci' ? '' : 'none';
          document.getElementById('tab-labs').style.opacity = tab === 'labs' ? '1' : '0.3';
          document.getElementById('tab-sci').style.opacity = tab === 'sci' ? '1' : '0.3';
        }}
        // Scientist search
        (function() {{
          const input = document.getElementById('sci-search');
          const grid = document.getElementById('sci-grid');
          const counter = document.getElementById('sci-count');
          if (!input || !grid) return;
          const cards = grid.querySelectorAll('.sci-card');
          input.addEventListener('input', function() {{
            const q = this.value.toLowerCase().trim();
            let visible = 0;
            cards.forEach(c => {{
              const name = c.dataset.name || '';
              const areas = c.dataset.areas || '';
              const match = !q || name.includes(q) || areas.includes(q);
              c.classList.toggle('hidden', !match);
              if (match) visible++;
            }});
            counter.textContent = visible + ' учёных';
          }});
        }})();
      </script>

      <!-- ═══ CHUNK 5: Projects ═══ -->
      <div class="section-header" id="section-projects">
        <h2 class="section-title">💼 Проекты НИОКР ({len(projects)})</h2>
        <span class="provenance-tag tag-egisu">ЕГИСУ</span>
      </div>
      <section class="glass rounded-[2.5rem] overflow-hidden mb-8">
        <div class="p-6 border-b border-white/10 flex items-center justify-between">
          <span class="text-sm text-zinc-400" id="proj-counter">Показаны 5 из {len(projects)}</span>
          <a href="{slug}/projects.html" class="text-xs font-bold text-red-400 hover:text-red-300 transition uppercase">Все проекты →</a>
        </div>
        <div id="proj-list">{projects_html}</div>
        <div class="p-4 text-center">
          <button id="proj-more" onclick="showMore('proj-item', 'proj-more', 'proj-counter', {len(projects)})" class="px-6 py-2 rounded-full bg-white/5 border border-white/10 text-[10px] font-bold uppercase tracking-widest hover:bg-white/10 transition text-zinc-400">
            Показать ещё 5
          </button>
        </div>
      </section>

      <!-- ═══ RID Section ═══ -->
      <div class="section-header" id="section-rid">
        <h2 class="section-title">🧬 Результаты интеллектуальной деятельности ({len(rids)})</h2>
        <span class="provenance-tag tag-egisu">ЕГИСУ</span>
      </div>
      <div class="rid-grid mb-6">
        {rid_cards_html}
      </div>
      <section class="glass rounded-[2.5rem] overflow-hidden mb-8">
        <div class="p-6 border-b border-white/10 flex items-center justify-between">
          <span class="text-sm text-zinc-400" id="rid-counter">Показаны 5 из {len(rids)}</span>
          <a href="{slug}/rid_list.html" class="text-xs font-bold text-red-400 hover:text-red-300 transition uppercase">Все РИД →</a>
        </div>
        <div id="rid-list">{rid_list_html}</div>
        <div class="p-4 text-center">
          <button id="rid-more" onclick="showMore('rid-item', 'rid-more', 'rid-counter', {len(rids)})" class="px-6 py-2 rounded-full bg-white/5 border border-white/10 text-[10px] font-bold uppercase tracking-widest hover:bg-white/10 transition text-zinc-400">
            Показать ещё 5
          </button>
        </div>
      </section>

      <script>
        // Generic show-more function
        function showMore(itemClass, btnId, counterId, total, step) {{
          step = step || 5;
          const items = document.querySelectorAll('.' + itemClass);
          let shown = 0;
          items.forEach(el => {{
            if (el.style.display !== 'none') shown++;
          }});
          items.forEach(el => {{
            const idx = parseInt(el.dataset.idx);
            if (idx < shown + step) {{
              el.style.display = '';
            }}
          }});
          const totalShown = Math.min(shown + step, items.length);
          document.getElementById(counterId).textContent = 'Показаны ' + totalShown + ' из ' + total;
          if (totalShown >= items.length) {{
            document.getElementById(btnId).style.display = 'none';
          }}
        }}
      </script>

    </main>

    <!-- Footer -->
    <footer class="py-20 border-t border-white/10 mt-20 bg-black/40">
      <div class="max-w-7xl mx-auto px-6 text-center">
        <div class="text-3xl font-black italic uppercase mb-8">МОС<span class="mos-red">НАУКА</span></div>
        <p class="text-zinc-500 text-sm max-w-2xl mx-auto italic mb-8">Единая экосистема технологического развития площадок и заказчиков в Москве.</p>
        <div class="flex justify-center gap-8 mb-8">
          <div class="text-[10px] text-zinc-600 uppercase font-bold">Источник: <span class="text-emerald-500">CoLab</span> — лаборатории, учёные</div>
          <div class="text-[10px] text-zinc-600 uppercase font-bold">Источник: <span class="text-sky-500">ЕГИСУ</span> — проекты, РИД</div>
        </div>
        <div class="text-white/20 text-[10px] uppercase font-bold tracking-[0.5em]">&copy; 2026 ЦИФРОВОЙ ПАСПОРТ ОБЪЕКТА</div>
      </div>
    </footer>

    <!-- Scroll to top button -->
    <button onclick="window.scrollTo({{top:0,behavior:'smooth'}})" id="scroll-top" class="fixed bottom-8 right-8 w-12 h-12 rounded-full bg-red-500/80 text-white flex items-center justify-center shadow-lg hover:bg-red-500 transition z-50" style="display:none" title="Наверх">
      <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M5 15l7-7 7 7"/></svg>
    </button>

    <!-- Request Modal -->
    <div id="requestModal" style="position:fixed;inset:0;background:rgba(0,0,0,0.7);backdrop-filter:blur(8px);z-index:100;display:none;align-items:center;justify-content:center;padding:1rem">
      <div style="background:#111;border:1px solid rgba(255,255,255,0.1);border-radius:1.5rem;max-width:32rem;width:100%;padding:2.5rem;position:relative">
        <button onclick="closeModal()" style="position:absolute;top:1.25rem;right:1.25rem;background:none;border:none;color:#52525b;font-size:1.5rem;cursor:pointer">&times;</button>
        <div id="modalForm">
          <h2 class="text-xl font-black mb-1">📨 Направить запрос</h2>
          <div id="modalContext" class="text-xs text-zinc-500 mb-6">через платформу МОСНАУКА</div>
          <label class="block text-[10px] uppercase font-black text-zinc-500 mb-1 tracking-widest">Ваше ФИО *</label>
          <input type="text" id="reqName" placeholder="Иванов Иван Иванович" class="w-full p-3 rounded-xl bg-white/5 border border-white/10 text-sm mb-3" style="color:white">
          <label class="block text-[10px] uppercase font-black text-zinc-500 mb-1 tracking-widest">Организация</label>
          <input type="text" id="reqOrg" placeholder="ООО «Компания»" class="w-full p-3 rounded-xl bg-white/5 border border-white/10 text-sm mb-3" style="color:white">
          <label class="block text-[10px] uppercase font-black text-zinc-500 mb-1 tracking-widest">Email *</label>
          <input type="email" id="reqEmail" placeholder="email@example.com" class="w-full p-3 rounded-xl bg-white/5 border border-white/10 text-sm mb-3" style="color:white">
          <label class="block text-[10px] uppercase font-black text-zinc-500 mb-2 tracking-widest">Тип запроса <span class="normal-case tracking-normal text-zinc-600">(можно выбрать несколько)</span></label>
          <div class="grid grid-cols-1 gap-2 mb-3" id="reqType">
            <label class="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/10 cursor-pointer hover:bg-white/[0.08] transition">
              <input type="checkbox" value="Запрос на НИОКР" checked class="w-4 h-4 rounded accent-red-500">
              <span class="text-sm text-zinc-300">Запрос на НИОКР</span>
            </label>
            <label class="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/10 cursor-pointer hover:bg-white/[0.08] transition">
              <input type="checkbox" value="Консультация" class="w-4 h-4 rounded accent-red-500">
              <span class="text-sm text-zinc-300">Консультация</span>
            </label>
            <label class="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/10 cursor-pointer hover:bg-white/[0.08] transition">
              <input type="checkbox" value="Сотрудничество / Партнёрство" class="w-4 h-4 rounded accent-red-500">
              <span class="text-sm text-zinc-300">Сотрудничество / Партнёрство</span>
            </label>
            <label class="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/10 cursor-pointer hover:bg-white/[0.08] transition">
              <input type="checkbox" value="Использование оборудования" class="w-4 h-4 rounded accent-red-500">
              <span class="text-sm text-zinc-300">Использование оборудования</span>
            </label>
            <label class="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/10 cursor-pointer hover:bg-white/[0.08] transition">
              <input type="checkbox" value="Другое" class="w-4 h-4 rounded accent-red-500">
              <span class="text-sm text-zinc-300">Другое</span>
            </label>
          </div>
          <label class="block text-[10px] uppercase font-black text-zinc-500 mb-1 tracking-widest">Сообщение *</label>
          <textarea id="reqMsg" placeholder="Опишите ваш запрос..." class="w-full p-3 rounded-xl bg-white/5 border border-white/10 text-sm mb-4" style="color:white;min-height:5rem;resize:vertical"></textarea>
          <button onclick="submitRequest()" class="w-full py-3 rounded-xl bg-red-500 text-white text-[11px] font-black uppercase tracking-widest hover:bg-red-600 transition">Отправить запрос</button>
        </div>
        <div id="modalSuccess" style="display:none;text-align:center;padding:2rem 0">
          <div style="font-size:3rem;margin-bottom:1rem">✅</div>
          <h3 class="text-lg font-black mb-2">Запрос отправлен!</h3>
          <p class="text-sm text-zinc-400">Ваш запрос направлен в личный кабинет организации через платформу МОСНАУКА. Ожидайте ответа в течение 3 рабочих дней.</p>
          <button onclick="closeModal()" class="mt-6 w-full py-3 rounded-xl bg-white/5 border border-white/10 text-sm font-bold text-zinc-400 hover:bg-white/10 transition">Закрыть</button>
        </div>
      </div>
    </div>

    <script>
      window.addEventListener('scroll', function() {{
        document.getElementById('scroll-top').style.display = window.scrollY > 400 ? 'flex' : 'none';
      }});
      function openRequestModal(context) {{
        document.getElementById('modalContext').textContent = context || 'через платформу МОСНАУКА';
        document.getElementById('modalForm').style.display = '';
        document.getElementById('modalSuccess').style.display = 'none';
        document.getElementById('requestModal').style.display = 'flex';
        document.body.style.overflow = 'hidden';
      }}
      function closeModal() {{
        document.getElementById('requestModal').style.display = 'none';
        document.body.style.overflow = '';
      }}
      function submitRequest() {{
        var n = document.getElementById('reqName').value.trim();
        var e = document.getElementById('reqEmail').value.trim();
        var m = document.getElementById('reqMsg').value.trim();
        if (!n || !e || !m) {{ alert('Пожалуйста, заполните обязательные поля'); return; }}
        document.getElementById('modalForm').style.display = 'none';
        document.getElementById('modalSuccess').style.display = '';
      }}
      document.getElementById('requestModal').addEventListener('click', function(e) {{
        if (e.target === this) closeModal();
      }});
    </script>
  </div>
</body>
</html>"""

    # Write file
    out_path = OUTPUT_DIR / f"passport-{slug}.html"
    with open(out_path, 'w') as f:
        f.write(page_html)
    print(f"✅ Chunks 1-5: Written {out_path}")
    print(f"   Budget: {total_budget:,.0f} тыс. руб = {budget_display} ₽")
    print(f"   About: {len(about_brief)} chars brief, {len(about_detail)} chars detail")
    print(f"   Labs: {len(laboratories)} laboratory cards (internal links)")
    print(f"   Scientists: {len(all_scientists)} unique ({matched} with internal links)")
    print(f"   Projects: {len(projects)} total ({min(30, len(projects))} shown)")
    print(f"   RID: {len(rids)} ({len(rid_types)} types)")


if __name__ == '__main__':
    import sys
    org_files = sorted(DATA_DIR.glob("org_*.json"))
    if not org_files:
        print("❌ No org_*.json files found in", DATA_DIR)
        sys.exit(1)
    for org_file in org_files:
        try:
            generate_passport(org_file)
        except Exception as e:
            print(f"❌ Error processing {org_file.name}: {e}")
