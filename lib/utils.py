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

class Timer():

    def __init__(self, interval: float, one_shoot: bool=True, autostart: bool=False, label: str=None):
        self.time = 0
        self.run: bool=autostart
        self.interval = interval
        self.one_shoot = one_shoot
        self.label = label

    def timeout(self, delta: float) -> bool:
        if not self.run:
            return False
        self.time += delta
        if self.time < self.interval:
            return False
        self.time = 0
        if self.one_shoot:
            self.run = False
        return True

    def stop(self):
        self.run = False

    def start(self):
        self.run = True

    def restart(self):
        self.time = 0
        self.run = True

    def set_timer(self, interval: float, one_shoot: bool=True):
        self.time = 0
        self.run: True
        self.interval = interval
        self.one_shoot = one_shoot
        

