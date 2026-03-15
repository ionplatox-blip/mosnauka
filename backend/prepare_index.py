#!/usr/bin/env python3
"""
МОСНАУКА — prepare_index.py
Читает все org_*.json из COLAB_DATA/passports/ и строит плоский search_index.json
Используется бэкендом для полнотекстового поиска

Запуск: python3 prepare_index.py
"""

import json
import os
import re
from pathlib import Path

PASSPORTS_DIR = Path("/Users/shakhgildyangy/COLAB_DATA/passports")
OUTPUT_FILE = Path("/Users/shakhgildyangy/mosnauka-backend/search_index.json")


def parse_budget(budget_list):
    """Суммируем все источники финансирования, возвращаем сумму в рублях."""
    total = 0.0
    for b in (budget_list or []):
        try:
            # funds хранится в тысячах рублей
            total += float(b.get("funds", 0)) * 1000
        except (ValueError, TypeError):
            pass
    return int(total)


def extract_keywords(keywords_raw):
    """Нормализуем ключевые слова в список строк."""
    if isinstance(keywords_raw, list):
        return [str(k).strip().lower() for k in keywords_raw if k]
    if isinstance(keywords_raw, str):
        # Разделяем по запятой, точке с запятой
        return [k.strip().lower() for k in re.split(r"[,;]+", keywords_raw) if k.strip()]
    return []


def extract_year(date_str):
    """Извлекаем год из строки даты."""
    if not date_str:
        return None
    m = re.search(r"\d{4}", str(date_str))
    return int(m.group(0)) if m else None


