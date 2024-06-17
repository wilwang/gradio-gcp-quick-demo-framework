import gradio as gr
from typing import Callable

def contract_component(handle_func: Callable, state: gr.State):
    """
    Document Contract Parser UI component

    Args:
        handle_func (Callable): function to handle the file upload event
        state (gradio.State): session state object of type gcp_functions.StateBag

    Returns:
        Nothing
    """
    # UI Layout
    with gr.Tab("Contracts") as tab:
        with gr.Row():
            file = gr.Textbox(lines=1, label="Upload Contract")
        with gr.Row():
            upload_btn = gr.UploadButton(
                "Click to upload",
                file_types=[".pdf"],
                file_count="single")
        with gr.Row():
            entities = gr.DataFrame(headers=['type', 'mentionText'], 
                                    column_widths=['200px'],
                                    label="Entities", 
                                    wrap=True)

    # set up the event handler for "upload"
    upload_btn.upload(handle_func,[upload_btn, state],[file, entities, state])

    # local function to handle when the summary tab is selected
    def set_active_tab(state: gr.State):
        state.active_tab = "contract"
        return state

    # set up event handler for tab "select"
    tab.select(set_active_tab, [state], [state])