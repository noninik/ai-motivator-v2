import random
import os
import sys
import json
from datetime import datetime, timezone, timedelta
import requests

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"
HISTORY_FILE = "post_history.json"

AFFILIATE_LINKS = [
    "🎓 Skillbox kursy so skidkoi: https://skillbox.ru/",
    "📚 Netologiya obuchenie: https://netology.ru/",
    "💻 Hexlet programmirovaniye: https://hexlet.io/",
]

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


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"post_count": 0, "used_themes": []}


def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def generate_post(used_themes):
    available = [t for t in THEMES if t not in used_themes]
    if not available:
        available = THEMES

    selected_theme = random.choice(available)

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

    print("Calling Groq API...")
    resp = requests.post(GROQ_URL, headers=headers, json=body, timeout=30)
    print("Status:", resp.status_code)

    if resp.status_code != 200:
        print("Groq error:", resp.text)
        sys.exit(1)

    result = resp.json()
    content = result["choices"][0]["message"]["content"]
    return content, selected_theme


def send_to_telegram(text):
    url = "https://api.telegram.org/bot" + TELEGRAM_BOT_TOKEN + "/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": True,
    }
    resp = requests.post(url, json=payload, timeout=30)
    return resp.json()


def main():
    print("=== AI MOTIVATOR START ===")

    if not TELEGRAM_BOT_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN not set")
        sys.exit(1)
    if not CHANNEL_ID:
        print("ERROR: CHANNEL_ID not set")
        sys.exit(1)
    if not GROQ_API_KEY:
        print("ERROR: GROQ_API_KEY not set")
        sys.exit(1)

    print("All env vars OK")

    history = load_history()
    count = history.get("post_count", 0)
    used = history.get("used_themes", [])
    print("Posts so far:", count)

    content, theme = generate_post(used)
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

    full_post = greeting + "\n\n" + content

    next_count = count + 1
    if next_count % 5 == 0:
        link = random.choice(AFFILIATE_LINKS)
        full_post = full_post + "\n\n" + link
        print("Added affiliate link")

    full_post = full_post + "\n\n" + HASHTAGS

    print("Sending to Telegram...")
    result = send_to_telegram(full_post)

    if result.get("ok"):
        print("SUCCESS!")
        history["post_count"] = next_count
        used.append(theme)
        if len(used) > 50:
            used = used[-50:]
        history["used_themes"] = used
        save_history(history)
        print("Total posts:", next_count)
    else:
        print("TELEGRAM ERROR:", result)
        sys.exit(1)

    print("=== DONE ===")


if __name__ == "__main__":
    main()
