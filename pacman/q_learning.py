import random
import pickle
import os
from pacman.util import get_path


class QLearning:
    def __init__(self, alpha, gamma, epsilon):
        self.alpha = alpha  # learning rate
        self.gamma = gamma  # discount rate
        self.epsilon = epsilon  # epsilon greedy rate

        self.q_table = {}

    def update_q_value(self, state, action, next_state, reward):
        cur_q_value = self.get_q_value(state, action)
        next_max_q_value = self.get_max_q_value(next_state)
        self.q_table[(state, action)] = cur_q_value + self.alpha * \
                                        (reward + self.gamma * next_max_q_value - cur_q_value)

    def get_max_q_value(self, state):
        available_action = state.get_action()
        q_values = [self.get_q_value(state, action) for action in available_action]
        return max(q_values)

    def get_q_value(self, state, action):
        q_value = self.q_table[(state, action)] if (state, action) in self.q_table else 0
        return q_value

    def get_state_chosen_action(self, state, actions):
        if random.random() < self.epsilon:
            return random.choice(actions)
        else:
            chosen_action = max(actions, key=lambda action: self.get_q_value(state, action))
            return chosen_action

    def save_model(self, map_num):
        dir = 'model/q_learning_map%d' % map_num
        model_path = get_path('q_model.pkl', dir)

        if not os.path.exists(dir):
            os.mkdir(dir)

        with open(model_path, 'wb') as f:
            pickle.dump(self.q_table, f)

    def load_model(self, map_num):
        dir = 'model/q_learning_map%d' % map_num
        model_path = get_path('q_model.pkl', dir)

        with open(model_path, 'rb') as f:
            self.q_table = pickle.load(f)