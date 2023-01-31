from chatgpt_wrapper import ChatGPT
import json


desc = '''Chef has an array A of size N. Chef wants to choose any subsequence of size exactly ⌈n/2⌉ from the array such that GCD of all the elements in that sequence must be 2. Chef names such a kind of sequence as a half-sequence.

Help Chef to find whether he would be able to select any half-sequence in the given array.

As a reminder,

A subsequence of an array is a sequence that can be derived from the given array by deleting zero or more elements without changing the order of the remaining elements.
GCD stands for Greatest Common Divisor. The greatest common divisor of a subsequence is the largest integer d such that all the numbers in sequence are divisible by d.
⌈x⌉ is the ceiling (round up) operation:
⌈3.5⌉ = 4, ⌈2⌉ = 2.

Input Format
- The first line contains an integer T denoting the number of test cases. The T test cases then follow.
- The first line of each test case contains a single integer N denoting the size of the array.
- The second line of each test case contains N space-separated integers A_1, A_2, ..., A_N denoting the given array.

Output Format
- For each test case, output on one line YES if Chef can find a half-sequence, else print NO. Output is case insensitive.

Constraints
1 <= T <= 20
2 <= N <= 10^5
1 <= A_i <= 10^9
Sum of N over all test cases does not exceed 10^5'''

solution = '''from itertools import combinations
from math import *
for _ in range(int(input())):
    n=int(input())
    tmp=list(map(int,input().split()))
    a=[]
    for i in tmp:
        if i%2==0:
            a.append(i)
    n=(n+1)//2
    if len(a)<n:
        print("NO")
        continue
    comb=combinations(a,n)
    if n<=18:
        ver=False
        for i in comb:
            i=list(i)
            g=i[0]
            for j in range(1,len(i)):
                g=gcd(g,i[j])
            if g==2:
                ver=True
                break
        if ver:
            print("YES")
        else:
            print("NO")
    else:
        g=a[0]
        for i in range(1,len(a)):
            g=gcd(g,a[i])
        if g==2:
            print("YES")
        else:
            print("NO")'''

answer = '''from math import ceil, gcd
from functools import reduce
for _ in range(int(input())):
    n = int(input());a = list(map(int, input().split()));size = ceil(n / 2);multiples_2 = [v // 2 for v in a if v % 2 == 0]
    if len(multiples_2) < size or reduce(gcd, multiples_2) > 1:print('NO')
    else:
        triats, g = [multiples_2[0]], multiples_2[0]
        for v in multiples_2:
            nou_g = gcd(g, v)
            if nou_g < g:
                triats.append(v);g = nou_g
                if g == 1:break
        print('YES') if len(triats) <= size else print('NO')'''


class SolutionComparator:
    def __init__(self, bot, desc, solution, answer):
        self.bot = bot
        self.desc = desc
        self.solution = solution
        self.answer = answer

    def _make_prompt(self):
        prompt = f'''You are the algorithm analyzer who figures out the main differences of given wrong solution code from the answer code, who are correct to solve given problem description. You need to figure out the main differences of the algorithm which makes the solution code failed to solve the problem, comparing the answer code. There might be only simple typo error, or simple logical error. Regardless of the size of the differences, you must specify the differences of the wrong solution code.

You must follow these instruction when you compare solution code and answer code.

- You need to tell me the name of the algorithm the code uses, both of solution code and answer code, if the name exists. When the name of the algorithms of two codes are different, the codes are different.
- You must specify the main differences is simple, like a typo error or simple logical error, or complex enough, such as inefficient algorithm or wrong approach, or existence of missing logic.
- If their time complexities are different although their algorithms are same, you can judge them as different algorithm.
- You can compare them line by line, but you need to compare them in abstracted level, so that I can compare them in terms of their main algorithm which the codes want to implement.
- When the differences of code lines are given, you must explain the differences of the algorithm considering the differences of code lines, and why that different lines make the different results.
- You must explain about the differences of the solution code only, not about the answer code. I want the result must not be include any direct explanation about the algorithm of the answer code, but only hints by giving a differences between them.
- You cannot describe the algorithm of the answer code directly. It must be hidden to viewer.

----
Here is the problem description:

{self.desc}

----
Here is wrong solution code:

{self.solution}

----
Here is the answer code:

{self.answer}'''
        return prompt

    def get_result(self):
        response = self.bot.ask(self._make_prompt())
        return response


