from itertools import chain
from random import randint, seed
from string import printable

import numpy as np
import pyglet
from pyglet import gl, shapes
from pyglet.window import key, mouse

# window configuration
window_width = 600
window_height = 800
window_title = "Py2048"
window_bg = (220, 225, 250, 255)
window = pyglet.window.Window(window_width, window_height, caption=window_title, resizable=False)

# scaling
scale = window.get_pixel_ratio()

# field configuration
field_width, field_height = 500*scale, 500*scale
field_x = (window_width*scale - field_width) // 2
field_y = (window_height*scale - field_height) // 2
field_color = (146, 163, 247)


# tiles configuration
x_tiles, y_tiles = 4, 4
tile_x_gap, tile_y_gap = 9.6*(4/x_tiles)*scale, 9.6*(4/y_tiles)*scale
tile_width, tile_height = (field_width-(tile_x_gap*(x_tiles+1)))/x_tiles, (field_height-(tile_y_gap*(y_tiles+1)))/y_tiles
tile_color = (208, 214, 247)
tiles_cords = [[] for _ in range(x_tiles)]


# squares configuration
square_width, square_height = tile_width, tile_height
squares_colors = {2: (105, 112, 245), 4: (64, 73, 245), 6: (7, 14, 148), 8: (20, 31, 250)}

# controls
moves = {
    key.UP: 0,
    key.DOWN: 1,
    key.LEFT: 2,
    key.RIGHT: 3
}

directions = {
    0: "up",
    1: "down",
    2: "left",
    3: "right"
}

# score
score_x = field_x + 75//6*scale
score_y = field_y - 37.5*scale
score_color = (133, 151, 242)
score_font_size = 36*scale

