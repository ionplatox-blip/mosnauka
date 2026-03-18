---
description: Деплой изменений на Render (git push → автодеплой)
---

// turbo-all

1. Перейти в директорию проекта:
```
cd /Users/shakhgildyangy/mosnauka
```

2. Проверить статус изменений:
```
git status
```

3. Добавить все изменения:
```
git add -A
```

4. Закоммитить с описанием:
```
git commit -m "описание изменений"
```

5. Запушить в main:
```
git push origin main
```

6. Проверить что Render начал деплой (~5 мин):
```
curl -sI "https://mosnauka.onrender.com/" | head -3
```
