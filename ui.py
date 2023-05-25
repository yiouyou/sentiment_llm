import gradio as gr
import os



output_sentiments_file = "sentiments.txt"

def read_file(file):
    if file:
        with open(file.name, encoding="utf-8") as f:
            content = f.read()
            return content

def chg_btn_color_if_file(file):
    if file:
        return gr.update(variant="primary")
    else:
        return gr.update(variant="secondary")

def show_generated_file(text):
    # print(f"text: {text}")
    if text:
        return gr.update(value=output_sentiments_file)
    else:
        return gr.update(value=output_sentiments_file)


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
    return (_re, _tokens, _cost, _log)

def sentiment_openai(key, txt_lines, N_batch):
    import os
    import re
    from langchain import OpenAI, PromptTemplate, LLMChain
    _log = ""
    _sentences_str = ""
    _sentiments_str = ""
    ##### set OpenAI API Key and prompt
    os.environ["OPENAI_API_KEY"] = key
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
    with open("openai_prompt.examples", "r", encoding="utf-8") as ef:
        _example = "".join(ef.readlines())
    chain = LLMChain(llm=llm, prompt=prompt)
    ##### split comment to sentences
    _sentences = []
    for i in txt_lines:
        i_li = i.strip()
        for j in i_li.split(". "):
            jj = ""
            if j[-1] == '.':
                jj = j
            else:
                jj = j+"."
            _sentences.append(jj)
    ##### call OpenAI API with _content and _example
    _log += "-" * 40 + "\n"
    all_re = ""
    total_cost = 0
    for i in range(0, len(_sentences)):
        if i % N_batch == 0:
            batch = _sentences[i:i+N_batch]
            # print(batch)
            _content = ""
            n = int(i / N_batch)
            for j in range(0, len(batch)):
                _content = _content + f"{n*N_batch +j +1}) {batch[j]}\n"
            _log += _content
            (b_re, b_tokens, b_cost, b_log) = call_openai(chain, _content, _example)
            _log += b_log
            total_cost += b_cost
            all_re += b_re + "\n"
    ##### parse response, generate _log, _sentences_str and _sentiments_str
    sentences = []
    sentiments = []
    all_re = re.sub(r" *\(", " (", all_re.lower())
    all_re = re.sub(r"\n+", "\n", all_re)
    _sentiments = all_re.split("\n")
    for i in _sentiments:
        if i != "":
            sentiments.append(i)
    _log += "-" * 40 + "\n"
    _log += "\n".join(sentiments) + "\n"
    _log += "-" * 40 + "\n"
    _log += f"\nTotal Cost: ${str(total_cost)}\n"
    if len(_sentences) == len(sentiments):
        for i in range(0, len(_sentences)):
            sentences.append(f"{i+1}) \"{_sentences[i]}\"")
        _sentences_str = "\n".join(sentences)
        _sentiments_str = "\n".join(sentiments)
    else:
        _log += "Error: len(sentences) != len(sentiments)" + "\n"
    return [_log, _sentences_str, _sentiments_str]

def sentiment_llm(key, file_name, N_batch):
    import os
    _log = ""
    _sentences_str = ""
    _sentiments_str = ""
    if os.path.exists(file_name):
        left, right = os.path.splitext(os.path.basename(file_name))
        global output_sentiments_file
        output_sentiments_file = f"{left}_sentiments.txt"
        with open(file_name, encoding='utf-8') as rf:
            txt_lines = rf.readlines()
    [_log, _sentences_str, _sentiments_str] = sentiment_openai(key, txt_lines, N_batch)
    if _sentences_str != "" and _sentiments_str != "":
        sentences = _sentences_str.split("\n")
        sentiments = _sentiments_str.split("\n")
        with open(output_sentiments_file, "w", encoding='utf-8') as wf:
            for i in range(0, len(sentences)):
                i_re= f"{sentences[i]}|{sentiments[i]}\n"
                wf.write(i_re)
            _log += f"Write file: {output_sentiments_file}" + "\n"
    return [_log, _sentences_str, _sentiments_str]

def run_sentiment_llm(key, file):
    if key and file:
        return sentiment_llm(key, file.name, 10)
    elif not file and key:
        return ["ERROR: Please upload a TXT file first!", "", ""]
    elif not key and file:
        return ["ERROR: Please input your OpenAI API Key first!", "", ""]
    else:
        return ["ERROR: Please input your OpenAI API Key AND upload a TXT file first!", "", ""]


with gr.Blocks(title = "Customer Sentiment Analysis by LLM") as demo:
    gr.Markdown("## Customer Sentiment Analysis by LLM")
    with gr.Tab(label = "Run Process"):
        with gr.Row():
            openai_api_key = gr.Textbox(label="OpenAI API Key", placeholder="sk-**********", lines=1)
        with gr.Row():
            with gr.Column(scale=2):
                upload_box = gr.File(label="Upload Single TXT File", file_count="single", type="file", file_types=['.txt'], interactive=True)
            with gr.Column(scale=3):
                input_content = gr.Textbox(label="TXT File Content", placeholder="TXT File Content", lines=10, interactive=False)
                upload_box.change(read_file, inputs=[upload_box], outputs=[input_content])
        with gr.Row():
            start_btn = gr.Button("Start Analysis", variant="secondary")
            upload_box.change(chg_btn_color_if_file, inputs=[upload_box], outputs=[start_btn])
            # download_btn = gr.Button("Download Sentiments", variant="secondary")
        with gr.Row():
            output_log = gr.Textbox(label="Logging", placeholder="Logging", lines=10, interactive=False)
            download_box = gr.File(label="Download Sentiments", file_count="single", type="file", file_types=['.txt'], interactive=False)
        with gr.Row():
            with gr.Column():
                output_comments = gr.Textbox(label="Comments", placeholder="Comments", lines=10, interactive=False)
            with gr.Column():
                output_sentiments = gr.Textbox(label="Sentiments", placeholder="Sentiments", lines=10, interactive=False)
            start_btn.click(run_sentiment_llm, inputs=[openai_api_key, upload_box], outputs=[output_log, output_comments, output_sentiments])
            output_sentiments.change(show_generated_file, inputs=[output_sentiments], outputs=[download_box])



from fastapi import FastAPI, Response
import json
app = FastAPI()

@app.get("/")
def index():
    return {"message": "Customer Sentiment Analysis by LLM"}

app = gr.mount_gradio_app(app, demo, path="/ui")

def api_sentiment_llm(key, txt, N_batch):
    _log = ""
    _sentences_str = ""
    _sentiments_str = ""
    txt_lines = txt.split("\n")
    [_log, _sentences_str, _sentiments_str] = sentiment_openai(key, txt_lines, N_batch)
    return [_log, _sentences_str, _sentiments_str]

@app.post("/api/v1/comments/")
async def sentiment_analysis_api(txt: str):
    key = "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"
    N_batch = 10
    _log = ""
    _sentences_str = ""
    _sentiments_str = ""
    [_log, _sentences_str, _sentiments_str] = api_sentiment_llm(key, txt, N_batch)
    res = {"log": _log, "sentences": _sentences_str, "sentiments": _sentiments_str}
    json_str = json.dumps(res, indent=4, default=str)
    return Response(content=json_str, media_type='application/json')


if __name__ == "__main__":
    demo.queue(concurrency_count=1).launch()

