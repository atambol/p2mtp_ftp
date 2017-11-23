import sys
import socket
from utils import *
import random
import os


def probabilistic_loss_service():
    rand = random.randint(0, len(probability_matrix)-1)
    return probability_matrix[rand]


def p2mp_ftp_receive():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_sock.settimeout(timeout)
    server_sock.bind(("localhost", int(port)))
    while True:
        data, address = server_sock.recvfrom(socket_buffer*8)
        pdu = ReceivePDU(data)
        received = probabilistic_loss_service()
        if not received:
            print "Packet #%05d : Lost" % pdu.sequence_number
            continue
        else:
            print "Packet #%05d : Received" % pdu.sequence_number
        if pdu.checksum_valid():
            f = open(file_path, 'ab')
            f.write(pdu.payload)
            f.close()
            ack = SendPDU("", 'ack', pdu.sequence_number)
            server_sock.sendto(ack.encode(), address)


socket_buffer = 1024 + 64
script_name, file_path, probability, port = sys.argv
if os.path.isfile(file_path):
    os.remove(file_path)
probability = float(probability)
assert 1.0 > probability > 0.0, 'probability should be within open interval (0,1)'
probability_matrix = [True]*int(probability*100) + [False]*(100-int(probability*100))
timeout = 60
sequence_number = 0
p2mp_ftp_receive()

