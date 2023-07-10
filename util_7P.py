##### v0
import pprint as pp
key = "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"
N_batch = 3

def call_openai(chain, _content, _example):
    from langchain.callbacks import get_openai_callback
    _re = ""
    _tokens = 0
    _cost = 0
    _log = ""
    with get_openai_callback() as cb:
        _re = chain.run(_content=_content, _example=_example)
        _tokens = cb.total_tokens
        _cost = cb.total_cost
        _log += f"\nTokens: {cb.total_tokens} = (Prompt {cb.prompt_tokens} + Completion {cb.completion_tokens})\n"
        _log += f"Cost: ${cb.total_cost}\n\n"
    # print(_re)
    return [_re, _tokens, _cost, _log]

def split_note_to_sentences(txt_lines):
    ##### split note to sentences
    _sentences = []
    for i in txt_lines:
        i_li = i.strip()
        if i_li:
            for j in i_li.split(". "):
                jj = ""
                if j[-1] == '.':
                    jj = j
                else:
                    jj = j+"."
                _sentences.append(jj)
    return _sentences

def P7_openai(key, txt_lines, N_batch):
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
Ignore previous instructions. As a marketing strategy analyst, your task is to identify and extract the 7Ps from each customer comment using nouns, according to the 7Ps Marketing Mix.

Below are some examples of 7Ps analysis for some customer comments in csv format, where the customer's comments are enclosed in double quotes, and after the comma is the 7Ps analysis results:
{_example}

The customer comments that require marketing strategy analysis are as follows:
{_content}

For each comment, identify and extract relative nouns of 7Ps from and only from the comment. Output the analysis result of each comment in JSON format in one line, with the 7Ps as the main key and the corresponding nouns as the values. The order of the main key is: Product, Price, Place, Promotion, People, Process, Physical evidence.

Please output the analysis results in English lowercase:
"""
    prompt = PromptTemplate(
        input_variables=["_content", "_example"],
        template=template,
    )
    ##### 随机取10个example
    import random
    with open("examples_7P.txt", "r", encoding="utf-8") as ef:
        _example = "".join(random.sample(ef.readlines(), 30))
    ##### LLMChain
    chain = LLMChain(llm=llm, prompt=prompt)
    ##### split note to sentences
    _sentences = split_note_to_sentences(txt_lines)
    ##### call OpenAI API with _content
    all_re = ""
    for i in range(0, len(_sentences)):
        if i % N_batch == 0:
            batch = _sentences[i:i+N_batch]
            # print(batch)
            _content = ""
            n = int(i / N_batch)
            for j in range(0, len(batch)):
                _content = _content + f"{n*N_batch +j +1}) {batch[j]}\n"
            _log += _content
            # print(prompt.format(_content=_content, _example=_example))
            [b_re, b_tokens, b_cost, b_log] = call_openai(chain, _content, _example)
            _log += b_log
            _total_cost += b_cost
            all_re += b_re + "\n"
            # print(b_re)
    _total_cost_str = format(_total_cost, ".5f")
    _7P_str = all_re.strip()
    return [_log, _7P_str, _total_cost_str, _sentences]

def parse_7P_str(_str, _sentences):
    import re
    import json
    _re = []
    _li = _str.split("\n")
    for i in _li:
        if i:
            # print(i)
            _1 = i.split(" {")
            _i = "{" + _1[1]
            # print(f"_i: {_i}")
            _re.append(_i)
    for i in range(len(_sentences)):
        # print(f"\n{i}, {_sentences[i]}")
        _i_json = json.loads(_re[i])
        # print(type(_i_json), _i_json)
        for j in _i_json:
            if _i_json[j].lower() not in _sentences[i].lower():
                # print(">>>", _i_json[j])
                _i_json[j] = ''
            if _i_json[j].lower() == 'none':
                _i_json[j] = ''
        _re[i] = json.dumps(_i_json, ensure_ascii=False)
        # print(type(_re[i]), _re[i], "\n")
    _re_str = '[' + ', '.join(_re) + ']'
    return _re_str

def P7_llm(_txt):
    global key
    _log = ""
    _7P_str = ""
    _total_cost = 0
    txt_lines = _txt.split("\n")
    [_log, _7P_str, _total_cost_str, _sentences] = P7_openai(key, txt_lines, N_batch)
    # print(_log)
    # print(_7P_str)
    import ast
    _7P_str = parse_7P_str(_7P_str, _sentences)
    # print(_7P_str)
    _7P = ast.literal_eval(_7P_str)
    # print(type(_7P), _7P)
    return [_7P, _total_cost_str]



##### v1
def call_openai_tagging(chain, _sentence):
    from langchain.callbacks import get_openai_callback
    _re = ""
    _tokens = 0
    _cost = 0
    _log = ""
    with get_openai_callback() as cb:
        _re = chain.run(_sentence)
        _tokens = cb.total_tokens
        _cost = cb.total_cost
        _log += f"\nTokens: {cb.total_tokens} = (Prompt {cb.prompt_tokens} + Completion {cb.completion_tokens})\n"
        _cost_str = format(cb.total_cost, ".5f")
        _log += f"Cost: ${_cost_str}\n\n"
    print(_sentence, _re)
    print(_log)
    return [_re, _tokens, _cost, _log]

def P7_openai_tagging(txt_lines):
    from langchain.chains import create_tagging_chain
    from dotenv import load_dotenv
    load_dotenv()
    from langchain.chat_models import ChatOpenAI
    llm = ChatOpenAI(temperature=0)
    #####
    schema = {
        "properties": {
            "Product": {
                "type": "string",
                "description": """
