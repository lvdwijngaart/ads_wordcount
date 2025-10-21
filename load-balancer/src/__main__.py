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


async def forward_stream(rx, wx):
    """
    Read from rx and forward to wx. Break on EOF and flush writes.
    """
    try:
        while True:
            data = await rx.read(4096)
            if not data:
                # peer closed; try to signal EOF to the writer side
                try:
                    wx.write_eof()
                except Exception:
                    pass
                await wx.drain()
                break
            wx.write(data)
            await wx.drain()
    except asyncio.CancelledError:
        raise
    except Exception:
        # ignore forward errors; caller will close sockets
        pass


async def handle_conn(rc: StreamReader, wc: StreamWriter):
    """
    Accept a client connection, pick a backend, open backend connection
    and forward bytes in both directions until EOF / error.
    """
    rs = ws = None
    try:
        rs, ws = await select_server()

        async with asyncio.TaskGroup() as tg:
            tg.create_task(forward_stream(rc, ws))  # client -> backend
            tg.create_task(forward_stream(rs, wc))  # backend -> client

    except Exception as e:
        # keep message short for logs
        print("connection error:", e)
    finally:
        # ensure all sockets are closed
        try:
            if ws is not None:
                ws.close()
                await ws.wait_closed()
        except Exception:
            pass
        try:
            if wc is not None:
                wc.close()
                await wc.wait_closed()
        except Exception:
            pass
        try:
            if rc is not None:
                rc.feed_eof()
        except Exception:
            pass
        try:
            if rs is not None:
                rs.feed_eof()
        except Exception:
            pass


async def main():
    server = await asyncio.start_server(handle_conn, SERVER_HOST, SERVER_PORT)
    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Serving on {addrs}")

    async with server:
        await server.serve_forever()


asyncio.run(main())
