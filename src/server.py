import socket
import numpy as np
import xmlrpc.server
import pickle
from player import Player
from payload import Payload
from room import Room
from _thread import *

class Server:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.current_player = 0
        self.game_board = np.zeros((16,16))

    def define_player_number(self):
        self.current_player = self.current_player + 1
        return self.current_player

    def update_matrix(self, player, coord):
        print(player, coord)
        x, y = coord
        self.game_board[x,y] = player

        if player == 1:
            self.current_player = 2
        else:
            self.current_player = 1

        return self.game_board.tolist()

    def get_matrix(self, player):
        print(player)
        if player == self.current_player:
            return self.game_board.tolist()
        else:
            return None

    def start_server(self):
        self.server = xmlrpc.server.SimpleXMLRPCServer((self.host, self.port ), allow_none=True, logRequests=False)

        self.server.register_function(self.define_player_number, "define_player_number")
        self.server.register_function(self.update_matrix, "update_matrix")
        self.server.register_function(self.get_matrix, "get_matrix")

        print('Server listening at port ' + str(self.port))

        self.server.serve_forever()

host = '127.0.0.1'
port = 1234

game_server = Server(host, port)
game_server.start_server()
