from tqdm import tqdm

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
    for path in tqdm(json_paths):
        try:
            with open(path , 'r', encoding='utf-8') as f:
                d = json.load(f)
            d.update(lines_info[d['id']])
            data[path.stem] = d
        except Exception as e:
            print(f'Error: {e}')

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


def visualize_single():
    print('SINGLE')

    json_dir = Path('pseudo_all')
    data = load_jsons(json_dir)
    ids = list(data.keys())

    while True:
        x = input('>>> ')
        if x == 'random':
            x = random.choice(ids)
        elif x not in ids:
            print(f'Cannot find key: [{x}]')
            continue

        d = data[x]
        print(f'[{d["id"]}]\n\n')

        print(f'[Wrong Code]\n{d["src"]}\n--------\n')
        print(f'[Correct Code]\n{d["tgt"]}\n--------\n')

        # print(f'Pseudo: src')
        # for a in d['pseudo_src']:
        #     if a.strip() == '':
        #         continue
        #     print(f'"""{a}"""')
        # print('\n--------\n')
        #
        # print(f'Pseudo: tgt')
        # for a in d['pseudo_tgt']:
        #     if a.strip() == '':
        #         continue
        #     print(f'"""{a}"""')
        # print('\n--------\n')

        if 'src_lines' in d:
            print(f'[Diff]\n--------\n{d["src_lines"]}\n--------\n{d["tgt_lines"]}\n\n')

        # print(f'{d["src_lines"]}\n--------\n')
        # print(f'{d["tgt_lines"]}\n--------\n')
        #
        # print(f'Diff:\n')
        # for a in d['diff']:
        #     if a.strip() == '':
        #         continue
        #     print(f'"""{a}"""')
        # print('\n--------\n')
        #
        # print(f'Change:\n')
        # for a in d['change']:
        #     if a.strip() == '':
        #         continue
        #     print(f'"""{a}"""')
        # print('\n--------\n')
        #
        # print(f'Error Find:\n')
        # for a in d['err_find']:
        #     if a.strip() == '':
        #         continue
        #     print(f'"""{a}"""')
        # print('\n--------\n')
        #
        # print(f'Error Explain:\n')
        # for a in d['err_explain']:
        #     if a.strip() == '':
        #         continue
        #     print(f'"""{a}"""')
        # print('\n--------\n')


def visualize_multi():
    print('MULTI')

    json_path = Path('multi_line_data.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    ids = list(data.keys())

    while True:
        x = input('>>> ')
        if x == 'random':
            x = random.choice(ids)
        elif x not in ids:
            print(f'Cannot find key: [{x}]')
            continue

        d = data[x]
        print(f'[{d["id"]}]\n\n')

        print(f'[Wrong Code]\n{d["src"]}\n--------\n')
        print(f'[Correct Code]\n{d["tgt"]}\n--------\n')


if __name__ == '__main__':
    visualize_multi()

