import time


def get_timestamp():
    return time.time_ns() // 1_000_000