"""
АРХИВ
Бот для внутрибиржевого арбитража (треугольный)
не сработал, так как биржа корректирует курсы
за 10 часов заработок меньше чем скачет курс COIN-USDT
"""

import asyncio
import datetime
import time

from api_keys import API_KEY, API_SECRET
from binance import AsyncClient


async def get_balance(client):
    q = await client.get_account()
    balance = {}
    for i in q["balances"]:
        if float(i["free"]) > 0:
            balance[i["asset"]] = float(i["free"])
    return balance


async def get_curses(client):
    j = await client.get_all_tickers()
    curses = {}
    for i in j:
        curses[i["symbol"]] = float(i["price"])
    return curses


async def buy(client, symbol, quoteOrderQty):
    order = await client.order_market_buy(
        symbol=symbol, quoteOrderQty=quoteOrderQty
    )
    return order


async def sell(client, symbol, quantity):
    order = await client.order_market_sell(symbol=symbol, quantity=quantity)
    return order


async def main(client):
    while True:
        st_main = time.perf_counter()
        st1 = time.time()
        task_balance = asyncio.create_task(get_balance(client))
        task_curses = asyncio.create_task(get_curses(client))
        balance, curses = await asyncio.gather(task_balance, task_curses)
        delta1 = time.time() - st1
        if delta1 < 0.4:
            sum = (
                balance["USDT"] * curses["USDTRUB"]
                + balance["LTC"] * curses["LTCRUB"]
                + balance["RUB"]
            )
            print(sum, end="\r")
            cross = (curses["LTCUSDT"] * curses["USDTRUB"]) / curses["LTCRUB"]
            st2 = time.time()
            if cross > 1.00225:
                print(f"before: {sum}")
                print(datetime.datetime.now())
                print(curses["LTCRUB"], curses["LTCUSDT"], curses["USDTRUB"])
                o1 = asyncio.create_task(
                    buy(client, symbol="LTCRUB", quoteOrderQty=balance["RUB"])
                )
                o2 = asyncio.create_task(
                    sell(
                        client,
                        symbol="LTCUSDT",
                        quantity=float(str(balance["LTC"])[:5]),
                    )
                )
                o3 = asyncio.create_task(
                    sell(
                        client, symbol="USDTRUB", quantity=int(balance["USDT"])
                    )
                )
                await asyncio.gather(o1, o2, o3)
                delta2 = time.time() - st2
                end_main = time.perf_counter()
                delta_main = 1 - ((end_main - st_main) % 1)
                time.sleep(delta_main)

            elif cross < 0.99775:
                print(f"before: {sum}")
                print(datetime.datetime.now())
                print(curses["LTCRUB"], curses["LTCUSDT"], curses["USDTRUB"])
                o3 = asyncio.create_task(
                    buy(client, symbol="USDTRUB", quoteOrderQty=balance["RUB"])
                )
                o2 = asyncio.create_task(
                    buy(
                        client,
                        symbol="LTCUSDT",
                        quoteOrderQty=int(balance["USDT"]),
                    )
                )
                o1 = asyncio.create_task(
                    sell(
                        client,
                        symbol="LTCRUB",
                        quantity=float(str(balance["LTC"])[:5]),
                    )
                )
                await asyncio.gather(o1, o2, o3)
                delta2 = time.time() - st2
                print(f"time to rub2usdt2ltc trade: {delta2:0.4f}\n")
                end_main = time.perf_counter()
                delta_main = 1 - ((end_main - st_main) % 1)
                time.sleep(delta_main)
            else:
                end_main = time.perf_counter()
                delta_main = 1 - ((end_main - st_main) % 1)
                time.sleep(delta_main + 2)
        else:
            end_main = time.perf_counter()
            delta_main = 1 - ((end_main - st_main) % 1)
            time.sleep(delta_main)


async def start():
    client = await AsyncClient.create(API_KEY, API_SECRET)
    now = time.perf_counter()
    time.sleep(int(now) + 1 - now)
    await main(client)


loop = asyncio.get_event_loop()
loop.run_until_complete(start())
