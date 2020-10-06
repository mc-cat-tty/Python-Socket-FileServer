import argparse
import logging
import threading
import asyncio

"""
Connect to this server using netcat or similar utilities
"""

HOST, PORT = "127.0.0.1", 9999

def handle_command(cmd: str, client_stream: asyncio.StreamWriter):
    if not cmd: return
    if cmd == '0':
        return f"Client address: {client_stream.get_extra_info('peername')}\n"
    elif cmd == '1':
        return f"Socket address: {client_stream.get_extra_info('sockname')}\n"
    elif cmd == '2':
        return f"Current thread name: {threading.current_thread().getName()}\n"
    elif cmd == '3':
        return f"Alive threads number: {threading.active_count()}\n"
    elif cmd == '4':
        return f"Alive threads: {[t.getName() for t in threading.enumerate()]}\n"
    else:  # Help
        return """'0': Return the remote address (client) to which the socket is connected;
'1': Return the server socket's own address;
'2': Return the current thread name;
'3': Return the number of alive threads;
'4': Return the list of names of alive threads (comma separated);
'q': Quit server when all the clients will be disconnected;
"""

async def server_handler(reader, writer):
    addr = writer.get_extra_info('peername')
    logging.info(f"Serving {addr}")
    while True:
        writer.write(">> ".encode())
        await writer.drain()
        data = await reader.read(1024)
        cmd = data.decode().strip()

        logging.info(f"Received {cmd} from {addr}")

        if not cmd:
            writer.close()
            break
        elif cmd == 'q':
            logging.warning(f"Closed connection: {addr}")
            writer.close()
            break
        else:
            writer.write(handle_command(cmd, writer).encode())
            await writer.drain()

async def main():
    global HOST, PORT
    logging.basicConfig(level=logging.DEBUG, format="%(threadName)s --> %(asctime)s - %(levelname)s: %(message)s",
                        datefmt="%H:%M:%S")
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--address", help="host address", default=HOST, type=str, dest="address")
    parser.add_argument("-p", "--port", help="port number", default=PORT, type=int, dest="port")
    args = parser.parse_args()
    PORT = args.port
    HOST = args.address

    logging.info(f"Server running on {HOST}:{PORT}...")

    server = await asyncio.start_server(server_handler, HOST, PORT)


    try:
        async with server:
            await server.serve_forever()
    except KeyboardInterrupt:
        logging.warning("Server stopping...")



if __name__ == "__main__":
    asyncio.run(main())
