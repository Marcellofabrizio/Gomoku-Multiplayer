

class Room:

    def __init__(self, player1=None, player2=None):
        self.player1 = player1
        self.player2 = player2

    @property
    def is_full(self):
        return self.player1 != None and self.player2 != None