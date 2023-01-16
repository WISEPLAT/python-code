import keyring
import argparse
"""
Tool for storage sensitive data (pass, keys, tokens in security storage
"""

parser = argparse.ArgumentParser(description='')
parser.add_argument('-API_TOKEN', type=str, help='API TOKEN for TINKOFF Invest')
parser.add_argument('-SAND_BOX', type=str, help='SAND BOX API TOKEN for TINKOFF Invest')


STORAGE = 'TINKOFF_API'
TINKOFF_API_TOKEN = 'TINKOFF_API_TOKEN'
TINKOFF_API_SAND_BOX_TOKEN = 'TINKOFF_API_SAND_BOX_TOKEN'


def setKeys(name, key):
    keyring.set_password(STORAGE, name, key)


def readKeys(config):
    combat_mode = True if config.get(section='main', option='combat_mode') == 'True' else False
    if combat_mode:
        return keyring.get_password(STORAGE, TINKOFF_API_TOKEN)
    else:
        return keyring.get_password(STORAGE, TINKOFF_API_SAND_BOX_TOKEN)


def main(args):
    if args.API_TOKEN:
        setKeys(TINKOFF_API_TOKEN, args.API_TOKEN)

    if args.SAND_BOX:
        setKeys(TINKOFF_API_SAND_BOX_TOKEN, args.SAND_BOX)


if __name__ == '__main__':
    main(parser.parse_args())



