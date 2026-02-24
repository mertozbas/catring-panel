import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'basak_yemek.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'database', 'schema.sql')

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8273447754:AAG9SfcSX18_Aq6JcyUq10kWrl-cdzAbRbM')

GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '').strip()

SECRET_KEY = os.environ.get('SECRET_KEY', 'basak-yemek-gizli-anahtar-2026')

OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'qwen3:4b')
OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')

OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-5-nano-2025-08-07')

FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5050
FLASK_DEBUG = True
