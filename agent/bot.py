"""
Basak Yemek Catering - Telegram Bot Agent
Strands SDK + OpenAI GPT ile calisir.

Ozellikler:
    - Birebir musteri portali (siparis, menu, takip)
    - Sirket ici grup bildirimleri
    - Inline keyboard ile siparis onay
    - Callback query handler

Kullanim:
    python agent/bot.py

Gereklilikler:
    - Flask uygulamasinin calisiyor olmasi (python app.py)
    - OPENAI_API_KEY environment variable
    - TELEGRAM_BOT_TOKEN environment variable
    - TELEGRAM_GROUP_CHAT_ID (opsiyonel - grup bildirimler icin)
"""
import os
import sys
import time
import json
import requests
import traceback
import urllib3

# DNS sorunu icin: api.telegram.org -> IP adresi ile baglan
TELEGRAM_IP = "149.154.166.110"

# SSL uyarisini kapat
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# requests session - SSL verify kapali
tg_session = requests.Session()
tg_session.verify = False
tg_session.headers.update({"Host": "api.telegram.org"})

# Proje kok dizinini path'e ekle
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
from agent.tools.route_tools import get_route_status, get_delivery_tracking
from agent.tools.inventory_tools import get_stock_status
from agent.tools.report_tools import get_daily_report_summary, get_weekly_summary

# System prompt
SYSTEM_PROMPT_PATH = os.path.join(os.path.dirname(__file__), 'prompts', 'system_prompt.txt')
with open(SYSTEM_PROMPT_PATH, 'r', encoding='utf-8') as f:
    SYSTEM_PROMPT = f.read()


def extract_text_from_result(result):
    """Strands Agent sonucundan duz metin cikarir."""
    # 1) result dogrudan string ise
    if isinstance(result, str):
        return result

    # 2) result dict ise (veya dict-like)
    raw = result
    if hasattr(result, 'message'):
        raw = result.message
    elif hasattr(result, 'content'):
        raw = result.content

    # Dict ise content alanini parse et
    if isinstance(raw, dict):
        content = raw.get('content', raw)
        # content bir liste ise text parcalarini birlestir
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
        # role/content yapisinda sadece text varsa
        text = raw.get('text', '')
        if text:
            return text

    # Liste ise (content list dogrudan)
    if isinstance(raw, list):
        texts = []
        for item in raw:
            if isinstance(item, dict) and 'text' in item:
                texts.append(item['text'])
            elif isinstance(item, str):
                texts.append(item)
        if texts:
            return "\n".join(texts)

    # Son care: str() ama temizle
    text = str(raw)
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
    """Strands Agent olusturur - OpenAI GPT ile."""
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
            get_route_status,
            get_delivery_tracking,
            get_stock_status,
            get_daily_report_summary,
            get_weekly_summary,
        ]
    )
    return agent


def send_chat_action(chat_id, action="typing"):
    """Telegram'da 'yaziyor...' animasyonu gosterir."""
    url = f"{TELEGRAM_API_IP}/sendChatAction"
    payload = {"chat_id": chat_id, "action": action}
    try:
        tg_session.post(url, json=payload, timeout=5)
    except Exception:
        pass


class TypingIndicator:
    """Agent dusunurken 'yaziyor...' animasyonunu surekli gonderir."""
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self._stop = False
        self._thread = None

    def start(self):
        import threading
        self._stop = False
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop = True

    def _loop(self):
        while not self._stop:
            send_chat_action(self.chat_id, "typing")
            time.sleep(4)


def send_telegram_message(chat_id, text, reply_markup=None):
    """Telegram'a mesaj gonderir. Opsiyonel inline keyboard destegi."""
    url = f"{TELEGRAM_API_IP}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text[:4096],
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    try:
        resp = tg_session.post(url, json=payload, timeout=10)
        result = resp.json()
        if not result.get("ok"):
            print(f"Telegram mesaj hatasi: {result}")
        return result
    except Exception as e:
        print(f"Telegram mesaj hatasi: {e}")
        return None


def answer_callback_query(callback_query_id, text=""):
    """Callback query'yi yanitla (butona basinca gosterilen bildirim)."""
    url = f"{TELEGRAM_API_IP}/answerCallbackQuery"
    payload = {"callback_query_id": callback_query_id}
    if text:
        payload["text"] = text[:200]
    try:
        tg_session.post(url, json=payload, timeout=5)
    except Exception:
        pass


