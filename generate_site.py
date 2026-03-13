#!/usr/bin/env python3
"""МОСНАУКА — Internal Pages Generator (step-by-step)"""

import json, html, os
from pathlib import Path

DATA_DIR = Path("/Users/shakhgildyangy/COLAB_DATA/passports")
OUTPUT_DIR = Path("/Users/shakhgildyangy/mosnauka")
CSS_PATH = "mosnauka-style.css"  # relative from org subdir

def esc(t):
    return html.escape(str(t)) if t else ''

def page_wrap(title, breadcrumbs_html, body_html, css_rel="../mosnauka-style.css"):
    """Wrap content in a full МОСНАУКА page with request modal."""
    return f"""<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width,initial-scale=1"/>
    <title>{title}</title>
    <link rel="stylesheet" href="{css_rel}">
    <style>
      .modal-overlay {{ position:fixed;inset:0;background:rgba(0,0,0,0.7);backdrop-filter:blur(8px);z-index:100;display:none;align-items:center;justify-content:center;padding:1rem }}
      .modal-overlay.active {{ display:flex }}
      .modal {{ background:#111;border:1px solid rgba(255,255,255,0.1);border-radius:1.5rem;max-width:32rem;width:100%;padding:2.5rem;position:relative }}
      .modal h2 {{ font-size:1.25rem;font-weight:900;margin-bottom:0.25rem }}
      .modal .sub {{ color:#a1a1aa;font-size:0.8rem;margin-bottom:1.5rem }}
      .modal label {{ display:block;font-size:0.65rem;text-transform:uppercase;font-weight:800;color:#52525b;margin-bottom:0.35rem;margin-top:1rem;letter-spacing:0.1em }}
      .modal input,.modal select,.modal textarea {{ width:100%;padding:0.75rem 1rem;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:0.75rem;color:white;font-size:0.85rem;font-family:inherit;outline:none;transition:border 0.2s }}
      .modal input:focus,.modal select:focus,.modal textarea:focus {{ border-color:#ff003c }}
      .modal textarea {{ min-height:5rem;resize:vertical }}
      .modal select {{ appearance:none }}
      .modal .close {{ position:absolute;top:1.25rem;right:1.25rem;background:none;border:none;color:#52525b;font-size:1.5rem;cursor:pointer }}
      .modal .close:hover {{ color:white }}
      .modal .submit {{ width:100%;margin-top:1.5rem;padding:0.875rem;background:#ff003c;color:white;border:none;border-radius:1rem;font-size:0.8rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;cursor:pointer;transition:background 0.2s }}
      .modal .submit:hover {{ background:#cc0030 }}
      .modal .success {{ text-align:center;padding:2rem 0 }}
      .modal .success .icon {{ font-size:3rem;margin-bottom:1rem }}
      .modal .success h3 {{ font-size:1.1rem;font-weight:800;margin-bottom:0.5rem }}
      .modal .success p {{ color:#a1a1aa;font-size:0.85rem }}
    </style>
</head>
<body>
<div class="mos-page">
  <header class="mos-header">
    <div class="mos-header-inner">
      <a class="mos-logo" href="../index.html">МОС<span class="mos-red">НАУКА</span></a>
      <span style="font-size:0.6rem;text-transform:uppercase;letter-spacing:0.2em;color:#52525b;font-weight:700">v2.0</span>
    </div>
  </header>
  <nav class="breadcrumbs">{breadcrumbs_html}</nav>
  <main class="mos-main">
    {body_html}
  </main>
  <footer class="mos-footer">
    <div class="logo">МОС<span class="mos-red">НАУКА</span></div>
    <div class="copy">&copy; 2026 ЦИФРОВОЙ ПАСПОРТ</div>
  </footer>
</div>

<!-- Request Modal -->
<div class="modal-overlay" id="requestModal">
  <div class="modal">
    <button class="close" onclick="closeModal()">&times;</button>
    <div id="modalForm">
      <h2>📨 Направить запрос</h2>
      <div class="sub" id="modalContext">через платформу МОСНАУКА</div>
      <label>Ваше ФИО *</label>
      <input type="text" id="reqName" placeholder="Иванов Иван Иванович">
      <label>Организация</label>
      <input type="text" id="reqOrg" placeholder="ООО «Компания»">
      <label>Email *</label>
      <input type="email" id="reqEmail" placeholder="email@example.com">
      <label>Тип запроса</label>
      <select id="reqType">
        <option>Запрос на НИОКР</option>
        <option>Консультация</option>
        <option>Сотрудничество / Партнёрство</option>
        <option>Использование оборудования</option>
        <option>Другое</option>
      </select>
      <label>Сообщение *</label>
      <textarea id="reqMsg" placeholder="Опишите ваш запрос..."></textarea>
      <button class="submit" onclick="submitRequest()">Отправить запрос</button>
    </div>
    <div id="modalSuccess" style="display:none">
      <div class="success">
        <div class="icon">✅</div>
        <h3>Запрос отправлен!</h3>
        <p>Ваш запрос направлен в личный кабинет организации через платформу МОСНАУКА. Ожидайте ответа в течение 3 рабочих дней.</p>
        <button class="submit" onclick="closeModal()" style="margin-top:1.5rem;background:rgba(255,255,255,0.1)">Закрыть</button>
      </div>
    </div>
  </div>
</div>

<script>
function openRequestModal(context) {{
  document.getElementById('modalContext').textContent = context || 'через платформу МОСНАУКА';
  document.getElementById('modalForm').style.display = '';
  document.getElementById('modalSuccess').style.display = 'none';
  document.getElementById('requestModal').classList.add('active');
  document.body.style.overflow = 'hidden';
}}
function closeModal() {{
  document.getElementById('requestModal').classList.remove('active');
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
</body>
</html>"""