def build_index():
    # Загружаем индекс организаций
    index_file = PASSPORTS_DIR / "index.json"
    with open(index_file, encoding="utf-8") as f:
        master_index = json.load(f)

    records = []
    orgs_summary = []

    for org_meta in master_index["organizations"]:
        org_file = PASSPORTS_DIR / org_meta["file"]
        if not org_file.exists():
            print(f"  ⚠ Файл не найден: {org_file}")
            continue

        with open(org_file, encoding="utf-8") as f:
            org = json.load(f)

        identity = org.get("identity", {})
        org_id = org.get("id", "")
        org_slug = org.get("slug", "")
        org_name_short = identity.get("name_short", "")
        org_name_full = identity.get("name_full", "")
        org_logo = identity.get("logo_url", "")
        org_website = identity.get("website", "")

        # ── ПРОЕКТЫ НИОКТР (EGISU ikrbs) ──
        egisu_projects = org.get("source_egisu", {}).get("data", {}).get("projects", [])
        org_project_count = len(egisu_projects)
        org_total_budget = 0

        for proj in egisu_projects:
            budget_rub = parse_budget(proj.get("budgets"))  # field is 'budgets' not 'budget'
            org_total_budget += budget_rub
            # keyword_list can be a list or a string
            raw_kw = proj.get("keyword_list") or proj.get("keywords") or []
            keywords = extract_keywords(raw_kw)
            rubric_names = [r.get("name", "") for r in (proj.get("rubrics") or [])]
            oecd_names = [o.get("name", "") for o in (proj.get("oecds") or [])]
            reg_num = proj.get("registration_number") or proj.get("reg_number", "")

            record = {
                "id": f"{org_id}_proj_{reg_num}",
                "type": "project",
                "org_id": org_id,
                "org_slug": org_slug,
                "org_name": org_name_short,
                "org_name_full": org_name_full,
                "org_logo": org_logo,
                "org_website": org_website,
                "title": proj.get("name", ""),
                "abstract": proj.get("abstract", ""),
                "keywords": keywords,
                "rubrics": rubric_names,
                "oecds": oecd_names,
                "report_type": proj.get("report_type", ""),
                "year_start": extract_year(proj.get("stage_start_date") or proj.get("stage_start")),
                "year_end": extract_year(proj.get("stage_end_date") or proj.get("stage_end")),
                "pub_count": proj.get("publication_count") or proj.get("pub_count", 0),
                "authors_count": len(proj.get("authors") or []) or proj.get("authors_count", 0),
                "budget_rub": budget_rub,
                "reg_number": reg_num,
                "nioktr": proj.get("nioktr", ""),
                # Полнотекстовое поле для поиска
                "_search_text": " ".join(filter(None, [
                    proj.get("name", ""),
                    proj.get("abstract", ""),
                    " ".join(keywords),
                    " ".join(rubric_names),
                    org_name_short,
                    org_name_full,
                ])).lower(),
            }
            records.append(record)

        # ── РИД ──
        rid_list = org.get("source_egisu", {}).get("data", {}).get("rid", [])
        for rid in rid_list:
            raw_kw = rid.get("keyword_list") or rid.get("keywords") or []
            kw = extract_keywords(raw_kw)
            rubric_names = [r.get("name", "") for r in (rid.get("rubrics") or [])]
            reg_num = rid.get("registration_number") or rid.get("reg_number", "")

            record = {
                "id": f"{org_id}_rid_{reg_num}",
                "type": "rid",
                "org_id": org_id,
                "org_slug": org_slug,
                "org_name": org_name_short,
                "org_name_full": org_name_full,
                "org_logo": org_logo,
                "org_website": org_website,
                "title": rid.get("name", ""),
                "abstract": rid.get("abstract", ""),
                "keywords": kw,
                "rubrics": rubric_names,
                "oecds": [],
                "rid_type": rid.get("rid_type", ""),
                "using_ways": rid.get("using_ways", ""),
                "year_start": extract_year(rid.get("created_date")),
                "year_end": None,
                "pub_count": 0,
                "authors_count": len(rid.get("authors") or []) or rid.get("authors_count", 0),
                "budget_rub": 0,
                "reg_number": reg_num,
                "nioktr": rid.get("nioktr", ""),
                "_search_text": " ".join(filter(None, [
                    rid.get("name", ""),
                    rid.get("abstract", ""),
                    rid.get("using_ways", ""),
                    " ".join(kw),
                    " ".join(rubric_names),
                    org_name_short,
                ])).lower(),
            }
            records.append(record)

        # ── ЛАБОРАТОРИИ (Colab) ──
        colab_labs = org.get("source_colab", {}).get("data", {}).get("laboratories", [])
        for lab in colab_labs:
            tags = lab.get("tags", [])
            record = {
                "id": f"{org_id}_lab_{lab.get('id', '')}",
                "type": "lab",
                "org_id": org_id,
                "org_slug": org_slug,
                "org_name": org_name_short,
                "org_name_full": org_name_full,
                "org_logo": org_logo,
                "org_website": org_website,
                "title": lab.get("name", ""),
                "abstract": lab.get("description", ""),
                "keywords": [t.lower() for t in tags],
                "rubrics": [],
                "oecds": [],
                "equipment": lab.get("equipment", []),
                "year_start": None,
                "year_end": None,
                "pub_count": 0,
                "authors_count": 0,
                "budget_rub": 0,
                "reg_number": "",
                "nioktr": "",
                "_search_text": " ".join(filter(None, [
                    lab.get("name", ""),
                    lab.get("description", ""),
                    " ".join(str(t) for t in tags),
                    org_name_short,
                ])).lower(),
            }
            records.append(record)

        # ── УЧЁНЫЕ (Colab) ──
        colab_sci = org.get("source_colab", {}).get("data", {}).get("standalone_researchers", [])
        top3 = org.get("source_colab", {}).get("data", {}).get("top3_scientists", [])
        all_sci = (top3 or []) + (colab_sci or [])
        seen_sci = set()
        for sci in all_sci:
            sci_id = sci.get("id") or sci.get("name", "")
            if sci_id in seen_sci:
                continue
            seen_sci.add(sci_id)
            areas = sci.get("areas") or sci.get("specialization") or ""
            record = {
                "id": f"{org_id}_sci_{sci_id}",
                "type": "scientist",
                "org_id": org_id,
                "org_slug": org_slug,
                "org_name": org_name_short,
                "org_name_full": org_name_full,
                "org_logo": org_logo,
                "org_website": org_website,
                "title": sci.get("name", ""),
                "abstract": areas,
                "keywords": [a.strip().lower() for a in str(areas).split(",") if a.strip()],
                "photo": sci.get("photo") or sci.get("avatar", ""),
                "colab_url": sci.get("url") or sci.get("colab_url", ""),
                "rubrics": [],
                "oecds": [],
                "year_start": None,
                "year_end": None,
                "pub_count": sci.get("pubs_count") or sci.get("pub_count", 0),
                "authors_count": 0,
                "budget_rub": 0,
                "reg_number": "",
                "nioktr": "",
                "_search_text": " ".join(filter(None, [
                    sci.get("name", ""),
                    areas,
                    org_name_short,
                ])).lower(),
            }
            records.append(record)

        # Сводка по организации
        orgs_summary.append({
            "id": org_id,
            "slug": org_slug,
            "name": org_name_short,
            "name_full": org_name_full,
            "logo": org_logo,
            "website": org_website,
            "projects_count": org_project_count,
            "total_budget_rub": org_total_budget,
        })

        print(f"  ✓ {org_name_short}: {org_project_count} проектов, {len(rid_list)} РИД, {len(colab_labs)} лаб")

    # Финальный индекс
    output = {
        "meta": {
            "total_records": len(records),
            "total_orgs": len(orgs_summary),
            "breakdown": {
                "projects": sum(1 for r in records if r["type"] == "project"),
                "rid": sum(1 for r in records if r["type"] == "rid"),
                "labs": sum(1 for r in records if r["type"] == "lab"),
                "scientists": sum(1 for r in records if r["type"] == "scientist"),
            }
        },
        "organizations": orgs_summary,
        "records": records,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=None, separators=(",", ":"))

    size_mb = OUTPUT_FILE.stat().st_size / 1024 / 1024
    print(f"\n✅ Индекс сохранён: {OUTPUT_FILE}")
    print(f"   Всего записей: {len(records)}")
    print(f"   Размер файла: {size_mb:.2f} MB")
    print(f"   Организаций: {len(orgs_summary)}")


if __name__ == "__main__":
    print("🔧 Строим поисковый индекс МОСНАУКА...\n")
    build_index()
