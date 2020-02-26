# Source: https://quentin.pradet.me/blog/how-do-you-rate-limit-calls-with-aiohttp.html

import asyncio
import time
import aiohttp

START = time.monotonic()

class RateLimiter:
    RATE = 0.5
    MAX_TOKENS = 5

    def __init__(self, client):
        self.client = client
        self.tokens = self.MAX_TOKENS
        self.updated_at = time.monotonic()

    async def get(self, *args, **kwargs):
        await self.wait_for_token()
        now = time.monotonic() - START
        #print(f'{now:.0f}s: ask {args[0]}')
        return self.client.get(*args, **kwargs)

    async def wait_for_token(self):
        while self.tokens < 1:
            self.add_new_tokens()
            await asyncio.sleep(0.1)
        self.tokens -= 1

    def add_new_tokens(self):
        now = time.monotonic()
        time_since_update = now - self.updated_at
        new_tokens = time_since_update * self.RATE
        if self.tokens + new_tokens >= 1:
            self.tokens = min(self.tokens + new_tokens, self.MAX_TOKENS)
            self.updated_at = now

async def fetch_one(client, url):
        async with await client.get(url) as resp:
            resp = await resp.json()
            now = time.monotonic() - START
            print(f"{now:.0f}s: got {resp['id']}")


async def main(urls):
    async with aiohttp.ClientSession() as client:
        client = RateLimiter(client)
        tasks = [asyncio.ensure_future(fetch_one(client, url)) for url in urls]
        await asyncio.gather(*tasks)