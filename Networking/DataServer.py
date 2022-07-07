import socket
from threading import Thread
from Networking.DataStream import *

host = '192.168.0.141'
#host = 'hardydog'
#port = 1241
port = 1242

def serve(dog):
    """
    Main socket server.  When a connection is made, a new thread "serve_thread" is launched.
    """

    print("Starting Socket Server")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen()
    print("Socket server is awaiting a connection...")

    while True:
        conn, addr = s.accept()
        print(f"New connection by {addr}")
        server_connection_thread = Thread(target=serve_client, daemon=True, args=(conn, addr, dog, )).start()

def serve_client(conn, addr, dog):
    """ Socket handler for each connection.  This will be launched in its own thread by serve().

    Args:
        conn: socket object
        addr: pair of (hostaddr, port)
        dog: dog object
    """

    with conn:
        
        print(f"Connected by {addr}")
        datastream = ServoDataStream(conn, dog)

        while True:
            
            if dog is None:
                # We are testing the Socket Server.
                # Bombard the socket with the 'A' character
                try:
                    conn.sendall(b'A')
                except ConnectionResetError:
                    print(f"Connection from {addr} closed")
                    conn.close()
                    exit()
                return

            datastream.update_data_sources()



if __name__ == '__main__':
    # Used to test the DataServer
   serve(None)