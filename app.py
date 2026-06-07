"""
Milestone 5 — Gradio query interface.

Run:  .venv/bin/python app.py   then open http://localhost:7860
"""

import gradio as gr

from query import ask


def handle_query(question):
    if not question or not question.strip():
        return "Please enter a question.", ""
    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"]) or "(no sources — insufficient information)"
    return result["answer"], sources


with gr.Blocks(title="The Unofficial Guide — GT CS Professors") as demo:
    gr.Markdown(
        "# The Unofficial Guide\n"
        "Ask about Georgia Tech CS professors. Answers come **only** from student reviews."
    )
    inp = gr.Textbox(label="Your question", placeholder="e.g. Is Will Perkins a tough grader?")
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])


if __name__ == "__main__":
    demo.launch()
