import gradio as gr

def search_component(init_engine_id: str, state: gr.State):
    """
    Vertex Search UI component

    Args:
        state (gradio.State): session state object of type gcp_functions.StateBag

    Returns:
        Nothing
    """
    # UI Layout
    with gr.Tab("Enterprise KB") as tab:
        with gr.Row():
            search_engine = gr.Textbox(lines=1, label="Search Engine Id", value=init_engine_id)

    # local function to handle search engine id change to update session state
    def handle_search_engine_change(engine_id: str, state: gr.State):
        state.engine_id = engine_id
        return state

    # set up event handler for search engine textbox change
    search_engine.change(handle_search_engine_change, [search_engine, state], [state])

    # local function to handle tab "select" event to update session state and engine id
    def set_active_tab(engine_id: str, state: gr.State):
        state.active_tab = "kb"
        state.engine_id = engine_id
        return state

    # set up event handler for tab select
    tab.select(set_active_tab, [search_engine, state], [state])          