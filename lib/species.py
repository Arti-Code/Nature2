from random import choice, random

names: list = [
    'am','af', 'ax', 'ar', 'av', 'al', 'aq', 'ak', 'ar', 'at',
    'mu', 'ma', "mo", "my", "mu", "me", "mo", "mv", "me", "md", "mf", "mf", "mt", "mi", "mj", "mk", "ml", "mr", "ms", "mz", "mw", "mm", "mu", "mp",
    'ju', 'ja', "jo", "jy", "ju", "je", "jo", "jv", "je", "jd", "jf", "jf", "jt", "ji", "jj", "jk", "jl", "jr", "js", "jz", "jw", "jj", "ju", "jp",
    'du', 'da', "do", "dy", "du", "de", "do", "dv", "de", "dd", "df", "df", "dt", "di", "dj", "dk", "dl", "dr", "ds", "dz", "dw", "dd", "du", "dp",
    'so', 'su', 'sa', 'si', 'se', 'sy', 'sl', 'sj', 'ss', 'sk', 'sr', 'st', 'sq', 'sf', 'sn',
    'nu', 'na', "no", "ny", "nu", "ne", "no", "nv", "ne", "nd", "nf", "nf", "nt", "ni", "nj", "nk", "nl", "nr", "ns", "nz", "nw", "nn", "nu", "np",
    'vu', 'va', "vo", "vy", "vu", "ve", "vo", "vv", "ve", "vd", "vf", "vf", "vt", "vi", "vj", "vk", "vl", "vr", "vs", "vz", "vw", "vv", "vu", "vp",
    'xu', 'xa', "xo", "xy", "xu", "xe", "xo", "xv", "xe", "xd", "xf", "xf", "xt", "xi", "xj", "xk", "xl", "xr", "xs", "xz", "xw", "xx", "xu", "xp",
    'pu', 'pa', "po", "py", "pu", "pe", "po", "pv", "pe", "pd", "pf", "pf", "pj", "pi", "pj", "pk", "pl", "pr", "ps", "pz", "pw", "pp", "pu", "pt",
    'lu', 'la', "lo", "ly", "lu", "le", "lo", "lv", "le", "ld", "lf", "lf", "lt", "li", "lj", "lk", "ll", "lr", "ls", "lz", "lw", "ll", "lu", "lp", 
    'ku', 'ka', "ko", "ky", "ku", "ke", "ko", "kv", "ke", "kd", "kf", "kf", "kt", "ki", "kj", "kk", "kl", "kr", "ks", "kz", "kw", "kk", "ku", "kp",
    'ru', 'ra', "ro", "ry", "ru", "re", "ro", "rv", "re", "rd", "rf", "rf", "rt", "ri", "rj", "rk", "rl", "rr", "rs", "rz", "rw", "rr", "ru", "rp",
    'fu', 'fa', "fo", "fy", "fu", "fe", "fo", "fv", "fe", "fd", "ff", "ff", "ft", "fi", "fj", "fk", "fl", "fr", "fs", "fz", "fw", "ff", "fu", "fp", 
    'ol', 'oi', 'oj', 'od', 'os', 'ot', 'ok', 'on', 'om', 'oc', 'ox', 'oz', 'op',
    'iu', 'ia', "io", "iy", "iu", "ie", "io", "iv", "ie", "id", "if", "if", "it", "ii", "ij", "ik", "il", "ir", "is", "iz", "iw", "ii", "iu", "ip",
    'wu', 'wa', "wo", "wy", "wu", "we", "wo", "wv", "we", "wd", "wf", "wf", "wt", "wi", "wj", "wk", "wl", "wr", "ws", "wz", "ww", "ww", "wu", "wp",
    'bu', 'ba', "bo", "by", "bu", "be", "bo", "bv", "be", "bd", "bf", "bf", "bt", "bi", "bj", "bk", "bl", "br", "bs", "bz", "bw", "bb", "bu", "bp",
    'qu', 'qa', "qo", "qy", "qu", "qe", "qo", "qv", "qe", "qd", "qf", "qf", "qt", "qi", "qj", "qk", "ql", "qr", "qs", "qz", "qw", "qq", "qu", "qp", 
    'uo', 'ui', 'ua', 'us', 'ud', 'uf', 'ug', 'ug', 'uj', 'uk', 'ul',
    'hu', 'ha', "ho", "hy", "hu", "he", "ho", "hv", "he", "hd", "hf", "hf", "ht", "hi", "hj", "hk", "hl", "hr", "hs", "hz", "hw", "hh", "hu", "hp", 
    'su', 'sa', "so", "sy", "su", "se", "so", "sv", "se", "sd", "sf", "sf", "st", "si", "sj", "sk", "sl", "sr", "ss", "sz", "sw", "ss", "su", "sp",
    'tu', 'ta', "to", "ty", "tu", "te", "to", "tv", "te", "td", "tf", "tf", "th", "ti", "tj", "tk", "tl", "tr", "ts", "tz", "tw", "tt", "tu", "tp",
    'zu', 'za', "zo", "zy", "zu", "ze", "zo", "zv", "ze", "zd", "zf", "zf", "zt", "zi", "zj", "zk", "zl", "zr", "zs", "zz", "zw", "zz", "zu", "zp"
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