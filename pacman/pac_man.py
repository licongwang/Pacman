from pacman.agent import Agent


class Pacman(Agent):
    """
    The Pacman class specifies various status of the Pacman, including its location and whether it's vulnerable to
    ghosts.
    """

    def __init__(self, game_map, location_index, player_number=0):
        super().__init__(game_map, location_index, player_number)
        self.label = 'P'
        self.powerup_time = 40
        self.invulnerable_timer = 0

    def update(self):
        """
        Update the location of the pacman according to its strategy
        """
        if self.is_dead():
            return

        super().update()
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1

    def powerup(self):
        """
        Grant the pacman invulnerability for a period of time, according to self.powerup_time
        """
        self.invulnerable_timer = self.powerup_time

    def is_invulnerable(self):
        return self.invulnerable_timer > 0

    def get_invulnerable_time(self):
        return self.invulnerable_timer
