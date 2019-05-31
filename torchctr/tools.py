import os
import time


def timmer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        res = func(*args, **kwargs)
        stop_time = time.time()
        print(f'Begin: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}\nfunc_name: {func.__name__}\nCost: {(stop_time - start_time):.4f}s')
        return res

    return wrapper


def num_cpus() -> int:
    "Get number of cpus"
    try:
        return len(os.sched_getaffinity(0))
    except AttributeError:
        return os.cpu_count()
