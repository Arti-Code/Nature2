from math import pi as PI
from json import loads, dumps

TITLE = "NATURE"
SUBTITLE = "v0.5.3"
AUTHOR = "2019-2021 Artur Gwoździowski"

class Configuration():

    def __init__(self, filename: str):
        self.WORLD = None
        self.SCREEN = None
        self.FONT_SIZE = None
        self.PLANT_MAX_SIZE = None
        self.PLANT_GROWTH = None
        self.PLANT_INIT_NUM = None
        self.PLANT_LIFE = None
        self.PLANT_MULTIPLY = None
        self.CREATURE_MULTIPLY = None
        self.CREATURE_MIN_NUM = None
        self.EAT = None
        self.CREATURE_INIT_NUM = None
        self.BASE_ENERGY = None
        self.MOVE_ENERGY = None
        self.REP_TIME = None
        self.REP_ENERGY = None
        self.SPEED = None
        self.TURN = None
        self.SENSOR_SPEED = None
        self.CREATURE_MIN_SIZE = None
        self.CREATURE_MAX_SIZE = None
        self.HIT = None
        self.MEM_TIME = None
        self.SENSOR_MAX_ANGLE = None
        self.ROCK_NUM = None
        self.RANK_SIZE = None
        self.MEAT_TIME = None
        self.VISUAL_RANGE = None
        self.SIZE2ENG = None
        self.SIZE_COST = None
        self.CHILDS_NUM = None
        self.MEAT2ENG = None
        self.VEGE2ENG = None
        self.HIT2FIT = None
        self.KILL2FIT = None
        self.VEGE2FIT = None
        self.MEAT2FIT = None
        self.DIFF: float
        self.AUTO_SAVE_TIME = None
        self.ATK_ENG = None
        self.EAT_ENG = None
        self.LINKS_RATE = None
        self.MUTATIONS = None
        self.TIME = None
        self.BORN2FIT = None
        self.RUN_TIME = None
        self.RUN_COST = None
        self.DIET_MOD = None
        self.SENSOR_RANGE = None
        self.MIN_CARNIVORES = None
        self.MIN_HERBIVORES = None
        self.NET = None
        self.RANK_DECAY = None
        self.STAT_PERIOD = None
        self.MAP_RES = None
        self.WATER_MOVE = None
        self.WATER_COST = None
        self.WATER = None
        self.load_from_file(filename)

    def load_from_file(self, filename: str):
        f = open(filename, 'r')
        json_cfg = f.read()
        f.close()
        cfg = loads(json_cfg)
        self.WORLD                  = cfg['WORLD']
        self.SCREEN                 = cfg['SCREEN']
        self.FONT_SIZE              = cfg['FONT_SIZE']
        self.PLANT_MAX_SIZE         = cfg['PLANT_MAX_SIZE']
        self.PLANT_GROWTH           = cfg['PLANT_GROWTH']
        self.PLANT_INIT_NUM         = cfg['PLANT_INIT_NUM']
        self.PLANT_LIFE             = cfg['PLANT_LIFE']
        self.PLANT_MULTIPLY         = cfg['PLANT_MULTIPLY']
        self.CREATURE_MULTIPLY      = cfg['CREATURE_MULTIPLY']
        self.CREATURE_MIN_NUM       = cfg['CREATURE_MIN_NUM']
        self.EAT                    = cfg['EAT']
        self.CREATURE_INIT_NUM      = cfg['CREATURE_INIT_NUM']
        self.BASE_ENERGY            = cfg['BASE_ENERGY']
        self.MOVE_ENERGY            = cfg['MOVE_ENERGY']
        self.REP_TIME               = cfg['REP_TIME']
        self.REP_ENERGY             = cfg['REP_ENERGY']
        self.SPEED                  = cfg['SPEED']
        self.TURN                   = cfg['TURN']
        self.SENSOR_SPEED           = cfg['SENSOR_SPEED']
        self.CREATURE_MIN_SIZE      = cfg['CREATURE_MIN_SIZE']
        self.CREATURE_MAX_SIZE      = cfg['CREATURE_MAX_SIZE']
        self.HIT                    = cfg['HIT']
        self.MEM_TIME               = cfg['MEM_TIME']
        self.SENSOR_MAX_ANGLE       = cfg['SENSOR_MAX_ANGLE']
        self.ROCK_NUM               = cfg['ROCK_NUM']
        self.RANK_SIZE              = cfg['RANK_SIZE']
        self.MEAT_TIME              = cfg['MEAT_TIME']
        self.VISUAL_RANGE           = cfg['VISUAL_RANGE']
        self.SIZE2ENG               = cfg['SIZE2ENG']
        self.SIZE_COST              = cfg['SIZE_COST']
        self.CHILDS_NUM             = cfg['CHILDS_NUM']
        self.MEAT2ENG               = cfg['MEAT2ENG']
        self.VEGE2ENG               = cfg['VEGE2ENG']
        self.HIT2FIT                = cfg['HIT2FIT']
        self.KILL2FIT               = cfg['KILL2FIT']
        self.DIFF                   = cfg['DIFF']
        self.VEGE2FIT               = cfg['VEGE2FIT']
        self.MEAT2FIT               = cfg['MEAT2FIT'] 
        self.AUTO_SAVE_TIME         = cfg['AUTO_SAVE_TIME']
        self.ATK_ENG                = cfg['ATK_ENG']
        self.EAT_ENG                = cfg['EAT_ENG']
        self.LINKS_RATE             = cfg['LINKS_RATE']
        self.MUTATIONS              = cfg['MUTATIONS']
        self.TIME                   = cfg['TIME']
        self.BORN2FIT               = cfg['BORN2FIT']
        self.RUN_TIME               = cfg['RUN_TIME']
        self.RUN_COST               = cfg['RUN_COST']
        self.DIET_MOD               = cfg['DIET_MOD']
        self.SENSOR_RANGE           = cfg['SENSOR_RANGE']
        self.MIN_CARNIVORES         = cfg['MIN_CARNIVORES']
        self.MIN_HERBIVORES         = cfg['MIN_HERBIVORES']
        self.NET                    = cfg['NET']
        self.RANK_DECAY             = cfg['RANK_DECAY']
        self.STAT_PERIOD            = cfg['STAT_PERIOD']
        self.MAP_RES                = cfg['MAP_RES']
        self.WATER_MOVE             = cfg['WATER_MOVE']
        self.WATER_COST             = cfg['WATER_COST']
        self.WATER_NEEDS            = cfg['WATER_NEEDS']
        self.WATER                  = cfg['WATER']

cfg = Configuration('config.json')