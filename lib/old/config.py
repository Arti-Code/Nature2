from math import pi as PI
from json import loads, dumps


TITLE = 'NATURE v0.4.5'
SUBTITLE = "2019-2021 Artur Gwoździowski"
#WORLD                       = (1500, 750)
#SCREEN                      = (1500, 750)
#FONT_SIZE                   = 12
WORLD                       = (1900, 1000)
SCREEN                      = (1900, 1000)
FONT_SIZE                   = 14
PLANT_MAX_SIZE              = 10
PLANT_GROWTH                = 0.3
PLANT_INIT_NUM              = 50
PLANT_LIFE                  = 500
PLANT_MULTIPLY              = 0.01
CREATURE_MULTIPLY           = 0.001
CREATURE_MIN_NUM            = 16
EAT                         = 200
CREATURE_INIT_NUM           = 75
BASE_ENERGY                 = 0.001
MOVE_ENERGY                 = 0.001
REP_TIME                    = 60
REP_ENERGY                  = 0.25
SPEED                       = 1
TURN                        = 0.18
SENSOR_SPEED                = 0.8
CREATURE_MIN_SIZE           = 3
CREATURE_MAX_SIZE           = 12
HIT                         = 220
MEM_TIME                    = 0.3
SENSOR_MAX_ANGLE            = PI/3
ROCK_NUM                    = 16
RANK_SIZE                   = 20
MEAT_TIME                   = 30
VISUAL_RANGE                = 200
SIZE2ENG                    = 80
SIZE_COST                   = 0.3
CHILDS_NUM                  = 1
# colors
BROWN = (110, 50, 9)
LIME = (127, 255, 0)


def log_to_file(msg: str, filename: str):
    f = open(filename, 'a')
    f.write(msg+"\n")
    f.close()

def load_config(filename: str):
    f = open(filename, 'r')
    json_cfg = f.read()
    f.close()
    global cfg
    cfg = loads(json_cfg)
    global PLANT_MAX_SIZE, PLANT_GROWTH, PLANT_INIT_NUM, PLANT_LIFE, PLANT_MULTIPLY, CREATURE_MULTIPLY, CREATURE_MIN_NUM, EAT, CREATURE_INIT_NUM, BASE_ENERGY, MOVE_ENERGY
    global REP_TIME, REP_ENERGY, SPEED, TURN, SENSOR_SPEED, REPRODUCTION_TIME, CREATURE_MIN_SIZE, CREATURE_MAX_SIZE, HIT, MEM_TIME, SENSOR_MAX_ANGLE, ROCK_NUM
    global RANK_SIZE, MEAT_TIME, VISUAL_RANGE, SIZE2ENG, SIZE_COST, CHILDS_NUM
    PLANT_MAX_SIZE              = cfg['PLANT_MAX_SIZE']
    PLANT_GROWTH                = cfg['PLANT_GROWTH']
    PLANT_INIT_NUM              = cfg['PLANT_INIT_NUM']
    PLANT_LIFE                  = cfg['PLANT_LIFE']
    PLANT_MULTIPLY              = cfg['PLANT_MULTIPLY']
    CREATURE_MULTIPLY           = cfg['CREATURE_MULTIPLY']
    CREATURE_MIN_NUM            = cfg['CREATURE_MIN_NUM']
    global EAT
    EAT                         = cfg['EAT']
    CREATURE_INIT_NUM           = cfg['CREATURE_INIT_NUM']
    BASE_ENERGY                 = cfg['BASE_ENERGY']
    MOVE_ENERGY                 = cfg['MOVE_ENERGY']
    REP_TIME                    = cfg['REP_TIME']
    REP_ENERGY                  = cfg['REP_ENERGY']
    SPEED                       = cfg['SPEED']
    TURN                        = cfg['TURN']
    SENSOR_SPEED                = cfg['SENSOR_SPEED']
    REPRODUCTION_TIME           = cfg['REPRODUCTION_TIME']
    CREATURE_MIN_SIZE           = cfg['CREATURE_MIN_SIZE']
    CREATURE_MAX_SIZE           = cfg['CREATURE_MAX_SIZE']
    HIT                         = cfg['HIT']
    MEM_TIME                    = cfg['MEM_TIME']
    SENSOR_MAX_ANGLE            = cfg['SENSOR_MAX_ANGLE']
    ROCK_NUM                    = cfg['ROCK_NUM']
    RANK_SIZE                   = cfg['RANK_SIZE']
    MEAT_TIME                   = cfg['MEAT_TIME']
    VISUAL_RANGE                = cfg['VISUAL_RANGE']
    SIZE2ENG                    = cfg['SIZE2ENG']
    SIZE_COST                   = cfg['SIZE_COST']
    CHILDS_NUM                  = cfg['CHILDS_NUM']

def save_config(filename: str):
    cfg: dict = {}
    cfg['PLANT_MAX_SIZE']       = 16               
    cfg['PLANT_GROWTH']         = 0.4    
    cfg['PLANT_INIT_NUM']       = 50        
    cfg['PLANT_LIFE']           = 300    
    cfg['PLANT_MULTIPLY']       = 0.02        
    cfg['CREATURE_MULTIPLY']    = 0.001            
    cfg['CREATURE_MIN_NUM']     = 10        
    cfg['EAT']                  = 200
    cfg['CREATURE_INIT_NUM']    = 50            
    cfg['BASE_ENERGY']          = 0.001    
    cfg['MOVE_ENERGY']          = 0.0025    
    cfg['REP_TIME']             = 60
    cfg['REP_ENERGY']           = 0.25    
    cfg['SPEED']                = 1
    cfg['TURN']                 = 0.1
    cfg['SENSOR_SPEED']         = 1    
    cfg['REPRODUCTION_TIME']    = 60            
    cfg['CREATURE_MIN_SIZE']    = 3            
    cfg['CREATURE_MAX_SIZE']    = 10            
    cfg['HIT']                  = 150
    cfg['MEM_TIME']             = 0.3
    cfg['SENSOR_MAX_ANGLE']     = PI/3        
    cfg['ROCK_NUM']             = 7
    cfg['RANK_SIZE']            = 10    
    cfg['MEAT_TIME']            = 30    
    cfg['VISUAL_RANGE']         = 180    
    cfg['SIZE2ENG']             = 80
    cfg['SIZE_COST']            = 0.2    
    cfg['CHILDS_NUM']           = 1    
    json_cfg = dumps(cfg)
    f = open(filename, 'w')
    f.write(json_cfg)
    f.close()


class Configuration():

    def __init__(self, filename: str=None):
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
        self.DIFF                   = cfg['DIFF'] 



cfg = Configuration('config.json')