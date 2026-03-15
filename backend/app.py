#!/usr/bin/env python3
"""
МОСНАУКА — AI Search Backend
Flask API сервер для ИИ-поиска по базе НИОКР

POST /api/ai-search  { query: string }
GET  /api/health

Деплой: Render Web Service (Python)
ENV: OPENROUTER_API_KEY
"""

import json
import math
import os
import re
import time
from collections import Counter, defaultdict
from pathlib import Path

import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["*"])  # В продакшне заменить на список разрешённых доменов
# ─────────────────────────────────────────────
# Загрузка индекса и эмбеддингов при старте
# ─────────────────────────────────────────────
INDEX_PATH = Path(__file__).parent / "search_index.json"
NPY_PATH = Path(__file__).parent / "embeddings.npy"
IDS_PATH = Path(__file__).parent / "embeddings_ids.json"

print("📂 Загружаем поисковый индекс и векторы...")
t0 = time.time()
with open(INDEX_PATH, encoding="utf-8") as f:
    _raw = json.load(f)

RECORDS = _raw["records"]
ORGS = {o["id"]: o for o in _raw["organizations"]}
INDEX_META = _raw["meta"]

# Маппинг id -> record для быстрого доступа
REC_BY_ID = {r["id"]: r for r in RECORDS}

# Пытаемся загрузить эмбеддинги
EMBEDDINGS = None
EMBED_IDS = []
try:
    if NPY_PATH.exists() and IDS_PATH.exists():
        import numpy as np
        EMBEDDINGS = np.load(NPY_PATH)
        with open(IDS_PATH, encoding="utf-8") as f:
            EMBED_IDS = json.load(f)
        print(f"✅ Векторы загружены: {EMBEDDINGS.shape}")
    else:
        print("⚠️ Векторы не найдены, поиск будет работать только по ключевым словам")
except Exception as e:
    print(f"⚠️ Ошибка загрузки векторов: {e}")

print(f"✅ Индекс готов: {len(RECORDS)} записей за {time.time()-t0:.2f}с")


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")


def get_query_embedding(query: str):
    """Получаем вектор запроса через OpenRouter (512-dim)."""
    if not OPENROUTER_API_KEY:
        return None
    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/embeddings",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "openai/text-embedding-3-small",
                "input": query,
                "dimensions": 512,
            },
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json()["data"][0]["embedding"]
    except Exception as e:
        print(f"Embedding API error: {e}")
    return None


# ─────────────────────────────────────────────
# Поиск: TF-IDF + Семантика (Hybrid Search)
# ─────────────────────────────────────────────
def tokenize(text: str) -> list[str]:
    """Разбиваем текст на токены (слова длиннее 2 символов)."""
    text = text.lower()
    return [t for t in re.findall(r"[а-яa-z\d]{3,}", text)]


def score_record(query_tokens: set[str], record: dict) -> float:
    """Считаем релевантность записи запросу (0..1)."""
    search_text = record.get("_search_text", "")
    rec_tokens = tokenize(search_text)
    if not rec_tokens:
        return 0.0

    # TF: доля совпавших токенов из запроса в тексте записи
    rec_set = set(rec_tokens)
    matched = query_tokens & rec_set
    if not matched:
        return 0.0

    base_score = len(matched) / max(len(query_tokens), 1)

    # Бонус за совпадение в названии
    title_tokens = set(tokenize(record.get("title", "")))
    title_bonus = len(query_tokens & title_tokens) / max(len(query_tokens), 1) * 0.5

    # Бонус за совпадение в ключевых словах
    kw_tokens = set(tokenize(" ".join(record.get("keywords", []))))
    kw_bonus = len(query_tokens & kw_tokens) / max(len(query_tokens), 1) * 0.3

    # Предпочитаем проекты, затем РИД, затем лаборатории
    type_bonus = {"project": 0.35, "rid": 0.08, "lab": 0.04, "scientist": 0.0}
    t_bonus = type_bonus.get(record.get("type", ""), 0.0)

    return min(1.0, base_score + title_bonus + kw_bonus + t_bonus)


def keyword_search(query: str) -> dict:
    """Keyword поиск — возвращает {record_id: score}."""
    query_tokens = set(tokenize(query))
    if not query_tokens:
        return {}
    scores = {}
    for rec in RECORDS:
        s = score_record(query_tokens, rec)
        if s > 0.0:
            scores[rec["id"]] = s
    return scores


