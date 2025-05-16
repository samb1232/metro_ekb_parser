import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
}

def parse_station_links(url):
    """Получаем список всех станций и ссылки на их расписания"""
    response = requests.get(url, headers=HEADERS, verify=False, timeout=10)
    response.raise_for_status() 
    soup = BeautifulSoup(response.text, 'html.parser')
    
    station_links = {}
    ul = soup.find('ul', class_='detail_schedule')
    if ul:
        for li in ul.find_all('li'):
            a = li.find('a')
            if a:
                station_name = a.get_text(strip=True)
                station_url = urljoin(url, a['href'])
                station_links[station_name] = station_url
    
    return station_links

def parse_schedule_table(table):
    """Парсим таблицу с расписанием и возвращаем список времени в формате HH:MM"""
    schedule = []
    rows = table.find_all('tr')[1:]  # Пропускаем заголовок
    for row in rows:
        cells = row.find_all('td')
        if len(cells) != 2:
            continue
            
        hour = cells[0].get_text(strip=True)
        minutes_text = cells[1].get_text(strip=True)
        
        # Извлекаем минуты, удаляя точки и лишние символы
        minutes = re.findall(r'\d+', minutes_text)
        
        # Формируем полное время в формате HH:MM
        for minute in minutes:
            time_str = f"{int(hour):02d}:{int(minute):02d}"
            schedule.append(time_str)
        
    return sorted(schedule)  # Сортируем по возрастанию времени

def parse_station_schedule(url, station_name):
    """Парсим расписание для конкретной станции"""
    response = requests.get(url, headers=HEADERS, verify=False, timeout=10)
    response.raise_for_status() 
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Находим все таблицы с расписанием
    tables = soup.find_all('table', class_='uss_table_black10')
    
    # Определяем, является ли станция конечной
    is_terminal = "Ботаническая" in station_name or "Проспект космонавтов" in station_name
    
    schedule = {
        'weekdays': {},
        'weekends': {}
    }
    
    if is_terminal:
        # Для конечных станций только 2 таблицы
        if len(tables) >= 2:
            # Определяем направление для конечных станций
            if "Ботаническая" in station_name:
                # Только в сторону Проспекта Космонавтов
                schedule['weekdays']['to_prospekt_kosmonavtov'] = parse_schedule_table(tables[0])
                schedule['weekends']['to_prospekt_kosmonavtov'] = parse_schedule_table(tables[1])
            elif "Проспект космонавтов" in station_name:
                # Только в сторону Ботанической
                schedule['weekdays']['to_botanicheskaya'] = parse_schedule_table(tables[0])
                schedule['weekends']['to_botanicheskaya'] = parse_schedule_table(tables[1])
    else:
        # Для обычных станций 4 таблицы
        if len(tables) >= 4:
            schedule['weekdays']['to_botanicheskaya'] = parse_schedule_table(tables[0])
            schedule['weekdays']['to_prospekt_kosmonavtov'] = parse_schedule_table(tables[1])
            schedule['weekends']['to_botanicheskaya'] = parse_schedule_table(tables[2])
            schedule['weekends']['to_prospekt_kosmonavtov'] = parse_schedule_table(tables[3])
    
    return schedule if (schedule['weekdays'] or schedule['weekends']) else None

def main():
    # URL страницы со списком станций
    stations_url = "https://metro-ektb.ru/podrobnye-grafiki-po-stanciyam/"
    
    # Получаем ссылки на расписания всех станций
    print("Получаю список станций...")
    station_links = parse_station_links(stations_url)
    
    if not station_links:
        print("Не удалось найти ссылки на расписания станций")
        return
    
    print(f"Найдено {len(station_links)} станций:")
    for name in station_links:
        print(f"- {name}")
    
    # Парсим расписание для каждой станции
    all_schedules = {}
    
    for station_name, station_url in station_links.items():
        print(f"\nПарсим расписание для станции '{station_name}'...")
        schedule = parse_station_schedule(station_url, station_name)
        
        if schedule:
            all_schedules[station_name] = schedule
            print(f"Успешно распарсено расписание для '{station_name}'")
        else:
            print(f"Не удалось распарсить расписание для '{station_name}'")
    
    # Сохраняем все расписания в JSON файл
    with open('all_metro_schedules.json', 'w', encoding='utf-8') as f:
        json.dump(all_schedules, f, ensure_ascii=False, indent=2)
    
    print("\nВсе расписания успешно сохранены в all_metro_schedules.json")

if __name__ == "__main__":
    main()