def generate_lab_pages(org_slug, org_short, laboratories):
    """Generate individual lab pages for an organization."""
    out_dir = OUTPUT_DIR / org_slug
    out_dir.mkdir(exist_ok=True)

    # Build global name→index map (same dedup order as generate_sci_pages)
    global_sci_idx = {}
    seen_names = set()
    gidx = 0
    for lab in laboratories:
        for s in lab.get('scientists', []):
            sname = s.get('name', '')
            if sname and sname not in seen_names:
                seen_names.add(sname)
                global_sci_idx[sname] = gidx
                gidx += 1

    for i, lab in enumerate(laboratories):
        name = esc(lab.get('name', 'Лаборатория'))
        desc = esc(lab.get('description', ''))
        tags = lab.get('tags', [])
        equipment = esc(lab.get('equipment', ''))
        methods = esc(lab.get('methods', ''))
        scientists = lab.get('scientists', [])

        # Tags HTML
        tags_html = ' '.join(
            f'<span class="tag">{esc(t)}</span>' for t in tags[:6]
        )

        # Research areas from lab
        areas = lab.get('research_areas', [])
        if isinstance(areas, str):
            areas = [a.strip() for a in areas.split(',') if a.strip()]
        areas_html = ''
        for area in areas:
            a_name = esc(area.get('name', area) if isinstance(area, dict) else area)
            a_desc = esc(area.get('description', '') if isinstance(area, dict) else '')
            areas_html += f"""<div class="info-card">
              <h3 style="font-size:0.9rem;font-weight:700;margin-bottom:0.5rem">{a_name}</h3>
              <p>{a_desc}</p>
            </div>\n"""

        # Scientists preview cards — use GLOBAL index for links
        sci_html = ''
        for j, s in enumerate(scientists):
            s_name = esc(s.get('name', ''))
            s_role = esc(s.get('role', ''))
            s_pubs = s.get('publications', 0)
            s_photo = s.get('photo_url', '')
            s_areas = s.get('research_areas', [])
            if isinstance(s_areas, str):
                s_areas = [x.strip() for x in s_areas.split(',') if x.strip()]
            s_areas_str = ', '.join(esc(a) for a in s_areas[:3])

            if s_photo:
                avatar_inner = f'<img src="{esc(s_photo)}" alt="{s_name}" loading="lazy">'
            else:
                parts = s_name.split()
                initials = ''.join(p[0] for p in parts[:2] if p)
                avatar_inner = f'<div class="initials">{initials}</div>'

            # Use global dedup index for correct link
            g_idx = global_sci_idx.get(s.get('name', ''), j)
            sci_html += f"""<a href="sci_{g_idx:03d}.html" class="preview-card">
              <div class="avatar">{avatar_inner}</div>
              <div style="min-width:0">
                <h3>{s_name}</h3>
                <div class="meta" style="color:#a1a1aa;margin-bottom:0.25rem">{s_role}</div>
                <div class="meta">{s_areas_str}</div>
                <div class="meta" style="margin-top:0.25rem">📚 {s_pubs or 0} публ.</div>
              </div>
            </a>\n"""

        # Equipment section
        equip_html = ''
        if equipment:
            equip_html = f"""<div class="info-card">
              <h2>🔬 Оборудование</h2>
              <p>{equipment}</p>
            </div>"""

        # Methods section
        methods_html = ''
        if methods:
            methods_html = f"""<div class="info-card">
              <h2>🧪 Методы</h2>
              <p>{methods}</p>
            </div>"""

        # Breadcrumbs
        bc = f'<a href="../index.html">МОСНАУКА</a> <span style="color:#333">/</span> '
        bc += f'<a href="../passport-{org_slug}.html">{esc(org_short)}</a> <span style="color:#333">/</span> '
        bc += f'<span style="color:#a1a1aa">{name[:50]}</span>'

        # Contacts from lab data
        lab_contacts = lab.get('contacts', [])
        contact_email = lab_contacts[0] if lab_contacts else ''
        email_html = f'<div style="font-size:0.8rem;color:#10b981;margin-bottom:0.5rem">✉ {esc(contact_email)}</div>' if contact_email else ''
        lab_url = esc(lab.get('url', ''))

        body = f"""
        <div class="detail-hero">
          <div style="display:flex;flex-wrap:wrap;gap:0.5rem;margin-bottom:1rem">{tags_html}</div>
          <h1>{name}</h1>
          <p style="color:#a1a1aa;line-height:1.7;margin-top:1rem">{desc}</p>
        </div>

        <!-- CTA Block -->
        <div style="background:linear-gradient(135deg,rgba(255,0,60,0.08),rgba(255,0,60,0.02));border:1px solid rgba(255,0,60,0.2);border-radius:1.5rem;padding:2rem;margin-bottom:2rem">
          <div style="font-size:1rem;font-weight:800;margin-bottom:0.75rem">📨 Связаться с лабораторией</div>
          {email_html}
          <div style="display:flex;flex-wrap:wrap;gap:0.75rem;margin-top:1rem">
            <button onclick="openRequestModal('Запрос на НИОКР — {name[:40]}')" style="display:inline-flex;align-items:center;gap:0.5rem;padding:0.75rem 1.5rem;border-radius:1rem;background:#ff003c;color:white;font-size:0.75rem;font-weight:800;text-transform:uppercase;letter-spacing:0.05em;border:none;cursor:pointer">📋 Направить запрос на НИОКР</button>
            <button onclick="openRequestModal('Запрос зав. лабораторией — {name[:30]}')" style="display:inline-flex;align-items:center;gap:0.5rem;padding:0.75rem 1.5rem;border-radius:1rem;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);color:#a1a1aa;font-size:0.75rem;font-weight:800;text-transform:uppercase;cursor:pointer">✉ Написать зав. лабораторией</button>
            {"<a href='" + lab_url + "' target='_blank' style='display:inline-flex;align-items:center;gap:0.5rem;padding:0.75rem 1.5rem;border-radius:1rem;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);color:#a1a1aa;font-size:0.75rem;font-weight:800;text-transform:uppercase'>🔗 Профиль CoLab</a>" if lab_url else ''}
          </div>
        </div>

        {equip_html}
        {methods_html}
        {areas_html}

        <div class="section-header" style="margin-top:2.5rem">
          <h2 class="section-title">👩‍🔬 Учёные ({len(scientists)})</h2>
        </div>
        <div class="cards-grid" style="grid-template-columns:repeat(auto-fill,minmax(300px,1fr))">
          {sci_html}
        </div>
        """

        page_html = page_wrap(f"{name} | {org_short}", bc, body)
        with open(out_dir / f"lab_{i:03d}.html", "w") as f:
            f.write(page_html)

    return len(laboratories)