def semantic_search(query: str) -> dict:
    """Семантический поиск — cosine similarity с embeddings. Возвращает {record_id: score}."""
    if EMBEDDINGS is None or not EMBED_IDS:
        return {}
    vec = get_query_embedding(query)
    if not vec:
        return {}
    import numpy as np
    q = np.array(vec, dtype=np.float32)
    q_norm = np.linalg.norm(q)
    if q_norm == 0:
        return {}
    q = q / q_norm
    norms = np.linalg.norm(EMBEDDINGS, axis=1, keepdims=True)
    norms[norms == 0] = 1e-10
    sims = np.dot(EMBEDDINGS / norms, q)
    scores = {}
    for i, sim in enumerate(sims):
        s = float((sim + 1) / 2)  # -1..1 → 0..1
        if s > 0.60:  # жёсткий порог — отрезает "доставку мРНК" при запросе "роботы доставки"
            scores[EMBED_IDS[i]] = s
    return scores


def hybrid_search(query: str, top_n: int = 100) -> list[tuple]:
    """Гибридный поиск: 80% семантика + 20% ключевые слова.
    
    Семантика доминирует — ловит смысл ("роботы доставки" ≠ "доставка мРНК").
    Keywords — только бустер для точных совпадений.
    """
    kw_scores = keyword_search(query)
    sem_scores = semantic_search(query)
    has_semantic = bool(sem_scores)

    # Если семантика работает — берём только записи с семантическим скором
    # Keyword-only записи НЕ попадают в результат (они дают мусор типа "доставка мРНК")
    if has_semantic:
        all_ids = set(sem_scores.keys())
    else:
        all_ids = set(kw_scores.keys())
    
    if not all_ids:
        return []

    max_kw = max(kw_scores.values()) if kw_scores else 1.0
    results = []
    for rid in all_ids:
        sem = sem_scores.get(rid, 0.0)
        kw = kw_scores.get(rid, 0.0) / max_kw
        if has_semantic:
            score = 0.80 * sem + 0.20 * kw
        else:
            score = kw
        if rid in REC_BY_ID:
            results.append((score, REC_BY_ID[rid]))

    results.sort(key=lambda x: x[0], reverse=True)
    return results[:top_n]


def search(query: str, top_n: int = 100) -> list[tuple]:
    """Обёртка — вызывает hybrid_search."""
    return hybrid_search(query, top_n)


# ─────────────────────────────────────────────
# Агрегация данных для ответа
# ─────────────────────────────────────────────
def build_stats(scored_records: list[tuple]) -> dict:
    """Считаем аналитику по найденным записям."""
    orgs_seen = set()
    total_budget = 0
    proj_count = 0
    rid_count = 0

    for score, rec in scored_records:
        rec_type = rec["type"]
        if rec_type == "project":
            proj_count += 1
            total_budget += rec.get("budget_rub", 0)
        elif rec_type == "rid":
            rid_count += 1
        orgs_seen.add(rec["org_id"])

    max_match = int(scored_records[0][0] * 100) if scored_records else 0

    return {
        "projects_count": proj_count,
        "rids_count": rid_count,
        "orgs_count": len(orgs_seen),
        "total_funding_rub": total_budget,
        "max_match_pct": max_match,
    }


def format_projects(scored_records: list[tuple], top_n: int = 6) -> list[dict]:
    """Форматируем топ-N проектов для фронта."""
    proj_records = [(s, r) for s, r in scored_records if r["type"] == "project"][:top_n]
    result = []
    for score, rec in proj_records:
        result.append({
            "title": rec["title"],
            "match_percentage": min(99, int(score * 100)),
            "tags": rec.get("keywords", [])[:4],
            "abstract_short": (rec.get("abstract") or "")[:300],
            "reg_number": rec.get("reg_number", ""),
            "report_type": rec.get("report_type", ""),
            "budget_rub": rec.get("budget_rub", 0),
            "year": rec.get("year_start"),
            "org_name": rec.get("org_name", ""),
            "org_slug": rec.get("org_slug", ""),
            "org_logo": rec.get("org_logo", ""),
        })
    return result


def format_organizations(scored_records: list[tuple], top_n: int = 3) -> list[dict]:
    """Топ-N организаций по релевантности.
    
    Проекты весят 1.0x, РИД — 0.6x, лаборатории — 0.3x.
    Это отражает реальную компетентность: готовый проект > РИД > лаб описание.
    """
    # Для каждой организации собираем взвешенные скоры
    TYPE_WEIGHT = {"project": 1.0, "rid": 0.6, "lab": 0.3, "scientist": 0.2}
    org_weighted = defaultdict(float)
    org_counts = defaultdict(lambda: {"project": 0, "rid": 0, "lab": 0})

    for score, rec in scored_records:
        rec_type = rec["type"]
        weight = TYPE_WEIGHT.get(rec_type, 0.2)
        org_id = rec["org_id"]
        org_weighted[org_id] += score * weight
        if rec_type in org_counts[org_id]:
            org_counts[org_id][rec_type] += 1

    ranked = sorted(org_weighted.items(), key=lambda x: x[1], reverse=True)[:top_n]

    result = []
    for org_id, weighted_score in ranked:
        org = ORGS.get(org_id, {})
        counts = org_counts[org_id]
        result.append({
            "org_name": org.get("name", ""),
            "org_name_full": org.get("name_full", ""),
            "logo": org.get("logo", ""),
            "website": org.get("website", ""),
            "slug": org.get("slug", ""),
            "projects_count": org.get("projects_count", 0),
            "matched_projects": counts["project"],
            "matched_rids": counts["rid"],
            "relevance_score": round(weighted_score, 2),
        })
    return result


