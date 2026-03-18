---
description: Добавление новой организации в платформу МОСНАУКА
---

1. Подготовить данные организации (проекты, РИД, лаборатории, учёные) в формате JSON.

2. Создать директорию для организации:
```
mkdir -p /Users/shakhgildyangy/mosnauka/<org_slug>
```

3. Запустить генератор паспортов:
```
python3 /Users/shakhgildyangy/mosnauka/generate_passports_v2.py
```

4. Обновить поисковый индекс:
```
cd /Users/shakhgildyangy/mosnauka/backend && python3 prepare_index.py
```

5. Перегенерировать эмбеддинги:
```
cd /Users/shakhgildyangy/mosnauka/backend && python3 generate_embeddings.py
```

6. Обновить базу экспертов (если есть новые учёные):
- Добавить записи в `backend/data/experts_index.json`
- Скопировать обновлённый файл: `cp backend/data/experts_index.json public/data/experts.json`

7. Задеплоить (см. workflow `/deploy`).
