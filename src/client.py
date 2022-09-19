import socket
import pickle
from payload import Payload
from _thread import *

host = '127.0.0.1'
port = 1234

def response_handler(connection):
    while True:
        response = connection.recv(4096)
        if response == 'CLOSE':
            exit(0)
        else:
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
    payload = Payload(user_name, msg)
    clientSocket.send(pickle.dumps(payload))
    #clientSocket.send(str.encode(msg))

clientSocket.close()
