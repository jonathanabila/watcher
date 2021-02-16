import multiprocessing
import os
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


def threader(target, jobs, pool_size):
    results_list = list()

    jobs_queue = multiprocessing.Queue()
    results_queue = multiprocessing.Queue()

    pool = [
        multiprocessing.Process(target=target, args=(jobs_queue, results_queue))
        for _ in range(pool_size)
    ]

    for p in pool:
        p.start()

    for i in jobs:
        jobs_queue.put(i)

    for _ in pool:
        jobs_queue.put(None)

    for p in pool:
        p.join()

    while not results_queue.empty():
        result = results_queue.get()
        results_list.append(result)

    return results_list


def clean_terminal():
    os.system("cls") if "nt" in os.name else os.system("clear")


def prettify(value):
    """
    bytes to mb
    """
    return round(value / (1024 * 1024 * 1024), 2)
