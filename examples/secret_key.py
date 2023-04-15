import json
import pathlib

import base58

if __name__ == '__main__': print([int(entry) for entry in base58.b58decode(json.load(open(pathlib.Path(__file__).parent.parent / 'config.json'))['secret_key'])])