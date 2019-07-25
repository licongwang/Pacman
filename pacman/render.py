import tkinter

pacman_color = {
    0: 'yellow',
    1: 'dark cyan',
}

ghost_color = {
    0: 'red',
    1: 'pink',
    2: 'cyan',
    3: 'orange'
}


class Render:
    def __init__(self, window_size, frame_interval=0.1):
        self.grid_size = 30
        self.w, self.h = map(self.to_window_index, (max(window_size[0], 20), window_size[1]))
        self.starting_x, self.starting_y = 0 if window_size[0] > 20 else (20 - window_size[0]) / 2, 0
        self.frame_interval = frame_interval
        self.setup()

    def setup(self):
        self._window = tkinter.Tk()
        self._window.title('Pac-Man')
        self._canvas = tkinter.Canvas(self._window, width=self.w, height=self.h + 50)
        self._canvas.pack()
        self._canvas.create_rectangle(0, 0, self.w, self.h + 50, fill='black')

        # create game related text
        self.font = 'Purisa 20'
        self.frame_time_text = self._canvas.create_text(self.w / 4, self.h + 25, fill='white', font=self.font,
                                                        text='time: %d' % 0)
        self.score_text = self._canvas.create_text(self.w / 2, self.h + 25, fill='white', font=self.font,
                                                   text='score: %d' % 0)
        self.powerup_time_text = self._canvas.create_text(3 * self.w / 4, self.h + 25, fill='white', font=self.font,
                                                          text='powerup: %d' % 0)

        # bind keyboard input
        self._window.bind("<KeyPress>", keyrelease)

    def set_game_state(self, game_state):
        self.game_state = game_state
        self.food_images = self.initialize_static_object()
        self.pacman_images = self.initialize_pacman()
        self.ghost_images = self.initialize_ghost()
        self.animated_images = []
        self._canvas.update()

    def update(self):
        # update display of pacman and ghost
        self.move_pacman()
        self.move_ghost()
        self.create_animation()

        # update display of game related text
        self.update_text(self.frame_time_text, 'time: %s' % self.game_state.get_time())
        self.update_text(self.powerup_time_text, 'powerup: %s' % self.game_state.get_pacman_invulnerable_time())
        self.update_text(self.score_text, 'score: %d' % self.game_state.get_score())

        # self._canvas.update()

    def initialize_static_object(self):
        """
        Create images of static object of the map, such as walls and food
        return: food dict, key: food location, value: a image of the food
        """
        food = {}
        for y, row in enumerate(self.game_state.static_object_lst):
            for x, col_elem in enumerate(row):
                x, y = x + self.starting_x, y + self.starting_y
                if col_elem == '#':
                    x1, y1, x2, y2 = map(self.to_window_index, (x, y, (x + 1), (y + 1)))
                    self.draw_rectangle((x1, y1, x2, y2), 'light grey')
                elif col_elem == '*' or col_elem == '@':
                    centre_x, centre_y = map(self.to_window_index, ((x + 0.5), (y + 0.5)))
                    radius = self.to_window_index(1 / 8) if col_elem == '*' else self.to_window_index(1 / 3)
                    fill_color = 'light yellow' if col_elem == '*' else 'red'
                    food[(x, y)] = self.draw_circle(centre_x, centre_y, radius, fill_color)
        return food

    def initialize_pacman(self):
        """
        Create images of the ghost by drawing a canvas arc shape
        return: pacman_images dict, key: pacman number, value: a image of the ghost
        """
        pacman_images = {}
        for k, pacman in enumerate(self.game_state.pacmans):
            x, y = pacman.x, pacman.y
            x, y = x + self.starting_x, y + self.starting_y
            centre_x, centre_y, radius = map(self.to_window_index, ((x + 0.5), (y + 0.5), 0.5))
            fill_color = pacman_color[k]

            image = self.draw_arc(centre_x, centre_y, radius, 22.5, 315, fill_color)
            pacman_images[k] = ((x, y), [image])
        return pacman_images

    def initialize_ghost(self):
        """
        Create images of the ghost by drawing and combining various canvas shapes
        return: ghost_images dict, key: ghost number, value: a list of image parts of the ghost
        """
        ghost_images = {}
        for k, ghost in enumerate(self.game_state.ghosts):
            x, y = ghost.x, ghost.y
            x, y = x + self.starting_x, y + self.starting_y
            centre_x, centre_y, radius = map(self.to_window_index, ((x + 0.5), (y + 0.5), 0.5))
            triangle1_vertices, triangle2_vertices = ((x + 0.25, y + 0.75), (x, y + 1), (x + 0.5, y + 1)), \
                                                     ((x + 0.75, y + 0.75), (x + 0.5, y + 1), (x + 1, y + 1))
            triangle1_vertices = tuple(map(lambda i: (self.to_window_index(i[0]), self.to_window_index(i[1])),
                                           triangle1_vertices))
            triangle2_vertices = tuple(map(lambda i: (self.to_window_index(i[0]), self.to_window_index(i[1])),
                                           triangle2_vertices))
            fill_color = ghost_color[k]

            image = []
            image.append(self.draw_arc(centre_x, centre_y, radius, 0, 180, fill_color))
            image.append(self.draw_rectangle((centre_x - radius, centre_y, centre_x + radius, centre_y + radius),
                                             fill_color, ''))
            image.append(self.draw_polygon(triangle1_vertices, 'black', ''))
            image.append(self.draw_polygon(triangle2_vertices, 'black', ''))
            image.append(self.draw_circle(centre_x - radius / 2.5, centre_y - radius / 5, radius / 3, 'white'))
            image.append(self.draw_circle(centre_x + radius / 2.5, centre_y - radius / 5, radius / 3, 'white'))
            image.append(self.draw_circle(centre_x - radius / 2.5, centre_y - radius / 5, radius / 8, 'black'))
            image.append(self.draw_circle(centre_x + radius / 2.5, centre_y - radius / 5, radius / 8, 'black'))
            ghost_images[k] = ((x, y), (0, 0), image)
        return ghost_images

    def move_pacman(self):
        for k, pacman in enumerate(self.game_state.pacmans):
            (old_x, old_y), image = self.pacman_images[k]
            x, y = pacman.x, pacman.y
            x, y = x + self.starting_x, y + self.starting_y
            x_diff, y_diff = x - old_x, y - old_y
            window_x_diff, window_y_diff = map(self.to_window_index, (x_diff, y_diff))

            # rotate pacman image if pacman's move direction changes
            if (x_diff, y_diff) != (0, 0):
                self.change_pacman_image(image, (x_diff, y_diff))

            # move pacman image
            self.animated_images.append((image, window_x_diff, window_y_diff))

            # update pacman image location
            self.pacman_images[k] = (x, y), image

            # remove food if necessary
            if (x, y) in self.food_images:
                self.delete_image(self.food_images[(x, y)])
                del self.food_images[(x, y)]

    def move_ghost(self):
        for k, ghost in enumerate(self.game_state.ghosts):
            (old_x, old_y), (old_x_diff, old_y_diff), image = self.ghost_images[k]
            x, y = ghost.x, ghost.y
            x, y = x + self.starting_x, y + self.starting_y
            x_diff, y_diff = x - old_x, y - old_y
            window_x_diff, window_y_diff = map(self.to_window_index, (x_diff, y_diff))

            # modify the ghost image if the ghost's status changes
            is_frightened = self.game_state.is_pacman_invulnerable()
            self.change_ghost_image(image, (x_diff, y_diff), (old_x_diff, old_y_diff), is_frightened, ghost_color[k])

            # move ghost image
            for i in image:
                if ghost.is_dead():
                    self._canvas.itemconfigure(i, state='hidden')
                else:
                    self._canvas.itemconfigure(i, state='normal')

                self.animated_images.append((i, window_x_diff, window_y_diff))

            # update ghost image location
            self.ghost_images[k] = (x, y), (x_diff, y_diff), image

    def change_pacman_image(self, image, direction):
        if direction != (0, 0):
            start = {
                (1, 0): 22.5,
                (-1, 0): 202.5,
                (0, 1): 292.5,
                (0, -1): 112.5
            }[direction]
            self._canvas.itemconfigure(image, start=start)

    def change_ghost_image(self, image, direction, old_direction, is_frightened, original_color):
        if direction != old_direction:
            dx, dy = direction[0] - old_direction[0], direction[1] - old_direction[1]

            for i in image[-2:]:
                self._canvas.move(i, dx * 2, dy * 2)

        for i in image[:2]:
            if is_frightened:
                self._canvas.itemconfigure(i, fill='white')
            else:
                self._canvas.itemconfigure(i, fill=original_color)

    def create_animation(self):
        step = 5
        for _ in range(step):
            for image, window_x_diff, window_y_diff in self.animated_images:
                self._canvas.move(image, window_x_diff / step, window_y_diff / step)
            self.sleep(1 / step)
        self.animated_images = []

    def update_text(self, text, text_content):
        self._canvas.itemconfigure(text, text=text_content)

    def to_window_index(self, n):
        return n * self.grid_size

    def draw_rectangle(self, vertices, fill_color, outline='black'):
        return self._canvas.create_rectangle(vertices, fill=fill_color, outline=outline)

    def draw_circle(self, centre_x, centre_y, radius, fill_color, outline='black'):
        return self._canvas.create_oval(centre_x - radius, centre_y - radius, centre_x + radius,
                                        centre_y + radius, fill=fill_color, outline=outline)

    def draw_arc(self, centre_x, centre_y, radius, start, extent, fill_color, outline='black'):
        return self._canvas.create_arc(centre_x - radius, centre_y - radius, centre_x + radius,
                                       centre_y + radius, start=start, extent=extent, fill=fill_color, outline=outline)

    def draw_polygon(self, vertices, fill_color, outline='black'):
        return self._canvas.create_polygon(vertices, fill=fill_color, outline=outline)

    def delete_image(self, image):
        self._canvas.delete(image)

    def sleep(self, frames):
        seconds = frames * self.frame_interval
        self._window.after(int(1000 * seconds), self._window.quit)
        self._window.mainloop()


# -------------------- capture player keyboard commands --------------------

key_commands1, key_commands2 = [], []


def keyrelease(event):
    global key_commands1, key_commands2
    valid_commands1, valid_commands2 = ['Up', 'Down', 'Left', 'Right', 'KP_Insert'], \
                                       ['w', 's', 'a', 'd', 'q']

    if event.keysym in valid_commands1 or event.keysym in valid_commands2:
        commands = key_commands1 if event.keysym in valid_commands1 else key_commands2
        commands.append(event.keysym)


def get_key_commands(player_num):
    if player_num == 1:
        return key_commands1
    elif player_num == 2:
        return key_commands2
    else:
        raise ValueError('invalid player number: %d' % player_num)


def clear_key_commands(player_num):
    if player_num == 1:
        global key_commands1
        key_commands1 = []
    elif player_num == 2:
        global key_commands2
        key_commands2 = []
    else:
        raise ValueError('invalid player number: %d' % player_num)


if __name__ == '__main__':
    render = Render((1080, 640))
    render.setup()
