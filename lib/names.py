from random import choice

names: list = [
    'am','af', 'ax', 'ar', 'av', 'al', 'aq', 'ak', 'ar', 'at',
    'ma', 'mi', 'me', 'mo', 'mu',
    'ju', 'ja', 'ji', 'jy',
    'da', 'de', 'dy', 'di',
    'so', 'su', 'sa', 'si', 'se', 'sy', 'sl', 'sj', 'ss', 'sk', 'sr', 'st', 'sq', 'sf', 'sn',
    'ne', 'na', 'ni', 'no', 'ny', 'nu',
    'vu', 'va', 'vi', 'vo', 'vy', 'vu',
    'xi', 'xa', 'xu', 'xe', 'xo', 'xy', 'xs', 'xi',
    'pa', 'pi', 
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
    'hu', 
    'sy', 'so', 'se',
    'tu', 'ta', "to", "ty", "tu", "te", "to", "tv", "te", "td", "tf", "t-", "th", "ti", "tj", "tk", "tl", "tr", "ts", "tz", "tw", "tt", "tu", "tp",
    'zo', 'zu', 'zi', 'za', 'ze', 'zi'
]

def random_name(length: int=3, upper: bool=False) -> str:
    name: str=''
    for i in range(length):
        name += choice(names)
    if upper:
        return name.upper()
    return name