const express = require('express');
const multer = require('multer');
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const app = express();
const upload = multer({ dest: 'uploads/' });

app.use(express.urlencoded({ extended: true }));

app.get('/', (req, res) => {
  res.send(`
    <h2>Facebook E2EE Auto Sender</h2>
    <form method="POST" action="/start" enctype="multipart/form-data">
      <label>App State JSON:</label>
      <input type="file" name="jsonFile" /><br><br>
      
      <label>Messages File (txt):</label>
      <input type="file" name="messageFile" /><br><br>
      
      <label>Chat URL:</label>
      <input type="text" name="chatUrl" /><br><br>
      
      <label>Prefix (e.g. hater name):</label>
      <input type="text" name="prefix" /><br><br>
      
      <label>Delay (in sec):</label>
      <input type="number" name="delay" value="3" /><br><br>
      
      <button type="submit">Start Sending</button>
    </form>
  `);
});

app.post('/start', upload.fields([{ name: 'jsonFile' }, { name: 'messageFile' }]), async (req, res) => {
  const jsonPath = req.files['jsonFile'][0].path;
  const messagePath = req.files['messageFile'][0].path;
  const { chatUrl, prefix, delay } = req.body;

  try {
    const jsonData = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
    const messages = fs.readFileSync(messagePath, 'utf8').split('\n').filter(Boolean);

    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();

    await context.addCookies(jsonData.map(c => ({
      name: c.name,
      value: c.value,
      domain: c.domain,
      path: c.path,
      httpOnly: c.httpOnly || false,
      secure: c.secure || false,
      expires: c.expires || -1
    })));

    const page = await context.newPage();
    await page.goto(chatUrl, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(5000);

    for (const msg of messages) {
      const finalMsg = `${prefix} ${msg}`;
      await page.fill('[contenteditable="true"]', finalMsg);
      await page.keyboard.press('Enter');
      await page.waitForTimeout((parseInt(delay) || 3) * 1000);
    }

    await browser.close();
    res.send('Messages sent successfully.');
  } catch (err) {
    console.error(err);
    res.status(500).send('Error sending messages.');
  } finally {
    fs.unlinkSync(jsonPath);
    fs.unlinkSync(messagePath);
  }
});

app.listen(10000, () => {
  console.log("Server running on port 10000");
});
