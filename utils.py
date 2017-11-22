class PDU:
    crc_order = 16
    sequence_counter = 0
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

    def __init__(self):
        self.payload = ''
        self.packet_category = ''
        self.sequence_number = None
        self.b_payload = ''
        self.b_sequence_number = ''
        self.b_packet_category = ''
        self.checksum = ''

    @staticmethod
    def binary_addition(b1, b2):
        if len(b1) == PDU.crc_order and len(b2) == PDU.crc_order:
            bsum = ["0"] * PDU.crc_order
            carry = "0"
            for i in range(PDU.crc_order - 1, -1, -1):
                bsum[i], carry = PDU.addition_map[b1[i]][b2[i]][carry]
            if carry == "1":
                carry = ["0"] * PDU.crc_order
                carry[-1] = "1"
                return PDU.binary_addition(bsum, carry)
            else:
                return bsum
        else:
            raise Exception("binary_addition failed as the bits were not of length %s" % PDU.crc_order)

    # data is a binary string of length of multiple of crc_order
    def calculate_checksum(self, data):
        checksum = '0'*PDU.crc_order
        for offset in range(len(data)/PDU.crc_order):
            two_bytes = data[offset * PDU.crc_order:(offset + 1) * PDU.crc_order]
            checksum = self.binary_addition(two_bytes, checksum)
        for i in range(len(checksum)):
            if checksum[i] == "0":
                checksum[i] = "1"
            else:
                checksum[i] = "0"
        return "".join(checksum)

    def display(self):
        print "Sequence number  : %s\n" \
              "Packet Category  : %s\n" \
              "Payload          : %s\n\n" % \
              (self.sequence_number, self.packet_category, self.payload)

    def encode(self):
        return "".join([self.b_sequence_number, self.b_packet_category, self.checksum, self.b_payload])


class SendPDU(PDU):
    # data : chunk of file of size MSS
    # category : 'data' or 'ack'
    def __init__(self, data, category, sequence_number=None):
        PDU.__init__(self)
        self.payload = data
        self.packet_category = category
        if sequence_number is None:
            self.sequence_number = self.get_sequence_number()
        else:
            self.sequence_number = sequence_number
        self.b_payload = self.get_b_payload()
        self.b_sequence_number = '{:032b}'.format(self.sequence_number)
        self.b_packet_category = self.get_b_packet_category()

        self.checksum = self.calculate_checksum(self.b_sequence_number + self.b_packet_category + self.b_payload)

    def get_b_payload(self):
        return ''.join('{0:08b}'.format(ord(x), 'b') for x in self.payload)

    def get_sequence_number(self):
        try:
            PDU.sequence_counter += 1
        except Exception:
            PDU.sequence_counter = 1
        return PDU.sequence_counter

    def get_b_packet_category(self):
        if self.packet_category == "data":
            return '0101010101010101'
        elif self.packet_category == "ack":
            return '1010101010101010'
        else:
            raise Exception("Invalid packet category '%s'" % self.packet_category)


class ReceivePDU(PDU):
    # data : chunk of file of size MSS
    # category : 'data' or 'ack'
    def __init__(self, data):
        PDU.__init__(self)
        self.validate_checksum(data)

        self.b_sequence_number = data[:32]
        self.b_packet_category = data[32:48]
        self.checksum = data[48:64]
        self.b_payload = data[64:]

        self.payload = self.get_payload()
        self.packet_category = self.get_packet_category()
        self.sequence_number = self.get_sequence_number()

    def get_payload(self):
        payload = ""
        for offset in range(len(self.b_payload)/8):
            byte = self.b_payload[offset*8:(offset+1)*8]
            payload += chr(int(byte, 2))
        return payload

    def get_sequence_number(self):
        return int(self.b_sequence_number, 2)

    def get_packet_category(self):
        if self.b_packet_category == '0101010101010101':
            return "data"
        elif self.b_packet_category == '1010101010101010':
            return "ack"
        else:
            raise Exception("Invalid packet category '%s'" % self.b_packet_category)

    def validate_checksum(self, data):
        checksum = self.calculate_checksum(data)
        print(checksum)
