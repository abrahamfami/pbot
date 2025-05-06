import requests
from bs4 import BeautifulSoup
import os
import time
from telethon import TelegramClient
import asyncio

api_id = 26161532
api_hash = '17ef95d1f688b80b860ec95c80144329'
session_name = 'dexscreener_scraper'
TARGETS = ['@mcqueen_bonkbot', -1001625576005]

SEEN_FILE = 'seen_tokens.txt'
seen = set()
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, 'r') as f:
        seen = set(line.strip() for line in f if line.strip())

URL = "https://dexscreener.com/solana/pumpfun?rankBy=pairAge&order=asc&minMarketCap=10000&maxMarketCap=50000&minAge=1&maxAge=5&min24HVol=26000"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://google.com",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9"
}

def fetch_new_token_addresses():
    try:
        response = requests.get(URL, headers=headers)
        if response.status_code != 200:
            print(f"[HATA] Sayfa yüklenemedi: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        tokens = set()

        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith("/solana/") and len(href.split("/")) == 3:
                addr = href.split("/")[-1]
                if 32 <= len(addr) <= 44:
                    tokens.add(addr)

        return list(tokens)

    except Exception as e:
        print(f"[EXCEPTION] {e}")
        return []

async def main():
    async with TelegramClient(session_name, api_id, api_hash) as client:
        print("[BOT] Başladı. Dexscreener scrape çalışıyor...
")
        while True:
            try:
                found = fetch_new_token_addresses()
                new_tokens = [t for t in found if t not in seen]

                print(f"[TARANDI] Toplam: {len(found)} token bulundu.")
                print(f"[YENİ] {len(new_tokens)} yeni token tespit edildi.")

                if new_tokens:
                    with open(SEEN_FILE, "a") as f:
                        for t in new_tokens:
                            f.write(t + "\n")
                            seen.add(t)
                            msg = f"**Yeni Token Tespit Edildi**\nhttps://dexscreener.com/solana/{t}"
                            for target in TARGETS:
                                await client.send_message(target, msg, parse_mode='markdown')
                            print(f"[GÖNDERİLDİ] {t}")

                time.sleep(60)

            except Exception as e:
                print(f"[HATA] {e}")
                time.sleep(30)

if __name__ == '__main__':
    asyncio.run(main())
