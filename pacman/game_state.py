from pacman.pac_man import Pacman
from pacman.ghost import Ghost
from pacman.game_state_repr import SimpleGameStateRepr
import math


class GameState:
    """
    A gameState specifies game state information, such as locations of the pacman, ghosts, and foods.

    The GameState is used by the GameEnv object to access state related info.
    """

    def __init__(self, width, height, map_string, pacman_player, ghost_player):
        self.width = width
        self.height = height
        self.map_string = map_string
        self.pacman_player = pacman_player
        self.ghost_player = ghost_player
        self.pacmans = []
        self.ghosts = []
        self.load_map(width, height, map_string)
        self.game_status = 'ongoing'
        self.ghost_killed_counter = 0

        self.time_count = 0
        self.score_count = 0

    def load_map(self, width, height, map_string):
        self.map_list = [[None for _ in range(width)] for _ in range(height)]
        self.map_repr_list = [[None for _ in range(width)] for _ in range(height)]
        self.static_object_list = [[None for _ in range(width)] for _ in range(height)]
        dots_counter = 0

        for k, str in enumerate(map_string):
            x, y = k % width, k // width
            if str == 'P':
                element = Pacman(self.map_list, (x, y), player_number=self.pacman_player)
                self.pacmans.append(element)
            elif str == 'M':
                element = Ghost(self.map_list, (x, y), player_number=self.ghost_player)
                self.ghosts.append(element)
                self.ghost_player = 0
            else:
                if str == '*':
                    dots_counter += 1
                element = str
                self.static_object_list[y][x] = str

            grid = GameGrid(self, (x, y), element)
            self.map_list[y][x] = grid
            self.map_repr_list[y][x] = grid.get_grid_repr()

        self.original_dots_counter = self.cur_dots_counter = dots_counter
        self.state_repr = (col.elements for row in self.map_list for col in row)

    def update(self):
        self.last_score = self.get_score()

        for pacman in self.pacmans:
            pacman.update()

        self.update_game_status()

        if not self.is_game_over():
            for ghost in self.ghosts:
                ghost.update()

        self.update_game_status()
        self.time_count += 1
        self.score_count = (- self.time_count + (self.original_dots_counter - self.cur_dots_counter) * 10 + \
                            self.ghost_killed_counter * 200) * (self.game_status != 'lose')

    def update_game_status(self):
        if all([pacman.is_dead() for pacman in self.pacmans]):
            self.game_status = 'lose'

        elif self.cur_dots_counter == 0:
            self.game_status = 'win'

    def display(self):
        for row in self.map_list:
            row_line = ''
            for col in row:
                row_line += col.__repr__()
            print(row_line + '\n' * 4)

    def get_original_dots_counter(self):
        return self.original_dots_counter

    def get_cur_dots_counter(self):
        return self.cur_dots_counter

    def get_game_status(self):
        return self.game_status

    def get_time(self):
        return self.time_count

    def get_score(self):
        return self.score_count

    def get_action_reward(self):
        return self.get_score() - self.last_score

    def get_pacman_invulnerable_time(self):
        invulnerable_time = 0
        for pacman in self.pacmans:
            invulnerable_time = max(pacman.get_invulnerable_time(), invulnerable_time)
        return invulnerable_time

    def get_state(self):
        game_state_repr = SimpleGameStateRepr(self)
        return game_state_repr

    def get_pacman_available_action(self, pacman_num=0):
        return self.pacmans[pacman_num].get_available_action()

    def get_ghost_available_action(self, ghost_num=0):
        return self.ghosts[ghost_num].get_available_action()

    def set_pacman_action(self, action, pacman_num=0):
        self.pacmans[pacman_num].set_action(action)

    def is_game_over(self):
        return self.get_game_status() != 'ongoing'

    def is_pacman_invulnerable(self):
        for pacman in self.pacmans:
            if pacman.is_invulnerable():
                return True
        return False


class GameGrid:
    """
    A GameGrid specifies the state of a single grid, including whether food/pacman/ghost exist in the grid.

    It also handles the update of the game logic inside the grid at each time step.

    The GameState class contains multiple GameGrid objects, as each corresponds to a single grid in the game map.
    """

    def __init__(self, game_state, location_index, obj):
        self.game_state = game_state
        self.x, self.y = location_index
        self.has_wall = self.has_food = self.has_powerup = self.has_pacman = self.has_ghost = False
        self.pacmans, self.ghosts = [], []
        self.add_object(obj)

    def add_object(self, obj):
        """
        Add an object from the current grid
        """
        if obj == '#':
            self.has_wall = True
        elif obj == '*':
            self.has_food = True
        elif obj == '@':
            self.has_powerup = True
        elif isinstance(obj, Pacman):
            self.has_pacman = True
            self.pacmans.append(obj)
        elif isinstance(obj, Ghost):
            self.has_ghost = True
            self.ghosts.append(obj)
        elif obj != ' ':
            raise ValueError('Undefined map object: %s' % obj)

        self.update_repr()

    def remove_object(self, obj):
        """
        Remove an object from the current grid
        """
        if obj == '#':
            self.has_wall = False
        elif obj == '*':
            self.has_food = False
        elif obj == '@':
            self.has_powerup = False
        elif isinstance(obj, Pacman):
            self.has_pacman = False
            self.pacmans.remove(obj)
        elif isinstance(obj, Ghost):
            self.has_ghost = False
            self.ghosts.remove(obj)
        elif obj != ' ':
            raise ValueError('Undefined map object: %s' % obj)

        self.update_repr()

    def update(self):
        if self.has_ghost and self.has_pacman:
            if any([pacman.is_invulnerable() for pacman in self.pacmans]):
                for ghost in self.ghosts:
                    ghost.destory()
                    self.game_state.ghost_killed_counter += 1
            else:
                for pacman in self.pacmans:
                    pacman.destory()
                    self.game_state.score = 0

        if self.has_pacman and self.has_food:
            self.has_food = False
            self.game_state.cur_dots_counter -= 1

        if self.has_pacman and self.has_powerup:
            self.has_powerup = False
            for pacman in self.pacmans:
                pacman.powerup()

        self.update_repr()

    def update_repr(self):
        self.game_state.map_repr_list[self.y][self.x] = self.get_grid_repr()

    def get_grid_repr(self):
        return self.has_wall * 1 + self.has_food * 2 + self.has_powerup * 4 + self.has_pacman * 8 + self.has_ghost * 16

    def get_closest_ghost_distance(self):
        pass

    def get_closest_food_distance(self):
        pass

    def get_closest_powerup_distance(self):
        pass
