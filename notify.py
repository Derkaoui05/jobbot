import os, requests

def telegram(text):
    tok, chat = os.getenv("TELEGRAM_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
    if not (tok and chat):
        print(text); return
    for i in range(0, len(text), 3800):
        requests.post(f"https://api.telegram.org/bot{tok}/sendMessage",
                      data={"chat_id": chat, "text": text[i:i+3800], "disable_web_page_preview": True}, timeout=30)
