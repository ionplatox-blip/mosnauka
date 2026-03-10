import os

def reorder_index():
    with open('/Users/shakhgildyangy/mosnauka/index.html', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    markers = {
        '<!-- Первый экран: Умное УТП -->': 'hero',
        '<!-- Горизонтальный мост -->': 'bridge',
        '<!-- Секция: Сервисные входы (6 карточек) -->': 'services',
        '<!-- Секция: Контраст (Проблема бизнеса VS Экосистема) -->': 'contrast',
        '<!-- Секция: Кто участвует в МОСНАУКА -->': 'participants',
        '<!-- Секция: Как искать исполнителя -->': 'search_flow',
        '<!-- Секция: Подтверждение расходов на НИОКР -->': 'coef2',
        '<!-- Секция: Интерактивная карта -->': 'map',
        '<!-- Секция: Задачи и Финансирование -->': 'tasks',
        '<!-- Секция: Экономика НИОКР -->': 'economy',
        '<!-- Секция: Профили центров (Реестр компетенций) -->': 'profiles',
        '<!-- Секция: Дополнительные модули -->': 'additional',
        '<!-- Секция: Городской эффект -->': 'city_effect',
        '<!-- Подвал -->': 'footer',
        '<!-- Модалка внутри index.html сразу же (универсальный попап) -->': 'modal'
    }
    
    blocks = {'prefix': []}
    current_block = 'prefix'
    
    for line in lines:
        stripped = line.strip()
        matched = False
        for marker, block_name in markers.items():
            if stripped == marker:
                current_block = block_name
                blocks[current_block] = []
                matched = True
                break
        blocks[current_block].append(line)
        
    # Desired order based on implementation plan:
    new_order = [
        'prefix',
        'hero',
        'bridge',
        'services',
        'contrast',
        'map',
        'profiles',
        'coef2',
        'economy',
        'participants',
        'search_flow',
        'tasks',
        'additional',
        'city_effect',
        'footer',
        'modal'
    ]
    
    output_lines = []
    for block_name in new_order:
        if block_name in blocks:
            output_lines.extend(blocks[block_name])
        else:
            print(f"Warning: block {block_name} not found in input HTML.")
            
    with open('/Users/shakhgildyangy/mosnauka/index-new.html', 'w', encoding='utf-8') as f:
        f.writelines(output_lines)
    print("Successfully generated index-new.html with reordered sections.")

if __name__ == '__main__':
    reorder_index()
