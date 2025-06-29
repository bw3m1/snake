import sys
import subprocess

try:
    import pygame as pg
except ImportError:
    install_flags = []
    if sys.platform == "win32":
        install_flags = [subprocess.CREATE_NO_WINDOW]
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "pygame"],
        creationflags=(install_flags[0] if install_flags else 0),
    )
    import pygame as pg

try:
    from numpy.random import randint
    from numpy import floor
    from numpy import gcd
except ImportError:
    install_flags = []
    if sys.platform == "win32":
        install_flags = [subprocess.CREATE_NO_WINDOW]
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "numpy"],
        creationflags=(install_flags[0] if install_flags else 0),
    )
    from numpy.random import randint
    from numpy import floor
    from numpy import gcd

pg.init()

cell_side_length = gcd(
    pg.display.Info().current_w // 2, pg.display.Info().current_h // 2
)

scale = [
    floor(pg.display.Info().current_w / cell_side_length) * cell_side_length,
    floor(pg.display.Info().current_h / cell_side_length) * cell_side_length,
]
surface = pg.display.set_mode(scale)
pg.display.set_caption("Snake Game")

FPS = 128 * 2  # Rendering FPS
clock = pg.time.Clock()

MOVE_DELAY = 150 / 1.614  # ms between moves
last_move_time = 0

bg_color = "#1e1e1e"
player_head_color = "#00ff00"
player_tail_color = "#0f8d0f"
apple_color = "#b71513"

game_over_header_color = "#b71513"
play_again_text_color = "#b71513"
play_again_color_base = "#1e1e1e"
play_again_color_hover = "#222222"
play_again_color_hold = "#333333"

paused_rect_color = (66, 66, 71, 128)
paused_rect_color_border = (66, 66, 71, 255)
paused_text_color = (66 * 1.614, 66 * 1.614, 71 * 1.614, 255)

