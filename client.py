import socket
from ProtocolImplementation.ClientProtocolImplementation.ClientProtocol import CODEBYTES, FileHandler, ProtocolHandler, StatusHandler
import argparse

class UserHandler:
    def __init__(self, s: socket):
        self.s = s

    def start(self):
        status_handler = StatusHandler(self.s)
        file_handler = FileHandler(self.s)
        protocol_handler = ProtocolHandler(self.s)
        while True:
            data = self.s.recv(CODEBYTES)
            if status_handler.is_code("Input", data):
                protocol_handler.input()
            elif status_handler.is_code("Output", data):
                protocol_handler.output()
            elif status_handler.is_code("GetBytes", data):
                file_handler.upload()
            elif status_handler.is_code("SendBytes", data):
                file_handler.download()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--address", help="host address", default=None, type=str, dest="address")
    parser.add_argument("-p", "--port", help="port number", default=None, type=int, dest="port")
    args = parser.parse_args()
    ip = args.address
    port = args.port
    try:
        if not ip:
            ip = input("Ip address: ")
        if not port:
            port = input("Port: ")
    except KeyboardInterrupt:
        print("\n\nExiting...")
        exit()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        print(f"Connected to {s.getsockname()}")
        user_handler = UserHandler(s)
        user_handler.start()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    finally:
        s.close()


if __name__ == "__main__":
    main()