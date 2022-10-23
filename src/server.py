import socket
import numpy as np
import xmlrpc.server
import pickle
from player import Player
from payload import Payload
from room import Room
from _thread import *

host = '127.0.0.1'
port = 1234
current_player = 0
matrix = np.zeros((15,15))

client_list = []
room_list = [Room()]*10
index_room = 0

def connection_handler(player, index_room):
    
    room = room_list[index_room]

    while True:
        data = player.connection.recv(4096)
        serialized_data = pickle.loads(data)
        print(len(data))
        if serialized_data.message == 'BYE':
            break
        
        if serialized_data.user_name == room.player1.user_name:
            client_list[room.player2.index].sendall(data)

        if serialized_data.user_name == room.player2.user_name:
            client_list[room.player1.index].sendall(data)

        print('Player: ' + str(player.user_name))

    player.connection.sendall(str.encode("CLOSE"))
    player.connection.close()

'''socket
def accept_connection(socket, current_player):
    global index_room
    client, addr = socket.accept()
    print(f'Connected to: {addr[0]}:{addr[1]}')
    client_list.append(client)
    user_name = client.recv(4096).decode('utf-8')
    client.sendall(str.encode(f"Connected to server"))
    print('User connected: ' + user_name)
    player = Player(client, user_name, current_player)

    if room_list[index_room].is_full:
        index_room+=1
        room_list[index_room] = Room()

    if room_list[index_room].player1 == None:
        room_list[index_room].player1 = player
    elif room_list[index_room].player2 == None:
        room_list[index_room].player2 = player

    start_new_thread(connection_handler, (player, index_room))'''


def define_player_number():
    current_player = current_player + 1
    return current_player

def update_matrix(player, coord):
    matrix[coord.x,coord.y] = player

    if player == 1:
        current_player = 2
    else:
        current_player = 1

    return 2

def get_matrix(player):
    if player == current_player:
        return 2
    else:
        return None

def start_server(host, port):
    server = xmlrpc.server.SimpleXMLRPCServer(("localhost", port ))

    server.register_function(define_player_number, "define_player_number")
    server.register_function(update_matrix, "update_matrix")
    server.register_function(get_matrix, "get_matrix")

    print('Server listening at port ' + str(port))

    server.serve_forever()

start_server(host, port)
