from lib.config import cfg, load_config

if __name__ == '__main__':
    #save_config('config.json')
    load_config('config.json')
    print(str(cfg['EAT']))