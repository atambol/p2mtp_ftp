import socket
import os
import math


class Segment:
    sequence_number = 0

    def __init__(self, data, ack):
        self.data = data
        self.sequence_number = self.get_sequence_number_field()
        self.packet_type = self.get_packet_type_field(ack)
        self.checksum = self.get_checksum_field()

    def display(self):
        print "Sequence Number : " + self.sequence_number
        print "Packet Type : " + self.packet_type
        print "Data : " + self.data
        print "Checksum : " + self.checksum

    @staticmethod
    def get_packet_type_field(ack):
        if ack:
            return b'1010101010101010'
        else:
            return b'0101010101010101'

    @staticmethod
    def get_data_field(data):
        return ''.join(format(b, 'b') for b in bytearray(data))

    @staticmethod
    def get_sequence_number_field():
        Segment.sequence_number += 1
        return format(Segment.sequence_number, '032b')

    def get_checksum_field(self):
        checksum = 0
        for offset in range(int(math.ceil(len(self.data)/16))):
            checksum += int(self.data[offset*16:(offset+1)*16])
        return format(checksum, '016b')

    def encode(self):
        return self.sequence_number + self.packet_type + self.checksum + self.data


def read_file_in_chunks(input_file_path, chunk_size):
    f = open(input_file_path, 'rb')
    data = f.read()
    f.close()
    offset = 0
    while offset*chunk_size < len(data):
        yield data[offset*chunk_size:(offset+1)*chunk_size]
        offset += 1


def rdt_send(file_chunks):
    for file_chunk in file_chunks:
        segment = Segment(data=file_chunk, ack=False)
        segment.display()


def main():
    file_chunks = read_file_in_chunks(input_file, mss)
    rdt_send(file_chunks)

# Start
project_path = os.path.dirname(os.path.realpath(__file__))
mss = 1024  # read from CMD
input_file = os.path.join(project_path, "e_mc2.pdf")
output_file = os.path.join(project_path, "output.pdf")
if __name__ == "__main__":
    main()
