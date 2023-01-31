import time

import openai
import os
from pathlib import Path
import random
import json


def generate_explanation(prompt, model='code-davinci-002', temperature=0.5, max_tokens=256, num_results=3,
                         frequency_penalty=0., presence_penalty=0., stop=None):

    openai.api_key = os.getenv("OPENAI_API_KEY")

    while True:
        try:
            res = openai.Completion.create(
                model=model,
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1.0,
                n=num_results,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stop=stop
            )
            return res.choices
        except openai.error.RateLimitError:
            time.sleep(3)
        except openai.error.InvalidRequestError:
            return None


def test_code():
    codes = list(Path('sample_codes').glob('*.py'))
    code_file = random.choices(codes)[0]
    # code_file = Path('codes', 'falling_path.py')
    print(code_file)
    with open(code_file, 'r') as f:
        code = f.read()

    # prompt = f'''## Specify the name of main algorithm used in the code below. You don't have to explain what the algorithm is, and you don't have to generate some code. \n\n{code}\n\n## Explanation: '''

    # prompt = f'''{code}\n\n## Question: What is the name of the algorithm used in the code above?\n## Answer: '''
    # res = generate_explanation(prompt, num_results=3, stop=['\n\n', '#'])
    # print([x.text for x in res])
    #
    # prompt = f'''{code}\n\n## Question: What is the time complexity of the algorithm used in the code above?\n## Answer: '''
    # res = generate_explanation(prompt, num_results=3, stop=['\n\n', '#'])
    # print([x.text for x in res])
    #
    # for tc in res:
    #     prompt = f'''{code}\n\n## Why do you think that the time complexity of the algorithm is {tc.text.strip()}? Explain your answer. \n## Answer: '''
    #     ex = generate_explanation(prompt, num_results=1, stop=['\n\n', '#'])
    #     print([x.text for x in ex])

    prompt = f'''## Show the simple pseudo-code for this algorithm in the python code below. The pseudo-code can use its own symbols but must be different from the given code. \n\n{code}\n\n## Pseudo-code: \n"""\n1. '''
    res = generate_explanation(prompt, num_results=4, stop=['\n\n', '"""'])
    print([x.text for x in res])


if __name__ == '__main__':
    source_dir = Path('single_instances', 'single_instances')
    sources = {}

    with open('single_line_data.json', 'r') as f:
        source_data = json.load(f)

    for d in source_data:
        repo, id_num = d['id'].rsplit('_', maxsplit=1)
        src_filename = d['source_filename']
        tgt_filename = d['target_filename']

        code_dir = source_dir / repo / id_num
        if not code_dir.exists():
            print(f'Cannot find repo: {repo} - {id_num}')
            continue

        key = f'{repo}_{id_num}'
        sources[key] = {'repo': repo}

        src_key = 'wrong'
        if src_key not in sources:
            with open(code_dir / 'wrong_file.py', 'r', encoding='utf-8') as f:
                src_file = f.readlines()
            sources[key][src_key] = ''.join(src_file)

        tgt_key = f'correct'
        if tgt_key not in sources:
            with open(code_dir / 'correct_file.py', 'r', encoding='utf-8') as f:
                tgt_file = f.readlines()
            sources[key][tgt_key] = ''.join(tgt_file)

    # print(source_data[0])

    dir_name = 'pseudo_all'
    os.makedirs(dir_name, exist_ok=True)

    json_output_path = Path('singles.json')

    results = {}
    for i, (pid, codes) in enumerate(sources.items()):
        repo = codes['repo']
        if not Path('codechef', 'data', repo).exists():
            print(f'Skip missing repo [{repo}] - {pid}')
            continue

        # output_path = Path(dir_name, f'{pid}.json')
        # if output_path.exists():
        #     print(f'Skipping existing file: [{str(output_path)}]')
        #     continue

        src = codes['wrong']
        tgt = codes['correct']

        # context = f'''## Original Code\n\n{src}\n\n## Changed Code\n\n{tgt}\n\n'''
        #
        # prompt = f'''{context}## Explain the differences between the codes above: \n\n"""'''
        # res = generate_explanation(prompt, num_results=4, stop=['\n\n', '"""', '##', '\n#'])
        # diff_explain = [x.text for x in res] if res is not None else None
        # # print(diff_explain)
        #
        # prompt = f'''{context}## The code must be changed because the algorithm has a problem. Explain the problem below: \n"""'''
        # res = generate_explanation(prompt, num_results=4, stop=['\n\n', '"""', '##', '\n#'])
        # change_explain = [x.text for x in res] if res is not None else None
        # # print(change_explain)
        #
        # prompt = f'''## The Student's Code is below:\n\n{src}## Find the lines of code which makes semantic error of the algorithm it uses: \n"""'''
        # res = generate_explanation(prompt, num_results=4, stop=['\n\n', '"""', '##', '\n#'])
        # error_find = [x.text for x in res] if res is not None else None
        # # print(error_find)
        #
        # prompt = f'''## The Student's Code is below:\n\n{src}## Explain any problems or vulnerabilities of its algorithm if they are exist: \n"""'''
        # res = generate_explanation(prompt, num_results=4, stop=['\n\n', '"""', '##', '\n#'])
        # error_explain = [x.text for x in res] if res is not None else None
        # # print(error_explain)

        # prompt = f'''## The Python 3 Code is below:\n\n{src}\n\n## The Pseudo-code who explains the code's algorithm above. \n\n## The pseudo-code only contains English sentences and indentation for its structures: \n"""\n1. '''
        # res = generate_explanation(prompt, num_results=4, stop=['\n\n', '"""', '##', '\n#'])
        # # res = generate_explanation(prompt, num_results=4)
        # pseudo_src = [x.text for x in res] if res is not None else None
        # # print(pseudo_src)
        #
        # prompt = f'''## The Python 3 Code is below:\n\n{tgt}\n\n## The Pseudo-code who explains the code's algorithm above. \n\n## The pseudo-code only contains English sentences and indentation for its structures: \n"""\n1. '''
        # res = generate_explanation(prompt, num_results=4, stop=['\n\n', '"""', '##', '\n#'])
        # # res = generate_explanation(prompt, num_results=4)
        # pseudo_tgt = [x.text for x in res] if res is not None else None
        # # print(pseudo_tgt)

        result = {
            'id': pid,
            'repo': repo,
            'src': src,
            'tgt': tgt,
            # 'pseudo_src': pseudo_src,
            # 'pseudo_tgt': pseudo_tgt,
        }
        results[pid] = result

        # with open(output_path, 'w', encoding='utf-8') as f:
        #     json.dump(result, f, indent=4, ensure_ascii=False)
        #
        # print(f'Successfully Saved [{pid}] - ({i+1}/{len(sources)})')

    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