def generate_sci_pages(org_slug, org_short, laboratories):
    """Generate individual scientist pages. Deduplicates across labs."""
    out_dir = OUTPUT_DIR / org_slug
    out_dir.mkdir(exist_ok=True)

    seen = set()
    idx = 0
    for lab in laboratories:
        lab_name = lab.get('name', '')
        for sci in lab.get('scientists', []):
            name = sci.get('name', '')
            if not name or name in seen:
                continue
            seen.add(name)

            s_name = esc(name)
            s_role = esc(sci.get('role', ''))
            s_photo = sci.get('photo_url', '')
            s_pubs = sci.get('publications', 0)
            s_h = sci.get('h_index')
            s_url = esc(sci.get('url', ''))
            areas = sci.get('research_areas', [])
            if isinstance(areas, str):
                areas = [a.strip() for a in areas.split(',') if a.strip()]

            # Avatar
            if s_photo:
                avatar = f'<img src="{esc(s_photo)}" style="width:6rem;height:6rem;border-radius:1rem;object-fit:cover;border:1px solid rgba(255,255,255,0.1)" alt="{s_name}" loading="lazy">'
            else:
                parts = name.split()
                ini = ''.join(p[0] for p in parts[:2] if p)
                avatar = f'<div style="width:6rem;height:6rem;border-radius:1rem;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#dc2626,#7f1d1d);color:white;font-size:1.5rem;font-weight:900">{ini}</div>'

            # Areas tags
            areas_html = ' '.join(f'<span class="tag">{esc(a)}</span>' for a in areas[:8])

            # Metrics
            metrics = ''
            if s_pubs:
                metrics += f'<div class="metric-box"><div class="label">Публикации</div><div class="value">{s_pubs}</div></div>'
            if s_h and str(s_h) != 'None':
                metrics += f'<div class="metric-box"><div class="label">h-index</div><div class="value" style="color:#ff003c">{s_h}</div></div>'

            bc = f'<a href="../index.html">МОСНАУКА</a> <span style="color:#333">/</span> '
            bc += f'<a href="../passport-{org_slug}.html">{esc(org_short)}</a> <span style="color:#333">/</span> '
            bc += f'<span style="color:#a1a1aa">{s_name[:40]}</span>'

            body = f"""
            <div class="detail-hero">
              <div style="display:flex;gap:1.5rem;align-items:flex-start;flex-wrap:wrap">
                {avatar}
                <div>
                  <h1 style="font-size:1.75rem">{s_name}</h1>
                  <div style="color:#a1a1aa;font-size:0.85rem;margin-top:0.25rem">{s_role}</div>
                  <div style="color:#52525b;font-size:0.75rem;margin-top:0.25rem">{esc(lab_name)}</div>
                </div>
              </div>
              <div style="display:flex;flex-wrap:wrap;gap:0.5rem;margin-top:1.5rem">{areas_html}</div>
            </div>

            <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:1rem;margin-bottom:2rem">
              {metrics}
            </div>

            <!-- CTA Block -->
            <div style="background:linear-gradient(135deg,rgba(255,0,60,0.08),rgba(255,0,60,0.02));border:1px solid rgba(255,0,60,0.2);border-radius:1.5rem;padding:2rem;margin-bottom:2rem">
              <div style="font-size:1rem;font-weight:800;margin-bottom:0.75rem">📨 Связаться с учёным</div>
              <p style="color:#a1a1aa;font-size:0.8rem;margin-bottom:1rem">Направьте запрос на сотрудничество, консультацию или совместный проект НИОКР.</p>
              <div style="display:flex;flex-wrap:wrap;gap:0.75rem">
                <button onclick="openRequestModal('Запрос учёному — {s_name}')" style="display:inline-flex;align-items:center;gap:0.5rem;padding:0.75rem 1.5rem;border-radius:1rem;background:#ff003c;color:white;font-size:0.75rem;font-weight:800;text-transform:uppercase;letter-spacing:0.05em;border:none;cursor:pointer">📩 Направить запрос</button>
                {"<a href='" + s_url + "' target='_blank' style='display:inline-flex;align-items:center;gap:0.5rem;padding:0.75rem 1.5rem;border-radius:1rem;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);color:#a1a1aa;font-size:0.75rem;font-weight:800;text-transform:uppercase'>🔗 Профиль CoLab</a>" if s_url else ''}
              </div>
            </div>
            """

            page_html = page_wrap(f"{s_name} | {org_short}", bc, body)
            with open(out_dir / f"sci_{idx:03d}.html", "w") as f:
                f.write(page_html)
            idx += 1

    return idx


