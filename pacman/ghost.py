from pacman.agent import Agent


class Ghost(Agent):
    """
    The Ghost class specifies various status of the ghost, including the location and a respawn timer
    """

    def __init__(self, game_map, location_index, player_number=0):
        super().__init__(game_map, location_index, player_number)
        self.initial_x, self.initial_y = location_index
        self.label = 'M'
        self.respawn_time = 30
        self.respawn_timer = 0

    def update(self):
        """
        Update the location of the ghost according to its strategy
        """
        super().update()
        if self.is_dead():
            self.respawn_timer = self.respawn_time if self.respawn_timer == 0 else self.respawn_timer - 1
            if self.respawn_timer == 0:
                self.respawn()

    def respawn(self):
        """
        When the respawn timer reaches 0, the ghost will respawn at its initial location
        """
        self.dead = False
        self.x, self.y = self.initial_x, self.initial_y
        self.game_map[self.y][self.x].add_element(self)
