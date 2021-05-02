from time import time
from typing import Callable


def measure_execution_time(Function: Callable):
    # Decorator Function
    def compute(*args, **kwargs):
        start = time()
        result = Function(*args, **kwargs)
        print("Executing Time: {:.6f}s".format(time() - start))
        return result
    return compute