def generate_proj_pages(org_slug, org_short, projects):
    """Generate individual project pages with full ЕГИСУ data."""
    out_dir = OUTPUT_DIR / org_slug
    out_dir.mkdir(exist_ok=True)

    for i, p in enumerate(projects):
        pname = esc(p.get('name', 'Проект'))
        abstract = esc(p.get('abstract', ''))
        keywords = p.get('keyword_list', [])
        reg_num = esc(p.get('registration_number', ''))
        budget_val = sum(float(b.get('funds', 0) or 0) for b in p.get('budgets', []))
        budget_str = f'{budget_val:,.0f} тыс. ₽' if budget_val > 0 else ''

        # New fields from ЕГИСУ
        customer = p.get('customer', {})
        cust_name = esc(customer.get('name', customer.get('short_name', ''))) if customer else ''
        cust_short = esc(customer.get('short_name', '')) if customer else ''

        executor = p.get('executor', {})
        exec_name = esc(executor.get('short_name', executor.get('name', ''))) if executor else ''

        authors = p.get('authors', [])
        stage_start = p.get('stage_start_date', '')
        stage_end = p.get('stage_end_date', '')
        stage_num = p.get('stage_number', '')
        pub_count = p.get('publication_count', 0) or 0

        rubrics = p.get('rubrics', [])
        work_sup = p.get('work_supervisor')
        org_sup = p.get('organization_supervisor')

        kw_html = ' '.join(f'<span class="tag">{esc(k)}</span>' for k in keywords[:10])

        # Rubrics tags
        rubric_html = ''
        if rubrics:
            rubric_html = ' '.join(
                f'<span class="tag" style="border-color:rgba(59,130,246,0.3);color:#93c5fd">{esc(r.get("name", ""))}</span>'
                for r in rubrics[:5] if r.get('name')
            )

        bc = f'<a href="../index.html">МОСНАУКА</a> <span style="color:#333">/</span> '
        bc += f'<a href="../passport-{org_slug}.html">{esc(org_short)}</a> <span style="color:#333">/</span> '
        bc += f'<span style="color:#a1a1aa">Проект НИОКТР</span>'

        # Metrics grid
        metrics = []
        if budget_str:
            metrics.append(f'<div class="metric-box"><div class="label">Бюджет</div><div class="value" style="font-size:1.25rem">{budget_str}</div></div>')
        if reg_num:
            metrics.append(f'<div class="metric-box"><div class="label">Рег. номер ЕГИСУ</div><div class="value" style="font-size:0.85rem;font-style:normal">{reg_num}</div></div>')
        if stage_start and stage_end:
            metrics.append(f'<div class="metric-box"><div class="label">Период</div><div class="value" style="font-size:0.9rem;font-style:normal">{stage_start} — {stage_end}</div></div>')
        if stage_num:
            metrics.append(f'<div class="metric-box"><div class="label">Этап</div><div class="value">№{stage_num}</div></div>')
        if pub_count:
            metrics.append(f'<div class="metric-box"><div class="label">Публикации</div><div class="value">{pub_count}</div></div>')
        metrics_html = '\n'.join(metrics)

        # Authors list
        auth_html = ''
        if authors:
            auth_items = []
            for a in authors[:15]:
                name_parts = [a.get('surname', ''), a.get('name', ''), a.get('patronymic', '')]
                full = ' '.join(p for p in name_parts if p)
                degree = a.get('degree', '')
                if degree:
                    auth_items.append(f'<li style="margin-bottom:0.25rem"><strong style="color:#e4e4e7">{esc(full)}</strong> <span style="color:#71717a;font-size:0.8rem">{esc(degree)}</span></li>')
                else:
                    auth_items.append(f'<li style="margin-bottom:0.25rem">{esc(full)}</li>')
            auth_html = f'''<div class="info-card">
              <h2>👥 Авторы ({len(authors)})</h2>
              <ul style="list-style:none;padding:0">{"".join(auth_items)}</ul>
              {"<p style='color:#52525b;font-size:0.8rem;margin-top:0.5rem'>...и ещё " + str(len(authors)-15) + "</p>" if len(authors) > 15 else ""}
            </div>'''

        # Customer & executor
        parties_html = ''
        if cust_name or exec_name:
            parts = []
            if cust_name:
                parts.append(f'''<div class="metric-box" style="text-align:left">
                  <div class="label">Заказчик</div>
                  <div style="color:#e4e4e7;font-size:0.9rem;font-weight:600">{cust_short or cust_name}</div>
                  {"<div style='color:#71717a;font-size:0.75rem;margin-top:0.25rem'>" + cust_name + "</div>" if cust_short and cust_name != cust_short else ""}
                </div>''')
            if exec_name:
                parts.append(f'''<div class="metric-box" style="text-align:left">
                  <div class="label">Исполнитель</div>
                  <div style="color:#e4e4e7;font-size:0.9rem;font-weight:600">{exec_name}</div>
                </div>''')
            parties_html = f'<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:1rem;margin-bottom:1.5rem">{"".join(parts)}</div>'

        body = f"""
        <div class="detail-hero">
          <div style="display:flex;flex-wrap:wrap;gap:0.5rem;margin-bottom:0.75rem">{kw_html}</div>
          {"<div style='display:flex;flex-wrap:wrap;gap:0.5rem;margin-bottom:0.75rem'>" + rubric_html + "</div>" if rubric_html else ""}
          <h1 style="font-size:1.5rem">{pname}</h1>
        </div>

        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:1rem;margin-bottom:2rem">
          {metrics_html}
        </div>

        {parties_html}

        {"<div class='info-card'><h2>📋 Аннотация</h2><p>" + abstract + "</p></div>" if abstract else ""}

        {auth_html}
        """

        page_html = page_wrap(f"Проект | {org_short}", bc, body)
        with open(out_dir / f"proj_{i:04d}.html", "w") as f:
            f.write(page_html)

    return len(projects)


