import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Конфигурация бота
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise Exception('BOT_TOKEN is not set')
API_KEY_WEATHER = os.getenv('API_KEY_WEATHER')
if not API_KEY_WEATHER:
    raise Exception('API_KEY_WEATHER is not set')
API_KEY_ACTIVITY = os.getenv('API_KEY_ACTIVITY')
if not API_KEY_ACTIVITY:
    raise Exception('API_KEY_ACTIVITY is not set')
UNITS = os.getenv('UNITS')
if not UNITS:
    raise Exception('UNITS is not set')
DATA_PATH = os.getenv('DATA_PATH')
if not DATA_PATH:
    raise Exception('DATA_PATH is not set')
