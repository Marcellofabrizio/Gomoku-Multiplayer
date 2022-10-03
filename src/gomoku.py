import pygame
import itertools
import pickle
import numpy as np
import re

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
        self.free_slots = np.zeros((self.rows, self.cols))
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

    def draw_piece(self, x, y, send_move=True):
        coord = (x * self.size + self.size//2, y * self.size + self.size//2)
        x_coord = (coord[0]*self.cols-1)//self.w
        y_coord = (coord[1]*self.rows-1)//self.h

        if self.free_slots[x_coord, y_coord] != 0:
            return

        color = Colors.WHITE if self.turn % 2 == 0 else Colors.BLACK
        self.free_slots[x_coord, y_coord] = (self.turn % 2)+1
        pygame.draw.circle(self.screen, color, coord, self.piece_size)
        pygame.display.update()

        if self.win_play(x_coord, y_coord):
            self.draw_outcome()
            print("WON")

        if send_move:
            self.conn_i.send((x_coord, y_coord), self.turn)
        self.turn += 1

    def draw_outcome(self):
        msg = "Whites win!" if self.turn % 2 == 0 else "Blacks win!"
        font_size = self.w // 10
        font = pygame.font.Font("freesansbold.ttf", font_size)
        label = font.render(msg, True, Colors.WHITE, Colors.BLACK)
        x = self.w // 2 - label.get_width() // 2
        y = self.h // 2 - label.get_height() // 2
        self.screen.blit(label, (x, y))
        pygame.display.update()

    def draw_background(self):
        rect = pygame.Rect(0, 0, self.w, self.h)
        pygame.draw.rect(self.screen, Colors.YELLOW, rect)

    def draw_board(self):
        self.draw_background()
        self.draw_lines()
        pygame.display.update()

    def serialize_board(self):
        return pickle.dumps(self.board)

    def win_play(self, x, y):
        turno = (self.turn % 2)+1

        if self.diagonal_principal(x, y, turno):
            print("funcionou principal")
            return True

        if self.diagonal_secundaria(x, y, turno):
            print("funcionou secundaria")
            return True

        if self.vertical(turno):
            print("funcionou vertical")
            return True

        if self.horizontal(turno):
            print("funcionou horizontal")
            return True

    def diagonal_principal(self, x, y, turno):
        new_x = 0
        new_y = 0
        vetor = []

        if x > y:
            new_x = x - y
        elif x < y:
            new_y = y - x

        while (new_x < 16 and new_y < 16):
            vetor.append(int(self.free_slots[new_x, new_y]))
            new_x += 1
            new_y += 1

        string_diagonal = "".join(map(str, vetor))

        retorno = re.search(str(turno) + "{5}", string_diagonal)

        return retorno != None

    def diagonal_secundaria(self, x, y, turno):
        new_x = 0
        new_y = 0
        vetor = []

        print("x", x)
        print("y", y)

        if x > y:
            new_y = x + y

        print("new x:", new_x)
        print("new y:", new_y)

        while (new_x >= 0 and new_y < 16):
            vetor.append(int(self.free_slots[new_x, new_y]))
            new_x -= 1
            new_y += 1

        string_diagonal = "".join(map(str, vetor))

        retorno = re.search(str(turno) + "{5}", string_diagonal)

        return retorno != None

    def vertical(self, turno):
        vetores = np.squeeze(np.asarray(self.free_slots))

        string_vertical = "".join(map(str, vetores))

        pattern = "(" + str(turno) + ". " + ")" + "{5}"

        retorno = re.search(pattern, string_vertical)

        return retorno != None

    def horizontal(self, turno):
        teste = np.transpose(self.free_slots)

        vetores = np.squeeze(teste)

        string_horizontal = "".join(map(str, vetores))

        pattern = "(" + str(turno) + ". " + ")" + "{5}"

        retorno = re.search(pattern, string_horizontal)

        return retorno != None

    def play(self):
        self.draw_board()
        can_play = True
        while True:

            if not tasks.empty():

                can_play = True
                msg = tasks.get()
                x, y = msg
                self.draw_piece(x, y, False)

            for event in pygame.event.get():
                if (can_play):
                    if event.type == pygame.MOUSEBUTTONUP:
                        x, y = pygame.mouse.get_pos()

                        x = x // self.size
                        y = y // self.size

                        self.draw_piece(x, y)
                        can_play = False
                if event.type == pygame.QUIT:
                    return
        if self.conn_i != None:
            self.conn_i.connection.close()

    def response_handler(self):

        while True:
            response = self.conn_i.connection.recv(4096)
            data = pickle.loads(response)
            tasks.put(data.message)