def edit_message_text(chat_id, message_id, text, reply_markup=None):
    """Mevcut mesaji duzenle."""
    url = f"{TELEGRAM_API_IP}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text[:4096],
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    try:
        tg_session.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Mesaj duzenleme hatasi: {e}")


def send_group_notification(text):
    """Sirket ici gruba bildirim gonder."""
    group_id = config.TELEGRAM_GROUP_CHAT_ID
    if not group_id:
        return
    send_telegram_message(group_id, text)


def send_inline_keyboard(chat_id, text, buttons):
    """Inline keyboard ile mesaj gonder.
    buttons: [[{"text": "Evet", "callback_data": "action:yes"}], ...]
    """
    reply_markup = {"inline_keyboard": buttons}
    return send_telegram_message(chat_id, text, reply_markup=reply_markup)


def handle_callback_query(callback_query, agent):
    """Inline keyboard buton tiklamalarini isler."""
    callback_id = callback_query["id"]
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    data = callback_query.get("data", "")
    user_name = callback_query["from"].get("first_name", "Kullanici")

    print(f"\n>>> [CALLBACK] {user_name}: {data}")

    parts = data.split(":")
    action = parts[0] if parts else ""

    if action == "confirm_order":
        # Siparis onay
        answer_callback_query(callback_id, "Siparis onaylandi!")
        edit_message_text(chat_id, message_id, "Siparis onaylandi!")

    elif action == "cancel_order":
        # Siparis iptal
        answer_callback_query(callback_id, "Siparis iptal edildi.")
        edit_message_text(chat_id, message_id, "Siparis iptal edildi.")

    elif action == "menu_today":
        # Bugunun menusu
        answer_callback_query(callback_id, "Menu yukleniyor...")
        typing = TypingIndicator(chat_id)
        typing.start()
        try:
            result = agent("Bugunun menusunu goster")
            typing.stop()
            response_text = extract_text_from_result(result)
            send_telegram_message(chat_id, response_text)
        except Exception:
            typing.stop()
            send_telegram_message(chat_id, "Menu alinamadi.")

    elif action == "menu_week":
        # Haftalik menu
        answer_callback_query(callback_id, "Haftalik menu yukleniyor...")
        typing = TypingIndicator(chat_id)
        typing.start()
        try:
            result = agent("Bu haftanin menusunu goster")
            typing.stop()
            response_text = extract_text_from_result(result)
            send_telegram_message(chat_id, response_text)
        except Exception:
            typing.stop()
            send_telegram_message(chat_id, "Menu alinamadi.")

    elif action == "daily_report":
        # Gunluk rapor
        answer_callback_query(callback_id, "Rapor hazirlaniyor...")
        typing = TypingIndicator(chat_id)
        typing.start()
        try:
            result = agent("Gunluk ozet raporu goster")
            typing.stop()
            response_text = extract_text_from_result(result)
            send_telegram_message(chat_id, response_text)
        except Exception:
            typing.stop()
            send_telegram_message(chat_id, "Rapor alinamadi.")

    elif action == "stock_check":
        # Stok durumu
        answer_callback_query(callback_id, "Stok kontrol ediliyor...")
        typing = TypingIndicator(chat_id)
        typing.start()
        try:
            result = agent("Dusuk stok uyarilarini goster")
            typing.stop()
            response_text = extract_text_from_result(result)
            send_telegram_message(chat_id, response_text)
        except Exception:
            typing.stop()
            send_telegram_message(chat_id, "Stok bilgisi alinamadi.")

    else:
        answer_callback_query(callback_id, "Bilinmeyen islem")


def get_updates(offset=None):
    """Telegram'dan yeni mesajlari alir."""
    url = f"{TELEGRAM_API_IP}/getUpdates"
    params = {"timeout": 30, "allowed_updates": '["message","callback_query"]'}
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
            print(f"[POLL] {len(results)} yeni guncelleme!")
        return results
    except Exception as e:
        print(f"[POLL] Hata: {e}")
        time.sleep(2)
        return []


def wait_for_api():
    """Flask API'nin ayaga kalkmasini bekler."""
    from agent.tools.order_tools import API_BASE
    api_url = API_BASE.replace('/api', '/')
    print(f"API bekleniyor: {api_url}")
    for i in range(30):
        try:
            resp = requests.get(api_url, timeout=2, allow_redirects=True)
            if resp.status_code < 500:
                print(f"API hazir! (deneme {i+1})")
                return True
        except Exception:
            pass
        time.sleep(2)
    print("UYARI: API 60 saniyede ayaga kalkmadi, yine de devam ediliyor.")
    return False