def generate_rid_pages(org_slug, org_short, rids):
    """Generate individual RID pages with full ЕГИСУ data."""
    out_dir = OUTPUT_DIR / org_slug
    out_dir.mkdir(exist_ok=True)

    for i, r in enumerate(rids):
        rname = esc(r.get('name', 'РИД'))
        rtype = esc(r.get('rid_type', ''))
        abstract = esc(r.get('abstract', ''))
        keywords = r.get('keyword_list', [])
        authors = r.get('authors', [])
        reg_num = esc(r.get('registration_number', ''))
        created_date = r.get('created_date', '')
        using_ways = esc(r.get('using_ways', ''))

        # Customer / executors
        customer = r.get('customer', {})
        cust_name = esc(customer.get('short_name', customer.get('name', ''))) if customer else ''
        executors = r.get('executors', [])
        exec_name = esc(executors[0].get('short_name', executors[0].get('name', ''))) if executors else ''

        rubrics = r.get('rubrics', [])
        e2e_tech = r.get('end_to_end_initiative_technologies', [])
        nti_markets = r.get('national_technology_initiative_markets', [])
        dev_priorities = r.get('development_priorities', [])

        kw_html = ' '.join(f'<span class="tag">{esc(k)}</span>' for k in keywords[:10])
        type_icon = {'Программа для ЭВМ': '💻', 'База данных': '🗄️', 'Ноу-хау': '🔐',
                     'Полезная модель': '⚙️', 'Изобретение': '💡'}.get(rtype, '📄')

        # Rubrics tags
        rubric_html = ''
        if rubrics:
            rubric_html = ' '.join(
                f'<span class="tag" style="border-color:rgba(59,130,246,0.3);color:#93c5fd">{esc(rb.get("name", ""))}</span>'
                for rb in rubrics[:5] if rb.get('name')
            )

        # Technology tags (e2e, NTI, priorities)
        tech_tags = []
        for t in e2e_tech[:3]:
            tech_tags.append(f'<span class="tag" style="border-color:rgba(16,185,129,0.3);color:#6ee7b7">{esc(t)}</span>')
        for t in nti_markets[:3]:
            tech_tags.append(f'<span class="tag" style="border-color:rgba(245,158,11,0.3);color:#fcd34d">{esc(t)}</span>')
        tech_html = ' '.join(tech_tags)

        # Authors list
        auth_html = ''
        if authors:
            auth_items = []
            for a in authors[:15]:
                name_parts = [a.get('surname', ''), a.get('name', ''), a.get('patronymic', '')]
                full = ' '.join(p for p in name_parts if p)
                degree = a.get('degree', '')
                if degree and degree != 'Отсутствует':
                    auth_items.append(f'<li style="margin-bottom:0.25rem"><strong style="color:#e4e4e7">{esc(full)}</strong> <span style="color:#71717a;font-size:0.8rem">{esc(degree)}</span></li>')
                else:
                    auth_items.append(f'<li style="margin-bottom:0.25rem">{esc(full)}</li>')
            auth_html = f'''<div class="info-card">
              <h2>👥 Авторы ({len(authors)})</h2>
              <ul style="list-style:none;padding:0">{"".join(auth_items)}</ul>
            </div>'''

        # Metrics
        metrics = []
        if rtype:
            metrics.append(f'<div class="metric-box"><div class="label">Тип РИД</div><div class="value" style="font-size:1rem;font-style:normal">{type_icon} {rtype}</div></div>')
        if reg_num:
            metrics.append(f'<div class="metric-box"><div class="label">Рег. номер</div><div class="value" style="font-size:0.85rem;font-style:normal">{reg_num}</div></div>')
        if created_date:
            metrics.append(f'<div class="metric-box"><div class="label">Дата регистрации</div><div class="value" style="font-size:0.9rem;font-style:normal">{created_date}</div></div>')
        if cust_name:
            metrics.append(f'<div class="metric-box" style="text-align:left"><div class="label">Заказчик</div><div style="color:#e4e4e7;font-size:0.9rem;font-weight:600">{cust_name}</div></div>')
        if exec_name:
            metrics.append(f'<div class="metric-box" style="text-align:left"><div class="label">Исполнитель</div><div style="color:#e4e4e7;font-size:0.9rem;font-weight:600">{exec_name}</div></div>')
        metrics_html = '\n'.join(metrics)

        bc = f'<a href="../index.html">МОСНАУКА</a> <span style="color:#333">/</span> '
        bc += f'<a href="../passport-{org_slug}.html">{esc(org_short)}</a> <span style="color:#333">/</span> '
        bc += f'<span style="color:#a1a1aa">РИД</span>'

        body = f"""
        <div class="detail-hero">
          <div style="display:flex;flex-wrap:wrap;gap:0.5rem;margin-bottom:0.75rem">{kw_html}</div>
          {"<div style='display:flex;flex-wrap:wrap;gap:0.5rem;margin-bottom:0.75rem'>" + rubric_html + "</div>" if rubric_html else ""}
          {"<div style='display:flex;flex-wrap:wrap;gap:0.5rem;margin-bottom:0.75rem'>" + tech_html + "</div>" if tech_html else ""}
          <h1 style="font-size:1.5rem">{rname}</h1>
        </div>

        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:1rem;margin-bottom:2rem">
          {metrics_html}
        </div>

        {"<div class='info-card'><h2>📋 Описание</h2><p>" + abstract + "</p></div>" if abstract else ""}

        {"<div class='info-card'><h2>🔧 Способы использования</h2><p style='white-space:pre-line'>" + using_ways + "</p></div>" if using_ways else ""}

        {auth_html}

        {"<div class='info-card'><h2>🎯 Приоритеты развития</h2><p>" + "; ".join(esc(dp[:120]) for dp in dev_priorities[:3]) + "</p></div>" if dev_priorities else ""}
        """

        page_html = page_wrap(f"РИД: {rname[:60]} | {org_short}", bc, body)
        with open(out_dir / f"rid_{i:04d}.html", "w") as f:
            f.write(page_html)

    return len(rids)


