class Agent:
    """
    The agent may be a pacman or ghost.
    This class specifies basic information and methods for an agent.
    """

    def __init__(self, game_map, location_index, player_number):
        self.label = 'A'
        self.game_map = game_map
        self.x, self.y = location_index
        self.player_number = player_number
        self.move_direction = (0, 0)
        self.dead = False

    def __repr__(self):
        return self.label

    def update(self):
        """
        Update the location of the agent according to its strategy
        """
        if not self.is_dead():
            self.get_move_direction()
            self.update_location()
            self.update_grid()

    def update_location(self):
        """
        Attempt to move the agent to its move_direction,
        will success if the next location is not a wall
        """
        if not self.is_direction_blocked(self.move_direction):
            next_x, next_y = self.x + self.move_direction[0], self.y + self.move_direction[1]
            self.game_map[next_y][next_x].add_element(self)
            self.game_map[self.y][self.x].remove_element(self)
            self.x, self.y = next_x, next_y

    def update_grid(self):
        """
        Call update on the grid which the agent is belonged to, will handle interaction between agents and
        static objects on the map
        """
        self.game_map[self.y][self.x].update()

    def get_location(self):
        return self.x, self.y

    def is_direction_blocked(self, direction):
        next_x, next_y = self.x + direction[0], self.y + direction[1]
        return self.game_map[next_y][next_x].has_wall()

    def is_dead(self):
        return self.dead

    def destory(self):
        self.dead = True
        self.game_map[self.y][self.x].remove_element(self)

    # -------------------- agent strategy --------------------

    def get_move_direction(self):
        if self.player_number != 0:
            self.get_human_move()
        else:
            self.get_random_strategy_move()

    def get_human_move(self):
        from pacman.render import get_key_commands, clear_key_commands

        direction_dict = {'Up': (0, -1), 'Down': (0, 1), 'Left': (-1, 0), 'Right': (1, 0), 'KP_Insert': (0, 0),
                          'w': (0, -1), 's': (0, 1), 'a': (-1, 0), 'd': (1, 0), 'q': (0, 0)}

        for key_command in get_key_commands(self.player_number):
            direction = direction_dict[key_command]
            if not self.is_direction_blocked(direction):
                self.move_direction = direction
                clear_key_commands(self.player_number)

    def get_random_strategy_move(self):
        import random

        possible_direction = [direction for direction in [(0, -1), (0, 1), (-1, 0), (1, 0)] if
                              not self.is_direction_blocked(direction)]

        last_direction = - self.move_direction[0], - self.move_direction[1]
        chosen_direction = [direction for direction in possible_direction if direction != last_direction]
        chosen_direction = chosen_direction if len(chosen_direction) > 0 else possible_direction
        self.move_direction = random.choice(chosen_direction)
