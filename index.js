const express = require('express');
const fs = require('fs');
const { chromium } = require('playwright');

const app = express();
const PORT = process.env.PORT || 10000;

app.use(express.json());

app.post('/send', async (req, res) => {
  const { appStateJson, chatUrl, message, delay } = req.body;

  if (!appStateJson || !chatUrl || !message) {
    return res.status(400).send("Missing required fields.");
  }

  try {
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();
    const page = await context.newPage();

    // Login via app state cookie
    const cookies = JSON.parse(appStateJson);
    await context.addCookies(cookies);
    await page.goto(chatUrl, { waitUntil: 'domcontentloaded' });

    await page.waitForTimeout(delay || 2000);

    await page.type('[contenteditable="true"]', message, { delay: 50 });
    await page.keyboard.press('Enter');

    await browser.close();

    res.send('Message sent successfully');
  } catch (e) {
    console.error(e);
    res.status(500).send("Something went wrong.");
  }
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