According to the 7Ps Marketing Mix, identify and extract the 'Product' of 7Ps using nouns. Remeber it's the item or service that we offer to our customers.

Below are some examples of 7Ps analysis for customer comments in csv format, where the customer's comments are enclosed in double quotes, and after the comma is the 7Ps analysis results:
"han sidder i VVS og har ikke meget med de her sager at gøre", {"product":"VVS", "price":"", "place":"", "promotion":"", "people":"", "process":"", "physical evidence":""}
"Jan Milling skriver i mail 28 juni at han skal forhandle renovation i oktober og omtaler vores "fine materiale".", {"product":"renovation", "price":"", "place":"", "promotion":"omtaler", "people":"", "process":"", "physical evidence":""}
"Der har været Opslag på Linked In af Laust omkring affaldssortering og vi talte om at tage vores dialog videre.", {"product":"affaldssortering", "price":"", "place":"", "promotion":"", "people":"", "process":"", "physical evidence":""}
"Vi skal tale med Mogens Bang om den her.", {"product":"", "price":"", "place":"", "promotion":"", "people":"", "process":"", "physical evidence":""}
""",
            },
            "Price": {
                "type": "string",
                "description": """
According to the 7Ps Marketing Mix, identify and extract the 'Price' of 7Ps using nouns. Remeber it's the amount of money that we charge for our product or service.

Below are some examples of 7Ps analysis for some customer comments in csv format, where the customer's comments are enclosed in double quotes, and after the comma is the 7Ps analysis results:
"Vi skal tale med Mogens Bang om den her.", {"product":"", "price":"", "place":"", "promotion":"", "people":"", "process":"", "physical evidence":""}
""",
            },
            "Place": {
                "type": "string",
                "description": """
According to the 7Ps Marketing Mix, identify and extract the 'Place' of 7Ps using nouns. Remeber it's the channels and locations that we use to distribute and sell our product or service.

Below are some examples of 7Ps analysis for some customer comments in csv format, where the customer's comments are enclosed in double quotes, and after the comma is the 7Ps analysis results:
"er en del af en kæde så det er dem jeg skal have fat i", {"product":"", "price":"", "place":"kæde", "promotion":"", "people":"", "process":"", "physical evidence":""}
"vil gerne høre lidt mere om det, et højaktuelt emne og hvad der er på markedet, omvendt det bekymrer ham at give 3.", {"product":"", "price":"", "place":"markedet", "promotion":"", "people":"", "process":"", "physical evidence":""}
"Vi skal tale med Mogens Bang om den her.", {"product":"", "price":"", "place":"", "promotion":"", "people":"", "process":"", "physical evidence":""}
""",
            },
            "Promotion": {
                "type": "string",
                "description": """
According to the 7Ps Marketing Mix, identify and extract the 'Promotion' of 7Ps using nouns. Remeber it's the ways that we communicate and advertise our product or service to our target market.

