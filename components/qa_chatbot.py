import gradio as gr
from typing import Callable

def qa_component(handle_func: Callable, state: gr.State):
    """
    Q&A chat UI component

    Args:
        state (gradio.State): session state object

    Returns:
        Nothing
    """
    # UI Layout
    with gr.Row():
        chatbot = gr.Chatbot(height=650)
    with gr.Row():
        msg = gr.Textbox()

    # set up the event handler for submit on the chat input textbox
    msg.submit(handle_func, [msg, chatbot, state], [msg, chatbot])    