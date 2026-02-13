import random
import os
import sys
import json
import subprocess
from datetime import datetime, timezone, timedelta
import requests

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"
TELEGRAPH_URL = "https://api.telegra.ph"

HASHTAGS = "#мотивация #саморазвитие #продуктивность #успех"
CHANNEL_LINK = "motivation_ai_daily"

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
    "почему утро определяет весь день",
    "как перестать бояться ошибок",
    "сила благодарности и как она меняет жизнь",
    "почему богатые думают иначе",
    "как научиться говорить нет",
    "токсичные привычки которые крадут твое время",
    "как справиться с выгоранием",
    "почему одиночество это суперсила",
    "как читать по одной книге в неделю",
    "секрет успеха в постоянстве а не в таланте",
    "как зарабатывать на том что любишь",
    "правило 5 секунд которое изменит твою жизнь",
    "почему тебе не нужен идеальный план",
    "как прокачать уверенность в себе",
    "три слова которые убивают твой успех",
    "как медитация меняет мозг за 8 недель",
    "почему successful люди встают в 5 утра",
    "как избавиться от зависимости от телефона",
    "что делать когда опускаются руки",
    "как построить привычку за 21 день это миф",
    "почему ты не там где хочешь быть",
    "как перестать жить на автопилоте",
    "один навык который стоит миллион",
    "как окружение программирует твой доход",
    "почему страх это компас к твоей цели",
    "как принимать решения быстро и не жалеть",
    "эффект сложного процента в саморазвитии",
    "как превратить провал в трамплин",
    "почему перфекционизм это ловушка",
    "как найти энергию когда сил нет",
]

POST_STYLES = [
    {
        "system": "Ты дерзкий мотивационный блогер. Короткие рубленые фразы. Без воды. Говоришь на ты.",
        "prompt": "Напиши мотивационный пост на тему: {theme}. Максимум 60 слов. Начни с провокационного вопроса. 2-3 коротких мощных предложения. В конце один конкретный совет.",
    },
    {
        "system": "Ты рассказчик историй. Короткие цепляющие истории. Без морализаторства.",
        "prompt": "Расскажи короткую историю на тему: {theme}. Максимум 60 слов. Начни сразу с действия. В конце одно предложение-вывод.",
    },
    {
        "system": "Ты жесткий ментор. Неудобная правда. Коротко и хлестко.",
        "prompt": "Напиши жесткий пост на тему: {theme}. Максимум 60 слов. Начни с правдивой фразы которая бесит. Объясни в 2 предложениях. Закончи действием.",
    },
    {
        "system": "Ты автор постов с неожиданными фактами.",
        "prompt": "Напиши пост на тему: {theme}. Максимум 60 слов. Начни с неожиданного факта. Свяжи с жизнью читателя. Закончи советом.",
    },
    {
        "system": "Ты пишешь мысленные эксперименты.",
        "prompt": "Напиши пост на тему: {theme}. Максимум 60 слов. Начни с 'Представь...' Задай вопрос. Закончи мощным выводом.",
    },
]


def call_groq(system, prompt):
    headers = {
        "Authorization": "Bearer " + GROQ_API_KEY,
        "Content-Type": "application/json",
    }
    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.9,
        "max_tokens": 300,
    }
    resp = requests.post(GROQ_URL, headers=headers, json=body, timeout=30)
    if resp.status_code != 200:
        print("Groq error:", resp.text)
        return None
    return resp.json()["choices"][0]["message"]["content"]


def generate_post(theme):
    style = random.choice(POST_STYLES)
    return call_groq(style["system"], style["prompt"].format(theme=theme))


def generate_quote(theme):
    return call_groq(
        "Ты создаешь мощные короткие цитаты на русском.",
        "Придумай мощную мотивационную цитату на тему: " + theme + ". Одно предложение. Максимум 15 слов. Без кавычек."
    )


def generate_voice_text(theme):
    return call_groq(
        "Ты мотивационный спикер. Пишешь текст для озвучки на русском.",
        "Напиши текст для голосового сообщения на тему: " + theme + ". 2-3 предложения. Максимум 40 слов. Без кавычек."
    )


def create_voice(text):
    try:
        # Шаг 1: создаём mp3
        subprocess.run(
            ["edge-tts", "--voice", "ru-RU-DmitryNeural", "--text", text, "--write-media", "voice.mp3"],
            timeout=30,
            check=True,
            capture_output=True,
        )
        print("MP3 created!")

        # Шаг 2: конвертируем в ogg opus (формат Telegram)
        subprocess.run(
            ["ffmpeg", "-y", "-i", "voice.mp3", "-c:a", "libopus", "-b:a", "64k", "voice.ogg"],
            timeout=30,
            check=True,
            capture_output=True,
        )
        print("OGG created!")

        if os.path.exists("voice.ogg"):
            return True
    except Exception as e:
        print("Voice error:", e)
    return False


