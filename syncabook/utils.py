import math


def get_number_of_digits_to_name(num):
    if num <= 0:
        return 0

    return math.floor(math.log10(num)) + 1


def drop_extension(filename):
    return filename.split('.')[0]


def format_duration(tdelta):
    hours = int(tdelta.total_seconds()) // 3600
    minutes = int(tdelta.total_seconds() % 3600) // 60
    seconds = int(tdelta.total_seconds()) % 60
    ms = int(tdelta.microseconds) // 1000
    return f'{hours:d}:{minutes:0>2d}:{seconds:0>2d}.{ms:0>3d}'
