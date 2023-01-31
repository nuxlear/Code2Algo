import numpy as np
from tqdm import tqdm
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path
import os
import json


def get_similarity(x, y):
    return np.einsum('ac,bc->ab', x, y)


def visualize_hist(values, ax: plt.Axes = None, title: str = None, bins=None):
    mu = np.mean(values)
    sigma = np.std(values)

    if ax is None:
        fig, ax = plt.subplots()
    if title is not None:
        ax.set_title(title)
    ax.hist(values, bins=bins)
    ax.plot([mu - sigma, mu - sigma], [0, 50], color='r')
    ax.plot([mu, mu], [0, 50], color='k')
    print(f'{title} = mu: {mu} - sigma: {sigma}')
    return ax


def analyze_xlcost():
    emb_dir = Path('results', 'xlcost', 'embeddings')
    emb_paths = sorted(list(emb_dir.glob('*.npy')))

    code_embs, text_embs, pseudo_embs = [], [], []
    for path in tqdm(emb_paths):
        emb = np.load(str(path))
        code_emb, text_emb, pseudo_emb = emb[:1], emb[1:2], emb[2:]
        code_embs.append(code_emb)
        text_embs.append(text_emb)
        pseudo_embs.append(pseudo_emb)

    # similarity
    code_text_sims, code_sims, text_sims = [], [], []
    for code_emb, text_emb, pseudo_embs in tqdm(zip(code_embs, text_embs, pseudo_embs), total=len(emb_paths)):
        code_text_sim = get_similarity(code_emb, text_emb)
        code_sim = get_similarity(code_emb, pseudo_embs)
        text_sim = get_similarity(text_emb, pseudo_embs)

        code_text_sims.append(code_text_sim)
        code_sims.append(code_sim)
        text_sims.append(text_sim)

    max_code_text_sims = np.max(np.concatenate(code_text_sims, axis=0), axis=1)
    max_code_sims = np.max(np.concatenate(code_sims, axis=0), axis=1)
    max_text_sims = np.max(np.concatenate(text_sims, axis=0), axis=1)

    # relative sim rank
    code_embs_np = np.concatenate(code_embs, axis=0)
    text_embs_np = np.concatenate(text_embs, axis=0)
    code_text_sim_matrix = get_similarity(code_embs_np, text_embs_np)
    N = len(code_text_sim_matrix)

    # text sim / code
    text_sim_per_code = np.argsort(code_text_sim_matrix, axis=1)
    self_text_sim_per_code = np.diag(text_sim_per_code)

    # code sim / text
    code_sim_per_text = np.argsort(code_text_sim_matrix, axis=0)
    self_code_sim_per_text = np.diag(code_sim_per_text)

    non_diag = np.where(~np.eye(N, dtype=bool), code_text_sim_matrix, 0)
    mean_other_text_sim_per_code = np.sum(non_diag, axis=1) / (N - 1)
    mean_other_code_sim_per_text = np.sum(non_diag, axis=0) / (N - 1)
    diff_text_sim_per_code = np.diag(code_text_sim_matrix) - mean_other_text_sim_per_code
    diff_code_sim_per_text = np.diag(code_text_sim_matrix) - mean_other_code_sim_per_text

    fig, axes = plt.subplots(ncols=3, figsize=(16, 4))
    visualize_hist(max_code_text_sims, axes[0], title='Code - Text', bins=np.arange(0, 1, 0.01))
    visualize_hist(max_code_sims, axes[1], title='Code - Pseudo', bins=np.arange(0, 1, 0.01))
    visualize_hist(max_text_sims, axes[2], title='Text - Pseudo', bins=np.arange(0, 1, 0.01))
    # plt.show()
    #
    # fig, axes = plt.subplots(ncols=2, figsize=(12, 4))
    # visualize_hist(self_text_sim_per_code / N, axes[0], title='rank of text per code', bins=np.arange(0, 1, 0.01))
    # visualize_hist(self_code_sim_per_text / N, axes[1], title='rank of code per text', bins=np.arange(0, 1, 0.01))

    fig, axes = plt.subplots(ncols=2, figsize=(12, 4))
    visualize_hist(diff_text_sim_per_code, axes[0], title='diff of text per code', bins=np.arange(-1, 1, 0.02))
    visualize_hist(diff_code_sim_per_text, axes[1], title='diff of code per text', bins=np.arange(-1, 1, 0.02))
    axes[0].plot([0, 0], [0, 100], color='lime')
    axes[1].plot([0, 0], [0, 100], color='lime')

    # fig, ax = plt.subplots(figsize=(15, 12))
    # sns.heatmap(code_text_sim_matrix, ax=ax)
    # plt.show()


