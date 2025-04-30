import asyncio
import time

async def fetch_weather():
    print("Fetching weather...")
    await asyncio.sleep(1)
    print("Weather fetched.")
    return "Sunny"

async def fetch_news():
    print("Fetching news...")
    await asyncio.sleep(1)
    print("News fetched.")
    return "Market up"

async def fetch_stocks():
    print("Fetching stocks...")
    await asyncio.sleep(1)
    print("Stocks fetched.")
    return "AAPL 150"

async def main_sequential():
    start = time.time()

    # weather = await fetch_weather()
    # news = await fetch_news()
    # stocks = await fetch_stocks()

    # Run all 3 at the same time
    weather, news, stocks = await asyncio.gather(
        fetch_weather(),
        fetch_news(),
        fetch_stocks()
    )

    print("\nResults:")
    print(f"Weather: {weather}")
    print(f"News: {news}")
    print(f"Stocks: {stocks}")

    print(f"\nSequential total time: {time.time() - start:.2f} seconds")

asyncio.run(main_sequential())
