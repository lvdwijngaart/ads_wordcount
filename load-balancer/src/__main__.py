import asyncio
from asyncio import StreamReader, StreamWriter
import os

RPYC_SERVERS = [
    addr.split(":")
    for addr in os.environ.get("RPYC_SERVERS","localhost:18900").splitlines()
]
SERVER_HOST = os.environ.get("SERVER_HOST","0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "18861"))


async def select_server() -> tuple[StreamReader, StreamWriter]:
    hostname, port = RPYC_SERVERS[0]
    return await asyncio.open_connection(hostname, int(port))

async def forward_stream(rx, wx):
    while not (wx.is_closing()):
        data_up = await rx.read(128)
        wx.write(data_up)
        await wx.drain()

async def handle_conn(rc: StreamReader, wc: StreamWriter):
    rs, ws = await select_server()

    try:
        async with asyncio.TaskGroup() as tg:
            upstream = tg.create_task(
                forward_stream(rc, ws)
            )
            downstream = tg.create_task(
                forward_stream(rs, wc)
            )

    except Exception as e:
        print(e)
    finally:
        ws.close()
        wc.close()
        await ws.wait_closed()
        await wc.wait_closed()


async def main():
    server = await asyncio.start_server(handle_conn, SERVER_HOST, SERVER_PORT)
    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving on {addrs}')

    async with server:
        await server.serve_forever()

asyncio.run(main())
