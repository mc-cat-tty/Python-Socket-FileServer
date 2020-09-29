import os
from datetime import date
import socket
import logging
from ProtocolImplementation.Protocol import DIMBYTESNUM, BUFFSIZENUM, CODEBYTES, StatusHandler
from typing import BinaryIO
import threading


class ProtocolHandler:
    def __init__(self, s: socket):
        self.s: socket = s
        self.status_handler = StatusHandler(self.s)

    def close_connection(self):
        self.s.close()
        logging.info(f"Connection closed on {threading.current_thread().getName()}")

    def get_input(self, text):
        self.status_handler.input()
        self.s.sendall(text.encode())
        data = self.s.recv(CODEBYTES)
        # logging.debug(data)
        if not self.status_handler.is_code("OK", data):
            raise ConnectionError("Client not confirming")

        data = self.s.recv(CODEBYTES)
        # logging.debug(data)
        if not self.status_handler.is_code("Response", data):
            raise ConnectionError("Client not responding")
        data = self.s.recv(BUFFSIZENUM).decode().strip()
        if not data:
            self.close_connection()
        else:
            self.status_handler.ok()
            self.status_handler.end()
        return data

    def send_output(self, text):
        self.status_handler.output()
        self.s.sendall(text.encode())
        if not self.status_handler.is_code("OK", self.s.recv(CODEBYTES)):
            raise ConnectionError("Client not confirming")
        self.status_handler.end()

    def get_file(self, file: BinaryIO, filename):
        self.status_handler.get_bytes()
        self.s.sendall(filename.encode())
        data = self.s.recv(CODEBYTES)
        if self.status_handler.is_code("FileTooLarge", data):
            raise BufferError("File too large")
        elif self.status_handler.is_code("FileNotFound", data):
            raise FileNotFoundError("File not found")
        elif not self.status_handler.is_code("OK", data):
            raise ConnectionError("Client not confirming")
        dim = int.from_bytes(self.s.recv(DIMBYTESNUM), 'big')
        received = 0
        while received < dim:
            data = self.s.recv(dim-received)
            file.write(data)
            received += len(data)
        # while dim > BUFFSIZENUM:
        #     data = self.s.recv(BUFFSIZENUM)
        #     file.write(data)
        #     dim -= len(data)
        # file.write(self.s.recv(dim))
        # logging.debug(file.tell())
        # logging.debug(original_dim)
        if file.tell() != dim:
            self.status_handler.error_file_recv_incomplete()
            raise ConnectionError("FileRecvIncomplete")
        else:
            logging.info("File received")
            self.status_handler.ok()
        self.status_handler.end()

    def send_file(self, file, filename):
        self.status_handler.ok()
        self.s.sendall(filename.encode())
        if not self.status_handler.is_code("OK", self.s.recv(CODEBYTES)):
            raise ConnectionError("Client not confirming")
        self.s.sendall(os.path.getsize(file.name).to_bytes(DIMBYTESNUM, 'big'))
        self.s.sendall(file.read())
        data = self.s.recv(CODEBYTES)
        if self.status_handler.is_code("FileRecvIncomplete", data):
            raise ConnectionError("Connection error, file incomplete")
        elif not self.status_handler.is_code("OK", data):
            raise ConnectionError("Server not confirming")
        if not self.status_handler.is_code("End", self.s.recv(CODEBYTES)):
            raise ConnectionError("Server not ending")


class FileHandler:
    def __init__(self, name, surname, s: socket):
        self.name = name
        self.surname = surname
        self.path = os.path.join(os.getcwd(), f"{name}_{surname}")
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        self.s = s
        self.protocol_handler = ProtocolHandler(self.s)
        self.status_handler = StatusHandler(self.s)

    def filename_builder(self, filename):
        filename = os.path.basename(filename)
        filename, extension = os.path.splitext(filename)
        new_name = f"{date.today().strftime('%Y-%m-%d')}_{self.surname}_{self.name}_{filename}"
        n = 1
        while os.path.exists(os.path.join(self.path, new_name + extension)):
            new_name = f"{date.today().strftime('%Y-%m-%d')}_{self.surname}_{self.name}_{filename}_{n}"
            n += 1
        return os.path.join(self.path, new_name + extension)

    def upload(self, filename_orig):
        filename = self.filename_builder(filename_orig)
        with open(filename, 'wb') as file:
            try:
                self.protocol_handler.get_file(file, filename_orig)
            except:
                logging.error("FileWriteError")
            else:
                logging.info(f"File received: {filename}")

    def download(self, filename):
        self.status_handler.send_bytes()
        if os.path.exists(os.path.join(os.getcwd(), f"{self.name}_{self.surname}", filename)):
            with open(os.path.join(os.getcwd(), f"{self.name}_{self.surname}", filename), 'rb') as file:
                try:
                    self.protocol_handler.send_file(file, filename)
                except:
                    logging.error("FileWriteError")
                else:
                    logging.info(f"File sent: {filename}")
        else:
            self.status_handler.error_file_not_found()
