from bs4 import BeautifulSoup
from selenium.webdriver import Chrome, ChromeOptions
from selenium.common.exceptions import TimeoutException, WebDriverException
import requests

import json


def main():
    option = ChromeOptions()
    option.add_argument('--headless')
    driver = Chrome(options=option)
    driver.implicitly_wait(time_to_wait=5)
    driver.set_page_load_timeout(30)

    with open('single_test_sample.txt', 'r') as f:
        single_ids = [x.strip() for x in f.readlines()]
    with open('multi_test_sample.txt', 'r') as f:
        multi_ids = [x.strip() for x in f.readlines()]

    output_filename = 'problem_samples.json'

    problem_text = dict.fromkeys([x.split('_')[0] for x in single_ids] + [x.split('_')[0] for x in multi_ids])
    for i, cid in enumerate(problem_text):
        try:
            driver.get(f'https://www.codechef.com/problems/{cid}')
        except Exception as e:
            print(f'Failed to get the sample: `{cid}`')
            continue

        container = driver.find_element('id', 'problem-statement')
        children = container.find_elements('xpath', '*')

        for child in children:
            spans = child.find_elements('xpath', ".//span[contains(@class, 'math-inline')]")
            if len(spans) == 0:
                continue

            for s in spans:
                t = s.find_element('xpath', ".//*[local-name()='annotation']")
                new_t = t.text.replace('\\', '&bsol;')
                driver.execute_script(f'arguments[0].outerHTML = "{new_t}";', s)

        problem_text[cid] = container.text
        print(f'Finished ({i+1}/{len(problem_text)}): `{cid}`')
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(problem_text, f, indent=4, ensure_ascii=False)

    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(problem_text, f, indent=4, ensure_ascii=False)
    print(f'Successfully saved to `{output_filename}`')


if __name__ == '__main__':
    main()
