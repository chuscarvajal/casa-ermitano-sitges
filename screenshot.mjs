import puppeteer from 'puppeteer-core';

const CHROME = process.env.CHROME_PATH || 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const url = process.argv[2] || 'http://localhost:3000';
const label = process.argv[3] || '';
const outDir = path.join(__dirname, 'temporary screenshots');
fs.mkdirSync(outDir, { recursive: true });

const existing = fs.readdirSync(outDir).filter((f) => /^screenshot-\d+/.test(f));
const next = existing.length
  ? Math.max(...existing.map((f) => Number(f.match(/^screenshot-(\d+)/)[1]))) + 1
  : 1;
const file = path.join(outDir, `screenshot-${next}${label ? `-${label}` : ''}.png`);

const browser = await puppeteer.launch({ headless: 'new', executablePath: CHROME });
const page = await browser.newPage();
await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 1 });
await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });
await page.screenshot({ path: file, fullPage: true });
await browser.close();
console.log(file);
