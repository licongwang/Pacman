from pacman.util import get_path
from pacman.game_state import GameState
from pacman.render import Render
import time


class GameEnv:
    def __init__(self, cfg):
        self.__dict__ = dict(self.__dict__, **cfg)

    def initialize_game(self):
        width, height, map_string = self.read_level(self.level)
        self.game_state = GameState(width, height, map_string, self.pacman_player, self.ghost_player)
        if self.display:
            self.render = Render(window_size=(width, height), frame_interval=0.1)
            self.render.set_game_state(self.game_state)

    def start_game(self):
        while not self.game_state.is_game_over():
            self.update()
        print('game over, you %s' % self.game_state.get_game_status())
        print('time used: %d, score: %d' % (self.game_state.get_time(), self.game_state.get_score()))
        time.sleep(10)

    def update(self):
        self.game_state.update()
        if self.display:
            self.render.update()

    # -------------------- helper methods --------------------

    def read_level(self, level):
        path = get_path('level%d.txt' % level, 'maps')
        with open(path) as f:
            map_rows = f.readlines()

        map_rows = [x.strip()[::2] for x in map_rows]
        width, height = len(max(map_rows, key=len)), len(map_rows)
        map_string = ''.join(map_rows)
        return width, height, map_string


if __name__ == '__main__':
    # player num:
    # 0 = random agent,
    # 1 = player 1,
    # 2 = player 2

    cfg = {
        'level': 2,
        'pacman_player': 1,
        'ghost_player': 0,
        'display': True,
        'display_speed': 1,
    }

    gameEnv = GameEnv(cfg)
    gameEnv.initialize_game()
    gameEnv.start_game()
