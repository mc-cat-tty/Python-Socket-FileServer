import socket
from ProtocolImplementation.ClientProtocolImplementation.ClientProtocol import CODEBYTES, FileHandler, ProtocolHandler, StatusHandler

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
    ip, port = input("Ip address: "), input("Port: ")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        print(f"Connected to {s.getsockname()}")
        user_handler = UserHandler(s)
        user_handler.start()
    finally:
        s.close()


if __name__ == "__main__":
    main()