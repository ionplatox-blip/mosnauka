#!/usr/bin/env python3
"""
generate_988_embeddings.py — Генерация эмбеддингов для 685 пунктов Перечня №988.

Запускается ОДИН РАЗ локально. Результат:
  - perechen_988_embeddings.npy   (685 × 512 float32)
  - perechen_988_ids.json         (маппинг index → item_id)

Стоимость: ~685 × 30 токенов = ~20K токенов ≈ $0.0004

Использование:
  export OPENROUTER_API_KEY="sk-or-v1-..."
  python3 generate_988_embeddings.py
"""

import json
import os
import time
from pathlib import Path

import numpy as np
import requests

# ─── Config ──────────────────────────────────────────────────────────────────
DATA_PATH = Path(__file__).parent / "backend" / "data" / "perechen_988.json"
OUT_NPY   = Path(__file__).parent / "backend" / "perechen_988_embeddings.npy"
OUT_IDS   = Path(__file__).parent / "backend" / "perechen_988_ids.json"

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
EMBED_MODEL    = "openai/text-embedding-3-small"
EMBED_DIMS     = 512
BATCH_SIZE     = 100  # Items are short (~30 tokens each), can batch more


def embed_batch(texts: list[str]) -> list[list[float]]:
    """Call OpenRouter /embeddings for a batch of texts."""
    for attempt in range(3):
        try:
            resp = requests.post(
                "https://openrouter.ai/api/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://mosnauka.onrender.com",
                    "X-Title": "MOSNAUKA Perechen988",
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
                if attempt < 2:
                    time.sleep(3)
                    continue
                raise RuntimeError(f"API error: {data}")

            items = sorted(data["data"], key=lambda x: x["index"])
            return [item["embedding"] for item in items]

        except requests.exceptions.Timeout:
            print(f"  ⏰ Timeout, attempt {attempt+1}/3")
            time.sleep(3)

    raise RuntimeError("All attempts exhausted")


def main():
    if not OPENROUTER_KEY:
        print("❌ Нет OPENROUTER_API_KEY. Установите: export OPENROUTER_API_KEY='sk-or-v1-...'")
        return

    print(f"📂 Загружаем Перечень: {DATA_PATH}")
    with open(DATA_PATH, encoding="utf-8") as f:
        items = json.load(f)
    print(f"   Пунктов: {len(items)}")

    texts = [it["embed_text"] for it in items]
    ids = [it["id"] for it in items]

    print(f"\n📝 Примеры embed_text:")
    for t in texts[:3]:
        print(f"   {t[:100]}")

    # Batch embedding
    all_embeddings = []
    total_batches = (len(texts) + BATCH_SIZE - 1) // BATCH_SIZE

    print(f"\n🚀 Генерируем: {len(texts)} embeddings, batch={BATCH_SIZE}, batches={total_batches}")
    print(f"   Model: {EMBED_MODEL}, dims: {EMBED_DIMS}")
    est_cost = len(texts) * 30 / 1_000_000 * 0.02
    print(f"   Estimated cost: ~${est_cost:.5f}\n")

    t0 = time.time()
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        print(f"  [{batch_num}/{total_batches}] Items {i}–{i+len(batch)-1}...", end=" ", flush=True)
        embeddings = embed_batch(batch)
        all_embeddings.extend(embeddings)
        print(f"✓")
        if batch_num < total_batches:
            time.sleep(0.2)

    elapsed = time.time() - t0
    print(f"\n✅ Generated in {elapsed:.1f}s")

    # Save
    arr = np.array(all_embeddings, dtype=np.float32)
    print(f"\n💾 Saving {arr.shape} float32 → {OUT_NPY}")
    np.save(OUT_NPY, arr)

    with open(OUT_IDS, "w", encoding="utf-8") as f:
        json.dump(ids, f, ensure_ascii=False)

    size_kb = OUT_NPY.stat().st_size / 1024
    print(f"   Size: {size_kb:.0f} KB")
    print(f"   IDs: {OUT_IDS}")
    print(f"\n🎉 Done!")


if __name__ == "__main__":
    main()
