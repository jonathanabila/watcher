import pygame


def handle_quit(event):
    pressed_keys = pygame.key.get_pressed()

    alt_pressed = pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT]
    alt_f4 = alt_pressed and event.type == pygame.KEYDOWN and event.key == pygame.K_F4

    escape = event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE

    x_button = event.type == pygame.QUIT

    return x_button or alt_f4 or escape
