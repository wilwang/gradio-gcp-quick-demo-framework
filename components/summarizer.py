import gradio as gr
from typing import Callable

def summary_component(handle_func: Callable, state: gr.State):
    """
    Document Summarizer UI component

    Args:
        handle_func (Callable): function to handle the file upload event
        state (gradio.State): session state object of type gcp_functions.StateBag

    Returns:
        Nothing
    """
    # Layout of component
    with gr.Tab("Summarize") as tab:
        with gr.Row():
            file = gr.Textbox(lines=1, label="Upload File")
        with gr.Row():
            upload_btn = gr.UploadButton(
                "Click to upload",
                file_types=[".pdf"],
                file_count="single")
        with gr.Row():
            summary = gr.Textbox(lines=20, label="Summary")

    # set up the event handler for "upload"
    upload_btn.upload(handle_func, [upload_btn, state], [file, summary, state])

    # local function to handle when the summary tab is selected
    def set_active_tab(state: gr.State):
        state.active_tab = "summary"
        return state

    # set up event handler for tab "select"
    tab.select(set_active_tab, [state], [state])