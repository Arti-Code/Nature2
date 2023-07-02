from json import loads

TITLE = "NATURE"
SUBTITLE = "v1.4.0" 
AUTHOR = "2019-2023 Artur Gwoździowski"

class Configuration():

    def __init__(self, filename: str):
        #self.norm_font = pygame.font.Font("res/fonts/fira.ttf", 12)
        #self.small_font = pygame.font.Font("res/fonts/fira.ttf", 8)
        self.WORLD = None
        self.SCREEN = None
        self.ITER = None
        self.FPS = None
        self.COLLIDE_TIME = None

        self.PLANT_MAX_SIZE = None
        self.PLANT_GROWTH = None
        self.PLANT_INIT_NUM = None
        self.PLANT_MIN_NUM = None
        self.PLANT_MAX_NUM = None
        self.PLANT_LIFE = None
        self.PLANT_RANGE = None
        self.PLANT_EDGE = None

        self.CREATURE_MULTIPLY = None
        self.CREATURE_MIN_NUM = None
        self.CREATURE_MAX_NUM = None
        self.CREATURE_INIT_NUM = None
        self.CREATURE_MIN_SIZE = None
        self.CREATURE_MAX_SIZE = None
        self.CREATURES_SEP = None

        self.BASE_ENERGY = None
        self.MOVE_ENERGY = None
        self.REP_ENERGY = None

        self.EAT = None
        self.SPEED = None
        self.HIDE_SPEED = None
        self.TURN = None
        self.HIT = None
        self.HIDE_MOD = None
        self.REP_TIME = None
        self.MEM_TIME = None
        self.MEAT_TIME = None

        self.MEMORY_SIZE_MAX = None

        self.SENSOR_MAX_ANGLE = None
        self.CLOSE_VISION = None

        self.ROCK_NUM = None
        self.ROCK_SIZE_MIN = None
        self.ROCK_SIZE_MAX = None
        self.ROCK_VERT_MIN = None

        self.RANK_SIZE = None
        self.SIZE2ENG = None
        self.SIZE_COST = None
        self.POWER_COST = None
        self.SPIKE_ENG = None
        self.CHILDS_NUM = None
        self.MEAT2ENG = None
        self.VEGE2ENG = None
        self.DMG2ENG = None
        self.HIT2FIT = None
        self.KILL2FIT = None
        self.VEGE2FIT = None
        self.MEAT2FIT = None
        self.DIFF = None
        self.AUTO_SAVE_TIME = None
        self.ATK_ENG = None
        self.EAT_ENG = None
        self.LINKS_RATE = None
        self.MUTATIONS = None
        self.DEL_LINK = None
        self.DEL_NODE = None
        self.TIME = None
        self.BORN2FIT = None
        self.RUN_TIME = None
        self.RUN_COST = None
        self.DIET_MOD = None
        self.SENSOR_RANGE = None
        self.NET = None
        self.RANK_DECAY = None
        self.STAT_PERIOD = None
        self.NEURON_MOD = None
        self.NET_BASE = None
        self.GENERATIONS_NUMBER = None
        self.NEURO_COST = None
        self.GRAPH_H = None
        self.GRAPH_V = None
        self.load_from_file(filename)

    def load_from_file(self, filename: str):
        f = open(filename, 'r')
        json_cfg = f.read()
        f.close()
        cfg = loads(json_cfg)
        for param in cfg:
            self.__setattr__(param, cfg[param])

cfg = Configuration('config.json')