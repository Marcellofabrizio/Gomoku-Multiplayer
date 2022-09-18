import socket
import pickle
from _thread import *

host = '127.0.0.1'
port = 1234

def response_handler(connection):
    while True:
        response = connection.recv(4096)
        print(response.decode('utf-8'))

user_name = input('Enter your user name: ')

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print('Atempting connecting to host...')

try:
    clientSocket.connect((host, port))
except socket.error as err:
    print(str(err))

clientSocket.sendall(str.encode(user_name))

response = clientSocket.recv(4096)
print(response.decode('utf-8'))
start_new_thread(response_handler, (clientSocket,))
while True:
    msg = input()
    #payload = None
    #payload.message = msg
    #payload.user_name = user_name
    #clientSocket.send(pickle.dumps(payload))
    clientSocket.send(str.encode(msg))

clientSocket.close()
