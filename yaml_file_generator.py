import yaml
import redis
from commandr import command, Run
from pprint import pprint

server = redis.Redis(host='localhost', port=6379)

rank_types = ["topselling_paid", "topselling_free", "topgrossing"]
host = "https://play.google.com"
url_stub = ("{host}/store/apps/category/{cat}/colle"
            "ction/{rank_type}?hl=en&gl={gl}")


def get_country_code():
    country_redis_name = 'country_code'
    country2code = server.hgetall(country_redis_name)
    data = {}
    for k, v in country2code.iteritems():
        k = k.lower()
        v = v.lower()
        data[k] = v
    return data

def get_categories():
    cat_redis_name = 'GoogleStoreCategory'
    cat2value = server.hgetall(cat_redis_name)
    data = {}
    for k, v in cat2value.iteritems():
        k = k.lower()
        v = k.upper()
        data[k] = v
    return data


@command('print_country_code')
def print_country_code():
    codes = get_country_code()
    pprint(codes)


@command('print_categories')
def print_categories():
    cats = get_categories()
    pprint(cats)

# Google Store Yaml
"""
data:
    country_codes: {
    },
    categories: {
        'lower': 'LOWER',
    },
"""


@command('save_yaml')
def save_yaml():
    cnt2code = get_country_code()
    cat2cat = get_categories()
    data = {
        'data': {
            'country2code': cnt2code,
            'category2category': cat2cat,
        },
    }
    stream = file('google_store.yaml', 'w')
    yaml.dump(data, stream)
    stream.close()


if __name__ == '__main__':
    Run()
