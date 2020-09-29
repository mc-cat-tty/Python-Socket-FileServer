import socket
import argparse
import logging
from select import select
from collections import defaultdict
import threading

HOST, PORT = "127.0.0.1", 9999

def handle_command(cmd: str, sock: socket):
    # sock.sendall(">> ".encode())
    # data = sock.recv(1024).decode()  # command
    # cmd = data[0]
    logging.debug(f"Received: {cmd}")
    if not cmd: return
    if cmd == '0':  # TODO
        return f"Client address: {sock.getpeername()}\n"
    elif cmd == '1':
        return f"Socket address: {sock.getsockname()}\n"
    elif cmd == '2':
        return f"Current thread name: {threading.current_thread().getName()}\n"
    elif cmd == '3':
        return f"Alive threads number: {threading.active_count()}\n"
    elif cmd == '4':
        return f"Alive threads: {[t.getName() for t in threading.enumerate()]}\n"
    elif cmd == 'q':  # TODO
        return
    else:  # Help  # TODO
        return """'0': Return the remote address (client) to which the socket is connected;
    '1': Return the server socket's own address;
    '2': Return the current thread name;
    '3': Return the number of alive threads;
    '4': Return the list of names of alive threads (comma separated);
    'q': Quit server when all the clients will be disconnected;
    """

def server_loop(server_sock: socket):
    sock_io = list()
    data = defaultdict(bytes)
    waiting = defaultdict(bool)  # True --> waiting data from the client
    sock_io.append(server_sock)
    while True:
        # logging.info("Waiting for events")
        readable, writable, exceptional = select(sock_io, sock_io, [])
        for r in readable:
            if r is server_sock:
                conn, addr = r.accept()
                sock_io.append(conn)
                logging.info(f"New connection: {addr}")
            else:
                buf = bytes()
                try:
                    while True:
                        buf += r.recv(1024)
                except socket.error:
                    pass

                if not buf:
                    logging.warning(f"Closed connection: {r.getsockname()}")
                    r.close()
                    sock_io.remove(r)
                else:
                    data[r] = buf  # Saving data
                    waiting[r] = False
                    logging.info(f"Received {buf.decode().strip()} from {r.getsockname()}")

        for w in writable:
            if data[w]:
                logging.info(f"Consuming {data[w]}")
                w.sendall(handle_command(data[w].decode().strip(), server_sock).encode())
                del data[w]
            elif not waiting[w]:
                w.sendall(">> ".encode())
                logging.info(f"Requested command from {r.getsockname()}")
                waiting[w] = True

def main():
    global HOST, PORT
    logging.basicConfig(level=logging.DEBUG, format="%(threadName)s --> %(asctime)s - %(levelname)s: %(message)s",
                        datefmt="%H:%M:%S")
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--address", help="host address", default=HOST, type=str, dest="address")
    parser.add_argument("-p", "--port", help="port number", default=PORT, type=int, dest="port")
    args = parser.parse_args()
    PORT = args.port
    HOST = args.address
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setblocking(False)
    server_sock.bind((HOST, PORT))
    server_sock.listen(5)
    logging.info(f"Server running on {HOST}:{PORT}...")
    server = threading.Thread(target=server_loop, args=(server_sock,), daemon=True)
    server.setName("server")
    server.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        logging.warning("Server stopping...")
    finally:
        server_sock.close()


if __name__ == "__main__":
    main()