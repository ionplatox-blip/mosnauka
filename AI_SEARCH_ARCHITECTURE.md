# МОСНАУКА — AI Search: Архитектура и данные

## 1. Что у нас есть (база данных)

### Местоположение
```
/Users/shakhgildyangy/COLAB_DATA/
├── passports/
│   ├── index.json              # Сводный индекс организаций
│   ├── org_001_mgu.json        # Полный паспорт МГУ
│   ├── org_002_mfti.json       # МФТИ
│   ├── org_003_misis.json      # МИСиС
│   ├── org_004_bauman.json     # МГТУ Бауман
│   ├── org_005_rhtu.json       # РХТУ
│   ├── org_006_skoltech.json   # Сколтех
│   ├── org_007_kurchatov.json  # НИЦ Курчатовский
│   ...и ещё 15 организаций
└── egisu_extracted/
    ├── ikrbs_by_org.json       # Проекты НИОКР (~1544 записи, 22 орг)
    └── rid_by_org.json         # РИД (~1388 записей)
```

### Статистика базы (из index.json)
| Показатель | Значение |
|---|---|
| Организаций | 22 |
| Проектов НИОКТР (ЕГИСУ) | 2210 |
| РИД (ЕГИСУ) | 1388 |
| Лабораторий (Colab) | ~170 |
| Учёных (Colab) | ~1500 |

---

## 2. Схема данных (что хранится в каждом паспорте)

### org_00X_name.json — структура
```json
{
  "id": "org_001",
  "slug": "mgu",
  "identity": {
    "name_short": "МГУ им. М.В. Ломоносова",
    "name_full": "Московский государственный университет...",
    "logo_url": "https://colab.ws/storage/images/...",
    "website": "https://www.msu.ru/",
    "address": "Москва, Ленинские горы, д. 1"
  },
  "source_colab": {
    "data": {
      "laboratories": [ ... ],         // лаборатории с тегами
      "top3_scientists": [ ... ],       // топ учёных
      "standalone_researchers": [ ... ] // все учёные
    }
  },
  "source_egisu": {
    "data": {
      "projects": [ ... ],  // НИОКР проекты
      "rid": [ ... ]        // РИД
    }
  }
}
```

### Проект НИОКР (поля IKRBS)
```
reg_number     — шифр (напр. "225021810690-2")
name           — полное название проекта
abstract       — аннотация (200-500 слов)
keywords       — список ключевых слов
report_type    — "Промежуточный" / "Заключительный"
stage_start    — начало этапа
stage_end      — конец этапа
pub_count      — кол-во публикаций
authors_count  — кол-во авторов
budget[]       — финансирование (funds + budget_type)
rubrics[]      — рубрики ГРНТИ
oecds[]        — OECD коды областей науки
nioktr         — шифр темы НИОКТР
```

### РИД (поля)
```
registration_number  — номер
name                 — название
rid_type             — патент / программа ЭВМ / база данных / ноу-хау
abstract             — описание
keyword_list         — ключевые слова
using_ways           — направления использования
authors[]            — авторы
customer             — заказчик
executors[]          — исполнители
```

### Лаборатория (Colab)
```
name          — название
description   — описание
tags[]        — теги компетенций
equipment[]   — оборудование
contacts      — email/телефон
```

---

## 3. Архитектура AI Search

```
[Пользователь] → вводит запрос (2 слова или большой текст)
      ↓
[ai_search_results.html] параметр ?q=...
      ↓
[search_api.js] → fetch POST /api/ai-search
      ↓
[Render Web Service — mosnauka-backend/app.py]
      │
      ├─ Шаг 1: Keyword Search по search_index.json
      │   → TF-IDF или просто матч по abstract + keywords + name
      │   → Берём топ-15 проектов с наивысшим score
      │
      ├─ Шаг 2: Дополняем данными организации
      │   → Для каждого проекта достаём org_name, logo_url, org_slug
      │   → Формируем список organizations (уникальные из топ-15)
      │   → Formируем список experts (учёные из этих орг)
      │
      ├─ Шаг 3: OpenRouter (Claude Haiku)
      │   Промпт: "Ты аналитик НИОКР. На основе запроса бизнеса
      │            и топ-15 похожих проектов сформируй:
      │            - ai_summary: деловой анализ темы
      │            - stats: { projects_count, orgs_count, total_funding_rub }
      │            - top_technologies: список технологий
      │            Верни JSON строго в формате."
      │
      └─ Шаг 4: Возвращает JSON клиенту
          {
            ai_summary: "...",
            stats: { projects_count, orgs_count, total_funding },
            projects: [ {title, match%, reg_number, org, abstract, ...} ],
            organizations: [ {name, logo, slug, projects_count} ],
            experts: [ {name, areas, org, photo} ]
          }
```

