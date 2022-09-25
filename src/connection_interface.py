import socket
import pickle
from gomoku import Gomoku
from payload import Payload

from random import randint
from _thread import *

host = '127.0.0.1'
port = 1234

class Connection:

    def __init__(self):
        self.host = host
        self.port = port
        self.connection = self.create_socket()
        self.player_name = 'Player ' + str(randint(0, 100))
        self.start_connection()

    def create_socket(self):
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start_connection(self):
        print('Trying to connect to host...')

        try:
            self.connection.connect((self.host, self.port))
        except socket.error as err:
            print(str(err))
            exit()

        self.connection.sendall(str.encode(self.player_name))
        response = self.connection.recv(4096)
        print(response.decode('utf-8'))
        start_new_thread(self.response_handler, ())
    
    def response_handler(self):
        
        while True:
            response = self.connection.recv(4096)
            data = pickle.loads(response)
            print(data.message)

    def send(self, board_matrix, turn):
        payload = Payload(self.player_name, board_matrix, turn)
        self.connection.send(pickle.dumps(payload))

