from connection_interface import Connection
from gomoku import Gomoku

conn_i = Connection()
game = Gomoku(conn_i)
game.play()
