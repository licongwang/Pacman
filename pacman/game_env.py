import time
from pacman.util import get_path
from pacman.game_state import GameState
from pacman.render import Render
from pacman.q_learning import QLearning


class GameEnv:
    """
    A game environment reads the config setting, then initialize state and display of the game.

    The class also provides methods for accessing game state information and taking actions.
    """

    def __init__(self, cfg):
        self.level = cfg['level']
        self.pacman_player = cfg['pacman_player']
        self.ghost_player = cfg['ghost_player']
        self.display = cfg['display']
        self.display_speed = cfg['display_speed']
        self.has_learning_agent = False

    def initialize_game(self):
        width, height, map_string = read_level(self.level)
        self.game_state = GameState(width, height, map_string, self.pacman_player, self.ghost_player)
        if self.display:
            self.render = Render(window_size=(width, height), frame_interval=0.1)
            self.render.set_game_state(self.game_state)

    def start_game(self):
        while not self.game_state.is_game_over():
            if self.has_learning_agent:
                state = self.game_state.get_state()
                actions = state.get_pacman_action()
                chosen_action = self.learning_agent.get_state_chosen_action(state, actions)
                self.game_state.set_pacman_action(chosen_action)

                self.update()

                next_state = self.game_state.get_state()
                reward = self.game_state.get_action_reward()

                self.learning_agent.update_q_value(state, chosen_action, next_state, reward)
            else:
                self.update()

        # print('game over, you %s' % self.game_state.get_game_status())
        # print('time used: %d, score: %d' % (self.game_state.get_time(), self.game_state.get_score()))
        # time.sleep(10)

    def set_learning_agent(self, learning_agent):
        self.has_learning_agent = True
        self.learning_agent = learning_agent

    def update(self):
        self.game_state.update()
        if self.display:
            self.render.update()

    def get_state(self):
        pass


# -------------------- helper methods --------------------

def read_level(level):
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
    # 2 = player 2,
    # 3 = Q learning agent

    cfg = {
        'level': 1,
        'pacman_player': 3,
        'ghost_player': 0,
        'display': False,
        'display_speed': 1,
    }

    alpha, gamma, epsilon = 1, 0.9, 0.00

    # training model
    t = time.time()
    q_learning = QLearning(alpha, gamma, epsilon)
    q_learning.load_model(cfg['level'])
    total_wins, total_score = 0, 0

    for i in range(10000):
        gameEnv = GameEnv(cfg)
        gameEnv.initialize_game()
        gameEnv.set_learning_agent(q_learning)
        gameEnv.start_game()

        total_wins += gameEnv.game_state.get_game_status() == 'win'
        total_score += gameEnv.game_state.get_score()

        print('train num:', i + 1, 'win rate:', total_wins / (i + 1), 'avg score:', total_score / (i + 1),
              len(q_learning.q_table))

    q_learning.save_model(map_num=cfg['level'])
    print(time.time() - t)

    # playing
    cfg = {
        'level': 1,
        'pacman_player': 3,
        'ghost_player': 0,
        'display': True,
        'display_speed': 1,
    }
    q_learning = QLearning(alpha, gamma, epsilon)
    q_learning.load_model(map_num=cfg['level'])
    q_learning.epsilon = 0

    gameEnv = GameEnv(cfg)
    gameEnv.initialize_game()
    gameEnv.set_learning_agent(q_learning)
    gameEnv.start_game()