def analyze_codechef():
    emb_dir = Path('results', 'codechef', 'embeddings')
    emb_paths = sorted(list(emb_dir.glob('*.npy')))

    info_path = Path('results', 'codechef', 'codechef_pseudo.json')
    with open(info_path, 'r', encoding='utf-8') as f:
        infos = json.load(f)

    src_embs, tgt_embs, pseudo_src_embs, pseudo_tgt_embs = [], [], [], []
    for path, info in tqdm(zip(emb_paths, infos), total=len(emb_paths)):
        emb = np.load(str(path))
        if info['pseudo_src'] is None:
            continue
        sl = len(info['pseudo_src'])
        src_emb, tgt_emb, pseudo_src_emb, pseudo_tgt_emb = emb[:1], emb[1:2], emb[2:2+sl], emb[2+sl:]

        src_embs.append(src_emb)
        tgt_embs.append(tgt_emb)
        pseudo_src_embs.append(pseudo_src_emb)
        pseudo_tgt_embs.append(pseudo_tgt_emb)

    src_tgt_sims, src_sims, tgt_sims = [], [], []
    for src_emb, tgt_emb, pseudo_src_emb, pseudo_tgt_emb in tqdm(zip(src_embs, tgt_embs, pseudo_src_embs, pseudo_tgt_embs), total=len(emb_paths)):
        src_tgt_sim = get_similarity(src_emb, tgt_emb)
        src_sim = get_similarity(src_emb, pseudo_src_emb)
        tgt_sim = get_similarity(tgt_emb, pseudo_tgt_emb)

        src_tgt_sims.append(src_tgt_sim)
        src_sims.append(src_sim)
        tgt_sims.append(tgt_sim)

    max_src_tgt_sims = np.max(np.concatenate(src_tgt_sims, axis=0), axis=1)
    max_src_sims = np.max(np.concatenate(src_sims, axis=0), axis=1)
    max_tgt_sims = np.max(np.concatenate(tgt_sims, axis=0), axis=1)

    # relative sim rank
    src_embs_np = np.concatenate(src_embs, axis=0)
    tgt_embs_np = np.concatenate(tgt_embs, axis=0)
    src_tgt_sim_matrix = get_similarity(src_embs_np, tgt_embs_np)
    N = len(src_tgt_sim_matrix)

    # text sim / code
    tgt_sim_per_src = np.argsort(src_tgt_sim_matrix, axis=1)
    self_tgt_sim_per_src = np.diag(tgt_sim_per_src)

    # code sim / text
    src_sim_per_tgt = np.argsort(src_tgt_sim_matrix, axis=0)
    self_src_sim_per_tgt = np.diag(src_sim_per_tgt)

    non_diag = np.where(~np.eye(N, dtype=bool), src_tgt_sim_matrix, 0)
    mean_other_tgt_sim_per_src = np.sum(non_diag, axis=1) / (N - 1)
    mean_other_src_sim_per_tgt = np.sum(non_diag, axis=0) / (N - 1)
    diff_tgt_sim_per_src = np.diag(src_tgt_sim_matrix) - mean_other_tgt_sim_per_src
    diff_src_sim_per_tgt = np.diag(src_tgt_sim_matrix) - mean_other_src_sim_per_tgt

    fig, axes = plt.subplots(ncols=3, figsize=(16, 4))
    visualize_hist(max_src_tgt_sims, axes[0], title='Src - Tgt', bins=np.arange(0, 1, 0.01))
    visualize_hist(max_src_sims, axes[1], title='Src - Pseudo', bins=np.arange(0, 1, 0.01))
    visualize_hist(max_tgt_sims, axes[2], title='Tgt - Pseudo', bins=np.arange(0, 1, 0.01))
    # plt.show()

    fig, axes = plt.subplots(ncols=2, figsize=(12, 4))
    visualize_hist(self_tgt_sim_per_src / N, axes[0], title='rank of tgt per src', bins=np.arange(0, 1, 0.01))
    visualize_hist(self_src_sim_per_tgt / N, axes[1], title='rank of src per tgt', bins=np.arange(0, 1, 0.01))

    fig, axes = plt.subplots(ncols=2, figsize=(12, 4))
    visualize_hist(diff_tgt_sim_per_src, axes[0], title='diff of tgt per src', bins=np.arange(-1, 1, 0.02))
    visualize_hist(diff_src_sim_per_tgt, axes[1], title='diff of src per tgt', bins=np.arange(-1, 1, 0.02))
    axes[0].plot([0, 0], [0, 100], color='lime')
    axes[1].plot([0, 0], [0, 100], color='lime')


if __name__ == '__main__':
    # analyze_xlcost()
    analyze_codechef()
    plt.show()
