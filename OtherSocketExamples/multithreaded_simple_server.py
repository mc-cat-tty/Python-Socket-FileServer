from socket import socket, AF_INET, SOCK_STREAM
import threading
import logging
import argparse

"""
Connect to this server using netcat or similar utilities
"""

# '0': Return the remote address (client) to which the socket is connected;
# '1': Return the server socket's own address;
# '2': Return the current thread name;
# '3': Return the number of alive threads;
# '4': Return the list of names of alive threads (comma separated);
# 'q': Quit server when all the clients will be disconnected;

HOST, PORT = "127.0.0.1", 9999
s = socket(AF_INET, SOCK_STREAM)


def client_handle(conn, addr):
    logging.info(f"New connection {addr}")
    while True:
        conn.sendall(">> ".encode())
        try:
            data = conn.recv(1024).decode()  # command
        except ConnectionResetError:
            logging.error(f"Closed connection - Reset Connection Error: {addr}")
            break
        cmd = data[0]
        logging.debug(f"Received: {cmd}")
        if not cmd: break
        if cmd == '0':
            conn.sendall(f"Client address: {addr}\n".encode())
        elif cmd == '1':
            conn.sendall(f"Server address: {s.getsockname()}\n".encode())
        elif cmd == '2':
            conn.sendall(f"Current thread name: {threading.current_thread().getName()}\n".encode())
        elif cmd == '3':
            conn.sendall(f"Alive threads number: {threading.active_count()}\n".encode())
        elif cmd == '4':
            conn.sendall(f"Alive threads: {[t.getName() for t in threading.enumerate()]}\n".encode())
        elif cmd == 'q':
            break
        else:  # Help
            conn.sendall("""'0': Return the remote address (client) to which the socket is connected;
'1': Return the server socket’s own address;
'2': Return the current thread name;
'3': Return the number of alive threads;
'4': Return the list of names of alive threads (comma separated);
'q': Quit server when all the clients will be disconnected;
""".encode())

    conn.close()
    logging.info(f"Connection closed by client {addr}")


def server_loop(s):
    client_id = 1
    while True:
        logging.info("Waiting for new connection")
        conn, addr = s.accept()
        handle_thread = threading.Thread(target=client_handle, args=(conn, addr), daemon=True)
        handle_thread.setName(f"client_{client_id}")
        handle_thread.start()
        client_id += 1


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
    s.bind((HOST, PORT))
    s.listen(5)
    logging.info(f"Server running on {HOST}:{PORT}...")
    server = threading.Thread(target=server_loop, args=(s,), daemon=True)
    server.setName("server")
    server.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        logging.warning("Server stopping...")
    finally:
        s.close()


if __name__ == "__main__":
    main()
