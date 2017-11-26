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
    server_sock.bind(("localhost", port))
    sequence_number = 0
    while True:
        data, address = server_sock.recvfrom(socket_buffer*8)
        pdu = ReceivePDU(data)
        if probabilistic_loss() <= probability:
            # print "#%05d : Lost" % pdu.sequence_number
            print "Packet loss, sequence number = %05d" % pdu.sequence_number
            continue

        if pdu.checksum_valid():
            if (sequence_number + 1) == pdu.sequence_number:
                # print "#%05d : Received" % pdu.sequence_number
                sequence_number = pdu.sequence_number
                f = open(file_path, 'ab')
                f.write(pdu.payload)
                f.close()
                ack = SendPDU("", 'ack', pdu.sequence_number)
            else:
                # print "#%05d : Out-of-order (previous packet# #%05d)" % (pdu.sequence_number, sequence_number)
                ack = SendPDU("", 'ack', sequence_number)
            server_sock.sendto(ack.encode(), address)


socket_buffer = 2048
assert len(sys.argv) > 3, "Usage: %s server-port# file-name loss-probability" % sys.argv[0]
port, file_path, probability = int(sys.argv[1]), sys.argv[2], float(sys.argv[3])
if os.path.isfile(file_path):
    os.remove(file_path)

assert 1.0 > probability > 0.0, 'probability should be within open interval (0,1)'
timeout = 600
p2mp_ftp_receive()

