from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F
import numpy as np
from tqdm import tqdm

from pathlib import Path
import os
import json

from unixcoder import UniXcoder


def get_embedding(model: UniXcoder, text, device='cpu'):
    if isinstance(text, str):
        text = [text]
    token_ids = model.tokenize(text, mode='<encoder-only>', padding=(len(text) > 1))
    input_ids = torch.tensor(token_ids).to(device)
    _, embedding = model(input_ids)
    return F.normalize(embedding.cpu(), dim=1)


def get_similarity(x, y):
    return float(torch.einsum('ac,bc->ab', x, y))


if __name__ == '__main__':
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = UniXcoder('microsoft/unixcoder-base')
    model.to(device)

    # # XLCoST
    # pseudo_path = Path('results', 'xlcost', 'desc-comment_pseudo.json')
    # with open(pseudo_path, 'r', encoding='utf-8') as f:
    #     d = json.load(f)
    #
    # output_path = Path('results', 'xlcost', 'embeddings')
    # os.makedirs(output_path, exist_ok=True)
    #
    # with torch.no_grad():
    #     for item in tqdm(d):
    #         emb_code = get_embedding(model, item['code'], device=device)
    #         emb_text = get_embedding(model, item['text'], device=device)
    #         embs = get_embedding(model, item['pseudo'], device=device)
    #         embs = torch.cat([emb_text, embs], dim=0)
    #         np.save(output_path / f'{item["id"]}.npy', embs)

    # CodeChef
    output_path = Path('results', 'codechef', 'embeddings')
    os.makedirs(output_path, exist_ok=True)

    pseudo_paths = sorted(list(Path('pseudo_all').glob('*.json')))

    infos = []
    with torch.no_grad():
        for path in tqdm(pseudo_paths):
            with open(path, 'r', encoding='utf-8') as f:
                d = json.load(f)
            infos.append(d)

            if (output_path / f'{d["id"]}.npy').exists():
                continue

            try:
                emb_src = get_embedding(model, d['src'], device=device)
                emb_tgt = get_embedding(model, d['tgt'], device=device)
                emb_pseudo_src = get_embedding(model, d['pseudo_src'], device=device)
                emb_pseudo_tgt = get_embedding(model, d['pseudo_tgt'], device=device)
                embs = torch.cat([emb_src, emb_tgt, emb_pseudo_src, emb_pseudo_tgt], dim=0)
                np.save(output_path / f'{d["id"]}.npy', embs)
            except Exception as e:
                print(e, e.__traceback__)
                continue

    with open(Path('results', 'codechef', 'codechef_pseudo.json'), 'w', encoding='utf-8') as f:
        json.dump(infos, f, indent=4, ensure_ascii=False)


