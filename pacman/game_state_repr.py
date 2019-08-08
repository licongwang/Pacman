class GameStateRepr:
    """
    A game state representation specifies information of a game state, providing methods to access
    available Pacman/Ghost action under the state.
    """

    def __init__(self, game_state):
        self.pacman_vulnerable = game_state.is_pacman_invulnerable()
        self.pacman_action = game_state.get_pacman_available_action()
        self.ghost_action = game_state.get_ghost_available_action()

    def get_pacman_action(self):
        return self.pacman_action

    def get_ghost_action(self):
        return self.ghost_action

    def get_action(self, agent='pacman'):
        if agent == 'pacman':
            return self.get_pacman_action()
        elif agent == 'ghost':
            return self.get_ghost_action()


class SimpleGameStateRepr(GameStateRepr):
    """
    A simple game state representation includes symbolized virtual representation of the game map,
    plus hidden status such as whether the Pacman is invulnerable.

    Learning agents may use this as the state during the learning process.
    """

    def __init__(self, game_state):
        super().__init__(game_state)
        self.state_repr = str(game_state.map_repr_list)

    def __eq__(self, other):
        if not isinstance(other, SimpleGameStateRepr):
            return False
        return self.state_repr == other.state_repr and self.pacman_vulnerable == other.pacman_vulnerable

    def __hash__(self):
        return hash(self.state_repr)


class FeatureGameStateRepr(GameStateRepr):
    def __init__(self, game_state):
        super().__init__(game_state)

    def __eq__(self, other):
        if not isinstance(other, FeatureGameStateRepr):
            return False
        pass

    def __hash__(self):
        pass
