from lib.config import *

if __name__ == '__main__':
    #save_config('config.json')
    print(str(EAT))
    load_config('config.json')
    print('-----')
    print(str(cfg['EAT']))
    print(str(EAT))