Below are some examples of 7Ps analysis for some customer comments in csv format, where the customer's comments are enclosed in double quotes, and after the comma is the 7Ps analysis results:
"Christian har skrevet at det ikke var aktuelt lige nu med hjemmesiden til udlejning, da der var kø, så der behøvede ikke PR", {"product":"hjemmesiden", "price":"", "place":"", "promotion":"PR", "people":"", "process":"kø", "physical evidence":""}
"Jan Milling skriver i mail 28 juni at han skal forhandle renovation i oktober og omtaler vores "fine materiale".", {"product":"renovation", "price":"", "place":"", "promotion":"omtaler", "people":"", "process":"", "physical evidence":""}
"Vi skal tale med Mogens Bang om den her.", {"product":"", "price":"", "place":"", "promotion":"", "people":"", "process":"", "physical evidence":""}
""",
            },
            "People": {
                "type": "string",
                "description": """
According to the 7Ps Marketing Mix, identify and extract the 'People' of 7Ps using nouns. Remeber it's the job titles who are involved in creating, delivering, and supporting our product or service, not the names of specific individuals. Focus only on job titles related to the company's business. DO NOT extract the names of specific individuals.

Below are some examples of 7Ps analysis for some customer comments in csv format, where the customer's comments are enclosed in double quotes, and after the comma is the 7Ps analysis results:
"Ikke inde i Niras, han er facility mand", {"product":"", "price":"", "place":"", "promotion":"", "people":"facility mand", "process":"", "physical evidence":""}
"Har givet den videre til Jan, som er ejer.", {"product":"", "price":"", "place":"", "promotion":"",  "people":"", "process":"", "physical evidence":""}
"Bad MM ringe tilbage eller sende tid for muligt møde på sms.", {"product":"", "price":"", "place":"", "promotion":"",  "people":"", "process":"", "physical evidence":""}"Helle Pedersen gik direkte på tlfsvarer.", {"product":"", "price":"", "place":"", "promotion":"",  "people":"", "process":"", "physical evidence":""}
"Vi skal tale med Mogens Bang om den her.", {"product":"", "price":"", "place":"", "promotion":"", "people":"", "process":"", "physical evidence":""}
""",
            },
            "Process": {
                "type": "string",
                "description": """
According to the 7Ps Marketing Mix, identify and extract the 'Process' of 7Ps using nouns. Remeber it's the steps and procedures that we follow to ensure quality and efficiency in your product or service delivery.

Below are some examples of 7Ps analysis for some customer comments in csv format, where the customer's comments are enclosed in double quotes, and after the comma is the 7Ps analysis results:
"Har ringet ind til deres fysioterapi tidsbestilling, men det er outsourcet til Meyers køkkener, så det er nok dem jeg skal tale med", {"product":"", "price":"", "place":"", "promotion":"", "people":"", "process":"outsourcet", "physical evidence":""}
"Thorballe var positiv, mente tilbuddet var som det skulle være, og det hele er kun stoppet grundet outsourcing, som de ikke kendte til.", {"product":"", "price":"", "place":"", "promotion":"", "people":"", "process":"outsourcing", "physical evidence":""}
"Vi skal tale med Mogens Bang om den her.", {"product":"", "price":"", "place":"", "promotion":"", "people":"", "process":"", "physical evidence":""}
""",
            },
            "Physical evidence": {
                "type": "string",
                "description": """
According to the 7Ps Marketing Mix, identify and extract the 'Physical evidence' of 7Ps using nouns. Remeber it's the tangible and intangible aspects that show and prove our product or service quality and value.

