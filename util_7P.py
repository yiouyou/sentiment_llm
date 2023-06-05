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


def P7_openai(key, txt_lines):
    import os
    import re
    from langchain import OpenAI, PromptTemplate, LLMChain
    _log = ""
    _7P_str = ""
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
    for i in txt_lines:
        i_li = i.strip()
        # [b_re, b_tokens, b_cost, b_log] = call_openai(chain, i_li)
        # _log += b_log
        # total_cost += b_cost
    return [_log, _7P_str, _total_cost]


def P7_llm(_txt):
    _log = ""
    _7P_str = ""
    _total_cost = 0
    txt_lines = _txt.split("\n")
    [_log, _7P_str, _total_cost] = P7_openai(key, txt_lines)
    print(_log)
    return [_7P_str, str(_total_cost)]



if __name__ == "__main__":

    _txt = "Ved ikke om de har noget organisk affald... på deres hovedkontor har de et køkken, men det er en ekstern operatør der driver det... det er Michael Kjær fra driften, et fælles køkken med andre virksomheder.. Ring til ham om det. NCC bestemmer desuden selv om de skal have vores projekt med i loopet på dgnb point i byggeriet... i deres koncept udvikling...; De er ved at definere det og vi kan vende retur til Martin i Januar, hvor han ved hvem vi skal have møde med om det."
    P7_llm(_txt)