def format_experts(scored_records: list[tuple], top_n: int = 3) -> list[dict]:
    """Топ учёных из наиболее релевантных организаций."""
    sci_records = [(s, r) for s, r in scored_records if r["type"] == "scientist"][:top_n]
    result = []
    for score, rec in sci_records:
        result.append({
            "name": rec.get("title", ""),
            "areas": rec.get("abstract", ""),
            "org_name": rec.get("org_name", ""),
            "org_logo": rec.get("org_logo", ""),
            "photo": rec.get("photo", ""),
            "colab_url": rec.get("colab_url", ""),
        })
    return result


# ─────────────────────────────────────────────
# OpenRouter — Claude Haiku
# ─────────────────────────────────────────────
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def call_claude(query: str, context_projects: list[dict], stats: dict) -> str:
    """Вызываем Claude Haiku через OpenRouter и получаем ai_summary."""
    if not OPENROUTER_API_KEY:
        return f"По теме «{query}» найдено {stats['projects_count']} проектов в {stats['orgs_count']} организациях. Подключите ключ OPENROUTER_API_KEY для AI-анализа."

    # Краткий контекст для промпта
    projects_ctx = "\n".join(
        f"- {p['title']} ({p['org_name']}, бюджет: {p['budget_rub']:,.0f} руб.)"
        for p in context_projects[:8]
    )
    funding_fmt = f"₽{stats['total_funding_rub']/1e6:.1f} млн" if stats['total_funding_rub'] else "н/д"

    system_prompt = """Ты — деловой аналитик платформы МОСНАУКА.
Пользователь ищет исполнителей НИОКР или партнёров для своей задачи.
На основе запроса и найденных проектов из базы ЕГИСУ — дай краткий, деловой анализ.

Пиши на русском, 2-3 предложения, без лишних вступлений.
Фокус: насколько тема проработана, какие организации лидируют, есть ли готовые решения."""

    user_prompt = f"""Запрос пользователя: «{query}»

Найдено {stats['projects_count']} похожих проектов в {stats['orgs_count']} организациях.
Суммарное финансирование по теме: {funding_fmt}.

Топ релевантных проектов:
{projects_ctx}

Дай деловой анализ темы (2-3 предложения)."""

    try:
        resp = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://mosnauka.onrender.com",
            },
            json={
                "model": "anthropic/claude-3-haiku",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "max_tokens": 300,
                "temperature": 0.3,
            },
            timeout=15,
        )
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"OpenRouter error: {e}")
        return f"По теме «{query}» найдено {stats['projects_count']} проектов в {stats['orgs_count']} организациях с суммарным финансированием {funding_fmt}."


# ─────────────────────────────────────────────
# API Endpoints
# ─────────────────────────────────────────────
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "records": len(RECORDS),
        "orgs": len(ORGS),
        "index_meta": INDEX_META,
    })


@app.route("/api/ai-search", methods=["POST"])
def ai_search():
    body = request.get_json(force=True, silent=True) or {}
    query = str(body.get("query", "")).strip()

    if not query:
        return jsonify({"error": "query is required"}), 400
    if len(query) > 5000:
        query = query[:5000]

    # 1. Поиск — все совпадения (для точной статистики)
    t0 = time.time()
    all_scored = search(query, top_n=500)  # широкая выборка для stats
    search_ms = int((time.time() - t0) * 1000)

    if not all_scored:
        return jsonify({
            "ai_summary": f"По запросу «{query}» подходящих проектов в базе не найдено. Попробуйте перефразировать или уточнить тему.",
            "stats": {"projects_count": 0, "orgs_count": 0, "total_funding_rub": 0, "max_match_pct": 0},
            "projects": [],
            "organizations": [],
            "experts": [],
        })

    # 2. Статистика — по всем найденным
    stats = build_stats(all_scored)

    # 3. Форматирование топ-результатов (топ-30 по score для карточек)
    top_scored = all_scored[:30]
    projects = format_projects(top_scored, top_n=6)
    organizations = format_organizations(top_scored, top_n=3)
    experts = format_experts(top_scored, top_n=3)

    # 4. AI-анализ
    ai_summary = call_claude(query, projects, stats)

    return jsonify({
        "ai_summary": ai_summary,
        "stats": stats,
        "projects": projects,
        "organizations": organizations,
        "experts": experts,
        "_debug": {"search_ms": search_ms, "total_found": len(all_scored)},
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)
