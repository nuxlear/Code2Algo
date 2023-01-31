from core import generate_explanation
from tqdm import tqdm

from pathlib import Path
import os
import re
import json


def generate_pseudo_code(code):
    prompt = f'''## The Python 3 Code is below:\n\n{code}\n\n## The Pseudo-code who explains the code's algorithm above. \n\n## The pseudo-code only contains English sentences and indentation for its structures: \n"""\n1. '''
    res = generate_explanation(prompt, num_results=4, stop=['\n\n', '"""', '##', '\n#'])
    pseudo = [x.text for x in res] if res is not None else None
    return pseudo


if __name__ == '__main__':
    json_path = Path('data', 'xlcost', 'desc-comment.json')

    with open(json_path, 'r', encoding='utf-8') as f:
        d = json.load(f)

    result_dir = Path('results', 'xlcost')
    os.makedirs(result_dir)

    results = []
    for item in tqdm(d):
        code = item['code']
        pseudo = generate_pseudo_code(code)
        res = {
            'id': item['id'],
            'code': code,
            'text': item['text'],
            'pseudo': pseudo,
        }
        results.append(res)

        with open(result_dir / 'desc-comment_pseudo.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