Below are some examples of 7Ps analysis for some customer comments in csv format, where the customer's comments are enclosed in double quotes, and after the comma is the 7Ps analysis results:
"Vi skal tale med Mogens Bang om den her.", {"product":"", "price":"", "place":"", "promotion":"", "people":"", "process":"", "physical evidence":""}
""",
            },
        },
        "required": ["Product", "Price", "Place", "Promotion", "People", "Process", "Physical evidence"],
    }
    chain = create_tagging_chain(schema, llm)
    ##### split notes to sentences
    _sentences = []
    for i in txt_lines:
        i_li = i.strip()
        if i_li:
            for j in i_li.split(". "):
                jj = ""
                if j[-1] == '.':
                    jj = j
                else:
                    jj = j+"."
                _sentences.append(jj)
    # print(len(_sentences))
    ##### 
    _log = ""
    _total_cost = 0
    _7P = []
    ##### call OpenAI API with _content and _example
    _log += "-" * 40 + "\n"
    for i in range(0, len(_sentences)):
        [i_re, i_tokens, i_cost, i_log] = call_openai_tagging(chain, _sentences[i])
        _log += i_log
        _total_cost += i_cost
        _7P.append(i_re)
    _total_cost_str = format(_total_cost, ".5f")
    # print(len(_7P))
    # print(_7P)
    ##### parse response, generate _log and _7P_str
    _log += "-" * 40 + "\n"
    _log += str(_7P) + "\n"
    _log += "-" * 40 + "\n"
    _log += f"\nTotal Cost: ${_total_cost_str}\n"
    _7P_str = ""
    if len(_sentences) == len(_7P):
        _7P_str = str(_7P)
    else:
        _log += "Error: len(sentences) != len(7P)" + "\n"
    return [_log, _7P_str, _total_cost_str, _sentences]

def P7_llm_tagging(_txt):
    import re
    _log = ""
    _7P_str = ""
    _total_cost = 0
    txt_lines = _txt.split("\n")
    [_log, _7P_str, _total_cost_str, _sentences] = P7_openai_tagging(txt_lines)
    # print(_log)
    # print(_7P_str)
    import ast
    _7P = ast.literal_eval(_7P_str)
    # print(type(_7P), _7P)
    return [_7P, _total_cost_str]



if __name__ == "__main__":

    # _txt = "Ved ikke om de har noget organisk affald... på deres hovedkontor har de et køkken, men det er en ekstern operatør der driver det... det er Michael Kjær fra driften, et fælles køkken med andre virksomheder.. Ring til ham om det. NCC bestemmer desuden selv om de skal have vores projekt med i loopet på dgnb point i byggeriet... i deres koncept udvikling...; De er ved at definere det og vi kan vende retur til Martin i Januar, hvor han ved hvem vi skal have møde med om det."
    # [_re, _cost] = P7_llm(_txt)
    # print("\n>>>", type(_re), _re)
    # print(type(_cost), _cost)

    _txt = """Har ringet ind til deres fysioterapi tidsbestilling, men det er outsourcet til Meyers køkkener, så det er nok dem jeg skal tale med.
er en del af en kæde så det er dem jeg skal have fat i.
han sidder i VVS og har ikke meget med de her sager at gøre.
Christian har skrevet at det ikke var aktuelt lige nu med hjemmesiden til udlejning, da der var kø, så der behøvede ikke PR.
Ikke inde i Niras, han er facility mand.
Jan Milling skriver i mail 28 juni at han skal forhandle renovation i oktober og omtaler vores 'fine materiale'.
Thorballe var positiv, mente tilbuddet var som det skulle være, og det hele er kun stoppet grundet outsourcing, som de ikke kendte til.
Der har været Opslag på Linked In af Laust omkring affaldssortering og vi talte om at tage vores dialog videre.
vil gerne høre lidt mere om det, et højaktuelt emne og hvad der er på markedet, omvendt det bekymrer ham at give 3.
Har givet den videre til Jan, som er ejer.
Jeg foreslog møde sidste halvdel Juli eller i august.
De har fået at vide, at det ville være på plads om 2-3 uger.
Bad MM ringe tilbage eller sende tid for muligt møde på sms.
Helle Pedersen gik direkte på tlfsvarer.
Vil gerne have en mail sådan at han kan give en status og han vil også gerne have en intromail.
Rune vil ringe til kunden imorgen høre dem ad.
Talte med ham ifm.
bud til Bent Brandt.
Fullgte 12 maj op på, hvorvidt den vandt gehør.
Han har ikke nævnt nogen specifik dato men sagde ca om 14 dage hvilket Er denne dato.
Følge op på denne&nbsp;.
Skal ringe igen om 3 uger.
Opfølgning 29/6-2023.
Opfølgning på lejeaftale.
Vi skal tale med Mogens Bang om den her.
bud til Bent Brand.
opfølgning 16 Juni.
"""
    [_re, _cost] = P7_llm_tagging(_txt)
    print(type(_re))
    for i in _re:
        print(i)
    print(type(_cost), _cost)