apple_pos = [
    randint(0, scale[0] // cell_side_length) * cell_side_length,
    randint(0, scale[1] // cell_side_length) * cell_side_length,
]
head_pos = [0, 0]
player_tail_quordenints = [[0, 0]]

last_direction = [0, 0]  # Current direction
direction_queue = []  # Queue of upcoming directions
move_processed = True  # Lock direction change after move until next tick

paused = False
game_over = False
active = True


def valid_direction_change(new_dir):
    if len(player_tail_quordenints) <= 1:
        return True
    return new_dir != [-last_direction[0], -last_direction[1]]


def enqueue_direction(sign, index):
    global direction_queue, last_direction, move_processed

    new_dir = [0, 0]
    new_dir[index] = sign

    last_queued = direction_queue[-1] if direction_queue else last_direction

    if len(player_tail_quordenints) > 1 and new_dir == [
        -last_queued[0],
        -last_queued[1],
    ]:
        return

    # Immediate update if possible
    if move_processed and not direction_queue:
        if valid_direction_change(new_dir):
            last_direction = new_dir
            move_processed = False
            return

    direction_queue.append(new_dir)


def move_snake():
    global apple_pos, game_over, last_direction, move_processed

    if direction_queue:
        last_direction = direction_queue.pop(0)

    if last_direction == [0, 0]:
        return

    new_head = [
        (head_pos[0] + last_direction[0] * cell_side_length) % scale[0],
        (head_pos[1] + last_direction[1] * cell_side_length) % scale[1],
    ]

    if new_head in player_tail_quordenints[:-1]:
        game_over = True
        return

    head_pos[0], head_pos[1] = new_head

    if head_pos != apple_pos:
        player_tail_quordenints.pop(0)
    else:
        bad_apple = True
        while bad_apple:
            apple_pos = [
                randint(0, scale[0] // cell_side_length) * cell_side_length,
                randint(0, scale[1] // cell_side_length) * cell_side_length,
            ]
            bad_apple = apple_pos in player_tail_quordenints

    player_tail_quordenints.append(list(head_pos))

    move_processed = True


while active:
    current_time = pg.time.get_ticks()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            active = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_q:
                active = False
            if not paused:
                if event.key in (pg.K_LEFT, pg.K_a, pg.K_j):
                    enqueue_direction(-1, 0)
                elif event.key in (pg.K_RIGHT, pg.K_d, pg.K_l):
                    enqueue_direction(1, 0)
                elif event.key in (pg.K_DOWN, pg.K_s, pg.K_k):
                    enqueue_direction(1, 1)
                elif event.key in (pg.K_UP, pg.K_w, pg.K_i):
                    enqueue_direction(-1, 1)
            if event.key == pg.K_SPACE:
                paused = not paused

    if not game_over and (current_time - last_move_time) > MOVE_DELAY and not paused:
        move_snake()
        last_move_time = current_time

    surface.fill(bg_color)

    if not game_over:
        for pixel in player_tail_quordenints:
            rect = pg.Rect(pixel[0], pixel[1], cell_side_length, cell_side_length)
            pg.draw.rect(surface, player_tail_color, rect)

        apple_rect = pg.Rect(
            apple_pos[0], apple_pos[1], cell_side_length, cell_side_length
        )
        pg.draw.rect(surface, apple_color, apple_rect)

        head_rect = pg.Rect(
            head_pos[0], head_pos[1], cell_side_length, cell_side_length
        )
        pg.draw.rect(surface, player_head_color, head_rect)

    if paused and not game_over:
        paused_rect = pg.Rect(scale[0] / 3, scale[1] / 2.5, scale[0] / 3, scale[1] / 5)

        # --- Draw semi-transparent box ---
        temp_surface = pg.Surface((paused_rect.width, paused_rect.height), pg.SRCALPHA)
        temp_surface.fill(paused_rect_color)  # RGBA tuple like (51, 51, 56, 128)
        surface.blit(temp_surface, paused_rect.topleft)

        # --- Draw border ---
        pg.draw.rect(
            surface, paused_rect_color_border, paused_rect, 2
        )  # 2-pixel border

        # --- Draw centered text ---
        font = pg.font.SysFont(
            None, int(paused_rect.height / 3)
        )  # adjust font size if needed
        text_surface = font.render("PAUSED", True, paused_text_color)
        text_rect = text_surface.get_rect(center=paused_rect.center)
        surface.blit(text_surface, text_rect)

    elif game_over:
        game_over_font_header = pg.font.SysFont("Arial", 64)
        play_again_font = pg.font.SysFont("Arial", 32)

        text_surface = game_over_font_header.render(
            "Game Over!", True, game_over_header_color
        )
        text_rect = text_surface.get_rect(center=(scale[0] // 2, scale[1] // 2 - 64))
        surface.blit(text_surface, text_rect)

        button_text = "Play Again"
        button_surface = play_again_font.render(
            button_text, True, play_again_text_color
        )
        button_rect = button_surface.get_rect(
            center=(scale[0] // 2, scale[1] // 2 + 32)
        )

        padding = 20
        bg_rect = pg.Rect(
            button_rect.left - padding // 2,
            button_rect.top - padding // 2,
            button_rect.width + padding,
            button_rect.height + padding,
        )

        mouse_pos = pg.mouse.get_pos()
        mouse_pressed = pg.mouse.get_pressed()
        hovering = bg_rect.collidepoint(mouse_pos)

        if hovering:
            color = (
                play_again_color_hold if mouse_pressed[0] else play_again_color_hover
            )
        else:
            color = play_again_color_base

        pg.draw.rect(surface, color, bg_rect, border_radius=8)
        surface.blit(button_surface, button_rect)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                active = False
            elif (event.type == pg.MOUSEBUTTONUP and event.button == 1) or (event.type == pg.KEYUP):
                if hovering or (event.type == pg.KEYUP):
                    head_pos = [0, 0]
                    player_tail_quordenints = [[0, 0]]
                    apple_pos = [
                        randint(0, scale[0] // cell_side_length) * cell_side_length,
                        randint(0, scale[1] // cell_side_length) * cell_side_length,
                    ]
                    game_over = False
                    last_direction = [0, 0]
                    direction_queue = []
                    last_move_time = pg.time.get_ticks()
                    move_processed = True

    pg.display.flip()
    clock.tick(FPS)

pg.quit()