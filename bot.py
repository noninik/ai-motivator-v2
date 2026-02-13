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
TELEGRAPH_URL = "https://api.telegra.ph"

HASHTAGS = "#мотивация #саморазвитие #продуктивность #успех"
CHANNEL_LINK = "motivation_ai_daily"  # ЗАМЕНИ НА СВОЙ например motivation_daily

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
    "как заработать первые деньги в интернете",
    "секреты продуктивности успешных людей",
    "как изменить свою жизнь за 30 дней",
    "почему важно инвестировать в себя",
    "как найти свое призвание",
    "простые привычки которые изменят жизнь",
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
    return resp.json()["choices"][0]["message"]["content"], selected_theme


def generate_article(theme):
    headers = {
        "Authorization": "Bearer " + GROQ_API_KEY,
        "Content-Type": "application/json",
    }
    body = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "Ты автор статей по саморазвитию. Пишешь подробно и интересно на русском.",
            },
            {
                "role": "user",
                "content": "Напиши статью 300-400 слов на тему: " + theme + ". Раздели на 3-4 абзаца. Без заголовков с решеткой. В конце напиши: Подписывайся на Telegram канал https://t.me/" + CHANNEL_LINK + " чтобы получать мотивацию каждый день!",
            },
        ],
        "temperature": 0.85,
        "max_tokens": 800,
    }
    resp = requests.post(GROQ_URL, headers=headers, json=body, timeout=30)
    if resp.status_code != 200:
        print("Article generation error:", resp.text)
        return None
    return resp.json()["choices"][0]["message"]["content"]


def publish_to_telegraph(title, content):
    acc = requests.get(TELEGRAPH_URL + "/createAccount", params={
        "short_name": "Motivator",
        "author_name": "Мотивация каждый день",
        "author_url": "https://t.me/" + CHANNEL_LINK,
    }, timeout=30).json()

    if not acc.get("ok"):
        print("Telegraph account error:", acc)
        return None

    token = acc["result"]["access_token"]

    paragraphs = content.split("\n")
    nodes = []
    for p in paragraphs:
        p = p.strip()
        if p:
            nodes.append({"tag": "p", "children": [p]})

    page = requests.post(TELEGRAPH_URL + "/createPage", data={
        "access_token": token,
        "title": title,
        "author_name": "Мотивация каждый день",
        "author_url": "https://t.me/" + CHANNEL_LINK,
        "content": json.dumps(nodes),
        "return_content": "false",
    }, timeout=30).json()

    if page.get("ok"):
        return page["result"]["url"]
    print("Telegraph page error:", page)
    return None


def send_to_telegram(text):
    url = "https://api.telegram.org/bot" + TELEGRAM_BOT_TOKEN + "/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": text, "disable_web_page_preview": False}
    return requests.post(url, json=payload, timeout=30).json()


def main():
    print("=== AI MOTIVATOR START ===")

    if not TELEGRAM_BOT_TOKEN or not CHANNEL_ID or not GROQ_API_KEY:
        print("ERROR: env vars not set")
        sys.exit(1)

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

    # Генерируем статью на Telegraph
    print("Generating Telegraph article...")
    article = generate_article(theme)
    if article:
        print("Publishing to Telegraph...")
        url = publish_to_telegraph(theme.capitalize(), article)
        if url:
            full_post += "\n\n📖 Читай подробнее: " + url
            print("Telegraph URL:", url)
        else:
            print("Telegraph publish failed, posting without link")
    else:
        print("Article generation failed, posting without link")

    print("Sending to Telegram...")
    result = send_to_telegram(full_post)

    if result.get("ok"):
        print("SUCCESS!")
    else:
        print("ERROR:", result)
        sys.exit(1)

    print("=== DONE ===")


if __name__ == "__main__":
    main()
