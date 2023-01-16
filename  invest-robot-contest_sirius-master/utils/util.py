import json
import logging
import os


def pretty_dict(val):
    return json.dumps(val, indent=2)


def write_dict_to_file(filename, dict_val):
    with open(filename, "w+") as f:
        f.write(json.dumps(dict_val))


def read_dict_from_file(filename):
    try:
        f = open(filename)
        data = json.load(f)
        f.close()
        return data
    except:
        return None


# TODO с деньгами так поступать нехорошо...
def price_to_float(units, nano):
    return float(units) + float(nano)/1000000000


def is_file_exists(filename):
    return os.path.exists(filename)


def delete_file_if_exists(filename):
    if is_file_exists(filename):
        os.remove(filename)
        logging.info("File '{}' has been deleted".format(filename))
