import os
import socket

DIMBYTESNUM = 4
BUFFSIZENUM = 1024  # bytes
CODEBYTES = 1

ProtocolCodes = {  # 1 byte long codes
    # Error codes
    "FileRecvIncomplete": b'\x00',
    "FileWriteError": b'\x01',
    "FileTooLarge": b'\x02',
    "FileNotFound": b'\x03',

    # Standard codes
    "OK": b'\x10',
    "Input": b'\x11',  # Start Input
    "Output": b'\x12',  # Start Output
    "Response": b'\x13',  # Start Response
    "End": b'\x14',
    "SendBytes": b'\x15',
    "GetBytes": b'\x16',
    }


class StatusHandler:
    Codes = ProtocolCodes

    def __init__(self, s: socket):
        self.s = s

    def is_code(self, codename, value):  # Check if 'value' is equal to the code associated with codename
        if value == ProtocolCodes[codename]:
            return True
        else:
            return False

    def __send_code(self, codename):
        self.s.sendall(ProtocolCodes[codename])

    def ok(self):
        self.__send_code("OK")

    def input(self):
        self.__send_code("Input")

    def output(self):
        self.__send_code("Output")

    def response(self):
        self.__send_code("Response")

    def end(self):
        self.__send_code("End")

    def send_bytes(self):
        self.__send_code("SendBytes")

    def get_bytes(self):
        self.__send_code("GetBytes")

    def error_file_recv_incomplete(self):
        self.__send_code("FileRecvIncomplete")

    def error_file_write_error(self):
        self.__send_code("FileWriteError")

    def error_file_too_large(self):
        self.__send_code("FileTooLarge")

    def error_file_not_found(self):
        self.__send_code("FileNotFound")
