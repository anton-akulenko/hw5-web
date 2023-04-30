import json
import platform
import logging
import asyncio
import aiohttp
import sys


from datetime import datetime, timedelta

currency_list = ["USD", "EUR"]


def create_url(date):
    day, month, year = date.strftime("%d %m %Y").split()
    return f"https://api.privatbank.ua/p24api/exchange_rates?json&date={day}.{month}.{year}"


async def request(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    r = await response.json()
                    return r
                logging.error(f"Error status {response.status} for {url}")
        except aiohttp.ClientConnectorError as e:
            logging.error(f"Connection error {url}: {e}")
        return None


async def get_exchange(date=datetime.now()):
    day, month, year = date.strftime("%d %m %Y").split()
    url = f"https://api.privatbank.ua/p24api/exchange_rates?json&date={day}.{month}.{year}"
    result = await request(url)
    currency = {}
    for record in result["exchangeRate"]:
        if record["currency"] in currency_list:
            currency[record["currency"]] = {
                "sale": record["saleRate"],
                "purchase": record["purchaseRate"]
                # "sale NB": round(record["saleRateNB"], 2),
                # "purchase NB": round(record["purchaseRateNB", 2]),
            }
        currency["date"] = result["date"]
    # rates = json.dumps(currency, ensure_ascii=False, indent=4)
    # curr_list.append(exchange_rate_for_a_date)
    return currency
    # return rates


async def get_period(days=0):
    if days in range(0, 10):
        days_rates = []
        for day in range(days):
            c_day = datetime.now() - timedelta(days=day)
            days_rates.append(await get_exchange(c_day))
    else:
        print("Wrong period. Should be from 1 to 10")
    return json.dumps(days_rates, ensure_ascii=False, indent=4)
    # return days_rates


async def main(period):
    # day = datetime.now() - timedelta(days=3)
    # res = await get_exchange(day)
    res2 = await get_period(period)
    # result = await request(create_url(datetime.now()))
    # curr = {}
    # for record in result["exchangeRate"]:
    #     if record["currency"] == "USD":
    #         curr[record["currency"]] = {
    #             "sale": record["saleRate"],
    #             "purchase": record["purchaseRate"],
    #             "sale NB": record["saleRateNB"],
    #             "purchase NB": record["purchaseRateNB"],
    #         }
    #     exchange_rate_for_a_date[result["date"]] = curr
    # curr_list.append(exchange_rate_for_a_date)
    return res2


# async with aiohttp.ClientSession() as session:
#     async with session.get(create_url(datetime.now())) as response:
#         print("Status:", response.status)
#         print("Content-type:", response.headers["content-type"])

#         html = await response.text()
#         print("Body:", html)


if __name__ == "__main__":
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        period = int(sys.argv[1])
    except:
        period = 0
    res = asyncio.run(main(period))
    print(res)
    # print(get_exchange(datetime.now()))
