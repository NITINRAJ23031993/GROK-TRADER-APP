import requests
import yaml

def send_telegram(message):
    with open('config/settings.yaml', 'r') as f:
        cfg = yaml.safe_load(f)['telegram']
    token = cfg['token']
    chat_id = cfg['chat_id']
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
    requests.get(url)