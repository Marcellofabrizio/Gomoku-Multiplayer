import pygame
import itertools
import pickle

class Colors:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    YELLOW = (249, 183, 73)

class Gomoku:

    def __init__(self):
        self.rows = 16
        self.cols = 16
        self.size = 40
        self.piece_size = 15
        self.w = self.size * self.cols 
        self.h = self.size * self.rows 
        self.board_matrix = [[0 for _ in range(self.cols)]]*self.rows
        self.turn = 1

        pygame.init()
        pygame.display.set_caption('Gomoku')

        self.screen = pygame.display.set_mode((self.w, self.h))
        self.screen.fill(Colors.WHITE)
        self.player_colors = {'w': Colors.WHITE, 'b': Colors.BLACK}

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

    def draw_piece(self, x ,y):
        coord = (x * self.size + self.size//2, y * self.size + self.size//2)
        #print(coord)
        x_coord = (coord[0]*self.cols-1)//self.w
        y_coord = (coord[1]*self.rows-1)//self.h
        color = Colors.BLACK if self.turn%2 == 0 else Colors.WHITE
        pygame.draw.circle(self.screen, color, coord, self.piece_size)
        pygame.display.update()
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
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    x,y = pygame.mouse.get_pos()

                    x = x // self.size
                    y = y // self.size

                    self.draw_piece(x,y)
                if event.type == pygame.QUIT:
                    return
