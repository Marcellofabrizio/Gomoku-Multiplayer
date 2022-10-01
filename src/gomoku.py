import pygame
import itertools
import pickle
import numpy as np

from _thread import *
from queue import Queue
import threading

tasks = Queue()

class Colors:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    YELLOW = (249, 183, 73)

class Gomoku:

    def __init__(self, connection=None):

        self.conn_i = connection

        self.rows = 16
        self.cols = 16
        self.size = 40
        self.piece_size = 15
        self.w = self.size * self.cols 
        self.h = self.size * self.rows 
        self.free_slots = np.zeros((self.rows,self.cols))
        self.turn = 1

        pygame.init()
        pygame.display.set_caption('Gomoku')

        self.screen = pygame.display.set_mode((self.w, self.h))
        self.screen.fill(Colors.WHITE)
        self.player_colors = {'w': Colors.WHITE, 'b': Colors.BLACK}

        response_thread = threading.Thread(target=self.response_handler)
        response_thread.start()

    def row_lines(self):
        half_size = self.size//2
        
        for y in range(half_size, self.h - half_size + self.size, self.size):
            yield (half_size, y), (self.w-half_size, y)

    def col_lines(self):
        half_size = self.size//2

        for x in range(half_size, self.w - half_size + self.size, self.size):
            yield (x, half_size), (x, self.h-half_size)

    def draw_lines(self):
        lines = itertools.chain(self.row_lines(), self.col_lines()) 

        for start, end in lines:
            pygame.draw.line(self.screen, Colors.WHITE, start, end, 3)

    def draw_piece(self, x ,y, send_move = True):
        coord = (x * self.size + self.size//2, y * self.size + self.size//2)
        x_coord = (coord[0]*self.cols-1)//self.w
        y_coord = (coord[1]*self.rows-1)//self.h

        for i in range(len(self.free_slots)):
            print(self.free_slots[i])
        print()

        if self.free_slots[x_coord, y_coord] != 0:
            return

        color = Colors.BLACK if self.turn%2 == 0 else Colors.WHITE
        self.free_slots[x_coord, y_coord] = (self.turn%2)+1
        pygame.draw.circle(self.screen, color, coord, self.piece_size)
        pygame.display.update()
        
        if send_move:
            self.conn_i.send((x_coord, y_coord), self.turn)
        self.turn += 1

    def draw_background(self):
        rect = pygame.Rect(0,0,self.w,self.h)
        pygame.draw.rect(self.screen, Colors.YELLOW, rect)

    def draw_board(self):
        self.draw_background()
        self.draw_lines()
        pygame.display.update()
    
    def serialize_board(self):
        return pickle.dumps(self.board)

    def play(self):
        self.draw_board()
        while True:

            if not tasks.empty():
                x,y = tasks.get()
                self.draw_piece(x,y,False)

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    x,y = pygame.mouse.get_pos()

                    x = x // self.size
                    y = y // self.size

                    self.draw_piece(x,y)
                if event.type == pygame.QUIT:
                    return
        if self.conn_i != None:
            self.conn_i.connection.close()


    def response_handler(self):
        
        while True:
            response = self.conn_i.connection.recv(4096)
            data = pickle.loads(response)
            tasks.put(data.message)