def is_group_chat(message):
    """Mesajin grup chattan gelip gelmedigini kontrol eder."""
    chat_type = message.get("chat", {}).get("type", "")
    return chat_type in ("group", "supergroup")


def run_bot():
    """Bot'u long-polling ile calistirir."""
    print("=" * 50)
    print("Basak Yemek Telegram Bot baslatiliyor...")
    print(f"Model: OpenAI {config.OPENAI_MODEL}")
    print(f"API Key: {os.environ.get('OPENAI_API_KEY', '')[:15]}...")
    print(f"API Base: {config.API_BASE}")
    if config.TELEGRAM_GROUP_CHAT_ID:
        print(f"Grup Chat ID: {config.TELEGRAM_GROUP_CHAT_ID}")
    else:
        print("Grup Chat ID: Ayarlanmamis (grup bildirimleri devre disi)")
    print("=" * 50)

    # Flask API'nin hazir olmasini bekle
    wait_for_api()

    agent = create_agent()
    print("Agent olusturuldu!")
    print("Bot hazir! Telegram'dan mesaj bekleniyor...\n")

    offset = None

    while True:
        try:
            updates = get_updates(offset)
            for update in updates:
                offset = update["update_id"] + 1

                # Callback query (inline keyboard butonu)
                if "callback_query" in update:
                    try:
                        handle_callback_query(update["callback_query"], agent)
                    except Exception as e:
                        print(f"!!! Callback hatasi: {e}")
                        traceback.print_exc()
                    continue

                message = update.get("message")
                if not message or not message.get("text"):
                    continue

                chat_id = message["chat"]["id"]
                user_text = message["text"]
                user_name = message["from"].get("first_name", "Kullanici")
                is_group = is_group_chat(message)

                print(f"\n>>> [{'GRUP' if is_group else 'DM'}] [{user_name}] ({chat_id}): {user_text}")

                # Grupta sadece bot mentionlandiginda veya komutlarda yanit ver
                if is_group:
                    bot_username = os.environ.get('BOT_USERNAME', '')
                    is_mentioned = bot_username and f"@{bot_username}" in user_text
                    is_command = user_text.startswith("/")
                    is_keyword = any(kw in user_text.lower() for kw in [
                        'ozet', 'rapor', 'stok', 'menu', 'rota', 'teslimat', 'siparis',
                        'haftalik', 'gunluk', 'durum'
                    ])

                    if not (is_mentioned or is_command or is_keyword):
                        continue  # Grup mesajlarinda ilgisiz mesajlari atla

                # /start komutu
                if user_text == "/start":
                    if is_group:
                        send_inline_keyboard(chat_id,
                            "Basak Yemek Asistani hazir! Ne yapmak istersiniz?",
                            [
                                [{"text": "Gunluk Rapor", "callback_data": "daily_report"},
                                 {"text": "Stok Durumu", "callback_data": "stock_check"}],
                                [{"text": "Bugun Menu", "callback_data": "menu_today"},
                                 {"text": "Haftalik Menu", "callback_data": "menu_week"}],
                            ])
                    else:
                        send_inline_keyboard(chat_id,
                            f"Merhaba {user_name}! Ben Basak Yemek asistaniyim.\n\n"
                            "Size su konularda yardimci olabilirim:\n"
                            "- Siparis vermek\n"
                            "- Menu goruntuleme\n"
                            "- Siparis durumu sorgulama\n\n"
                            "Nasil yardimci olabilirim?",
                            [
                                [{"text": "Bugun Menu", "callback_data": "menu_today"},
                                 {"text": "Haftalik Menu", "callback_data": "menu_week"}],
                            ])
                    print("<<< /start yaniti gonderildi")
                    continue

                # /menu komutu
                if user_text.startswith("/menu"):
                    send_inline_keyboard(chat_id,
                        "Hangi menuyu gormek istersiniz?",
                        [
                            [{"text": "Bugunun Menusu", "callback_data": "menu_today"},
                             {"text": "Haftalik Menu", "callback_data": "menu_week"}],
                        ])
                    continue

                # /rapor komutu
                if user_text.startswith("/rapor") or user_text.startswith("/ozet"):
                    send_inline_keyboard(chat_id,
                        "Rapor secin:",
                        [
                            [{"text": "Gunluk Rapor", "callback_data": "daily_report"}],
                            [{"text": "Stok Durumu", "callback_data": "stock_check"}],
                        ])
                    continue

                # Agent ile konusma
                try:
                    # Yaziyor animasyonunu baslat
                    typing = TypingIndicator(chat_id)
                    typing.start()

                    # Grup/DM bilgisini prompt'a ekle
                    context = f"[is_group={'true' if is_group else 'false'}, chat_id={chat_id}]"
                    prompt = f"{context} Kullanici ({user_name}): {user_text}"
                    result = agent(prompt)

                    # Yaziyor animasyonunu durdur
                    typing.stop()

                    # Strands agent result'tan duz text cikar
                    response_text = extract_text_from_result(result)

                    # Bos yanit kontrolu
                    if not response_text or response_text.strip() == '' or response_text == 'None':
                        response_text = "Anlayamadim, tekrar yazar misiniz?"

                    send_telegram_message(chat_id, response_text)
                    print(f"<<< [BOT]: {response_text[:150]}...")
                except Exception as e:
                    typing.stop()
                    print(f"!!! Agent hatasi: {e}")
                    traceback.print_exc()
                    send_telegram_message(chat_id,
                        "Uzgunum, bir hata olustu. Lutfen tekrar deneyin.")

        except KeyboardInterrupt:
            print("\nBot durduruluyor...")
            break
        except Exception as e:
            print(f"!!! Dongu hatasi: {e}")
            traceback.print_exc()
            time.sleep(5)


