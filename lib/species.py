from random import choice, random

names: list = [
    'am','af', 'ax', 'ar', 'av', 'al', 'aq', 'ak', 'ar', 'at',
    'ma', 'mi', 'me', 'mo', 'mu',
    'ju', 'ja', 'ji', 'jy',
    'da', 'de', 'dy', 'di',
    'so', 'su', 'sa', 'si', 'se', 'sy', 'sl', 'sj', 'ss', 'sk', 'sr', 'st', 'sq', 'sf', 'sn',
    'ne', 'na', 'ni', 'no', 'ny', 'nu',
    'vu', 'va', 'vi', 'vo', 'vy', 'vu',
    'xi', 'xa', 'xu', 'xe', 'xo', 'xy', 'xs', 'xi',
    'pu', 'pa', "po", "py", "pu", "pe", "po", "pv", "pe", "pd", "pf", "pf", "ph", "pi", "pj", "pk", "pl", "pr", "ps", "pz", "pw", "pp", "pu", "pt",
    'li', 'lo', 
    'ko', 'ka', 'ku', 'ki', 'ke', 'ko',
    're', 'ra', 'ry', 'ri', 'ru',
    'fu', 'fa','fi', 
    'zu', 'za', 'zi', 
    'ol', 'oi', 'oj', 'od', 'os', 'ot', 'ok', 'on', 'om', 'oc', 'ox', 'oz', 'op',
    'ip', 
    'wu', 'wi', 
    'zy', 'zu', 'zo',
    'qe', 'qi', 'qu', 
    'uo', 'ui', 'ua', 'us', 'ud', 'uf', 'ug', 'uh', 'uj', 'uk', 'ul',
    'hu', 'ha', "ho", "hy", "hu", "he", "ho", "hv", "he", "hd", "hf", "hf", "ht", "hi", "hj", "hk", "hl", "hr", "hs", "hz", "hw", "hh", "hu", "hp", 
    'sy', 'so', 'se',
    'tu', 'ta', "to", "ty", "tu", "te", "to", "tv", "te", "td", "tf", "tf", "th", "ti", "tj", "tk", "tl", "tr", "ts", "tz", "tw", "tt", "tu", "tp",
    'zo', 'zu', 'zi', 'za', 'ze', 'zi'
]

def random_name(length: int=3, upper: bool=False) -> str:
    name: str=''
    for i in range(length):
        name += choice(names)
    if upper:
        return name.upper()
    return name

def modify_name(name: str) -> str:
    ch = random_name(1, True)
    rnd = random()
    if rnd <= 0.5:
        new_name = name[0:4]+ch
    elif rnd <= 0.85:
        new_name = name[0:2]+ch+name[4:6]
    else:
        new_name = ch + name[2:6]
    return new_name