---

## 4. Что строим (Чанки)

### Чанк 1 ✅ — Документация данных (этот файл)

### Чанк 2 — Скрипт подготовки поискового индекса
**Файл:** `mosnauka-backend/prepare_index.py`

Читает все 22 `org_*.json` → создаёт плоский `search_index.json`:
```json
[
  {
    "id": "mgu_proj_001",
    "org_id": "org_001",
    "org_name": "МГУ им. М.В. Ломоносова",
    "org_slug": "mgu",
    "org_logo": "https://...",
    "type": "project",
    "title": "Разработка технологии...",
    "abstract": "...",
    "keywords": ["покрытие", "титан", "ПЭО"],
    "budget_rub": 23268828,
    "year": 2024,
    "report_type": "Промежуточный",
    "reg_number": "225021810690-2"
  },
  ...
]
```
Всего ~2200 записей × ~500 байт ≈ ~1.1 MB — нормально для in-memory поиска.

### Чанк 3 — Flask Backend
**Файл:** `mosnauka-backend/app.py`
- `POST /api/ai-search` → keyword search + Claude
- `GET /api/health` → проверка работоспособности
- CORS для mosnauka.onrender.com
- ENV: `OPENROUTER_API_KEY`

### Чанк 4 — Обновление фронтенда
**Файл:** `mosnauka/search_api.js`
- Убрать мок
- Реальный fetch к бэкенду
- Добавить fallback на случай ошибки

### Чанк 5 — Деплой на Render
- Отдельный Web Service (Python)
- Free tier (750 часов/мес)
- `render.yaml` для автодеплоя

---

## 5. Ключевые решения

| Вопрос | Решение | Почему |
|---|---|---|
| Поиск | Keyword / TF-IDF | Не нужен GPU, работает на Free Render |
| ИИ-модель | Claude Haiku (OpenRouter) | Уже есть ключ MOSNAUKA |
| БД | JSON in-memory | ~1.1 MB, быстро, не нужен PostgreSQL |
| Бэкенд | Python Flask | Минимум зависимостей |
| Хостинг | Render Web Service | Уже используем Render для фронта |
| Холодный старт | 30-60 сек на Free | Приемлемо для демо |

---

## 6. Формат промпта к Claude

```python
system_prompt = """
Ты — аналитик и брокер НИОКР платформы МОСНАУКА.
На основе запроса бизнеса и найденных проектов в базе ЕГИСУ НИОКТР:

1. Дай деловой анализ: насколько тема проработана, есть ли готовые технологии
2. Оцени суммарный объём вложенных средств (посчитай по полю budget)
3. Выдели ключевых исполнителей (топ-3 организации по кол-ву проектов)
4. Укажи максимальный % совпадения (match_percentage)

ВАЖНО: Отвечай кратко и по-деловому. Запрос может быть 2-3 слова или длинный текст ТЗ — оба случая обрабатывай одинаково качественно.

Верни СТРОГО JSON:
{
  "ai_summary": "2-3 предложения анализа",
  "stats": {
    "projects_count": N,
    "orgs_count": N,
    "total_funding_rub": N,
    "max_match_pct": N
  },
  "top_technologies": ["технология1", "технология2"],
  "projects": [...топ-3 проекта...],
  "organizations": [...топ-3 организации...],
  "experts": [...топ-3 эксперта...]
}
"""
```
