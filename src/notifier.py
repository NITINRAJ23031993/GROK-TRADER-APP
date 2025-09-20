import json
from src.utils.logger import info, error
try:
    from telegram import Bot
except Exception:
    Bot = None
def send_telegram(text):
    cfg = json.load(open('config/settings.yaml'))
    token = cfg.get('telegram', {}).get('bot_token')
    chat_id = cfg.get('telegram', {}).get('chat_id')
    if not token or not chat_id:
        info('Telegram not configured.')
        return
    if Bot is None:
        error('python-telegram-bot not installed')
        return
    bot = Bot(token=token)
    bot.send_message(chat_id=chat_id, text=text)