from functions import millis


class ServoDataStream:

    do_stream = True
    period = 1000  # How often, in ms, to send a packet
    last_packet_time = 0

    def __init__(self, conn, dog):
        self.dog = dog
        self.conn = conn

    def update_data_sources(self):
        cur_millis = millis()
        if self.last_packet_time + self.period < cur_millis:
            
            # create the packet
            packet = ServoDataPacket(self.dog)

            # send the packet
            self.conn.sendall(bytes(packet))

            # update the time the last packet was sent
            self.last_packet_time = cur_millis


    def send_packet(self):
        pass

class ServoDataPacket:

    def __init__(self, dog):
        HEADER = b'SD'                                  # 2 bytes for type.  SD  = Servo Data
        TIMESTAMP = int(millis()).to_bytes(6, 'big')    # 6 bytes for timestamp.  Big endian.
        DATA = bytes(dog.servos)
        DATA_LEN = len(DATA).to_bytes(2, 'big')         # 2 bytes for DATA size.  Big endian.

        self.packet_buff = HEADER + TIMESTAMP + DATA_LEN + DATA + b'\x00'  # Send an empty byte at the end.

    def __bytes__(self):
        return self.packet_buff

    


