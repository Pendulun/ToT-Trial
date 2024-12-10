from timeit import default_timer as timer

PRINT_ENABLED = True


def timer_dec(func):

    def inner(*args, **kwargs):
        start = timer()
        result = func(*args, **kwargs)
        end = timer()
        if PRINT_ENABLED:
            print(func.__name__, end - start, " s")
        return result

    return inner
