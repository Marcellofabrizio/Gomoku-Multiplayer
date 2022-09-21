import pygame
import itertools

class Colors:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    YELLOW = (249, 183, 73)

class Gomoku:

    def __init__(self):
        self.rows = 16
        self.cols = 16
        self.size = 60
        self.w = self.size * self.cols 
        self.h = self.size * self.rows 

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
            print(start, end)
            pygame.draw.line(self.screen, Colors.WHITE, start, end, 3)

    def draw_background(self):
        rect = pygame.Rect(0,0,self.w,self.h)
        pygame.draw.rect(self.screen, Colors.YELLOW, rect)

    def draw_board(self):
        self.draw_background()
        self.draw_lines()
        pygame.display.update()

    def play(self):
        self.draw_board()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

