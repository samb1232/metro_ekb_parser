import requests
from bs4 import BeautifulSoup
import json
import re

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
}

def parse_schedule_table(table):
    schedule = {}
    rows = table.find_all('tr')[1:]  # Пропускаем заголовок
    for row in rows:
        cells = row.find_all('td')
        if len(cells) != 2:
            continue
            
        hour = cells[0].get_text(strip=True)
        minutes_text = cells[1].get_text(strip=True)
        
        # Извлекаем минуты, удаляя точки и лишние символы
        minutes = re.findall(r'\d+', minutes_text)
        schedule[hour] = minutes
        
    return schedule

def parse_metro_schedule(url):
    response = requests.get(url, headers=HEADERS, verify=False, timeout=10)
    response.raise_for_status() 
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Находим все таблицы с расписанием
    tables = soup.find_all('table', class_='uss_table_black10')
    
    if len(tables) < 4:
        return None
    
    # Расписание в будни и выходные для обоих направлений
    schedule = {
        'weekdays': {
            'to_botanicheskaya': parse_schedule_table(tables[0]),
            'to_prospekt_kosmonavtov': parse_schedule_table(tables[1])
        },
        'weekends': {
            'to_botanicheskaya': parse_schedule_table(tables[2]),
            'to_prospekt_kosmonavtov': parse_schedule_table(tables[3])
        }
    }
    
    return schedule

# URL страницы с расписанием
url = "https://metro-ektb.ru/podrobnye-grafiki-po-stancii-mashinostroiteley-s-03-03-2025-g/"

# Парсим расписание
metro_schedule = parse_metro_schedule(url)

if metro_schedule:
    # Сохраняем в JSON файл
    with open('metro_schedule.json', 'w', encoding='utf-8') as f:
        json.dump(metro_schedule, f, ensure_ascii=False, indent=2)
    
    print("Расписание успешно сохранено в metro_schedule.json")
else:
    print("Не удалось распарсить расписание")