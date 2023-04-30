import json
import platform
import logging
import asyncio
import aiohttp
import sys


from datetime import datetime, timedelta

currency_list = ["USD", "EUR"]


async def get_exchange(days):
    urls = get_period(days)
    days_rates = []

    async with aiohttp.ClientSession() as session:
        for url in urls:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        result = await response.json()
                        currency = {}
                        for record in result["exchangeRate"]:
                            if record["currency"] in currency_list:
                                currency[record["currency"]] = {
                                    "sale": record["saleRate"],
                                    "purchase": record["purchaseRate"],
                                }
                            currency["date"] = result["date"]
                        days_rates.append(currency)
                    else:
                        print(f"Error status {response.status} for {url}")
            except aiohttp.ClientConnectionError as err:
                print(f"Connection error: {url}", str(err))
        return json.dumps(days_rates, ensure_ascii=False, indent=4)


def get_period(days=1):
    if days in range(11):
        urls = []
        for day in range(days):
            c_day = datetime.now() - timedelta(days=day)
            day, month, year = c_day.strftime("%d %m %Y").split()
            url = f"https://api.privatbank.ua/p24api/exchange_rates?json&date={day}.{month}.{year}"
            urls.append(url)
    else:
        raise ValueError("Wrong period. Should be from 1 to 10")

    return urls


async def main(period):
    res2 = await get_exchange(period)

    return res2


if __name__ == "__main__":
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        period = int(sys.argv[1])
    except:
        period = 1
    res = asyncio.run(main(period))
    print(res)
