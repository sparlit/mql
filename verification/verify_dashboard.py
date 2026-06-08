import asyncio
from playwright.async_api import async_playwright
import os
import time
import subprocess

async def run_verification():
    # Start the server in the background
    proc = subprocess.Popen(["python", "src/core/main.py"], env={**os.environ, "PYTHONPATH": "."})
    time.sleep(3) # Give it time to start

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            await page.goto("http://127.0.0.1:8000")
            await page.wait_for_selector("h1")
            await page.screenshot(path="docs/v5_dashboard_check.png")
            print("Dashboard screenshot captured at docs/v5_dashboard_check.png")
        except Exception as e:
            print(f"Verification failed: {e}")
        finally:
            await browser.close()
            proc.terminate()

if __name__ == "__main__":
    asyncio.run(run_verification())
