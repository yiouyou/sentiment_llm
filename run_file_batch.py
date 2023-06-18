# coding=utf-8
# python run_file_batch.py -openaikey sk-*** -input test_notes.txt -batch 10
import os
import argparse
import pprint as pp
from util_sentiment_index import sentiment_openai


parser = argparse.ArgumentParser(description='', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-openaikey', action='store', help='openai_api_key', type=str, default="")
parser.add_argument('-input', action='store', help='input text file', type=str, default="job_test.txt")
parser.add_argument('-batch', action='store', help='batch sentence number', type=int, default=10)
options = parser.parse_args()
key = options.openaikey
_file = options.input
N_batch = options.batch


if os.path.exists(_file):
    with open(_file, encoding='utf8') as rf:
        txt_lines = rf.readlines()
    _log = ""
    _sentences_str = ""
    _sentiments_str = ""
    _total_cost = 0
    [_log, _sentences_str, _sentiments_str, _total_cost] = sentiment_openai(key, txt_lines, N_batch)
    print(f"_log:\n{_log}\n")
    print(f"_sentences_str:\n{_sentences_str}\n")
    print(f"_sentiments_str:\n{_sentiments_str}\n")
    print(f"_total_cost:\n{_total_cost}\n")
