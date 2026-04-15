import os
import httpx
from fastapi import FastAPI, Request, BackgroundTasks

app = FastAPI()

# Railway will automatically pull these from your Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

async def send_telegram_msg(message: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)

@app.get("/")
async def health_check():
    return {"status": "active", "info": "Chartink-Telegram Bridge"}

@app.post("/webhook")
async def handle_chartink(request: Request, background_tasks: BackgroundTasks):
    # Chartink sends data as a JSON payload
    data = await request.json()
    
    scan_name = data.get("scan_name", "Unnamed Scan")
    stocks = data.get("stocks", "No stocks found")
    scan_url = data.get("scan_url", "#")
    
    # Format the message for Telegram
    message = (
        f"🔔 *Chartink Alert: {scan_name}*\n\n"
        f"🚀 *Stocks:* {stocks}\n\n"
        f"[View Screener]({scan_url})"
    )
    
    # Send message in background so we can respond to Chartink immediately
    background_tasks.add_task(send_telegram_msg, message)
    
    return {"status": "success"}