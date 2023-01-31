from tqdm import tqdm

import os
from pathlib import Path
import json


def parse_dataset(data_dir, out_path=None):
    data_paths = sorted([x for x in data_dir.glob('*') if x.stem.isalnum()])

    data = {}
    for mp in tqdm(data_paths):
        sols = sorted([x for x in mp.glob('*') if x.stem.isnumeric()], key=lambda x: int(x.stem))
        for sol in sols:
            with open(sol / 'wrong_file.py', 'r', encoding='utf-8') as f:
                wrong_code = f.read()
            with open(sol / 'correct_file.py', 'r', encoding='utf-8') as f:
                correct_code = f.read()

            sol_id = f'{mp.stem}_{sol.stem}'
            item = {
                'id': sol_id,
                'src': wrong_code,
                'tgt': correct_code,
            }
            data[sol_id] = item

    out_path = out_path or 'dataset.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f'Successfully parsed dataset: `{str(data_dir)}` to file: `{out_path}`')

    return data


def main():
    multi_dir = Path(f'multi_line_instances', 'multi_line_instances')
    single_dir = Path(f'single_instances', 'single_instances')

    parse_dataset(multi_dir, 'multis.json')
    parse_dataset(single_dir, 'singles.json')


if __name__ == '__main__':
    main()
