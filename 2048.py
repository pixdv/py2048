import pyglet
from pyglet import shapes
from pyglet import gl
from pyglet.window import key, mouse
from random import randint
from itertools import chain

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
squares_matrix = [[0 for _ in range(x_tiles)] for _ in range(y_tiles)]
squares_colors = {2: (105, 112, 245), 4: (64, 73, 245), 6: (7, 14, 148), 8: (20, 31, 250)}


# controls
moves = {
    key.UP: "up",
    key.DOWN: "down",
    key.LEFT: "left",
    key.RIGHT: "right"
}


# score
score = 0
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
victory = False
won = False
victory_no_outline_color = (184, 224, 206)

# game over
game_over = False
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
pyglet.font.add_file("Not Jam UI 12.ttf")
NotJamUI12 = pyglet.font.load("Not Jam UI 12")
font_name = "Not Jam UI 12"


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


def summon_squares(amount):
    global squares_matrix
    available_cords = list(chain(*squares_matrix)).count(0)
    if not available_cords:
        return
    elif available_cords < amount:
        amount = available_cords
    for _ in range(amount):
        cords = (randint(0, x_tiles-1), randint(0, y_tiles-1))
        while squares_matrix[cords[0]][cords[1]]:
            cords = (randint(0, x_tiles-1), randint(0, y_tiles-1))

        n = 4 if randint(1, 10) == 5 else 2
        squares_matrix[cords[0]][cords[1]] = n


def draw_squares():
    for my, row in enumerate(squares_matrix[::-1]):
        for mx, n in enumerate(row):
            if n:
                x, y = tiles_cords[my][mx]
                square_color = squares_colors.get(n%10, (0, 0, 0))
                square = shapes.Rectangle(x, y, square_width, square_height, color=square_color)
                square.draw()

                sn = str(n)
                label = pyglet.text.Label(sn, x+15, y+15, font_size=20*scale*(4/y_tiles), font_name=font_name)
                label.draw()


def draw_score():
    score_label = pyglet.text.Label(f"Score: {score}", score_x, score_y, font_size=score_font_size, font_name=font_name, color=score_color, anchor_y="center")
    score_label.draw()


def draw_title():
    title_label = pyglet.text.Label(title, title_x, title_y, font_size=title_font_size, font_name=font_name, anchor_x="center", anchor_y="center", color=title_color)
    title_label.draw()


def draw_no():
    batch = pyglet.graphics.Batch()
    gof_bg = shapes.Rectangle(no_bg_x, no_bg_y, no_bg_w, no_bg_h, no_bg_color, batch=batch)
    gof_bg.draw()
    outline = shapes.Rectangle(no_outline_x, no_outline_y, no_outline_w, no_outline_h, no_outline_color)
    outline.draw()
    gof = shapes.Rectangle(no_x, no_y, no_width, no_height, no_color)
    gof.draw()
    gof_text = pyglet.text.Label("YOU WON! :)" if victory else "GAME OVER! :(", no_text_x, no_text_y, font_name=font_name, font_size=no_text_size, anchor_x="center", color=no_text_color)
    gof_text.draw()
    score_text = pyglet.text.Label(f"Score: {score}", no_text_x, no_text_y - no_text_y//10, font_name=font_name, font_size=no_text_size, anchor_x="center", color=no_text_color)
    score_text.draw()


def buttons():
    restart_button = Button(
        no_button_x,
        no_button_y,
        no_button_w,
        no_button_h,
        restart,
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
        continue_,
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
            restart,
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


def move(direction):
    global squares_matrix, score
    moved = False
    match direction:
        case "down":
            matrix = squares_matrix
        case "up":
            matrix = [r[::-1] for r in squares_matrix]
        case "left":
            matrix = list(map(list, zip(*squares_matrix[::-1])))
        case "right":
            matrix = [list(r) for r in list(zip(*squares_matrix))[::-1]]
        case _:
            return
    for ri, row in enumerate(matrix):
        changed = []
        for i, s in enumerate(row):
            if i and s:
                ci = i
                while ci and not row[ci-1]:
                    row[ci] = 0
                    row[ci-1] = s
                    ci-=1
                    if not moved:
                        moved = True
                else:
                    if ci and ci-1 not in changed and row[ci-1] == s:
                        row[ci] = 0
                        row[ci-1] *= 2
                        score += row[ci-1]
                        ci-=1
                        changed.append(ci)
                        if not moved:
                            moved = True
        matrix[ri] = row
    match direction:
        case "down":
            squares_matrix = matrix
        case "up":
            squares_matrix = [r[::-1] for r in matrix]
        case "left":
            squares_matrix = [list(r) for r in list(zip(*matrix))[::-1]]
        case "right":
            squares_matrix = list(map(list, zip(*matrix[::-1])))
    if moved:
        summon_squares(1)


def check_2048(_):
    global victory
    if not victory and not won:
        if 2048 in list(chain(*squares_matrix)):
            victory = True


def check_available_moves(_):
    global game_over
    available = False
    if not list(chain(*squares_matrix)).count(0):
        for row in squares_matrix:
            for i, s in enumerate(row):
                if i and row[i-1] == s or i < x_tiles-1 and row[i+1] == s:
                    available = True
                    break
        if not available:
            for row in list(map(list, zip(*squares_matrix[::-1]))):
                for i, s in enumerate(row):
                    if i and row[i-1] == s or i < x_tiles-1 and row[i+1] == s:
                        available = True
                        break
        if not available:
            game_over = True


def restart():
    global squares_matrix, tiles_cords, score, game_over, victory, won
    squares_matrix, tiles_cords = [[0 for _ in range(x_tiles)] for _ in range(y_tiles)], [[] for _ in range(x_tiles)]
    score = 0
    game_over = False
    victory = False
    won = False
    summon_squares(2)


def continue_():
    global victory, won
    victory = False
    won = True


def main():
    global window
    gl.glClearColor(*map(lambda x: x*(1/255), window_bg))
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    summon_squares(2)

    restart_button, continue_button, retry_button = buttons()

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
        draw_squares()
        draw_score()
        retry_button.draw()
        if victory or game_over:
            retry_button.active = False
            draw_no()
            restart_button.active = True
            restart_button.draw()
            if victory:
                continue_button.active = True
                continue_button.draw()
        else:
            retry_button.active = True

    @window.event
    def on_key_press(symbol, _):
        if not game_over and not victory and moves.get(symbol, None):
            move(moves.get(symbol, None))

    pyglet.clock.schedule_interval(check_2048, 0.5)
    pyglet.clock.schedule_interval(check_available_moves, 1)

    
    pyglet.app.run()


if __name__ == "__main__":
    main()