# ============ GRUP BILDIRIM FONKSIYONLARI ============

def send_daily_menu_notification():
    """Sabah grup bildirimi: Gunun menusu."""
    if not config.TELEGRAM_GROUP_CHAT_ID:
        return
    try:
        from datetime import date
        resp = requests.get(f"{config.API_BASE}/menu/current", timeout=5)
        if resp.status_code != 200:
            return

        data = resp.json()
        day_names = ['Pazartesi', 'Sali', 'Carsamba', 'Persembe', 'Cuma', 'Cumartesi']
        today_idx = date.today().weekday()
        if today_idx >= 6:
            return

        today_name = day_names[today_idx]
        items = data.get('days', {}).get(today_name, [])
        if not items:
            return

        text = f"BUGUNUN MENUSU ({today_name})\n\n"
        for item in items:
            text += f"  - {item}\n"
        text += "\nAfiyet olsun!"

        send_group_notification(text)
    except Exception as e:
        print(f"Menu bildirimi hatasi: {e}")


def send_order_summary_notification():
    """Siparis ozeti grup bildirimi."""
    if not config.TELEGRAM_GROUP_CHAT_ID:
        return
    try:
        from datetime import date
        resp = requests.get(f"{config.API_BASE}/summary/{date.today().isoformat()}", timeout=5)
        summary = resp.json()
        total = summary.get('total_portions', 0)
        if not total:
            return

        text = (f"SIPARIS OZETI\n\n"
                f"Toplam: {summary.get('total_orders', 0)} siparis, {total} porsiyon\n"
                f"Sefer Tasi: {summary.get('sefer_tasi', 0)} | Paket: {summary.get('paket', 0)} | "
                f"Kuvet: {summary.get('kuvet', 0)} | Tepsi: {summary.get('tepsi', 0)} | "
                f"Poset: {summary.get('poset', 0)}")

        send_group_notification(text)
    except Exception as e:
        print(f"Siparis ozet bildirimi hatasi: {e}")


def send_route_complete_notification(route_name, driver_name):
    """Rota tamamlaninca grup bildirimi."""
    if not config.TELEGRAM_GROUP_CHAT_ID:
        return
    text = f"ROTA TAMAMLANDI\n\n{route_name}\nSofor: {driver_name}"
    send_group_notification(text)


def send_low_stock_notification(items):
    """Dusuk stok uyarisi grup bildirimi."""
    if not config.TELEGRAM_GROUP_CHAT_ID:
        return
    text = f"DUSUK STOK UYARISI\n\n"
    for item in items[:10]:
        text += f"  - {item['ingredient_name']}: {item['current_stock']}/{item['min_stock_level']} {item['unit']}\n"
    send_group_notification(text)


if __name__ == "__main__":
    run_bot()
