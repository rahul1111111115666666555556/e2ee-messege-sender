// === render-server.js (for Render deployment) ===
// Run with: node render-server.js
const express = require("express");
const fs = require("fs");
const puppeteer = require("puppeteer");
const app = express();
const PORT = process.env.PORT || 3000;

app.get("/", async (req, res) => {
  if (!fs.existsSync("task.json")) return res.send("No task.json found");
  const task = JSON.parse(fs.readFileSync("task.json", "utf8"));
  const { cookie, messages, prefix, delay, chatId } = task;

  try {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();
    await page.setUserAgent(
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36"
    );

    await page.setCookie(...cookie
      .split(";")
      .map(c => {
        const [name, ...rest] = c.trim().split("=");
        return { name, value: rest.join("="), domain: ".facebook.com" };
      })
    );

    const url = `https://www.facebook.com/messages/t/${chatId}`;
    await page.goto(url, { waitUntil: "networkidle2" });
    await page.waitForSelector("[contenteditable='true']", { timeout: 15000 });

    for (let i = 0; i < messages.length; i++) {
      const msg = `${prefix} ${messages[i]}`;
      await page.type("[contenteditable='true']", msg);
      await page.keyboard.press("Enter");
      console.log("✅ Sent:", msg);
      await new Promise(r => setTimeout(r, delay * 1000));
    }

    await browser.close();
    res.send("✅ All messages sent!");
  } catch (err) {
    console.error("❌ Error:", err);
    res.status(500).send("Something went wrong.");
  }
});

app.listen(PORT, () => console.log(`🚀 Server running on port ${PORT}`));
