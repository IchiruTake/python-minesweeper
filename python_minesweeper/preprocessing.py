from time import time
from typing import Tuple, Union, List, Optional, Callable
from logging import warning
from numpy import ndarray


def measure_execution_time(Function: Callable):
    def compute(*args, **kwargs):
        start = time()
        result = Function(*args, **kwargs)
        print("Executing Time ({}): {:.6f}s".format(Function, time() - start))
        return result
    return compute


def object_memory_profiler(Object: object, verbose: bool = True, sorting_mode: bool = True,
                           descending: bool = True) -> None:
    # Hyper-parameter Verification
    if True:
        if not isinstance(verbose, bool):
            warning(" In-valid Hyper-parameter. Setting verbose to be True")
            verbose = True

        if not isinstance(sorting_mode, bool):
            warning(" In-valid Hyper-parameter. Setting sorting_mode to be True")
            sorting_mode = True

        if not isinstance(descending, bool):
            warning(" In-valid Hyper-parameter. Setting descending to be True")
            descending = True
        pass

    from sys import getsizeof
    print("=" * 30, "Memory Profiler", "=" * 30)
    total: int = 0
    numpy_total: int = 0
    arr = []
    for name in Object.__dict__:
        obj = getattr(Object, name)
        size = obj.nbytes if isinstance(obj, ndarray) else getsizeof(obj)
        total += size
        if isinstance(obj, ndarray):
            numpy_total += size

        if verbose is True and sorting_mode is False:
            msg = "{} ({}): \t\t\t\t{} bytes --> Shape: {}".format(name, type(obj), size, obj.shape) \
                if isinstance(obj, ndarray) else "{} ({}): \t\t\t\t{} bytes".format(name, type(obj), size)
            print(msg)

        arr.append([name, type(obj), size])
    if sorting_mode is True and verbose is True:
        arr.sort(key=lambda item: int(item[2]), reverse=descending)
        for name, dtype, size in arr:
            msg = "{} ({}): \t\t\t\t{} bytes --> Shape: {}".format(name, dtype, size, getattr(Object, name).shape) \
                if isinstance(getattr(Object, name), ndarray) else "{} ({}): \t\t\t\t{} bytes".format(name, dtype, size)
            print(msg)

    print("-" * 80)
    percentage: float = numpy_total / total
    print("Attribute Memory: {} bytes ({} MB - {} GB)"
          .format(total, round(total / (1024 * 1024), 6), round(total / (1024 * 1024 * 1024), 6)))
    print("Numpy Attribute Memory: {} bytes ({} MB - {} GB) ---> Percentage: {} %"
          .format(numpy_total, round(numpy_total / (1024 * 1024), 6),
                  round(numpy_total / (1024 * 1024 * 1024), 6), round(100 * percentage, 6)))
    print("Remaining Memory: {} bytes ({} MB - {} GB) ---> Percentage: {} %"
          .format(total - numpy_total, round((total - numpy_total) / (1024 * 1024), 6),
                  round((total - numpy_total) / (1024 * 1024 * 1024), 6), round(100 * (1 - percentage), 6)))


def timing_profiler(Function: Callable):
    def compute(*args, **kwargs):
        from cProfile import Profile
        profiler = Profile()
        profiler.enable()
        result = Function(*args, **kwargs)
        profiler.disable()
        profiler.print_stats(sort=True)
        return result
    return compute


def binarySearch(array: List[int], value: int) -> int:
    if array:
        start, end = 0, len(array)
        while start <= end:
            mid = (start + end) // 2
            if value < array[mid]:
                end = mid
            elif value > array[mid]:
                start = mid
            else:
                return mid
        return -1
    return -1
