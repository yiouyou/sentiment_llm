# coding=utf-8
# python run_file_batch.py -openaikey sk-*** -input job_test.txt -batch 10
import os
import re
import sys
import argparse
import pprint as pp
from langchain import OpenAI, PromptTemplate, LLMChain
from langchain.callbacks import get_openai_callback


parser = argparse.ArgumentParser(description='', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-openaikey', action='store', help='openai_api_key', type=str, default="")
parser.add_argument('-input', action='store', help='input text file', type=str, default="job_test.txt")
parser.add_argument('-batch', action='store', help='batch sentence number', type=int, default=10)
options = parser.parse_args()
os.environ["OPENAI_API_KEY"] = options.openaikey
_file = options.input
N_batch = options.batch


llm = OpenAI(temperature=0)
template = """
Ignore previous instructions. You are a sentiment analyst of customer comments. You assist the company in further operations by dividing customer comments into three categories: positive, negative and neutral. The main purpose is to judge whether customers have a positive attitude towards the products we are trying to sell to them. When analyzing comments, in addition to the general sentiment analysis principles, the following rules must be followed:
1) If the customer is likely to agree to our call back, it is considered positive
2) If the customer is willing to communicate further or is likely to purchase in the future, it is considered positive
3) If the main content of the comment involves numbers, phone numbers, dates, addresses or web addresses, it is considered neutral
4) If the main content of the comment is dominated by interjections, modal particles, nouns or adjectives with no obvious emotional meaning, it is considered neutral

Below are some examples of sentiment analysis for some customer comments in csv format, where the customer's comments are enclosed in double quotes, and after the comma is the sentiment classification of the comments:
{_example}

The customer comment texts that require sentiment analysis are as follows:
{_content}

For each comment, there is no need to output the comment itself, just output the comment index, sentiment classification and short classification reason in the format of "index) classification(reason)", and output the analysis results in English lowercase:
"""
prompt = PromptTemplate(
    input_variables=["_content", "_example"],
    template=template,
)
chain = LLMChain(llm=llm, prompt=prompt)


def call_openai(_content, _example):
    _re = ""
    _tokens = 0
    _cost = 0
    with get_openai_callback() as cb:
        _re = chain.run(_content=_content, _example=_example)
        _tokens = cb.total_tokens
        _cost = cb.total_cost
        print(f"Tokens: {cb.total_tokens} = (Prompt {cb.prompt_tokens} + Completion {cb.completion_tokens})")
        print(f"Cost: ${cb.total_cost}\n")
    # print(_re)
    return (_re, _tokens, _cost)


left, right = os.path.splitext(os.path.basename(_file))
_wf = f"{left}_sentiments.txt"

with open("openai_prompt.examples", "r", encoding="utf8") as ef:
    _example = "".join(ef.readlines())
# print(_example)


if os.path.exists(_file):
    all_re = ""
    total_cost = 0
    
    with open(_file, encoding='utf8') as rf:
        rf_txt = rf.readlines()

    # comment_sentences = {}
    sentences = []
    for i in rf_txt:
        i_li = i.strip()
        # comment_sentences[i_li] = []
        if i_li:
            for j in i_li.split(". "):
                jj = ""
                if j[-1] == '.':
                    jj = j
                else:
                    jj = j+"."
                # comment_sentences[i_li].append({jj: {}})
                sentences.append(jj)
    # print(len(comment_sentences))
    # pp.pprint(comment_sentences)
    # print(len(sentences))
    # pp.pprint(sentences)

    print("-" * 40)
    for i in range(0, len(sentences)):
        if i % N_batch == 0:
            batch = sentences[i:i+N_batch]
            # print(batch)
            _content = ""
            n = int(i / N_batch)
            for j in range(0, len(batch)):
                _content = _content + f"{n*N_batch +j +1}) {batch[j]}\n"
            print(_content)
            (b_re, b_tokens, b_cost) = call_openai(_content, _example)
            total_cost += b_cost
            all_re += b_re + "\n"
    all_re = re.sub(r" *\(", " (", all_re.lower())
    all_re = re.sub(r"\n+", "\n", all_re)
    print("-" * 40)
    print(all_re)
    print(total_cost)

    _sentiments = all_re.split("\n")
    sentiments = []
    for i in _sentiments:
        if i != "":
            sentiments.append(i)
    # print(sentiments)

    if len(sentences) == len(sentiments):
        with open(_wf, "w", encoding='utf8') as wf:
            for i in range(0, len(sentences)):
                i_re= f"{i+1}) \"{sentences[i]}\"|{sentiments[i]}\n"
                # print(i_re)
                wf.write(i_re)
    else:
        print("Error: len(sentences) != len(sentiments)")

