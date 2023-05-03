import asyncio
import logging
import aiohttp
import json
from main_chat import main as curr
import websockets
import names
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK

# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EXC Logger")
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

ch.setFormatter(formatter)

logger.addHandler(ch)

fh = logging.FileHandler("app.log")
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)

logger.addHandler(fh)


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


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f"{ws.remote_address} connects")

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f"{ws.remote_address} disconnects")

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distrubute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distrubute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            if message.startswith("exchange"):
                r = message.split(" ")
                if len(r) > 2:
                    lst_curr = []
                    lst_curr += r[2:]
                logger.info("Exchange rate request sent...")
                res = await curr(int(r[1]), lst_curr)
                for r in res:
                    d = r.pop("date")
                    tmp = {k: v for k, v in r.items()}
                    to_show = f"Date: {d}  Currency: {tmp} "
                    await self.send_to_clients(json.dumps(to_show))
                logger.info("Exchange rate request received")
            else:
                await self.send_to_clients(f"{ws.name}: {message}")


async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, "localhost", 8080):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    asyncio.run(main())
