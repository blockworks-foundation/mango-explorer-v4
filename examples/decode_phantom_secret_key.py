import base58
import json
import pathlib


def main():
    print([int(entry) for entry in base58.b58decode(json.load(open(pathlib.Path(__file__).parent.parent / 'config.json'))['secret_key'])])


if __name__ == '__main__':
    main()