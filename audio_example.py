import gradio as gr
import pandas
import gcp_functions.stateBag as sb
import gcp_functions.storage as StorageHelper
from gcp_functions.config import ProjectConfig, AudioConfig
from gcp_functions.gemini import gemini_audio_response


def handle_audio_finish(audio_filepath: str, state: gr.State):
    upload_bucket = AudioConfig.upload_bucket()
    f, gcs = StorageHelper.file_upload(audio_filepath, upload_bucket)
    
    audio_file_uri = gcs

    prompt = """The audio is in Spanish. Provide a translation of the audio into English.
    You are a native Spanish speaker. Evaluate and provide feedback in English on the grammar and pronunciation. 
    Ignore pronunciation of names."""
    
    response = gemini_audio_response(audio_file_uri, prompt)

    return response



from typing import Callable
def audio_input(handle_func: Callable, state: gr.State):
    input_audio = gr.Audio(
        sources=["microphone"],
        type="filepath"
    )
    text = gr.Text()
    input_audio.stop_recording(handle_func, [input_audio, state], text)


def main():
    """
    Main UI layout. Set share=True to get a hosted version of the app

    Add "/?__theme=light" at the end of the query string for light mode; it defaults to dark 
    """
    # UI Layout
    with gr.Blocks() as demo:
        bag = sb.StateBag(project_id=ProjectConfig.get_project_id())

        # create the session state to be used within this Block()
        state = gr.State(bag)

        # logo on top of the page
        with gr.Row():
            logo = ProjectConfig.get_logo()
            gr.HTML(f"""<div><img src="file/images/{logo}" /></div>""")
        with gr.Row():
            audio_input(handle_audio_finish, state)

    demo.launch(share=False, debug=True, allowed_paths=["images"])



# run the main routine
main()