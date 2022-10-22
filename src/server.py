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
