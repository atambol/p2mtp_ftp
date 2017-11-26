import sys
import socket
from utils import *
import threading


def get_file_chunks(file_path, mss):
    f = open(file_path, 'rb')
    data = f.read()
    f.close()
    offset = 0
    while offset*mss < len(data):
        yield data[offset*mss:(offset+1)*mss]
        offset += 1


def p2mp_ftp_send(recipients, file_chunks):
    for file_chunk in file_chunks:
        pdu = SendPDU(file_chunk, 'data')
        threads = []
        for recipient in recipients:
            thread = threading.Thread(target=rdt_send, args=(recipient, port, pdu,))
            thread.daemon = True
            threads.append(thread)
        for thread in threads:
            thread.start()

        pdu_sent = False
        while not pdu_sent:
            pdu_sent = True
            for thread in threads:
                if thread.isAlive():
                    pdu_sent = False
                    break


def rdt_send(ip, port, pdu):
    data_sent = False
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(timeout)
    while not data_sent:
        try:
            client_socket.sendto(pdu.encode(), (ip, port))
            # print "#%05d : [%s, %s] : Sent" % (pdu.sequence_number, ip, port)
            data, server = client_socket.recvfrom(socket_buffer)
            ack = ReceivePDU(data)
            if ack.sequence_number == pdu.sequence_number:
                data_sent = True
                # print "#%05d : [%s, %s] : Acknowledged" % (ack.sequence_number, ip, port)
            # else:
            #     print "#%05d : [%s, %s] : Out-of-order acknowledgement" % (ack.sequence_number, ip, port)
        except socket.timeout:
            # print '#%05d : [%s, %s] : Acknowledgement timeout' % (pdu.sequence_number, ip, port)
            print "Timeout, sequence number = %05d" % pdu.sequence_number


assert len(sys.argv) > 4, "Usage: %s server-list server-port# file-name MSS" % sys.argv[0]
port = int(sys.argv[-3])
file_path = sys.argv[-2]
mss = int(sys.argv[-1])
recipients = [x for x in sys.argv[1:-3]]

timeout = 5
sequence_number = 0
socket_buffer = mss + 64

file_chunks = get_file_chunks(file_path, mss)
p2mp_ftp_send(recipients, file_chunks)
