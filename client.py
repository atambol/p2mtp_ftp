import sys
import socket

addition_map = {
    "0": {
        "0": {
            "0": ["0", "0"],
            "1": ["1", "0"]
        },
        "1": {
            "0": ["1", "0"],
            "1": ["0", "1"]
        }
    },
    "1": {
        "0": {
            "0": ["1", "0"],
            "1": ["0", "1"]
        },
        "1": {
            "0": ["0", "1"],
            "1": ["1", "1"]
        }
    }
}


def binary_addition(b1, b2):
    if len(b1) == crc_order and len(b2) == crc_order:
        bsum = ["0"] * crc_order
        carry = "0"
        for i in range(crc_order - 1, -1, -1):
            bsum[i], carry = addition_map[b1[i]][b2[i]][carry]
        if carry == "1":
            carry = ["0"] * crc_order
            carry[-1] = "1"
            return binary_addition(bsum, carry)
        else:
            return bsum
    else:
        raise Exception("binary_addition failed as the bits were not of length %s" % crc_order)


class Packet:
    sequence_counter = 1

    # data : chunk of file of size MSS
    # category : 'data' or 'ack'
    def __init__(self, data, category):
        self.data = data
        self.payload = self.get_payload(data)
        self.sequence_number = self.get_sequence_number()
        self.packet_category = self.get_packet_category(category)
        self.checksum = self.get_checksum()

    def get_payload(self, data):
        return ''.join('{0:08b}'.format(ord(x), 'b') for x in self.data)

    # data is a binary string of length of multiple of crc_order
    def get_checksum(self):
        checksum = '0'*crc_order
        data = self.sequence_number + self.packet_category + self.payload
        for offset in range(len(data)/crc_order):
            two_bytes = data[offset * crc_order:(offset + 1) * crc_order]
            checksum = binary_addition(two_bytes, checksum)
        for i in range(len(checksum)):
            if checksum[i] == "0":
                checksum[i] = "1"
            else:
                checksum[i] = "0"
        return "".join(checksum)

    def get_sequence_number(self):
        try:
            self.sequence_counter += 1
        except Exception:
            self.sequence_counter = 1
        return '{:032b}'.format(self.sequence_counter)

    def get_packet_category(self, category):
        if category == "data":
            return '0101010101010101'
        else:
            return '1010101010101010'

    def display(self):
        print "Sequence number  : %s\n" \
              "Checksum         : %s\n" \
              "Packet Category  : %s\n" \
              "Payload          : %s\n" \
              "Data             : %s\n\n" % \
              (self.sequence_number, self.checksum, self.packet_category, self.payload, self.data)

    def encode(self):
        return "".join([self.sequence_number, self.checksum, self.packet_category, self.payload])


def get_file_chunks(file_path, mss):
    f = open(file_path, 'rb')
    data = f.read()
    f.close()
    offset = 0
    while offset*mss < len(data):
        yield data[offset*mss:(offset+1)*mss]
        offset += 1


def p2mp_ftp(recipients, file_chunks):
    for file_chunk in file_chunks:
        Packet(file_chunk, 'data').display()
        # for recipient in recipients:
        #     rdt_send(recipient[0], recipient[0], packet)


def rdt_send(ip, port, packet):
    data_sent = False
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(5)
    while data_sent is not True:
        try:
            client_socket.sendto(packet, (ip, port))
            packet, server = client_socket.recvfrom(socket_buffer)
            #check data for ACK
            data_sent = True
        except socket.timeout:
            print 'rdt_send timeout for %s,%s' % (ip, port)


script_name, file_path, mss = sys.argv
mss = int(mss)
crc_order = 16
timeout = 5
sequence_number = 0
socket_buffer = mss + 64

recipients = [["localhost", 7735]]

file_chunks = get_file_chunks(file_path, mss)
p2mp_ftp(recipients, file_chunks)