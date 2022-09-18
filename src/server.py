import socket
import pickle
from player import Player
from payload import Payload
from room import Room
from _thread import *

host = '127.0.0.1'
port = 1234

client_list = []
room_list = [Room()]*10
index_room = 0

def connection_handler(player, index_room):
    
    room = room_list[index_room]

    while True:
        data = player.connection.recv(4096)
        serialized_data = pickle.loads(data)
        #message = data.decode('utf-8')
        if serialized_data.message == 'BYE':
            break
        
        if serialized_data.user_name == room.player1.user_name:
            client_list[room.player2.index].sendall(str.encode(f'Player {player.user_name} says: {serialized_data.message}'))

        if serialized_data.user_name == room.player2.user_name:
            client_list[room.player1.index].sendall(str.encode(f'Player {player.user_name} says: {serialized_data.message}'))

        reply = f'Server: {serialized_data.message}'
        print('Player: ' + str(player.user_name))
        player.connection.sendall(str.encode(reply))

    player.connection.close()

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

    start_new_thread(connection_handler, (player, index_room))

def start_server(host, port):
    current_player = 0
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        serverSocket.bind((host, port))
    except socket.error as err:
        print(str(err))

    print('Server listening at port ' + str(port))
    serverSocket.listen(2)

    while True:
        accept_connection(serverSocket, current_player)
        current_player += 1

start_server(host, port)
