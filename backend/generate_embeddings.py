#!/usr/bin/env python3
"""
generate_embeddings.py — Генерация векторных эмбеддингов для семантического поиска.

Запускается ОДИН РАЗ локально. Результат:
  - embeddings.npy     (4344 × 512 float32, ~8.5 MB)
  - embeddings_ids.json (маппинг index → record_id)

Использует OpenRouter: openai/text-embedding-3-small (dimensions=512)
Стоимость: ~4344 × 125 токенов = ~550K токенов ≈ $0.011 (один раз!)

Использование:
  export OPENROUTER_API_KEY="sk-or-v1-..."
  python3 generate_embeddings.py
"""

import json
import os
import time
from pathlib import Path

import numpy as np
import requests

# ─── Конфиг ──────────────────────────────────────────────────────────────────
INDEX_PATH      = Path(__file__).parent / "search_index.json"
OUT_NPY         = Path(__file__).parent / "embeddings.npy"
OUT_IDS         = Path(__file__).parent / "embeddings_ids.json"

OPENROUTER_KEY  = os.getenv("OPENROUTER_API_KEY", "")
EMBED_MODEL     = "openai/text-embedding-3-small"
EMBED_DIMS      = 512          # 512-dim: ~8.5 MB, quality ~= 1536-dim
BATCH_SIZE      = 64           # кол-во записей в одном запросе к API
RETRY_ATTEMPTS  = 3
RETRY_DELAY_S   = 5


def build_embed_text(rec: dict) -> str:
    """Формируем текст для эмбеддинга — title + abstract + keywords (компактно)."""
    parts = []
    if rec.get("title"):
        parts.append(rec["title"])
    if rec.get("abstract"):
        # берём первые 500 символов абстракта
        parts.append(rec["abstract"][:500])
    if rec.get("keywords"):
        kws = rec["keywords"] if isinstance(rec["keywords"], list) else []
        parts.append(" ".join(kws[:15]))
    # добавляем org_name для контекста организации
    if rec.get("org_name"):
        parts.append(rec["org_name"])
    return " | ".join(parts)[:2000]  # OpenAI лимит 8191 токенов, 2000 символов ≈ 500 токенов


def embed_batch(texts: list[str]) -> list[list[float]]:
    """Вызываем OpenRouter /embeddings для батча текстов."""
    for attempt in range(RETRY_ATTEMPTS):
        try:
            resp = requests.post(
                "https://openrouter.ai/api/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://mosnauka.onrender.com",
                    "X-Title": "MOSNAUKA Search",
                },
                json={
                    "model": EMBED_MODEL,
                    "input": texts,
                    "dimensions": EMBED_DIMS,
                },
                timeout=60,
            )
            data = resp.json()

            if resp.status_code != 200:
                print(f"  ⚠️ API error {resp.status_code}: {data}")
                if attempt < RETRY_ATTEMPTS - 1:
                    print(f"  Повтор через {RETRY_DELAY_S}с...")
                    time.sleep(RETRY_DELAY_S)
                    continue
                raise RuntimeError(f"API error: {data}")

            # Сортируем по index (OpenAI гарантирует порядок, но на всякий случай)
            items = sorted(data["data"], key=lambda x: x["index"])
            return [item["embedding"] for item in items]

        except requests.exceptions.Timeout:
            print(f"  ⏰ Timeout, attempt {attempt+1}/{RETRY_ATTEMPTS}")
            time.sleep(RETRY_DELAY_S)

    raise RuntimeError("Все попытки исчерпаны")


def main():
    if not OPENROUTER_KEY:
        print("❌ Нет OPENROUTER_API_KEY. Установите: export OPENROUTER_API_KEY='sk-or-v1-...'")
        return

    print(f"📂 Загружаем индекс: {INDEX_PATH}")
    with open(INDEX_PATH, encoding="utf-8") as f:
        raw = json.load(f)

    records = raw["records"]
    print(f"✅ Записей: {len(records)}")

    # Строим тексты для эмбеддинга
    texts = [build_embed_text(r) for r in records]
    record_ids = [r["id"] for r in records]

    # Пример текста для контроля
    print(f"\n📝 Пример текста (запись 0):\n  {texts[0][:200]}...\n")

    # Батчевая генерация
    all_embeddings = []
    total_batches = (len(texts) + BATCH_SIZE - 1) // BATCH_SIZE

    print(f"🚀 Генерируем эмбеддинги: {len(texts)} записей, батч {BATCH_SIZE}, итого {total_batches} запросов")
    print(f"   Модель: {EMBED_MODEL}, dims: {EMBED_DIMS}")
    print(f"   Ожидаемая стоимость: ~${len(texts) * 125 / 1_000_000 * 0.02:.4f}\n")

    t0 = time.time()
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1

        print(f"  [{batch_num}/{total_batches}] Записи {i}–{i+len(batch)-1}...", end=" ", flush=True)
        embeddings = embed_batch(batch)
        all_embeddings.extend(embeddings)
        print(f"✓ (dim={len(embeddings[0])})")

        # Небольшая пауза чтобы не перегружать API
        if batch_num < total_batches:
            time.sleep(0.3)

    elapsed = time.time() - t0
    print(f"\n✅ Сгенерировано за {elapsed:.1f}с")

    # Сохраняем
    arr = np.array(all_embeddings, dtype=np.float32)
    print(f"\n💾 Сохраняем {arr.shape} float32 → {OUT_NPY}")
    np.save(OUT_NPY, arr)

    with open(OUT_IDS, "w", encoding="utf-8") as f:
        json.dump(record_ids, f, ensure_ascii=False)

    size_mb = OUT_NPY.stat().st_size / 1024 / 1024
    print(f"   Размер: {size_mb:.1f} MB")
    print(f"   ID маппинг: {OUT_IDS}")
    print(f"\n🎉 Готово! Теперь запустите: python3 app.py")


if __name__ == "__main__":
    main()
