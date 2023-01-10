import json
import os
from pathlib import Path
import random


def load_jsons(json_dir: Path):
    def get_repo_num(x):
        x = x.stem.rsplit('_', maxsplit=1)
        return x[0], int(x[1])

    json_paths = sorted(list(json_dir.glob('*.json')), key=get_repo_num)
    lines_info = get_single_line_data()

    data = {}
    for path in json_paths:
        with open(path , 'r', encoding='utf-8') as f:
            d = json.load(f)
        d.update(lines_info[d['id']])
        data[path.stem] = d

    return data


def get_single_line_data():
    with open('single_line_data.json', 'r') as f:
        sources = json.load(f)

    data = {}
    for x in sources:
        data[x['id']] = {
            'src_lines': x['source_code'],
            'tgt_lines': x['target_code'],
        }
    return data


if __name__ == '__main__':
    json_dir = Path('outputs')
    data = load_jsons(json_dir)
    ids = list(data.keys())

    while True:
        x = input('>>> ')
        if x == 'random':
            k = random.choices(ids)
        elif x not in ids:
            print(f'Cannot find key: [{x}]')
            continue

        d = data[x]
        print(f'[{d["id"]}]\n--------\n')

        print(f'{d["src"]}\n--------\n')
        print(f'{d["tgt"]}\n--------\n')

        print(f'{d["src_lines"]}\n--------\n')
        print(f'{d["tgt_lines"]}\n--------\n')

        print(f'Diff:\n')
        for a in d['diff']:
            if a.strip() == '':
                continue
            print(f'"""{a}"""')
        print('\n--------\n')

        print(f'Change:\n')
        for a in d['change']:
            if a.strip() == '':
                continue
            print(f'"""{a}"""')
        print('\n--------\n')

        print(f'Error Find:\n')
        for a in d['err_find']:
            if a.strip() == '':
                continue
            print(f'"""{a}"""')
        print('\n--------\n')

        print(f'Error Explain:\n')
        for a in d['err_explain']:
            if a.strip() == '':
                continue
            print(f'"""{a}"""')
        print('\n--------\n')

