import random
import os
import sys
from datetime import datetime, timezone, timedelta
import requests

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"

HASHTAGS = "#мотивация #саморазвитие #продуктивность #успех"

THEMES = [
    "как начать действовать прямо сейчас",
    "почему неудачи это топливо для роста",
    "как перестать сравнивать себя с другими",
    "утренние ритуалы успешных людей",
    "как побороть страх перед новым делом",
    "правило 2 минут для борьбы с ленью",
    "почему маленькие шаги важнее больших планов",
    "как найти мотивацию когда все надоело",
    "почему дисциплина важнее мотивации",
    "как правильно ставить цели",
    "как выйти из зоны комфорта",
    "как перестать откладывать на завтра",
    "энергия и здоровье как фундамент успеха",
    "баланс между работой и отдыхом",
]


def generate_post():
    selected_theme = random.choice(THEMES)
    headers = {
        "Authorization": "Bearer " + GROQ_API_KEY,
        "Content-Type": "application/json",
    }
    body = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "Ты автор мотивационного контента. Пишешь емко и сильно на русском языке.",
            },
            {
                "role": "user",
                "content": "Напиши короткий мотивационный пост 80-120 слов на тему: " + selected_theme,
            },
        ],
        "temperature": 0.85,
        "max_tokens": 400,
    }
    resp = requests.post(GROQ_URL, headers=headers, json=body, timeout=30)
    if resp.status_code != 200:
        print("Groq error:", resp.text)
        sys.exit(1)
    result = resp.json()
    return result["choices"][0]["message"]["content"], selected_theme


def send_to_telegram(text):
    url = "https://api.telegram.org/bot" + TELEGRAM_BOT_TOKEN + "/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": text, "disable_web_page_preview": True}
    return requests.post(url, json=payload, timeout=30).json()


def main():
    print("=== START ===")
    content, theme = generate_post()
    print("Theme:", theme)

    msk = timezone(timedelta(hours=3))
    hour = datetime.now(msk).hour
    if 5 <= hour < 12:
        greeting = "🌅 Доброе утро!"
    elif 12 <= hour < 17:
        greeting = "☀️ Добрый день!"
    elif 17 <= hour < 22:
        greeting = "🌆 Добрый вечер!"
    else:
        greeting = "🌙 Доброй ночи!"

    full_post = greeting + "\n\n" + content + "\n\n" + HASHTAGS

    result = send_to_telegram(full_post)
    if result.get("ok"):
        print("SUCCESS!")
    else:
        print("ERROR:", result)
        sys.exit(1)


if __name__ == "__main__":
    main()
