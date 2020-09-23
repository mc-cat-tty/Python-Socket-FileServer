import socketserver
import logging
from ProtocolImplementation.ServerProtocolImplementation.ServerProtocol import FileHandler, ProtocolHandler
import socket
import os

HOST, PORT = "", 1234


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        logging.info(f"New connection {self.client_address}")
        s: socket = self.request
        protocol_handler = ProtocolHandler(s)

        name = protocol_handler.get_input("Name: ")
        if not name: return

        surname = protocol_handler.get_input("Surname: ")
        if not surname: return

        logging.info(f"Name: {name} Surname: {surname}")

        file_handler = FileHandler(name, surname, s)

        while True:
            cmd = protocol_handler.get_input(">> ")  # command
            if not cmd: break
            logging.debug(f"Received: {cmd}")

            if cmd == 'u' or cmd == 'U':
                filename = protocol_handler.get_input("Filename: ")
                if not filename: break
                logging.info(f"Upload request from {self.client_address}. File: {filename}")
                file_handler.upload(filename)
            elif cmd == 'd' or cmd == 'D':
                filename = protocol_handler.get_input("Filename: ")
                if not filename: break
                logging.info(f"Download request from {self.client_address}. File: {filename}")
                file_handler.download(filename)
            elif cmd == 'l' or cmd == 'L':
                s = "\n"
                ls = os.listdir(os.path.join(os.getcwd(), f"{name}_{surname}"))
                for ele in ls:
                    s += f"{ele}\n"
                protocol_handler.send_output(s)
            elif cmd == 'h' or cmd == 'H':
                protocol_handler.send_output("""u/U: upload
d/D: Download
l/L: List
h/H: Help
q: Exit""")
            elif cmd == 'q':
                break
            else:
                protocol_handler.send_output("Command not found")

        # s.close_connection()


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def main():
    logging.basicConfig(level=logging.DEBUG, format="%(threadName)s --> %(asctime)s - %(levelname)s: %(message)s",
                        datefmt="%H:%M:%S")
    logging.info("Server running...")
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
