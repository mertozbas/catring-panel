"""
Başak Yemek Catering - Telegram Bot Agent
Strands SDK + OpenAI GPT ile çalışır.

Kullanım:
    python agent/bot.py

Gereklilikler:
    - Flask uygulamasının çalışıyor olması (python app.py)
    - OPENAI_API_KEY environment variable
    - TELEGRAM_BOT_TOKEN environment variable
"""
import os
import sys
import time
import requests
import traceback
import urllib3

# DNS sorunu için: api.telegram.org -> IP adresi ile bağlan
TELEGRAM_IP = "149.154.166.110"

# SSL uyarısını kapat
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# requests session - SSL verify kapalı
tg_session = requests.Session()
tg_session.verify = False
tg_session.headers.update({"Host": "api.telegram.org"})

# Proje kök dizinini path'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Strands SDK imports
from strands import Agent
from strands.models.openai import OpenAIModel

# Telegram API
TELEGRAM_API = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}"
TELEGRAM_API_IP = f"https://{TELEGRAM_IP}/bot{config.TELEGRAM_BOT_TOKEN}"

# Custom tools
from agent.tools.order_tools import get_todays_orders, create_order, get_daily_summary
from agent.tools.menu_tools import get_current_menu, get_todays_menu
from agent.tools.customer_tools import search_customer, list_customers, register_customer
from agent.tools.notification_tools import format_menu_for_telegram

# System prompt
SYSTEM_PROMPT_PATH = os.path.join(os.path.dirname(__file__), 'prompts', 'system_prompt.txt')
with open(SYSTEM_PROMPT_PATH, 'r', encoding='utf-8') as f:
    SYSTEM_PROMPT = f.read()


def extract_text_from_result(result):
    """Strands Agent sonucundan düz metin çıkarır."""
    # 1) result doğrudan string ise
    if isinstance(result, str):
        return result

    # 2) result dict ise (veya dict-like)
    raw = result
    if hasattr(result, 'message'):
        raw = result.message
    elif hasattr(result, 'content'):
        raw = result.content

    # Dict ise content alanını parse et
    if isinstance(raw, dict):
        content = raw.get('content', raw)
        # content bir liste ise text parçalarını birleştir
        if isinstance(content, list):
            texts = []
            for item in content:
                if isinstance(item, dict) and 'text' in item:
                    texts.append(item['text'])
                elif isinstance(item, str):
                    texts.append(item)
            if texts:
                return "\n".join(texts)
        elif isinstance(content, str):
            return content
        # role/content yapısında sadece text varsa
        text = raw.get('text', '')
        if text:
            return text

    # Liste ise (content list doğrudan)
    if isinstance(raw, list):
        texts = []
        for item in raw:
            if isinstance(item, dict) and 'text' in item:
                texts.append(item['text'])
            elif isinstance(item, str):
                texts.append(item)
        if texts:
            return "\n".join(texts)

    # Son çare: str() ama temizle
    text = str(raw)
    # {'role': 'assistant', 'content': [...]} formatını temizlemeyi dene
    if text.startswith('{') and "'text'" in text:
        try:
            import ast
            parsed = ast.literal_eval(text)
            if isinstance(parsed, dict):
                content = parsed.get('content', [])
                if isinstance(content, list):
                    return "\n".join(
                        item.get('text', '') for item in content
                        if isinstance(item, dict) and 'text' in item
                    )
        except Exception:
            pass
    return text


def create_agent():
    """Strands Agent oluşturur - OpenAI GPT ile."""
    model = OpenAIModel(
        model_id=config.OPENAI_MODEL,
    )

    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[
            get_todays_orders,
            create_order,
            get_daily_summary,
            get_current_menu,
            get_todays_menu,
            search_customer,
            list_customers,
            register_customer,
            format_menu_for_telegram,
        ]
    )
    return agent


def send_telegram_message(chat_id, text):
    """Telegram'a mesaj gönderir."""
    url = f"{TELEGRAM_API_IP}/sendMessage"
    # Markdown karakterlerini escape et (basit yaklaşım)
    payload = {
        "chat_id": chat_id,
        "text": text[:4096],
    }
    try:
        resp = tg_session.post(url, json=payload, timeout=10)
        result = resp.json()
        if not result.get("ok"):
            print(f"Telegram mesaj hatası: {result}")
    except Exception as e:
        print(f"Telegram mesaj hatası: {e}")


def get_updates(offset=None):
    """Telegram'dan yeni mesajları alır."""
    url = f"{TELEGRAM_API_IP}/getUpdates"
    params = {"timeout": 30}
    if offset is not None:
        params["offset"] = offset
    try:
        resp = tg_session.get(url, params=params, timeout=35)
        data = resp.json()
        if not data.get("ok"):
            print(f"[POLL] Telegram hata: {data}")
            return []
        results = data.get("result", [])
        if results:
            print(f"[POLL] {len(results)} yeni mesaj alındı!")
        return results
    except Exception as e:
        print(f"[POLL] Hata: {e}")
        time.sleep(2)
        return []


def run_bot():
    """Bot'u long-polling ile çalıştırır."""
    print("=" * 50)
    print("Başak Yemek Telegram Bot başlatılıyor...")
    print(f"Model: OpenAI {config.OPENAI_MODEL}")
    print(f"API Key: {os.environ.get('OPENAI_API_KEY', '')[:15]}...")
    print("=" * 50)

    agent = create_agent()
    print("Agent oluşturuldu!")
    print("Bot hazır! Telegram'dan mesaj bekleniyor...\n")

    offset = None

    while True:
        try:
            updates = get_updates(offset)
            for update in updates:
                offset = update["update_id"] + 1

                message = update.get("message")
                if not message or not message.get("text"):
                    continue

                chat_id = message["chat"]["id"]
                user_text = message["text"]
                user_name = message["from"].get("first_name", "Kullanıcı")

                print(f"\n>>> [{user_name}] ({chat_id}): {user_text}")

                # /start komutu
                if user_text == "/start":
                    send_telegram_message(chat_id,
                        f"Merhaba {user_name}! Ben Başak Yemek asistanıyım.\n\n"
                        "Size şu konularda yardımcı olabilirim:\n"
                        "- Sipariş vermek\n"
                        "- Menüyü görüntülemek\n"
                        "- Sipariş durumu sorgulamak\n"
                        "- Müşteri bilgisi sorgulamak\n\n"
                        "Nasıl yardımcı olabilirim?")
                    print("<<< /start yanıtı gönderildi")
                    continue

                # Agent ile konuşma
                try:
                    prompt = f"Kullanıcı ({user_name}, chat_id: {chat_id}): {user_text}"
                    result = agent(prompt)

                    # Strands agent result'tan düz text çıkar
                    response_text = extract_text_from_result(result)

                    # Boş yanıt kontrolü
                    if not response_text or response_text.strip() == '' or response_text == 'None':
                        response_text = "Anlayamadım, tekrar yazar mısınız?"

                    send_telegram_message(chat_id, response_text)
                    print(f"<<< [BOT]: {response_text[:150]}...")
                except Exception as e:
                    print(f"!!! Agent hatası: {e}")
                    traceback.print_exc()
                    send_telegram_message(chat_id,
                        "Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.")

        except KeyboardInterrupt:
            print("\nBot durduruluyor...")
            break
        except Exception as e:
            print(f"!!! Döngü hatası: {e}")
            traceback.print_exc()
            time.sleep(5)


if __name__ == "__main__":
    run_bot()