def main_iterative():
    first_prompt = '''You are the algorithm analyzer that figure out the logical flaw from the given code. I will give you the problem description, followed by the buggy python3 code. Once I gave that, I can give you some test cases that the code failed, continuously. The testcase consist of the input, expected output and the actual output from the code. You are responsible to analyze the algorithm of the code, and find why the code cannot pass the testcase. You may suggest the fixed code, but you must explain the reason of the testcase failure first, and the suggested code must pass all given testcases before. Do you understand?'''

    bot = ChatGPT()
    response = bot.ask(first_prompt)
    print(response)
    print(bot.parent_message_id)
    print(bot.conversation_id)

    prompt = ''
    while True:
        cmd = input('> ')
        if cmd.startswith('!'):
            if cmd == '!exit':
                break
            elif cmd == '!':
                response = bot.ask(prompt)
                print(response)
                print(bot.parent_message_id)
                print(bot.conversation_id)
                prompt = ''
                continue
            else:
                print('invalid command. ')
                continue
        prompt += cmd + '\n'


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(path, obj):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    bot = ChatGPT()

    problems = load_json('problem_samples_after.json')
    singles = load_json('singles.json')
    multis = load_json('multis.json')

    solutions = singles.copy()
    solutions.update(multis)

    with open('single_test_sample.txt', 'r') as f:
        single_samples = [x.strip() for x in f.readlines()]
    with open('multi_test_sample.txt', 'r') as f:
        multi_samples = [x.strip() for x in f.readlines()]

    totals = single_samples + multi_samples

    # Different case
    results = {}
    for i, sample_id in enumerate(totals):
        problem_id, solution_id = sample_id.split('_')

        if problem_id not in problems:
            print(f'Cannot find problem: {problem_id}')
            continue
        desc = problems[problem_id]

        if sample_id not in solutions:
            print(f'Cannot find solution: {sample_id}')
            continue
        solution = solutions[sample_id]

        bot.new_conversation()
        comparator = SolutionComparator(bot, desc, solution['src'], solution['tgt'])
        res = comparator.get_result()
        results[sample_id] = {
            'desc': desc,
            'solution': solution['src'],
            'answer': solution['tgt'],
            'result': res,
            'expected_result': 'different',
        }

        save_json('chatgpt_result_analysis_diff_v2.json', results)
        print(f'Finished ({i+1}/{len(totals)}): `{sample_id}`')

    print('Different Finished!')

    # # Same case
    # results = {}
    # for i, sample_id in enumerate(totals):
    #     problem_id, solution_id = sample_id.split('_')
    #
    #     if problem_id not in problems:
    #         print(f'Cannot find problem: {problem_id}')
    #         continue
    #     desc = problems[problem_id]
    #
    #     if sample_id not in solutions:
    #         print(f'Cannot find solution: {sample_id}')
    #         continue
    #     solution = solutions[sample_id]
    #
    #     bot.new_conversation()
    #     comparator = SolutionComparator(bot, desc, solution['tgt'], solution['tgt'])
    #     res = comparator.get_result()
    #     results[sample_id] = {
    #         'desc': desc,
    #         'solution': solution['tgt'],
    #         'answer': solution['tgt'],
    #         'result': res,
    #         'expected_result': 'same',
    #     }
    #
    #     save_json('chatgpt_result_comparing_same.json', results)
    #     print(f'Finished ({i+1}/{len(totals)}): `{sample_id}`')
    #
    # print('Same Finished!')

    # solution_comparator = SolutionComparator(bot, desc, solution, answer)
    # res = solution_comparator.get_result()
    # print(res)
