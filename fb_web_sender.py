from flask import Flask, request, render_template_string
import os, json, subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML_FORM = '''
<!DOCTYPE html>
<html>
<head><title>Facebook E2EE Sender</title></head>
<body>
    <h2>Facebook E2EE Auto Messenger</h2>
    <form method="post" enctype="multipart/form-data">
        <label>Upload app_state.json:</label><br>
        <input type="file" name="appstate" required><br><br>

        <label>Upload messages.txt:</label><br>
        <input type="file" name="messages" required><br><br>

        <label>Hater Name:</label><br>
        <input type="text" name="hater" required><br><br>

        <label>Prefix (optional):</label><br>
        <input type="text" name="prefix"><br><br>

        <label>Delay (seconds):</label><br>
        <input type="number" name="delay" required><br><br>

        <label>Facebook E2EE Chat Link:</label><br>
        <input type="text" name="chatlink" required><br><br>

        <button type="submit">🚀 Start Messaging</button>
    </form>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        app_file = request.files['appstate']
        msg_file = request.files['messages']
        hater = request.form['hater']
        prefix = request.form.get('prefix', '')
        delay = int(request.form['delay'])
        chatlink = request.form['chatlink']

        app_path = os.path.join(UPLOAD_FOLDER, 'app_state.json')
        msg_path = os.path.join(UPLOAD_FOLDER, 'messages.txt')
        app_file.save(app_path)
        msg_file.save(msg_path)

        config = {
            'hater': hater,
            'prefix': prefix,
            'delay': delay,
            'chatlink': chatlink
        }
        with open('config.json', 'w') as f:
            json.dump(config, f)

        with open('loader.js', 'w') as f:
            f.write(generate_loader_js())

        subprocess.Popen(['node', 'loader.js'])
        return '✅ Auto messaging started in background!'
    return render_template_string(HTML_FORM)

def generate_loader_js():
    return """
const fs = require('fs');
const puppeteer = require('puppeteer');

const cookies = JSON.parse(fs.readFileSync('./uploads/app_state.json', 'utf-8'));
const messages = fs.readFileSync('./uploads/messages.txt', 'utf-8').split('\\n').filter(Boolean);
const config = JSON.parse(fs.readFileSync('./config.json', 'utf-8'));

const hater = config.hater;
const prefix = config.prefix || '';
const delay = parseInt(config.delay) * 1000;
const chatLink = config.chatlink;

(async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();
  await page.setCookie(...cookies);

  await page.goto(chatLink, { waitUntil: 'networkidle2' });
  await page.waitForSelector('div[contenteditable="true"]', { timeout: 15000 });

  const textbox = await page.$('div[contenteditable="true"]');

  let i = 0;
  while (true) {
    const msg = messages[i % messages.length];
    const fullMessage = `${prefix}${hater} ${msg}`;
    await textbox.type(fullMessage);
    await page.keyboard.press('Enter');
    console.log(`[Sent] ${fullMessage}`);
    await new Promise(r => setTimeout(r, delay));
    i++;
  }
})();
"""

if __name__ == '__main__':
    app.run(debug=True, port=5000)
