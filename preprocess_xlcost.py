import pandas as pd

import os
from pathlib import Path
import json


def load_dataset(data_dir, mode='test'):
    files = sorted([x for x in data_dir.glob('*') if x.name.startswith(mode) and x.suffix != '.jsonl'])
    data = {}
    for path in files:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        key = None
        if path.suffix == '.py':
            key = 'code'
        if path.suffix == '.txt':
            key = 'text'
        data[key] = lines

    return pd.DataFrame(data)


def dump_code(code_token):
    special_tokens = {'NEW_LINE', 'INDENT', 'DEDENT'}
    indent = 0
    text = []
    first_of_line = True
    for tok in code_token:
        if tok not in special_tokens:
            if first_of_line:
                text.append('    ' * indent)
            text.append(tok + ' ')
            first_of_line = False
            continue

        if tok == 'NEW_LINE':
            text.append('\n')
            first_of_line = True
        if tok == 'INDENT':
            indent += 1
        if tok == 'DEDENT':
            indent -= 1

    return ''.join(text)


if __name__ == '__main__':
    python_desc_path = Path('1.Python-desc', 'Python-desc')
    python_comment_path = Path('2.Python-comment', 'Python-comment')
    python_desc_comment_path = Path('3.Python-desc and comment', 'Python-desc')

    dataset_paths = [python_desc_path, python_comment_path, python_desc_comment_path]
    dataset_name = ['desc', 'comment', 'desc-comment']
    modes = ['train', 'val', 'test']

    output_path = Path('data', 'xlcost')
    os.makedirs(output_path, exist_ok=True)

    for dp, dn in zip(dataset_paths, dataset_name):
        data = []
        for mode in modes:
            df = load_dataset(dp, mode)
            for i, x in df.iterrows():
                item = {
                    'id': f'{dn}_{mode}_{i:05d}',
                    'dataset': dn,
                    'mode': mode,
                    'text': x['text'],
                    'code': dump_code(x['code'].split()),
                }
                data.append(item)
        out_file = output_path / f'{dn}.json'
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f'Finished: {dn} -> {str(out_file)}')
