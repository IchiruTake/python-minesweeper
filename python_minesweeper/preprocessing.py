from time import time
from typing import Tuple, Union, List, Optional, Callable
from logging import warning
from numpy import ndarray
import pandas as pd


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


def FixPath(FileName: str, extension: str):
    if not isinstance(FileName, str):
        raise TypeError("FileName must be string")

    if not isinstance(extension, str):
        raise TypeError("extension must be string")

    return FileName + extension if FileName.rfind(extension) != len(FileName) - len(extension) else FileName


def ReadFile(FilePath: Optional[str], header: Optional[int] = 0, dtype=None, get_values: bool = False,
             get_columns: bool = False, nrows: Optional[int] = None, blocksize: Union[float, int] = 64e6,
             dtypes_memory_identifier: Union[float, int] = 1, usecols: Union[List[int], List[str]] = None,
             skiprows: Optional[Union[List, int]] = None) \
        -> Optional[Union[pd.DataFrame, List, ndarray, Tuple[ndarray, List]]]:
    """
    Default implementation used to call a .csv documentation.
    1 MiB = 2^10 KiB = 2^20 bytes = 1048576 bytes
    1 MB = 10^3 KB = 10^6 bytes = 1000000 bytes

    :param FilePath: The path contained the .csv file. This hyper-parameter does not need extension name as
                     it have to be checked directly before accessing pandas library (str).
    :type FilePath: str

    :param header: The position of column name used as label/features identifier (int). Default to 0.
    :type header: int

    :param dtype: pandas dtype // numpy.dtype
    :type dtype: dtype

    :param get_values: Whether to get values only
    :type get_values: bool

    :param get_columns: Whether to get columns only
    :type get_columns: bool

    :param nrows: number of rows for computing
    :type nrows: Optional[int]

    :param skiprows: number of rows or row's position for skipping
    :type skiprows: Optional[Union[List, int]]

    :param usecols: number of rows or row's position for skipping
    :type usecols: Optional[Union[List, int]]

    :param blocksize: The chunking memory for paralleling (Dask Library), Default to be 64 MB
    :type blocksize: float or int

    :param dtypes_memory_identifier: The coefficient memory adding when reading csv by Dask Library (default to be 1).
                                     Base case: 1 MiB (mebibytes)
    :type dtypes_memory_identifier: float or int

    :return: pd.DataFrame
    """
    if True:
        if FilePath is None or FilePath == "":
            return None

        if not isinstance(get_values, bool):
            raise TypeError("get_values must be boolean")

        if not isinstance(get_columns, bool):
            raise TypeError("get_columns must be boolean")

        if not isinstance(FilePath, str):
            raise TypeError("FilePath must be a string")

        pass

    FilePath: str = FixPath(FileName=FilePath, extension=".csv")
    File: pd.DataFrame = pd.read_csv(FilePath, dtype=dtype, nrows=nrows, skiprows=skiprows, usecols=usecols,
                                     header=header, low_memory=True, cache_dates=False)

    if get_values is False and get_columns is False:
        return File
    elif get_values is False and get_columns is True:
        return File.columns.tolist()
    elif get_values is True and get_columns is False:
        return File.to_numpy()

    return File.to_numpy(), File.columns.tolist()


def ExportFile(DataFrame: pd.DataFrame, FilePath: str, index: bool = False, index_label: Optional[str] = None) -> None:
    """
    Default implementation used to return the .csv documentation from DataFrame
    :param DataFrame: The DataFrame needs for creating the .csv file (pd.DataFrame).
    :type DataFrame: pd.DataFrame

    :param FilePath: The path contained the .csv file. This hyper-parameter does not need extension name as it have to
                     be checked directly before accessing pandas library (str).
    :type FilePath: str

    :param index: The implicit array-like used for row indexing (Array-like). Default to False
    :type index: List[str] or Tuple[str] or bool or List[int] or Tuple[int]

    :param index_label: The name of index column
    :type index_label: str or None

    :return: None
    """
    if not isinstance(DataFrame, pd.DataFrame):
        raise TypeError("DataFrame must be a DataFrame")
    if FilePath is not None:
        if not isinstance(FilePath, str):
            raise TypeError("FilePath must be a string")
        FilePath = FixPath(FileName=FilePath, extension=".csv")
        DataFrame.to_csv(FilePath, index=index, index_label=index_label)
