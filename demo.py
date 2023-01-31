from chatgpt_wrapper import ChatGPT
from chatgpt_wrapper.core.config import Config

import gradio as gr
import openai

import argparse
import threading
from queue import Queue
import time
import asyncio

backends = ['api', 'wrapper']


class ChatGPTRunner:
    def __init__(self, config=None):
        self.bot = None

        self.tasks = Queue()
        self._thread = threading.Thread(target=self._run_loop, args=(config,), daemon=True, name='GPT-Runner')
        self._thread.start()

    def _run_loop(self, config):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        self.bot = ChatGPT(config=config)
        print(f'Bot initialized.')

        while True:
            prompt, q = self.tasks.get()
            print(f'Get prompt:\n\n```\n{prompt}\n```')
            res = self.bot.ask(prompt)
            print('finished!')
            q.put(res)
            time.sleep(0.5)

    def set_model(self, model):
        if model == 'gpt-4':
            model = 'gpt4'
        self.bot.agpt.set_active_model(model)
        print(f'Set model=`{model}` to bot.')

    def ask(self, prompt):
        q = Queue()
        self.tasks.put((prompt, q))
        return q


def get_system_prompt():
    return f'''You are the algorithm analyzer who figures out the main differences of given wrong answer code from the solution code, who are correct to solve given problem description. You need to figure out the main differences of the algorithm which makes the answer code failed to solve the problem, comparing the solution code. There might be only simple typo error, or simple logical error. Regardless of the size of the differences, you must specify the differences of the wrong answer code.

You must follow these instruction when you compare answer code and solution code.

- You need to tell me the name of the algorithm the code uses, both of answer code and solution code, if the name exists. When the name of the algorithms of two codes are different, the codes are different.
- You must specify the main differences is simple, like a typo error or simple logical error, or complex enough, such as inefficient algorithm or wrong approach, or existence of missing logic.
- If their time complexities are different although their algorithms are same, you can judge them as different algorithm.
- You can compare them line by line, but you need to compare them in abstracted level, so that I can compare them in terms of their main algorithm which the codes want to implement.
- When the differences of code lines are given, you must explain the differences of the algorithm considering the differences of code lines, and why that different lines make the different results.
- You must explain about the differences of the answer code only, not about the solution code. I want the result must not be include any direct explanation about the algorithm of the solution code, but only hints by giving a differences between them.
- You cannot describe the algorithm of the solution code directly. It must be hidden to viewer.'''


def make_user_prompt(desc, answer, solution):
    return f'''Here is the problem description:

{desc}

----
Here is wrong answer code:

{answer}

----
Here is the correct solution code:

{solution}'''


def make_prompts(desc, answer, solution):
    prompt = f'''{get_system_prompt()}

    ----
    {make_user_prompt(desc, answer, solution)}'''
    return prompt


def get_analysis_from_chatgpt(messages, model='gpt-3.5-turbo'):
    try:
        return openai.ChatCompletion.create(
            model=model,
            messages=messages
        )
    except openai.InvalidRequestError as e:
        raise gr.Error(str(e))
    except openai.error.RateLimitError:
        raise gr.Error('User limit exceeded. Please try later.')


def code_analyzer(desc, wrong, correct, backend='api', model='gpt-4'):
    if backend not in backends:
        raise gr.Error(f'Invalid backend: `{backend}`')

    if backend == 'api':
        sys_prompt = get_system_prompt()
        user_prompt = make_user_prompt(desc, wrong, correct)
        messages = [
            {'role': 'system', 'content': sys_prompt},
            {'role': 'user', 'content': user_prompt},
        ]
        res = get_analysis_from_chatgpt(messages, model)
        if res is None or len(res['choices']) == 0:
            raise gr.Error(f'No results found from ChatGPT API...')

        return res['choices'][0]['message']['content']

    if backend == 'wrapper':
        # cfg = Config()
        # if model == 'gpt-4':
        #     cfg.set('chat.model', 'gpt4')

        prompt = make_prompts(desc, wrong, correct)
        bot = globals()['bot']
        bot.set_model(model)

        success, response, message = bot.ask(prompt).get()
        if not success:
            raise gr.Error(f'Failed to get result from ChatGPT wrapper...\n\n{message}')

        return response


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--openai_key', type=str, default=None)
    parser.add_argument('--backend', type=str, choices=backends)

    args = parser.parse_args()

    globals()['bot'] = ChatGPTRunner()

    if args.openai_key:
        openai.api_key = args.openai_key

    with gr.Blocks() as demo:
        with gr.Blocks() as inputs:
            backend = gr.Radio(label='ChatGPT backend mode', choices=backends, value='api')
            with gr.Row():
                with gr.Column():
                    desc = gr.Textbox(label='Problem description', lines=20, placeholder='Please enter your problem description.')
                with gr.Column():
                    answer = gr.Textbox(label='Wrong answer code', lines=15, placeholder='Please enter your wrong answer code.')
                with gr.Column():
                    solution = gr.Textbox(label='Solution code', lines=15, placeholder='Please enter the correct solution code.')

            submit = gr.Button('Analyze')

        with gr.Blocks() as output:
            explain = gr.Textbox(label='Result', lines=50)

        submit.click(
            fn=code_analyzer,
            inputs=[desc, answer, solution, backend],
            outputs=[explain],
        )
    demo.launch()
