# Code2Algo: Code Analysis & Comparator in an algorithmic manner

## Description

이 프로젝트는 학생이 프로그래밍 또는 알고리즘 과제를 수행하면서 제출한 Python code가 틀린 경우 그 원인을 분석하고 해결 방법을 제시해 학생이 지식을 익히는 데에 도움을 주는 Assistant 역할을 수행하는 AI 서비스를 구현하고자 한다. 

위 서비스에서는 pre-trained된 LLM(Large Language-Model) 을 활용해 Python code를 분석하도록 한다. 입력으로 학생이 제출한 wrong code와 실제 정답인 correct code를 함께 넣어주고, 학생이 풀려고 하는 문제 description을 함께 넣어 주어 wrong code가 무엇이 잘못되었고 correct code로 바뀌기 위해 어떤 게 필요한 지 분석해주는 자연어 설명 텍스트를 생성한다. 

해당 입출력 예시는 GPT-4 모델을 통해 이뤄진다. 서비스 데모를 [Gradio](https://gradio.app/) 로 구현했고, user prompt에 들어갈 내용만 입력해 주면 되도록 설정해 두었다. 

데모로 구현한 시스템 외의 실험 내용은 PPT 자료 및 이후 기술할 프로젝트 소스 코드에서 참고할 수 있다. 

## Quickstart

Requirement에 있는 git 저장소 형태의 `chatgpt-wrapper`를 설치했다면, 처음에 터미널에 다음과 같이 입력해 ChatGPT 계정을 로그인해야 한다.
```shell
chatgpt install
```

그러면 기본적으로 웹 브라우저가 뜰 텐데, 해당 페이지에서 사용할 ChatGPT 계정으로 (**GPT-4**를 사용하려면 ChatGPT Pro 권한이 있는 계정으로) 로그인한 뒤 창을 닫으면 설정이 완료된다.

chatgpt-wrapper의 자세한 설치 방법 및 다른 사용 방법을 확인하려면 아래 링크를 참고하는 게 좋다.

https://github.com/mmabrouk/chatgpt-wrapper#installation

또한, Gradio 서비스를 실행하기 위해 다음과 같은 과정을 진행해야 한다. 

먼저 Requirements를 설치한다. torch의 GPU 가속을 원한다면 사전에 CUDA 호환되는 torch를 설치하는 게 좋다. 
```shell
pip install -r requirements.txt
```

이후 `demo.py`를 실행해 Gradio 웹 서버를 실행시킨다. 이 때 openai의 API key는 argument로 주거나, 환경 변수 `OPENAI_API_KEY` 를 설정해야 한다. 
```shell
python demo.py --openai_key=[OPENAI_API_KEY]
```

### Use ChatGPT wrapper instead of OpenAI API
만약 OpenAI API 키가 없거나, API 성능이 마음에 들지 않는 등의 이유로 ChatGPT의 웹 페이지에서와 같이 사용하고 싶다면, 아래와 같이 [ChatGPT wrapper](https://github.com/mmabrouk/chatgpt-wrapper) 를 사용해 모델을 사용할 수 있다. 

## Project Structure

해당 프로젝트는 여러 실험을 진행하면서 전처리, 분석, 배치 실행 코드가 여러 개 섞이게 되었다. 따라서 이 섹션에서는 각 소스 코드의 목적과 입출력을 설명해 차후 재현 가능하도록 지원한다. 

### Dataset / Preprocess codes

- **parse_data.py**
  - `single_instances/`, `multi_line_instances/` 등의 형태로 구성된 raw dataset을 JSON 포맷의 파일 하나로 모아서 저장하는 코드. 해당 출력 결과인 `singles.json` 및 `multis.json`는 예시로 함께 commit해 두었음.
- **preprocess_xlcost.py**
  - [XLCoST](https://github.com/reddy-lab-code-research/XLCoST) 데이터셋 중 Python description + code 관련 데이터를 전처리해 tokenzied code를 raw source code로 변환하고, `data/xlcost/` 아래에 각 데이터셋 별로 JSON 파일을 만드는 코드

### Crawler codes

- **crawl_leetcode.py**
  - [LeetCode](https://leetcode.com/problemset/all/) 의 문제와 인기순 정렬된 solution들을 크롤링해서 가져오는 코드. LeetCode가 사용하는 GraphQL 구조를 활용해 데이터를 가져오는 형태라 이후 API 변화가 발생하면 크롤링이 되지 않을 수 있음.
  - Output directory에 `[문제번호]_[문제Slug].json`으로 파일들을 저장함 
- **crawl_codechef_problem.py**
  - 실험 중 [CodeChef](https://www.codechef.com/practice) 에 있는 문제들의 problem description을 가져오면서 LaTeX 표현식이 깨지는 문제를 해결하기 위해 직접 구현한 크롤러 코드. CodeChef HTML 구조가 바뀌게 되거나 권한이 없으면 크롤링되지 않을 수 있음.
  - `single_test_sample.txt`와 `multi_test_sample.txt`의 두 파일에서 문제 Slug (문제 string id)를 가져와 `problem_samples.json`에 저장함.
  - 전처리 로직이 완벽하지 않아 **약간의 수작업 후처리**가 필요할 수 있음.

### Inference / Experiment codes

- **core.py**
  - Codex 모델을 활용해 pseudo-code를 생성하는 실험을 진행했던 스크립트. 
  - **위의 `parse_data.py`와 다른 구조의 JSON 파일을 사용했기 때문에 곧바로 실행시킬 수는 없고, 해당 구현을 참고하거나 prompt만 참고하기를 권장함.**
- **generate_pseudo_xlcost.py**
  - XLCoST 데이터셋으로 pseudo code를 생성하는 로직. 앞서 전처리한 XLCoST 데이터셋의 JSON 파일들을 읽어 `desc-comment_pseudo.json`의 출력 JSON 파일을 생성함.
- **evaluate_pseudo_xlcost.py**
  - [UniXCoder](https://github.com/microsoft/CodeBERT/tree/master/UniXcoder#1-code-and-nl-embeddings) 모델을 사용해 XLCoST 또는 CodeChef 데이터셋으로 생성한 pseudo code와 기존 코드, description의 embedding을 추출하는 코드. `results/[데이터셋 이름]/embeddings` 디렉토리에 `.npy` 파일들을 저장함.
- **calculate_similarity.py**
  - 추출한 embedding vector들을 불러와 유사도를 계산하고 시각화하는 코드. 필요에 따라 그래프를 만들었기 때문에 전체적인 내용을 참고하되, `evaluate_pseudo_xlcost.py` 에서 생성한 `.npy` 파일의 구조와 동일하게 embedding들을 가져와야 함.
- **chatgpt_test.py**
  - ChatGPT wrapper를 활용해 correct code와 wrong code 간 비교 분석용 prompt 구성 및 실험을 진행한 코드.
  - API로 사용하는 gpt-3.5-turbo의 성능이 웹 페이지보다 낮은 것 같다는 판단으로 API 대신 wrapper 사용
- **demo.py**
  - GPT-4 API를 사용해 Gradio 웹 데모로 만든 구현체 코드.
---
- **test_codex.ipynb**
  - Codex 모델 및 CodeChef 데이터셋으로 여러 prompt 및 실험 구성을 테스트하기 위해 만든 jupyter notebook.
- **test_chatgpt.ipynb**
  - ChatGPT 모델의 API가 열린 이후 해당 API 테스트를 위해 여러 실험용 데이터셋 전처리 & prompt 테스트가 진행된 jupyter notebook. CodeChef의 문제 description에 등장하는 LaTeX 표현식을 전처리하는 코드가 포함되어 있음. 
- **visualize_xlcost.ipynb**
  - XLCoST를 전처리하기 전 데이터셋을 눈으로 확인하고 전처리 로직을 실험해보기 위한 용도로 생성한 jupyter notebook.

### Utility codes

- **visualize.py**
  - `single_instances/`, `multi_line_instances`을 전처리한 JSON 파일의 각 instance를 보기 쉽게 출력하기 위해 만든 코드. 곧바로 실행되지는 않을 수 있어 필요에 따라 사용/수정하면 됨.
- **unixcoder.py**
  - UniXCoder 모델을 사용하기 위한 구현체 코드.
- **vis_pseudo.py**
  - Codex의 pseudo code generation 결과를 시각화하기 위한 Gradio 기반 웹 데모.

## Contributor

- Junwon Hwang
- Jinseok Heo (mrhjs225@gmail.com)
- Eunseok Lee (leees@skku.edu)
