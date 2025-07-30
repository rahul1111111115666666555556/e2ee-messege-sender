import asyncio
import json
import time
import os
from flask import Flask, request
from playwright.async_api import async_playwright

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return '''
    <h2>Facebook E2EE Auto Sender</h2>
    <form method="POST" action="/start">
        <label>App State JSON file path: </label><input name="json_path"><br>
        <label>Chat ID: </label><input name="chat_id"><br>
        <label>Hater Name: </label><input name="hater"><br>
        <label>Delay (in seconds): </label><input name="delay" type="number"><br>
        <input type="submit" value="Start Sending">
    </form>
    '''

@app.route('/start', methods=['POST'])
def start_sender():
    json_path = request.form['json_path']
    chat_id = request.form['chat_id']
    hater = request.form['hater']
    delay = int(request.form['delay'])
    asyncio.create_task(run_sender(json_path, chat_id, hater, delay))
    return f'Started sending messages to Chat ID: {chat_id}'

async def run_sender(json_path, chat_id, hater, delay):
    messages = []
    if os.path.exists("messages.txt"):
        with open("messages.txt", "r", encoding="utf-8") as f:
            messages = [line.strip() for line in f if line.strip()]
    else:
        print("messages.txt not found.")
        return

    with open(json_path, "r") as f:
        cookies = json.load(f)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        await context.add_cookies([{
            "name": c["name"],
            "value": c["value"],
            "domain": c["domain"],
            "path": c["path"],
            "httpOnly": c.get("httpOnly", False),
            "secure": c.get("secure", False),
            "expires": c.get("expires", -1)
        } for c in cookies])

        page = await context.new_page()
        await page.goto(f"https://www.facebook.com/messages/t/{chat_id}")
        await page.wait_for_timeout(5000)

        while True:
            for msg in messages:
                try:
                    full_msg = f"{hater} {msg}"
                    await page.fill('div[aria-label="Message"]', full_msg)
                    await page.keyboard.press("Enter")
                    print(f"[Sent] {full_msg}")
                    await page.wait_for_timeout(delay * 1000)
                except Exception as e:
                    print(f"[Error] {e}")
                    await page.wait_for_timeout(5000)

        await browser.close()

if __name__ == '__main__':
    import threading
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000)).start()
