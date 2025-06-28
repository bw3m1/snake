import sys
import subprocess

try:
    import pygame as pg
except ImportError:
    # Install pygame automatically if missing
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
except ImportError:
    # Install pygame automatically if missing
    install_flags = []
    if sys.platform == "win32":
        install_flags = [subprocess.CREATE_NO_WINDOW]

    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "numpy"],
        creationflags=(install_flags[0] if install_flags else 0),
    )
    from numpy.random import randint
    from numpy import floor


pg.init()  # initialise pygame

scale = [floor(pg.display.Info().current_w / 50)*50, floor(pg.display.Info().current_h / 50)*50]
surface = pg.display.set_mode(scale)
pg.display.set_caption("Snake Game")

bg_color = "#1e1e1e"
player_head_color = "#00ff00"
player_tail_color = "#0f8d0f"
apple_color = "#b71513"

game_over_header_color = "#b71513"
play_again_text_color = "#b71513"
play_again_color_base = "#1e1e1e"
play_again_color_hover = "#222222"
play_again_color_hold = "#333333"

apple_pos = [randint(0, scale[0] / 50) * 50, randint(0, scale[1] / 50) * 50]
head_pos = [0, 0]
cell_side_length = 50
player_tail_quordenints = [[0, 0]]

game_over = False
active = True


def handelInput(sign, index):
    """
    Arguments:
        sign (_string_): _in the sign, which tells it to ether add ("+") or subtract ("-") cell_side_length_
        index (_integer_): _tells it wether its operating on the X (0) or Y (1) quordenints_
    """

    global apple_pos
    global game_over

    # update player head
    head_pos[index] = eval(f"{head_pos[index] + sign*cell_side_length}")
    head_pos[index] %= scale[index]

    # update player tail
    if head_pos != apple_pos:
        player_tail_quordenints.pop(0)
    else:
        bad_apple = True
        while bad_apple:
            apple_pos = [
                randint(0, scale[0] // 50) * 50,
                randint(0, scale[1] // 50) * 50,
            ]
            bad_apple = False
            for location in player_tail_quordenints:
                if location == apple_pos:
                    bad_apple = True
                    break

    # end the game if the head is on the tail
    for i, tail_segment in enumerate(player_tail_quordenints):
        if head_pos == tail_segment:
            if i == 0:
                continue  # skip checking against the head itself
            else:
                game_over = True
                break

    player_tail_quordenints.append(list(head_pos))

while active:

    # event muniment
    for event in pg.event.get():
        if event.type == pg.QUIT:
            active = False
        elif event.type == pg.KEYDOWN:

            if event.key == pg.K_LEFT or event.key == pg.K_a or event.key == pg.K_j:
                handelInput(-1, 0)

            elif event.key == pg.K_RIGHT or event.key == pg.K_d or event.key == pg.K_l:
                handelInput(1, 0)

            elif event.key == pg.K_DOWN or event.key == pg.K_s or event.key == pg.K_k:
                handelInput(1, 1)

            elif event.key == pg.K_UP or event.key == pg.K_w or event.key == pg.K_i:
                handelInput(-1, 1)

    # rendering stuff

    surface.fill(bg_color)

    if not game_over:

        # draw players tail
        for pixel in player_tail_quordenints:
            current_tail_pixel = pg.Rect(
                pixel[0], pixel[1], cell_side_length, cell_side_length
            )
            pg.draw.rect(surface, player_tail_color, current_tail_pixel)

        # draw apple
        player_head = pg.Rect(
            apple_pos[0], apple_pos[1], cell_side_length, cell_side_length
        )
        pg.draw.rect(surface, apple_color, player_head)

        # draw players head
        player_head = pg.Rect(
            head_pos[0], head_pos[1], cell_side_length, cell_side_length
        )
        pg.draw.rect(surface, player_head_color, player_head)

    elif game_over:
        # Fonts
        game_over_font_header = pg.font.SysFont("Arial", 64)
        play_again_font = pg.font.SysFont("Arial", 32)

        # Game Over Text
        text_surface = game_over_font_header.render(
            "Game Over!", True, game_over_header_color
        )
        text_rect = text_surface.get_rect(center=(scale[0] // 2, scale[1] // 2 - 64))
        surface.blit(text_surface, text_rect)

        # Button Geometry
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

        # Mouse interaction
        mouse_pos = pg.mouse.get_pos()
        mouse_pressed = pg.mouse.get_pressed()

        hovering = bg_rect.collidepoint(mouse_pos)

        # Button State Colors
        if hovering:
            if mouse_pressed[0]:  # Mouse button down
                color = play_again_color_hold
            else:
                color = play_again_color_hover
        else:
            color = play_again_color_base

        # Draw the button
        pg.draw.rect(surface, color, bg_rect, border_radius=8)
        surface.blit(button_surface, button_rect)

        # Detect mouse release (click)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                active = False
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if hovering:
                    # RESET GAME STATE
                    head_pos = [0, 0]
                    player_tail_quordenints = [[0, 0]]
                    apple_pos = [
                        randint(0, scale[0] // 50) * 50,
                        randint(0, scale[1] // 50) * 50,
                    ]
                    game_over = False

    # flip display
    pg.display.flip()

pg.quit()