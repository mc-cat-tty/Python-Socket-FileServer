import argparse
import logging
import threading
import asyncio

"""
Connect to this server using netcat or similar utilities
"""

HOST, PORT = "127.0.0.1", 9999  # Default values

CLIENTS = list()


def handle_command(cmd: str, client_stream: asyncio.StreamWriter):
    """
    This function handle a command and returns the output (as a string) which has to be sent to the client

    :param cmd: command to be handled
    :param client_stream: StreamWriter connected to the client that performs the request
    :return:
    :rtype: str
    """

    if not cmd: return  # Connection terminated
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
    elif cmd == '5':
        return f"Number of connected clients {len(CLIENTS)}\n"
    elif cmd == '6':
        return f"Connected clients: {CLIENTS}\n"
    else:  # Help
        return """'0': Return the remote address (client) to which the socket is connected;
'1': Return the server socket's own address;
'2': Return the current thread name;
'3': Return the number of alive threads;
'4': Return the list of alive threads' names;
'5': Return the number of connected clients;
'6': Return the list of connected clients' names;
'q': Quit server when all the clients will be disconnected;
"""


async def close_connection(writer: asyncio.StreamWriter):
    global CLIENTS
    addr = writer.get_extra_info('peername')
    logging.warning(f"Closed connection: {addr}")
    CLIENTS.remove(writer.get_extra_info('peername'))
    writer.close()
    await writer.wait_closed()


async def server_handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    global CLIENTS
    addr = writer.get_extra_info('peername')
    logging.info(f"Serving {addr}")
    CLIENTS.append(addr)
    while True:
        writer.write(">> ".encode())
        await writer.drain()  # Flushing data
        try:
            data = await reader.readline()
        except ConnectionResetError:  # Netcat for Windows sends RST packet to close the connection
            await close_connection(writer)
            logging.error(f"Closed connection - Reset Connection Error: {addr}")
            break
        cmd = data.decode().strip()

        logging.info(f"Received {cmd} from {addr}")

        if not cmd:
            await close_connection(writer)
            break
        elif cmd == 'q':
            await close_connection(writer)
            break
        else:
            writer.write(handle_command(cmd, writer).encode())
            await writer.drain()


async def keyboard_listener():
    while True:
        await asyncio.sleep(1)


async def main(host, port):
    server = await asyncio.start_server(server_handler, HOST, PORT)

    logging.info(f"Server running on {host}:{port}...")

    keyboard_listener_task = asyncio.create_task(keyboard_listener())
    await keyboard_listener_task  # Concurrent task

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s: %(message)s",
                        datefmt="%H:%M:%S")
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--address", help="host address", default=HOST, type=str,
                        dest="address")  # If an argument is not provided the default value is used
    parser.add_argument("-p", "--port", help="port number", default=PORT, type=int, dest="port")
    args = parser.parse_args()
    PORT = args.port
    HOST = args.address

    try:
        asyncio.run(main(HOST, PORT))
    except KeyboardInterrupt:
        logging.warning("Server stopping...")
