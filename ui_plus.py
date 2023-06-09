import gradio as gr
from util_sentiment import sentiment_openai_tagging
from util_competitor import competitor_openai_tagging
from util_7P import P7_openai_tagging


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


def llm_sentiment(file_name):
    import os, re
    _log = ""
    _sentences_str = ""
    _sentiments_str = ""
    _total_cost_str = ""
    # print(f"file_name: {file_name}")
    if os.path.exists(file_name):
        left, right = os.path.splitext(os.path.basename(file_name))
        global output_sentiments_file
        output_sentiments_file = f"{left}_sentiments.txt"
        with open(file_name, encoding='utf-8') as rf:
            txt_lines = rf.readlines()
        [_log, _sentences_str, _sentiments_str, _total_cost_str] = sentiment_openai_tagging(txt_lines)
        if _sentences_str != "" and _sentiments_str != "":
            sentences = _sentences_str.split("\n")
            sentiments = _sentiments_str.split("\n")
            sentiments_ = []
            for i in sentiments:
                sentiments_.append(re.sub('\d+\)\s+', '', i))
            with open(output_sentiments_file, "w", encoding='utf-8') as wf:
                for i in range(0, len(sentences)):
                    i_re= f"{sentences[i]}|{sentiments_[i]}\n"
                    wf.write(i_re)
            _log += f"Write file: {output_sentiments_file}" + "\n"
    return [_log, _sentences_str, sentiments_]

def run_llm_sentiment(file):
    if file:
        return llm_sentiment(file.name)
    else:
        return ["ERROR: Please upload a TXT file first!", "", ""]

def show_sentiment_file(text):
    # print(f"text: {text}")
    if text:
        return gr.update(value=output_sentiments_file, visible=True)
    else:
        return gr.update(value=output_sentiments_file)


def llm_7P(file_name):
    import os
    import re
    _log = ""
    _7P_str = ""
    _total_cost_str = ""
    # print(f"file_name: {file_name}")
    if os.path.exists(file_name):
        left, right = os.path.splitext(os.path.basename(file_name))
        global output_7P_file
        output_7P_file = f"{left}_7P.txt"
        with open(file_name, encoding='utf-8') as rf:
            txt_lines = rf.readlines()
        [_log, _7P_str, _total_cost_str, _sentences] = P7_openai_tagging(txt_lines)
        with open(output_7P_file, "w", encoding='utf-8') as wf:
            wf.write(_7P_str)
    return _7P_str

def run_llm_7P(file):
    if file:
        return llm_7P(file.name)
    else:
        return ["ERROR: Please upload a TXT file first!"]

def show_7P_file(text):
    # print(f"text: {text}")
    if text:
        return gr.update(value=output_7P_file, visible=True)
    else:
        return gr.update(value=output_7P_file)


def llm_competitor(file_name):
    import os
    import re
    _log = ""
    _competitor_str = ""
    _total_cost_str = ""
    # print(f"file_name: {file_name}")
    if os.path.exists(file_name):
        left, right = os.path.splitext(os.path.basename(file_name))
        global output_competitor_file
        output_competitor_file = f"{left}_competitor.txt"
        with open(file_name, encoding='utf-8') as rf:
            txt_lines = rf.readlines()
        [_log, _competitor_str, _total_cost_str, _sentences] = competitor_openai_tagging(txt_lines)
        with open(output_competitor_file, "w", encoding='utf-8') as wf:
            wf.write(_competitor_str)
    return _competitor_str

def run_llm_competitor(file):
    if file:
        return llm_competitor(file.name)
    else:
        return ["ERROR: Please upload a TXT file first!"]

def show_competitor_file(text):
    # print(f"text: {text}")
    if text:
        return gr.update(value=output_competitor_file, visible=True)
    else:
        return gr.update(value=output_competitor_file)



with gr.Blocks(title = "Customer Sentiment Plus Analysis by LLM") as demo:
    gr.Markdown("## Customer Sentiment Plus Analysis by LLM")
    with gr.Tab(label = "Run Process"):
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
            with gr.Column():
                output_log = gr.Textbox(label="Logging", placeholder="Logging", lines=12, interactive=False)
            with gr.Column():
                with gr.Row():
                    download_sentiment = gr.File(label="Download Sentiments", file_count="single", type="file", file_types=['.txt'], interactive=False, visible=False)
                with gr.Row():
                    download_7P = gr.File(label="Download 7Ps", file_count="single", type="file", file_types=['.txt'], interactive=False, visible=False)
                with gr.Row():
                    download_competitor = gr.File(label="Download Competitor", file_count="single", type="file", file_types=['.txt'], interactive=False, visible=False)
        with gr.Row():
            with gr.Column():
                output_sentences = gr.Textbox(label="Sentences", placeholder="Sentences", lines=10, interactive=False)
            with gr.Column():
                output_sentiments = gr.Textbox(label="Sentiments", placeholder="Sentiments", lines=10, interactive=False)
            start_btn.click(run_llm_sentiment, inputs=[upload_box], outputs=[output_log, output_sentences, output_sentiments])
            output_sentiments.change(show_sentiment_file, inputs=[output_sentiments], outputs=[download_sentiment])
            with gr.Column():
                output_7P = gr.Textbox(label="7P Marketing", placeholder="7P Marketing", lines=10, interactive=False)
            start_btn.click(run_llm_7P, inputs=[upload_box], outputs=[output_7P])
            output_7P.change(show_7P_file, inputs=[output_7P], outputs=[download_7P])
            with gr.Column():
                output_competitor = gr.Textbox(label="Competitor", placeholder="Competitor", lines=10, interactive=False)
            start_btn.click(run_llm_competitor, inputs=[upload_box], outputs=[output_competitor])
            output_competitor.change(show_competitor_file, inputs=[output_competitor], outputs=[download_competitor])



# from fastapi import FastAPI, Response
# import json
# app = FastAPI()

# @app.get("/")
# def index():
#     return {"message": "Customer Sentiment Plus Analysis by LLM"}

# app = gr.mount_gradio_app(app, demo, path="/ui")

# @app.post("/api/v1/sentiment/")
# async def sentiment_analysis_api(txt: str):
#     key = "sk-**********"
#     N_batch = 5
#     _log = ""
#     _sentences_str = ""
#     _sentiments_str = ""
#     _total_cost_str = ""
#     txt_lines = txt.split("\n")
#     [_log, _sentences_str, _sentiments_str, _total_cost_str] = sentiment_openai_tagging(key, txt_lines, N_batch)
#     res = {"log": _log, "sentences": _sentences_str, "sentiments": _sentiments_str, "cost": _total_cost_str}
#     json_str = json.dumps(res, indent=4, default=str)
#     return Response(content=json_str, media_type='application/json')


if __name__ == "__main__":
    # demo.queue(concurrency_count=1).launch(share=True)
    demo.queue(concurrency_count=1).launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
    )

