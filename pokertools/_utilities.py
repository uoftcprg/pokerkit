from functools import reduce
from operator import mul


def distinct(values):
    values = tuple(values)

    return len(values) == len(set(values))


def rotate(values, index):
    return values[index:] + values[:index]


def prod(values):
    return reduce(mul, values, 1)
