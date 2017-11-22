import sys
import socket
from utils import *


def p2mp_ftp_receive():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("localhost", 7735))
    while True:
        data, address = sock.recvfrom(socket_buffer)
        pdu = ReceivePDU(data)
        f = open(file_path, 'ab')
        f.write(pdu.payload)
        f.close()
        ack = SendPDU("", 'ack', pdu.sequence_number)
        sock.sendto(ack.encode(), address)


socket_buffer = 1024 + 64
script_name, file_path = sys.argv
timeout = 5
sequence_number = 0
p2mp_ftp_receive()

