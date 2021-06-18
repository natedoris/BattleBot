class Player:
    _player = None
    _score = 0
    _deaths = 0
    _self_destruct = 0
    nemesis = {}

    def __init__(self, player):
        self.player = player

    def add_score(self, amount):
        self._score += 1

    def deaths(self, amount):
        self._deaths += 1
