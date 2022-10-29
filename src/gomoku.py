import pygame
import itertools
import pickle
import re
import time
import numpy as np
import threading

from _thread import *
import xmlrpc.client
from queue import Queue

tasks = Queue()


class Colors:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    YELLOW = (249, 183, 73)


class Gomoku:

    def __init__(self):
        
        self.server = xmlrpc.client.ServerProxy('http://localhost:1234', allow_none=True)
        self.player_number = self.server.define_player_number()
        print(f"Receive player number {self.player_number}")

        self.rows = 16
        self.cols = 16
        self.size = 40
        self.piece_size = 15
        self.w = self.size * self.cols
        self.h = self.size * self.rows
        self.free_slots = np.zeros((self.rows, self.cols))
        self.game_over = False

        pygame.init()
        pygame.display.set_caption('Gomoku')

        self.screen = pygame.display.set_mode((self.w, self.h))
        self.screen.fill(Colors.WHITE)
        self.player_colors = {'w': Colors.WHITE, 'b': Colors.BLACK}

        self.start_response_thread()

    def start_response_thread(self):
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

    def draw_piece(self, player, x, y, send_move=True):
        coord = (x * self.size + self.size//2, y * self.size + self.size//2)
        x_coord = (coord[0]*self.cols-1)//self.w
        y_coord = (coord[1]*self.rows-1)//self.h

        if self.free_slots[x_coord, y_coord] != 0:
            return

        if player == 1:
            color = Colors.BLACK
        else:
            color = Colors.WHITE

        self.free_slots[x_coord, y_coord] = player
        
        pygame.draw.circle(self.screen, color, coord, self.piece_size)
        pygame.display.update()

        if self.win_play(player, x_coord, y_coord):
            self.draw_outcome(player)
            self.game_over = True
            print("WON")

        if send_move:
            self.server.update_matrix(player, (x_coord, y_coord))

    def draw_outcome(self, player):
        if player == 1:
            msg = "Blacks win!" 
        else:
            msg = "Whites win!"

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

    def win_play(self, player, x, y):

        if self.diagonal_principal(x, y, player):
            return True

        if self.diagonal_secundaria(x, y, player):
            return True

        if self.vertical(player):
            return True

        if self.horizontal(player):
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
        new_y = 0
        new_x = x + y
        vetor = []

        if new_x > 15:
            new_y = new_x - 15
            new_x = 15

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
        self.can_play = True if self.player_number == 1 else False
        while not self.game_over:
            
            if not tasks.empty():
                msg = tasks.get()
                player, coord = msg
                if player and player != self.player_number:
                    self.can_play = True
                    x, y = coord
                    self.draw_piece(player, x, y, False)
            
            for event in pygame.event.get():
                self.event_handler(event)

        self.quit_game()

    def quit_game(self):
        time.sleep(5)
        
        pygame.quit()
        exit()

    def event_handler(self, event):
        
        if self.can_play:
            if event.type == pygame.MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()

                x = x // self.size
                y = y // self.size

                self.draw_piece(self.player_number,x, y)
                self.can_play = False
        
        if event.type == pygame.QUIT:
            pygame.quit()

    def response_handler(self):
        while True:
            time.sleep(0.25)
            response = self.server.get_matrix(self.player_number)
            tasks.put(response)