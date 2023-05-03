import json
import platform
import logging
import asyncio
import aiohttp
import sys
import logging

logging.basicConfig(level=logging.INFO)


from datetime import datetime, timedelta

# currency_list = ["USD", "EUR"]


async def get_exchange(days, currency_list):
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
                                    "sale": record["saleRateNB"],
                                    "purchase": record["purchaseRateNB"],
                                }
                            currency["date"] = result["date"]
                        days_rates.append(currency)
                    else:
                        print(f"Error status {response.status} for {url}")
            except aiohttp.ClientConnectionError as err:
                print(f"Connection error: {url}", str(err))

        return days_rates


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


async def main(period=1, currency_add=None):
    currency_list = ["USD", "EUR"]
    currency_list += currency_add
    res2 = await get_exchange(period, currency_list)

    return res2


if __name__ == "__main__":
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    currency_list = ["USD", "EUR"]
    try:
        period = int(sys.argv[1])

        l = len(sys.argv)
        if l > 2:
            for c in range(l - 2):
                currency_list.append(sys.argv[c + 2])
    except:
        period = 1
    asyncio.run(main(period=period, currency_list=currency_list))