if __name__ == '__main__':
    import sys
    org_files = sorted(DATA_DIR.glob("org_*.json"))
    if not org_files:
        print("❌ No org_*.json files found in", DATA_DIR)
        sys.exit(1)

    total_stats = {'labs': 0, 'sci': 0, 'proj': 0, 'rid': 0}
    for org_file in org_files:
        with open(org_file) as f:
            org = json.load(f)

        slug = org.get('slug', '')
        if not slug:
            print(f"⚠️ Skipping {org_file.name}: no slug")
            continue
        short = org.get('identity', {}).get('name_short', slug)
        labs = org.get('source_colab', {}).get('data', {}).get('laboratories', [])
        projects = org.get('source_egisu', {}).get('data', {}).get('projects', [])
        rids = org.get('source_egisu', {}).get('data', {}).get('rid', [])

        out_dir = OUTPUT_DIR / slug
        out_dir.mkdir(exist_ok=True)

        n_labs = generate_lab_pages(slug, short, labs)
        n_sci = generate_sci_pages(slug, short, labs)
        n_proj = generate_proj_pages(slug, short, projects)
        n_rid = generate_rid_pages(slug, short, rids)

        total_stats['labs'] += n_labs
        total_stats['sci'] += n_sci
        total_stats['proj'] += n_proj
        total_stats['rid'] += n_rid

        print(f"✅ {short:<30} {n_labs:>3} labs  {n_sci:>4} sci  {n_proj:>4} proj  {n_rid:>4} rid")

    print(f"\n📁 Total: {total_stats['labs']} labs, {total_stats['sci']} scientists, "
          f"{total_stats['proj']} projects, {total_stats['rid']} RID pages")


