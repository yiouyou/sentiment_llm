# python run.py -openaikey sk-*** -input job_test.txt
import os
import sys
import argparse
from langchain import OpenAI, PromptTemplate, LLMChain
from langchain.callbacks import get_openai_callback


parser = argparse.ArgumentParser(description='', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-openaikey', action='store', help='openai_api_key', type=str, default="")
parser.add_argument('-input', action='store', help='input text file', type=str, default="job_test.txt")
options = parser.parse_args()
os.environ["OPENAI_API_KEY"] = options.openaikey
_file = options.input


llm = OpenAI(temperature=0)
template = """
Ignore previous instructions. You are a sentiment analyst of customer comments. You assist the company in further operations by dividing customer comments into three categories: positive, negative and neutral. The main purpose is to judge whether customers have a positive attitude towards the products we are trying to sell to them. When analyzing comments, in addition to the general sentiment analysis principles, the following rules must be followed:
1) If the customer is likely to agree to our call back, it is considered positive
2) If the customer is willing to communicate further or is likely to purchase in the future, it is considered positive
3) If the main content of the comment involves numbers, phone numbers, dates, addresses or web addresses, it is considered neutral
4) If the main content of the comment is dominated by interjections, modal particles, nouns or adjectives with no obvious emotional meaning, it is considered neutral

Below are some examples of sentiment analysis for some customer comments in csv format, where the customer's comments are enclosed in double quotes, and after the comma is the sentiment classification of the comments:
{_example}

The customer comment text that requires sentiment analysis is as follows:
{_content}

Output the sentiment classification and a short reason for the classification in "classification (reason)" format, and output the analysis results in English lowercase:
"""
prompt = PromptTemplate(
    input_variables=["_content", "_example"],
    template=template,
)
chain = LLMChain(llm=llm, prompt=prompt)


def call_openai(_content, _example):
    with get_openai_callback() as cb:
        _re = chain.run(_content=_content, _example=_example)
        print(f"Total Tokens: {cb.total_tokens}")
        print(f"Prompt Tokens: {cb.prompt_tokens}")
        print(f"Completion Tokens: {cb.completion_tokens}")
        print(f"Total Cost (USD): ${cb.total_cost}")
    # print(_re)
    return _re


left, right = os.path.splitext(os.path.basename(_file))
_wf = f"{left}.sentiment"

with open("openai_prompt.examples", "r", encoding="utf8") as ef:
    _example = "".join(ef.readlines())
# print(_example)


_seg = "-"*40
if os.path.exists(_file):
    with open(_file, encoding='utf8') as rf:
        rf_txt = rf.readlines()
    with open(_wf, "w", encoding='utf8') as wf:
        n = 0
        for i in rf_txt:
            i_li = i.strip()
            # wf.write(f"> \"{i_li}\"\n")
            wf.write(f"{_seg}{_seg}\n")
            for j in i_li.split(". "):
                n = n + 1
                jj = ""
                if j[-1] == '.':
                    jj = j
                else:
                    jj = j+"."
                j_re = "***###***"
                j_re = call_openai(jj, _example)
                j_re = j_re.replace("\n", "")
                wf.write(f"{n}) \"{jj}\", {j_re}\n")
            wf.write(f"{_seg}{_seg}\n\n")

