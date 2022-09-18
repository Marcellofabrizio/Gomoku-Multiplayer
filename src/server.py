import socket
from _thread import *

host = '127.0.0.1'
port = 1234

client_list = []

def connection_handler(connection, player):
    
    while True:
        data = connection.recv(4096)
        message = data.decode('utf-8')
        if message == 'BYE':
            break
        
        if player == 0:
            client_list[1].sendall(str.encode('Player 0 says: ' + message))

        if player == 1:
            client_list[0].sendall(str.encode('Player 1 says: ' + message))

        reply = f'Server: {message}'
        print('Player: ' + str(player))
        connection.sendall(str.encode(reply))

    connection.close()

def accept_connection(socket, current_player):
    client, addr = socket.accept()
    print(f'Connected to: {addr[0]}:{addr[1]}')
    client_list.append(client)
    user_name = client.recv(4096).decode('utf-8')
    client.sendall(str.encode(f"Connected to server"))
    print('User connected: ' + user_name)
    start_new_thread(connection_handler, (client, current_player))

def start_server(host, port):
    current_player = 0
    serverSocket = socket.socket()
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