def send_voice_to_telegram(file_path):
    url = "https://api.telegram.org/bot" + TELEGRAM_BOT_TOKEN + "/sendVoice"
    with open(file_path, "rb") as f:
        files = {"voice": f}
        data = {"chat_id": CHANNEL_ID}
        resp = requests.post(url, data=data, files=files, timeout=30)
    return resp.json()


def send_photo_to_telegram(photo_url, caption):
    url = "https://api.telegram.org/bot" + TELEGRAM_BOT_TOKEN + "/sendPhoto"
    payload = {"chat_id": CHANNEL_ID, "photo": photo_url, "caption": caption}
    return requests.post(url, json=payload, timeout=30).json()


def send_to_telegram(text):
    url = "https://api.telegram.org/bot" + TELEGRAM_BOT_TOKEN + "/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": text, "disable_web_page_preview": False}
    return requests.post(url, json=payload, timeout=30).json()


def generate_article(theme):
    return call_groq(
        "Ты блогер с живым языком. Без канцелярита. Говоришь на ты.",
        "Напиши статью 200-300 слов на тему: " + theme + ". Начни с истории. 3-4 абзаца. В конце: Подписывайся на Telegram канал https://t.me/" + CHANNEL_LINK + " — мотивация без воды каждый день!"
    )


def publish_to_telegraph(title, content):
    acc = requests.get(TELEGRAPH_URL + "/createAccount", params={
        "short_name": "Motivator",
        "author_name": "Мотивация без воды",
        "author_url": "https://t.me/" + CHANNEL_LINK,
    }, timeout=30).json()

    if not acc.get("ok"):
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
        "author_name": "Мотивация без воды",
        "author_url": "https://t.me/" + CHANNEL_LINK,
        "content": json.dumps(nodes),
        "return_content": "false",
    }, timeout=30).json()

    if page.get("ok"):
        return page["result"]["url"]
    return None


def main():
    print("=== AI MOTIVATOR START ===")

    if not TELEGRAM_BOT_TOKEN or not CHANNEL_ID or not GROQ_API_KEY:
        print("ERROR: env vars not set")
        sys.exit(1)

    theme = random.choice(THEMES)
    print("Theme:", theme)

    msk = timezone(timedelta(hours=3))
    hour = datetime.now(msk).hour
    if 5 <= hour < 12:
        greeting = "🌅"
    elif 12 <= hour < 17:
        greeting = "⚡"
    elif 17 <= hour < 22:
        greeting = "🔥"
    else:
        greeting = "🌙"

    # 1. Голосовое сообщение
    print("Generating voice text...")
    voice_text = generate_voice_text(theme)
    if voice_text:
        print("Voice text:", voice_text)
        print("Creating audio...")
        if create_voice(voice_text):
            print("Sending voice...")
            vr = send_voice_to_telegram("voice.ogg")
            if vr.get("ok"):
                print("Voice sent!")
            else:
                print("Voice send error:", vr)
        else:
            print("Voice creation failed")
    else:
        print("Voice text generation failed")

    # 2. Картинка с цитатой
    print("Generating quote...")
    quote = generate_quote(theme)
    if quote:
        print("Quote:", quote)
        photo_url = "https://picsum.photos/800/500?random=" + str(random.randint(1, 99999))
        pr = send_photo_to_telegram(photo_url, "💬 " + quote)
        if pr.get("ok"):
            print("Photo sent!")

    # 3. Текстовый пост
    print("Generating post...")
    content = generate_post(theme)
    if not content:
        print("Post generation failed")
        sys.exit(1)

    full_post = greeting + "\n\n" + content + "\n\n" + HASHTAGS

    # 4. Telegraph статья
    print("Generating article...")
    article = generate_article(theme)
    if article:
        tg_url = publish_to_telegraph(theme.capitalize(), article)
        if tg_url:
            full_post += "\n\n📖 Подробнее: " + tg_url
            print("Telegraph:", tg_url)

    print("Sending post...")
    result = send_to_telegram(full_post)

    if result.get("ok"):
        print("SUCCESS!")
    else:
        print("ERROR:", result)
        sys.exit(1)

    print("=== DONE ===")


if __name__ == "__main__":
    main()
