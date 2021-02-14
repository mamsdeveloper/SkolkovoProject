from itertools import zip_longest
from random import shuffle

keys_to_count={
                'W': 16, 'SPACE': 403, 'ESCAPE': 1,
                'D': 4, 'E': 2,
                'A': 4, 'S': 1,
                'F': 2, 'H': 11,
                'LWIN': 10001
            }

def _sort_keys():
    keys = list(keys_to_count.keys())
    sorted_keys = []

    short = filter(lambda x: len(x) == 1, keys)
    long = filter(lambda x: len(x) > 1, keys)

    alone_keys = []

    for l_key, s_key in zip_longest(long, short, fillvalue=None):
        if l_key:
            if len(l_key) % 2:
                sorted_keys += [(s_key, l_key)]
            else:
                sorted_keys += [(l_key, s_key)]
        else:
            alone_keys += [s_key]
    
    for grouped_key in zip(*[iter(alone_keys)] * 3):
        sorted_keys += [grouped_key]
    
    shuffle(sorted_keys)

    sorted_keys += alone_keys[-(len(alone_keys) % 3):]
    print(sorted_keys)

    result = {}

    for grouped_key in sorted_keys:
        for key in grouped_key:
            result.update({key: keys_to_count[key]})
    
    return result
    
            
print(_sort_keys())
