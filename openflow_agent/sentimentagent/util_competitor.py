import pprint as pp


key = "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"


def call_openai(chain, _content):
    from langchain.callbacks import get_openai_callback
    _re = ""
    _tokens = 0
    _cost = 0
    _log = ""
    with get_openai_callback() as cb:
        _re = chain.run(_content=_content)
        _tokens = cb.total_tokens
        _cost = cb.total_cost
        _log += f"\nTokens: {cb.total_tokens} = (Prompt {cb.prompt_tokens} + Completion {cb.completion_tokens})\n"
        _log += f"Cost: ${cb.total_cost}\n\n"
    # print(_re)
    return [_re, _tokens, _cost, _log]


def competitor_openai(key, txt_lines):
    import os
    import re
    from langchain import OpenAI, PromptTemplate, LLMChain
    _log = ""
    _competitor_str = ""
    _total_cost = 0
    ##### set OpenAI API Key and prompt
    os.environ["OPENAI_API_KEY"] = key
    llm = OpenAI(temperature=0)
    template = """
Ignore previous instructions. 

The customer comment texts that require sentiment analysis are as follows:
{_content}

By using nouns, please identify parameters of the the 7P model in upper given customer note, and output in json format in wich in which each 7P should be the MAIN key.
"""
    prompt = PromptTemplate(
        input_variables=["_content"],
        template=template,
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    # [b_re, b_tokens, b_cost, b_log] = call_openai(chain, txt_lines)
    # _log += b_log
    # total_cost += b_cost
    return [_log, _competitor_str, _total_cost]


def competitor_7P_llm(_txt):
    _log = ""
    _competitor_str = ""
    _total_cost = 0
    [_log, _competitor_str, _total_cost] = competitor_openai(key, _txt)
    print(_log)
    return [_competitor_str, str(_total_cost)]
