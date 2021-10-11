from enum import Enum, IntEnum

def log_to_file(msg: str, filename: str):
    f = open(filename, 'a')
    f.write(msg+"\n")
    f.close()

class Detection(IntEnum):
    CREATURE = 1
    PLANT = 2
    MEAT = 3
    ROCK = 4