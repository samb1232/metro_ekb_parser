# Metro Schedule Parser for Yekaterinburg Metro

## Overview

This Python script scrapes and parses train schedules for all stations of the Yekaterinburg Metro system from the official website (https://metro-ektb.ru). It extracts timetable information for both weekdays and weekends, in both directions (toward "Botanicheskaya" and "Prospekt Kosmonavtov" stations).

## Features

- Scrapes schedule data for all metro stations
- Outputs clean, structured JSON data
- Formats times as "HH:MM" strings

## Requirements

- Python 3.6+
- Required packages:
  - requests
  - beautifulsoup4
  - lxml (or another HTML parser for BeautifulSoup)

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the script:

```bash
python parser.py
```

## Output Format

The script generates a JSON file with the following structure:

```json
{
  "Station Name": {
    "weekdays": {
      "to_botanicheskaya": ["05:53", "06:02", ...],
      "to_prospekt_kosmonavtov": ["06:12", "06:21", ...]
    },
    "weekends": {
      "to_botanicheskaya": ["05:53", "06:05", ...],
      "to_prospekt_kosmonavtov": ["06:15", "06:28", ...]
    }
  },
  "Botanicheskaya": {
    "weekdays": {
      "to_prospekt_kosmonavtov": ["05:56", "06:07", ...]
    },
    "weekends": {
      "to_prospekt_kosmonavtov": ["05:59", "06:13", ...]
    }
  }
}
```

## License

This project is open-source and available for free use.
