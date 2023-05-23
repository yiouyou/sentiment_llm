import string
import gradio as gr
import os


def read_file(file):
    if file:
        with open(file.name, encoding="utf-8") as f:
            content = f.read()
            return content

def chg_color_file(file):
    if file:
        return gr.update(variant="primary")
    else:
        return gr.update(variant="secondary")

# def chg_color_text(text):
#     print(f"text: {text}")
#     if text:
#         return gr.update(variant="primary")
#     else:
#         return gr.update(variant="secondary")

def run_sentiment_analysis(key, file):
    file_name = file.name
    if key and file_name:
        return sentiment_llm(key, file_name, 10)
    elif not file_name and key:
        return "ERROR: Please upload a TXT file first!"
    elif not key and file_name:
        return "ERROR: Please input your OpenAI API Key first!"
    else:
        return "ERROR: Please input your OpenAI API Key AND upload a TXT file first!"


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


def sentiment_llm(key, file_name, N_batch):
    import os
    import re
    from langchain import OpenAI, PromptTemplate, LLMChain
    _file = file_name
    _key = key
    # print(_file)
    # print(_key)
    _log = ""
    left, right = os.path.splitext(os.path.basename(_file))
    _output = f"{left}.sentiment"
    os.environ["OPENAI_API_KEY"] = _key
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
    with open("openai_prompt.examples", "r", encoding="utf-8") as ef:
        _example = "".join(ef.readlines())
    # print(_example)
    if os.path.exists(_file):
        all_re = ""
        total_cost = 0
        with open(_file, encoding='utf-8') as rf:
            rf_txt = rf.readlines()
        # comment_sentences = {}
        _sentences = []
        for i in rf_txt:
            i_li = i.strip()
            # comment_sentences[i_li] = []
            for j in i_li.split(". "):
                jj = ""
                if j[-1] == '.':
                    jj = j
                else:
                    jj = j+"."
                # comment_sentences[i_li].append({jj: {}})
                _sentences.append(jj)
        _log += "-" * 40 + "\n"
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
        all_re = re.sub(r" *\(", " (", all_re.lower())
        all_re = re.sub(r"\n+", "\n", all_re)
        _sentiments = all_re.split("\n")
        sentiments = []
        for i in _sentiments:
            if i != "":
                sentiments.append(i)
        _log += "-" * 40 + "\n"
        _log += "\n".join(sentiments) + "\n"
        _log += "-" * 40 + "\n"
        _log += f"\nTotal Cost: ${str(total_cost)}\n"
        sentences = []
        if len(_sentences) == len(sentiments):
            with open(_output, "w", encoding='utf-8') as wf:
                for i in range(0, len(_sentences)):
                    sentences.append(f"{i+1}) {_sentences[i]}")
                    i_re= f"{i+1}) {_sentences[i]}, {sentiments[i]}\n"
                    # print(i_re)
                    wf.write(i_re)
                _log += f"Write file: {_output}" + "\n"
        else:
            _log += "Error: len(sentences) != len(sentiments)" + "\n"
    return [_log, "\n".join(sentences), "\n".join(sentiments)]


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
            upload_box.change(chg_color_file, inputs=[upload_box], outputs=[start_btn])
            # download_btn = gr.Button("Download Sentiments", variant="secondary")
        with gr.Row():
            output_log = gr.Textbox(label="Logging", placeholder="Logging", lines=10, interactive=False)
            download_box = gr.File(label="Download Sentiments", file_count="single", type="file", file_types=['.txt'], interactive=False)
        with gr.Row():
            with gr.Column():
                output_comments = gr.Textbox(label="Comments", placeholder="Comments", lines=10, interactive=False)
            with gr.Column():
                output_sentiments = gr.Textbox(label="Sentiments", placeholder="Sentiments", lines=10, interactive=False)
            start_btn.click(run_sentiment_analysis, inputs=[openai_api_key, upload_box], outputs=[output_log, output_comments, output_sentiments])
            # output_sentiments.change(chg_color_text, inputs=[output_sentiments], outputs=[download_btn])


from fastapi import FastAPI
app = FastAPI()
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    demo.queue(concurrency_count=1).launch()
