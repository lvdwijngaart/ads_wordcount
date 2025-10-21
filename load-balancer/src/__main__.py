import asyncio
from asyncio import StreamReader, StreamWriter
import os

RPYC_SERVERS = [
    addr.split(":")
    for addr in os.environ.get("RPYC_SERVERS", "localhost:18900").splitlines()
]

RPYC_SERVER_COUNT = len(RPYC_SERVERS)
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "18861"))

rr_counter = 0


async def select_server() -> tuple[StreamReader, StreamWriter]:
    global rr_counter
    hostname, port = RPYC_SERVERS[rr_counter]
    rr_counter = (rr_counter + 1) % RPYC_SERVER_COUNT
    print(f"selecting server '{hostname}:{port}'")
    return await asyncio.open_connection(hostname, int(port))


async def forward_stream(rx: StreamReader, wx: StreamWriter):
    while not rx.at_eof():
        data_up = await rx.read(256)
        wx.write(data_up)
        await wx.drain()


async def handle_conn(rc: StreamReader, wc: StreamWriter):
    print(f"incoming connection {wc}")
    rs, ws = await select_server()

    upstream = asyncio.create_task(forward_stream(rc, ws))
    downstream = asyncio.create_task(forward_stream(rs, wc))

    try:
        await asyncio.gather(upstream, downstream)
    except Exception as e:
        print(e)
        upstream.cancel()
        downstream.cancel()
    finally:
        wc.close()
        ws.close()


async def main():
    server = await asyncio.start_server(handle_conn, SERVER_HOST, SERVER_PORT)
    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Serving on {addrs}")

    async with server:
        await server.serve_forever()


asyncio.run(main())
