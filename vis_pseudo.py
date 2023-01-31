import gradio as gr
from pathlib import Path
import json


def visualize_pseudo(repo, id):
    data_dir = Path('pseudo_all')

    with open(data_dir / f'{repo}_{id}.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    data['pseudo_src'] = [f'1. {x}' for x in data['pseudo_src']]
    data['pseudo_tgt'] = [f'1. {x}' for x in data['pseudo_tgt']]

    return data['src'], data['tgt'], *data['pseudo_src'], *data['pseudo_tgt']


if __name__ == '__main__':
    with gr.Blocks() as vis:
        with gr.Row():
            with gr.Column():
                repo = gr.Text(label='repo', placeholder='Repo name')
            with gr.Column():
                idnum = gr.Text(label='id', placeholder='ID')

        btn = gr.Button(value='Show')

        pseudo_srcs = []
        pseudo_tgts = []

        with gr.Blocks() as out:
            with gr.Row():
                with gr.Column():
                    src = gr.Textbox(label='src (wrong)', max_lines=40)

                with gr.Column():
                    tgt = gr.Textbox(label='tgt (correct)', max_lines=40)

            with gr.Blocks():
                for i in range(4):
                    with gr.Tab(str(i)):
                        with gr.Row():
                            with gr.Column():
                                pseudo_src = gr.Textbox(label='pseudo src', max_lines=40)
                                pseudo_srcs.append(pseudo_src)
                            with gr.Column():
                                pseudo_tgt = gr.Textbox(label='pseudo tgt', max_lines=40)
                                pseudo_tgts.append(pseudo_tgt)

        btn.click(
            fn=visualize_pseudo,
            inputs=[repo, idnum],
            outputs=[src, tgt, *pseudo_srcs, *pseudo_tgts]
        )

    vis.launch()
