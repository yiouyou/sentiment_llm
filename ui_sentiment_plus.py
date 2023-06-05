import gradio as gr
from util_sentiment import sentiment_openai
from util_competitor import competitor_openai
from util_7P import P7_openai


output_sentiments_file = "_sentiments.txt"
output_competitor_file = "_competitor.txt"
output_7P_file = "_7P.txt"


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


def llm_sentiment(key, file_name, N_batch):
    import os
    _log = ""
    _sentences_str = ""
    _sentiments_str = ""
    _total_cost = 0
    if os.path.exists(file_name):
        left, right = os.path.splitext(os.path.basename(file_name))
        global output_sentiments_file
        output_sentiments_file = f"{left}_sentiments.txt"
        with open(file_name, encoding='utf-8') as rf:
            txt_lines = rf.readlines()
        [_log, _sentences_str, _sentiments_str, _total_cost] = sentiment_openai(key, txt_lines, N_batch)
        if _sentences_str != "" and _sentiments_str != "":
            sentences = _sentences_str.split("\n")
            sentiments = _sentiments_str.split("\n")
            with open(output_sentiments_file, "w", encoding='utf-8') as wf:
                for i in range(0, len(sentences)):
                    i_re= f"{sentences[i]}|{sentiments[i]}\n"
                    wf.write(i_re)
            _log += f"Write file: {output_sentiments_file}" + "\n"
    return [_log, _sentences_str, _sentiments_str]

def run_llm_sentiment(key, file):
    if key and file:
        return llm_sentiment(key, file.name, 10)
    elif not file and key:
        return ["ERROR: Please upload a TXT file first!", "", ""]
    elif not key and file:
        return ["ERROR: Please input your OpenAI API Key first!", "", ""]
    else:
        return ["ERROR: Please input your OpenAI API Key AND upload a TXT file first!", "", ""]

def show_sentiment_file(text):
    # print(f"text: {text}")
    if text:
        return gr.update(value=output_sentiments_file)
    else:
        return gr.update(value=output_sentiments_file)


def llm_7P(key, file_name):
    import os
    _log = ""
    _7P_str = ""
    _total_cost = 0
    if os.path.exists(file_name):
        left, right = os.path.splitext(os.path.basename(file_name))
        global output_sentiments_file
        output_7P_file = f"{left}_7P.txt"
        with open(file_name, encoding='utf-8') as rf:
            txt_lines = rf.readlines()
        [_log, _7P_str, _total_cost] = P7_openai(key, txt_lines)
        with open(output_7P_file, "w", encoding='utf-8') as wf:
            wf.write(_7P_str)
    return [_7P_str]

def run_llm_7P(key, file):
    if key and file:
        return llm_7P(key, file.name)
    elif not file and key:
        return ["ERROR: Please upload a TXT file first!", "", ""]
    elif not key and file:
        return ["ERROR: Please input your OpenAI API Key first!", "", ""]
    else:
        return ["ERROR: Please input your OpenAI API Key AND upload a TXT file first!", "", ""]

def show_7P_file(text):
    # print(f"text: {text}")
    if text:
        return gr.update(value=output_7P_file)
    else:
        return gr.update(value=output_7P_file)


def llm_competitor(key, file_name):
    import os
    _log = ""
    _competitor_str = ""
    _total_cost = 0
    if os.path.exists(file_name):
        left, right = os.path.splitext(os.path.basename(file_name))
        global output_sentiments_file
        output_competitor_file = f"{left}_competitor.txt"
        with open(file_name, encoding='utf-8') as rf:
            txt_lines = rf.readlines()
        [_log, _competitor_str, _total_cost] = competitor_openai(key, txt_lines)
        with open(output_competitor_file, "w", encoding='utf-8') as wf:
            wf.write(_competitor_str)
    return [_competitor_str]

def run_llm_competitor(key, file):
    if key and file:
        return llm_competitor(key, file.name)
    elif not file and key:
        return ["ERROR: Please upload a TXT file first!", "", ""]
    elif not key and file:
        return ["ERROR: Please input your OpenAI API Key first!", "", ""]
    else:
        return ["ERROR: Please input your OpenAI API Key AND upload a TXT file first!", "", ""]

def show_competitor_file(text):
    # print(f"text: {text}")
    if text:
        return gr.update(value=output_competitor_file)
    else:
        return gr.update(value=output_competitor_file)



with gr.Blocks(title = "Customer Sentiment Plus Analysis by LLM") as demo:
    gr.Markdown("## Customer Sentiment Plus Analysis by LLM")
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
                output_sentences = gr.Textbox(label="Sentences", placeholder="Sentences", lines=10, interactive=False)
            with gr.Column():
                output_sentiments = gr.Textbox(label="Sentiments", placeholder="Sentiments", lines=10, interactive=False)
            start_btn.click(run_llm_sentiment, inputs=[openai_api_key, upload_box], outputs=[output_log, output_sentences, output_sentiments])
            output_sentiments.change(show_sentiment_file, inputs=[output_sentiments], outputs=[download_box])
            with gr.Column():
                output_7P = gr.Textbox(label="7P Marketing", placeholder="7P Marketing", lines=10, interactive=False)
            start_btn.click(run_llm_7P, inputs=[openai_api_key, upload_box], outputs=[output_7P])
            output_7P.change(show_7P_file, inputs=[output_7P], outputs=[download_box])
            with gr.Column():
                output_competitor = gr.Textbox(label="Competitor", placeholder="Competitor", lines=10, interactive=False)
            start_btn.click(run_llm_competitor, inputs=[openai_api_key, upload_box], outputs=[output_competitor])
            output_competitor.change(show_competitor_file, inputs=[output_competitor], outputs=[download_box])



from fastapi import FastAPI, Response
import json
app = FastAPI()

@app.get("/")
def index():
    return {"message": "Customer Sentiment Plus Analysis by LLM"}

app = gr.mount_gradio_app(app, demo, path="/ui")


@app.post("/api/v1/sentiment/")
async def sentiment_analysis_api(txt: str):
    key = "sk-**********"
    N_batch = 10
    _log = ""
    _sentences_str = ""
    _sentiments_str = ""
    _total_cost = 0
    txt_lines = txt.split("\n")
    [_log, _sentences_str, _sentiments_str, _total_cost] = sentiment_openai(key, txt_lines, N_batch)
    res = {"log": _log, "sentences": _sentences_str, "sentiments": _sentiments_str, "cost": _total_cost}
    json_str = json.dumps(res, indent=4, default=str)
    return Response(content=json_str, media_type='application/json')


if __name__ == "__main__":
    demo.queue(concurrency_count=1).launch(share=True)

