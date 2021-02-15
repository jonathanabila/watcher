import time
from functools import wraps

import pygame


def handle_quit(event):
    pressed_keys = pygame.key.get_pressed()

    alt_pressed = pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT]
    alt_f4 = alt_pressed and event.type == pygame.KEYDOWN and event.key == pygame.K_F4

    escape = event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE

    x_button = event.type == pygame.QUIT

    return x_button or alt_f4 or escape


def scheduler_timer(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        start_time, start_clock = time.time(), time.perf_counter()
        result = f(*args, **kwargs)

        print(f"Before: Time: {start_time} - Clock: {start_clock}")
        print(f"After: Time: {time.time()} - Clock: {time.perf_counter()}")
        return result

    return wrap
