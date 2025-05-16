import requests
from bs4 import BeautifulSoup
import json
import re

# Добавляем заголовки, имитирующие браузер
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
}

def parse_schedule_table(table):
    schedule = {}
    rows = table.find_all('tr')
    for row in rows[1:]:  # Пропускаем заголовок
        cells = row.find_all('td')
        if len(cells) != 2:
            continue
            
        hour = cells[0].get_text(strip=True)
        minutes_text = cells[1].get_text(strip=True)
        
        # Извлекаем минуты (удаляем точки в конце и разделяем по ;)
        minutes = []
        for m in re.split(r'[;,]', minutes_text.replace('.', '')):
            m_clean = m.strip()
            if m_clean:
                minutes.append(m_clean)
        
        schedule[hour] = minutes
    return schedule

def parse_metro_schedule(url):
    try:
        # Добавляем параметры для игнорирования SSL ошибок и указываем заголовки
        response = requests.get(url, headers=HEADERS, verify=False, timeout=10)
        response.raise_for_status()  # Проверяем успешность запроса
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Находим все таблицы с расписанием
        tables = soup.find_all('table', class_='uss_table_black10')
        
        if len(tables) < 2:
            print("Не найдено достаточно таблиц с расписанием")
            return None
        
        # Парсим расписания
        result = {
            'station': 'Проспект Космонавтов',
            'schedules': {
                'weekdays': {
                    'to_botanicheskaya': parse_schedule_table(tables[0])
                },
                'weekends': {
                    'to_botanicheskaya': parse_schedule_table(tables[1])
                }
            }
        }
        
        return result
    
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к сайту: {e}")
        return None

def save_schedule_to_json(schedule, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(schedule, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    # Отключаем предупреждения о SSL
    requests.packages.urllib3.disable_warnings()
    
    url = 'https://metro-ektb.ru/podrobnyy-grafik-s-03-03-2025/'
    schedule = parse_metro_schedule(url)
    
    if schedule:
        output_file = 'ekaterinburg_metro_schedule.json'
        save_schedule_to_json(schedule, output_file)
        print(f'Расписание успешно сохранено в файл {output_file}')
    else:
        print('Не удалось получить расписание')
        