# title
title = window_title
title_x = window_width // (2 / scale)
title_y = (window_height*scale - (window_height*scale - (field_y + field_height)) // 2)
title_font_size = 59 * scale
title_color = (81, 105, 245)

# victory
victory_no_outline_color = (184, 224, 206)

# game over
go_no_outline_color = (237, 172, 166)

# notification overlay
no_bg_x, no_bg_y = 0, 0
no_bg_w = window_width*scale
no_bg_h = window_height*scale
no_bg_color = (4, 5, 12, 180)
no_outline_w = field_width - 9.6 * 2 * scale
no_outline_h = field_height / 2
no_outline_x = field_x + 9.6 * scale
no_outline_y = field_y + field_height - no_outline_h - 9.6 * scale
no_outline_color = (161, 172, 255)
no_x = no_outline_x + 9.6 * scale
no_y = no_outline_y + 9.6 * scale
no_width = no_outline_w - 9.6 * 2 * scale
no_height = no_outline_h - 9.6 * 2 * scale
no_color = (220, 225, 250)
no_text_x = no_x + no_width // 2
no_text_y = no_y + no_height // 2
no_text_size = 36 * scale
no_text_color = (56, 73, 255)

# buttons
no_button_x = no_outline_x + no_outline_w // 12
no_button_y = no_outline_y - no_outline_h // 3 * 1.3
no_button_w = no_outline_w - no_outline_w // 6
no_button_h = no_outline_h // 3
no_button_outline_thickness = 9.6 * scale
no_button_outline_color = (161, 172, 255)
no_button_color = (101, 119, 252)
no_button_hover_color = (97, 105, 242)
no_button_pressed_color = (45, 56, 138)
no_button_text_color = (228, 229, 245)
no_button_text_size = 36 * scale

# font configuration
pyglet.font.add_file("NotJamUI12.ttf")
NotJamUI12 = pyglet.font.load("Not Jam UI 12")
font_name = "Not Jam UI 12"


class Game:
    def __init__(self):
        self.score = 0
        self.field_size = (4, 4)
        self.field = np.zeros((self.field_size[0], self.field_size[1]))

        self.victory = False
        self.won = False
        self.game_over = False

        self.__add_squares(2)

    def __add_squares(self, amount):
        available_cords = self.field_size[0] * self.field_size[1] - np.count_nonzero(self.field)
        if not available_cords:
            return
        elif available_cords < amount:
            amount = available_cords
        for _ in range(amount):
            r, c = randint(0, self.field_size[0] - 1), randint(0, self.field_size[1] - 1)
            while self.field[r, c] != 0:
                r, c = randint(0, self.field_size[0] - 1), randint(0, self.field_size[1] - 1)
            self.field[r, c] = 4 if randint(1, 10) == 10 else 2

    def reset(self):
        self.field = np.zeros((self.field_size[0], self.field_size[1]))
        self.score = 0

        self.victory = False
        self.won = False
        self.game_over = False

        self.__add_squares(2)

    def move(self, direction):
        direction = directions.get(direction, None)
        if direction is None: return
        moved = False
        match direction:
            case "left":
                pass
            case "right":
                self.field = np.flip(self.field, 1)
            case "up":
                self.field = np.rot90(self.field, 1, (0, 1))
            case "down":
                self.field = np.rot90(self.field, 1, (1, 0))
            case _:
                return
        for y, row in enumerate(self.field):
            changed = []
            for x, n in enumerate(row):
                if x and n:
                    cx = x
                    while cx and not row[cx - 1]:
                        row[cx] = 0
                        row[cx - 1] = n
                        cx -= 1
                        if not moved:
                            moved = True
                    if cx and cx - 1 not in changed and row[cx - 1] == n:
                        row[cx - 1] *= 2
                        row[cx] = 0
                        self.score += row[cx - 1]
                        cx -= 1
                        changed.append(cx)
                        if not moved:
                            moved = True
            self.field[y] = row
        match direction:
            case "left":
                pass
            case "right":
                self.field = np.flip(self.field, 1)
            case "up":
                self.field = np.rot90(self.field, 1, (1, 0))
            case "down":
                self.field = np.rot90(self.field, 1, (0, 1))
        if moved:
            self.__add_squares(1)

    def is_over(self, _=None):
        if not self.field_size[0] * self.field_size[1] - np.count_nonzero(self.field):
            for row in self.field:
                for i, s in enumerate(row):
                    if i and row[i - 1] == s or i < x_tiles - 1 and row[i + 1] == s:
                        return False
            for row in np.rot90(self.field, 1, (0, 1)):
                for i, s in enumerate(row):
                    if i and row[i - 1] == s or i < x_tiles - 1 and row[i + 1] == s:
                        return False
            self.game_over = True
            return True
        return False

    def get_biggest_square(self):
        return self.field.max()

    def continue_game(self):
        self.victory = False
        self.won = True

    def check_2048(self, _=None):
        if self.get_biggest_square() >= 2048 and not self.won and not self.victory:
            self.victory = True


class Button(pyglet.event.EventDispatcher):
    def __init__(
            self,
            x,
            y,
            width,
            height,
            func,
            text,
            text_color,
            font_size,
            font,
            color,
            hover_color,
            pressed_color,
            outline,
            outline_color
        ):
        super().__init__()

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.func = func
        self.text = text
        self.text_color = text_color
        self.font_size = font_size
        self.font = font
        self.color = color
        self.hover_color = hover_color or color
        self.pressed_color = pressed_color or color
        self.outline = outline or 0
        self.outline_color = outline_color

        self.active = False

        self.outline_shape = shapes.Rectangle(x, y, width, height, color=outline_color)
        self.button = shapes.Rectangle(x+outline, y+outline, width-outline*2, height-outline*2, color=color)
        self.text_label = pyglet.text.Label(text, x+width//2, y+height//2, font_size=font_size, font_name=font, color=text_color, anchor_x="center", anchor_y="center")

        self.is_pressed = True

    def check_hover(self, mx, my):
        return self.x < mx < self.x + self.width and self.y < my < self.y + self.height

    def on_mouse_motion(self, x, y, dx, dy):
        if not self.is_pressed and self.active:
            if self.check_hover(x, y):
                self.button.color = self.hover_color
            else:
                self.button.color = self.color

    def on_mouse_press(self, x, y, button, modifiers):
        if self.check_hover(x, y) and button == mouse.LEFT and self.active:
            self.is_pressed = True
            self.button.color = self.pressed_color
            self.func()

    def on_mouse_release(self, x, y, button, modifiers):
        if self.is_pressed and button == mouse.LEFT and self.active:
            self.is_pressed = False
            self.button.color = self.color
            return pyglet.event.EVENT_HANDLED

    def draw(self):
        self.outline_shape.draw()
        self.button.draw()
        self.text_label.draw()


def draw_field():
    field = shapes.Rectangle(field_x, field_y, field_width, field_height, color=field_color)
    field.draw()


def draw_tiles():
    x = field_x + tile_x_gap
    y = field_y + tile_y_gap
    for xn in range(x_tiles):
        for _ in range(y_tiles):
            if len(list(chain(tiles_cords))) < x_tiles*y_tiles:
                tiles_cords[xn].append((x, y))
            tile = shapes.Rectangle(x, y, tile_width, tile_height, color=tile_color)
            tile.draw()
            y += round(tile_height + tile_y_gap)
        x += round(tile_width + tile_x_gap)
        y = field_y + tile_y_gap
        if len(list(chain(tiles_cords))) < x_tiles*y_tiles:
            tiles_cords[xn].append((x, y))


def draw_squares(game: Game):
    for mx, row in enumerate(game.field[::-1]):
        for my, n in enumerate(row):
            if n:
                x, y = tiles_cords[my][mx]
                square_color = squares_colors.get(n%10, (0, 0, 0))
                square = shapes.Rectangle(x, y, square_width, square_height, color=square_color)
                square.draw()

                sn = str(int(n))
                label = pyglet.text.Label(sn, x+15, y+15, font_size=20*scale*(4/y_tiles), font_name=font_name)
                label.draw()


def draw_score(game: Game):
    score_label = pyglet.text.Label(f"Score: {int(game.score)}", score_x, score_y, font_size=score_font_size, font_name=font_name, color=score_color, anchor_y="center")
    score_label.draw()


def draw_title():
    title_label = pyglet.text.Label(title, title_x, title_y, font_size=title_font_size, font_name=font_name, anchor_x="center", anchor_y="center", color=title_color)
    title_label.draw()


def draw_no(game):
    batch = pyglet.graphics.Batch()
    gof_bg = shapes.Rectangle(no_bg_x, no_bg_y, no_bg_w, no_bg_h, no_bg_color, batch=batch)
    gof_bg.draw()
    outline = shapes.Rectangle(no_outline_x, no_outline_y, no_outline_w, no_outline_h, no_outline_color)
    outline.draw()
    gof = shapes.Rectangle(no_x, no_y, no_width, no_height, no_color)
    gof.draw()
    gof_text = pyglet.text.Label("YOU WON! :)" if game.victory else "GAME OVER! :(", no_text_x, no_text_y, font_name=font_name, font_size=no_text_size, anchor_x="center", color=no_text_color)
    gof_text.draw()
    score_text = pyglet.text.Label(f"Score: {int(game.score)}", no_text_x, no_text_y - no_text_y//10, font_name=font_name, font_size=no_text_size, anchor_x="center", color=no_text_color)
    score_text.draw()


def buttons(game: Game):
    restart_button = Button(
        no_button_x,
        no_button_y,
        no_button_w,
        no_button_h,
        game.reset,
        "RESTART",
        no_button_text_color,
        no_button_text_size,
        font_name,
        no_button_color,
        no_button_hover_color,
        no_button_pressed_color,
        no_button_outline_thickness,
        no_button_outline_color
    )
    continue_button = Button(
        no_button_x,
        no_button_y - no_button_h * 1.2,
        no_button_w,
        no_button_h,
        game.continue_game,
        "CONTINUE",
        no_button_text_color,
        no_button_text_size,
        font_name,
        no_button_color,
        no_button_hover_color,
        no_button_pressed_color,
        no_button_outline_thickness,
        no_button_outline_color
    )
    retry_button = Button(
            window_width*scale-125*scale-15*scale,
            15 * scale,
            125*scale,
            50 * scale,
            game.reset,
            "Retry",
            no_button_text_color,
            19*scale,
            font_name,
            no_button_color,
            no_button_hover_color,
            no_button_pressed_color,
            no_button_outline_thickness*3/4,
            no_button_outline_color
        )
    return restart_button, continue_button, retry_button


def main():
    game = Game()

    gl.glClearColor(*[c*(1/255) for c in window_bg])
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    restart_button, continue_button, retry_button = buttons(game)

    window.push_handlers(
    on_mouse_motion=retry_button.on_mouse_motion,
    on_mouse_press=retry_button.on_mouse_press,
    on_mouse_release=retry_button.on_mouse_release
    )

    window.push_handlers(
        on_mouse_motion=continue_button.on_mouse_motion,
        on_mouse_press=continue_button.on_mouse_press,
        on_mouse_release=continue_button.on_mouse_release
    )

    window.push_handlers(
            on_mouse_motion=restart_button.on_mouse_motion,
            on_mouse_press=restart_button.on_mouse_press,
            on_mouse_release=restart_button.on_mouse_release
    )

    @window.event
    def on_draw():
        window.clear()
        draw_title()
        draw_field()
        draw_tiles()
        draw_squares(game)
        draw_score(game)
        retry_button.draw()
        if game.victory or game.game_over:
            retry_button.active = False
            draw_no(game)
            restart_button.active = True
            restart_button.draw()
            if game.victory:
                continue_button.active = True
                continue_button.draw()
        else:
            retry_button.active = True

    @window.event
    def on_key_press(symbol, _):
        if not game.game_over and not game.victory:
            game.move(moves.get(symbol, 4))
            print("[-----[FIELD]-----]")
            print(game.field)

    pyglet.clock.schedule_interval(game.check_2048, 0.5)
    pyglet.clock.schedule_interval(game.is_over, 1)

    pyglet.app.run()


if __name__ == "__main__":
    main()
