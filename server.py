import sys
import socket
from utils import *
import random
import os


def probabilistic_loss():
    return random.uniform(0, 1)


def p2mp_ftp_receive():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_sock.settimeout(timeout)
    server_sock.bind(("localhost", 7735))
    sequence_number = 0
    while True:
        data, address = server_sock.recvfrom(socket_buffer*8)
        pdu = ReceivePDU(data)
        if probabilistic_loss() <= probability:
            print "#%05d : Lost" % pdu.sequence_number
            continue

        if pdu.checksum_valid():
            if (sequence_number + 1) == pdu.sequence_number:
                print "#%05d : Received" % pdu.sequence_number
                sequence_number = pdu.sequence_number
                f = open(file_path, 'ab')
                f.write(pdu.payload)
                f.close()
                ack = SendPDU("", 'ack', pdu.sequence_number)
            else:
                print "#%05d : Out-of-order (previous packet# #%05d)" % (pdu.sequence_number, sequence_number)
                ack = SendPDU("", 'ack', sequence_number)
            server_sock.sendto(ack.encode(), address)


socket_buffer = 1024 + 64
assert len(sys.argv) > 2, "Usage: %s <file path> <PDU loss probability>" % sys.argv[0]
file_path, probability = sys.argv[1], sys.argv[2]
if os.path.isfile(file_path):
    os.remove(file_path)
probability = float(probability)
assert 1.0 > probability > 0.0, 'probability should be within open interval (0,1)'
timeout = 600
p2mp_ftp_receive()

