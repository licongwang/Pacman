from pacman.pac_man import Pacman
from pacman.ghost import Ghost
import math


class GameState:
    def __init__(self, width, height, map_string, pacman_player, ghost_player):
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
        self.map_lst = [[None for _ in range(width)] for _ in range(height)]
        self.static_object_lst = [[None for _ in range(width)] for _ in range(height)]
        dots_counter = 0

        for k, str in enumerate(map_string):
            x, y = k % width, k // width
            if str == 'P':
                element = Pacman(self.map_lst, (x, y), player_number=self.pacman_player)
                self.pacmans.append(element)
            elif str == 'M':
                element = Ghost(self.map_lst, (x, y), player_number=self.ghost_player)
                self.ghosts.append(element)
                self.ghost_player = 0
            else:
                if str == '*':
                    dots_counter += 1
                element = str
                self.static_object_lst[y][x] = str

            self.map_lst[y][x] = GameGrid(self, (x, y), element)
        self.original_dots_counter = self.cur_dots_counter = dots_counter

    def update(self):
        for pacman in self.pacmans:
            pacman.update()

        self.update_game_status()
        if self.is_game_over():
            return

        for ghost in self.ghosts:
            ghost.update()

        self.update_game_status()
        self.time_count += 1
        self.score_count = - self.time_count + (self.original_dots_counter - self.cur_dots_counter) * 10 + \
                           self.ghost_killed_counter * 200

    def update_game_status(self):
        if all([pacman.is_dead() for pacman in self.pacmans]):
            self.game_status = 'lose'
        elif self.cur_dots_counter == 0:
            self.game_status = 'win'

    def display(self):
        for row in self.map_lst:
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

    def get_pacman_invulnerable_time(self):
        invulnerable_time = 0
        for pacman in self.pacmans:
            invulnerable_time = max(pacman.get_invulnerable_time(), invulnerable_time)
        return invulnerable_time

    def is_game_over(self):
        return self.get_game_status() != 'ongoing'

    def is_pacman_invulnerable(self):
        for pacman in self.pacmans:
            if pacman.is_invulnerable():
                return True
        return False


class GameGrid:
    def __init__(self, game_state, location_index, element):
        self.game_state = game_state
        self.x, self.y = location_index
        self.elements = [element]

    def __repr__(self):
        element_str = ''.join([e.__repr__() for e in self.elements])
        element_str = element_str.replace('\'', '')

        if len(self.elements) < 5:
            left_white_space, right_white_space = ' ' * (5 - math.floor(len(self.elements) / 2)), \
                                                  ' ' * (5 - math.ceil(len(self.elements) / 2))
            output = left_white_space + element_str + right_white_space
        else:
            output = element_str
        return output

    def add_element(self, element):
        self.elements.append(element)

    def remove_element(self, element):
        if element in self.elements:
            self.elements.remove(element)

    def update(self):
        if self.has_ghost() and self.has_pacman():
            pacmans = [e for e in self.elements if isinstance(e, Pacman)]
            if any([pacman.is_invulnerable() for pacman in pacmans]):
                ghosts = [e for e in self.elements if isinstance(e, Ghost)]
                for ghost in ghosts:
                    ghost.destory()
                    self.game_state.ghost_killed_counter += 1
            else:
                for pacman in pacmans:
                    pacman.destory()

        if self.has_pacman() and self.has_food():
            self.elements.remove('*')
            self.game_state.cur_dots_counter -= 1

        if self.has_pacman() and self.has_powerup():
            self.elements.remove('@')
            pacmans = [e for e in self.elements if isinstance(e, Pacman)]
            for pacman in pacmans:
                pacman.powerup()

    def has_pacman(self):
        return any([isinstance(e, Pacman) for e in self.elements])

    def has_ghost(self):
        return any([isinstance(e, Ghost) for e in self.elements])

    def has_food(self):
        return any([e == '*' for e in self.elements])

    def has_powerup(self):
        return any([e == '@' for e in self.elements])

    def has_wall(self):
        return any([e == '#' for e in self.elements])
