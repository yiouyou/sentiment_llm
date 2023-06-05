# coding=utf-8
# python run_1note.py -openaikey sk-*** -input "Ved ikke om de har noget organisk affald... på deres hovedkontor har de et køkken, men det er en ekstern operatør der driver det... det er Michael Kjær fra driften, et fælles køkken med andre virksomheder.. Ring til ham om det. NCC bestemmer desuden selv om de skal have vores projekt med i loopet på dgnb point i byggeriet... i deres koncept udvikling...; De er ved at definere det og vi kan vende retur til Martin i Januar, hvor han ved hvem vi skal have møde med om det."
import os
import argparse
import pprint as pp
from util_sentiment import sentiment_openai
from util_competitor import competitor_openai
from util_7P import P7_openai


parser = argparse.ArgumentParser(description='', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-openaikey', action='store', help='openai_api_key', type=str, default="")
parser.add_argument('-input', action='store', help='input text string', type=str, default="")
options = parser.parse_args()
key = options.openaikey
_txt = options.input
N_batch = 20


if _txt:
    _log = ""
    _sentences_str = ""
    _sentiments_str = ""
    _total_cost = 0
    [_log, _sentences_str, _sentiments_str, _total_cost] = sentiment_openai(key, [_txt], N_batch)
    print(f"_log:\n{_log}\n")
    print(f"_sentences_str:\n{_sentences_str}\n")
    print(f"_sentiments_str:\n{_sentiments_str}\n")
    print(f"_total_cost:\n{_total_cost}\n")

    _log = ""
    _competitor_str = ""
    _total_cost = 0
    [_log, _competitor_str, _total_cost] = competitor_openai(key, [_txt], N_batch)
    print(f"_log:\n{_log}\n")
    print(f"_sentences_str:\n{_competitor_str}\n")
    print(f"_total_cost:\n{_total_cost}\n")

    _log = ""
    _7P_str = ""
    _total_cost = 0
    [_log, _7P_str, _total_cost] = P7_openai(key, [_txt], N_batch)
    print(f"_log:\n{_log}\n")
    print(f"_7P_str:\n{_7P_str}\n")
    print(f"_total_cost:\n{_total_cost}\n")

