import gradio as gr
import pandas

import gcp_functions.storage as StorageHelper
from gcp_functions.docai import process_document
from gcp_functions.config import SummaryParserConfig, ContractParserConfig, ProjectConfig, DiscoveryEngineConfig
from gcp_functions.gemini import gemini_docqa_response
from gcp_functions.discoveryengine import search
from typing import Callable

from google.oauth2.service_account import Credentials
import json
from urllib.parse import urlparse

# only needed for edge case: contract parser in another GCP project
from dotenv import load_dotenv
import os

'''####################################################################
Handler function for uploading a file for doc summarization

Will take a local file and upload to a Cloud Storage bucket and then
use DocAI processor to make a batch request (to handle larger files)
and then parse out the Summary and OCR Text from the json results

NOTE: While the processing function can use any DocAI parser, the 
code assumes the json result to be from the Summarizer parser
####################################################################'''
def handle_summary_upload(file_url: str):
    upload_bucket = SummaryParserConfig.upload_bucket()
    
    # upload the file from the local dir to the cloud bucket
    f, gcs = StorageHelper.file_upload(file_url, upload_bucket)
    
    project_id = ProjectConfig.get_project_id()
    location = SummaryParserConfig.location()
    processor_id = SummaryParserConfig.processor_id()
    mime_type = SummaryParserConfig.mime_type()
    field_mask = SummaryParserConfig.field_mask()
    gcs_input_uri = gcs
    gcs_output_uri = f"gs://{SummaryParserConfig.output_bucket()}"

    # make a request for processing the uploaded file
    metadata = process_document(
        project_id=project_id, 
        location=location, 
        processor_id=processor_id, 
        mime_type=mime_type, 
        field_mask=field_mask, 
        gcs_input_uri=gcs_input_uri, 
        gcs_output_uri=gcs_output_uri
    )

    # assumes result json is from a DocAI Workbench Summarizer parser
    output_gcs_destination = metadata.individual_process_statuses[0].output_gcs_destination
    json_uri, summary, text = StorageHelper.extract_from_summary_output(output_gcs_destination)
    
    # returns the result location, the summary portion, and the OCR text
    return f, summary, text
    
'''####################################################################
Document Summarizer UI component

####################################################################'''
def summary_component(full_text: gr.components.textbox.Textbox, 
                      handle_func: Callable,
                      state: gr.State):
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
            
        upload_btn.upload(
            handle_func,
            [upload_btn],
            [file, summary, full_text])


    def set_active_tab(state: gr.State):
        state["active_tab"] = "summary"
        return state

    tab.select(set_active_tab, [state], [state])


'''####################################################################
Handler function for uploading a file for doc contract parser

Will take a local file and upload to a Cloud Storage bucket and then
use DocAI processor to make a batch request (to handle larger files)
and then parse out the Entities and OCR Text from the json results

NOTE: While the processing function can use any DocAI parser, the 
code assumes the json result to be from the Contract parser
####################################################################'''
def handle_contract_upload(file_url: str):
    load_dotenv()

    upload_bucket = ContractParserConfig.upload_bucket()

    # use service account because Contract Parser is in another project in another tenant
    service_account_info = json.load(open(os.environ.get('CONTRACT_PROJECT_SA_KEY'))) 
    credentials = Credentials.from_service_account_info(service_account_info)    
    
    # upload the file from the local dir to the cloud bucket
    f, gcs = StorageHelper.file_upload(file_url, upload_bucket, credentials)
    
    project_id = os.environ.get('CONTRACT_PROJECT_ID')
    location = ContractParserConfig.location()
    processor_id = ContractParserConfig.processor_id()
    mime_type = ContractParserConfig.mime_type()
    field_mask = ContractParserConfig.field_mask()
    gcs_input_uri = gcs
    gcs_output_uri = f"gs://{ContractParserConfig.output_bucket()}"    

    # make a request for processing the uploaded file
    metadata = process_document(
        project_id=project_id, 
        location=location, 
        processor_id=processor_id, 
        mime_type=mime_type, 
        field_mask=field_mask, 
        gcs_input_uri=gcs_input_uri, 
        gcs_output_uri=gcs_output_uri,
        credentials=credentials
    )
    
    # assumes result json is from a DocAI Workbench Contract parser
    output_gcs_destination = metadata.individual_process_statuses[0].output_gcs_destination
    json_uri, entities, text = StorageHelper.extract_from_contract_output(output_gcs_destination, credentials)
    
    df_entities = pandas.DataFrame(entities)
    
    # returns the result location, the extracted entities, and the OCR text
    return f, df_entities, text

'''####################################################################
Document Contract Parser UI component

####################################################################'''
def contract_component(full_text: gr.components.textbox.Textbox, 
                      handle_func: Callable,
                      state: gr.State):
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
        
        upload_btn.upload(
            handle_func,
            [upload_btn],
            [file, entities, full_text])


    def set_active_tab(state: gr.State):
        state["active_tab"] = "contract"
        return state

    tab.select(set_active_tab, [state], [state])

'''####################################################################
Enterprise Search UI component

####################################################################'''
def search_component(full_text: gr.components.textbox.Textbox, 
                    state: gr.State):
    with gr.Tab("Enterprise KB") as tab:
        with gr.Row():
            datasource_url = gr.Textbox(lines=1,
                                        label="Data Source URL", 
                                        value=DiscoveryEngineConfig.engine_id())

        def handle_search(engine_id: str):
            print (engine_id)
            return engine_id

        datasource_url.change(handle_search, [datasource_url], [full_text])

    def set_active_tab(datasource_url: gr.Textbox,
                        state: gr.State):
        state["active_tab"] = "kb"
        print(datasource_url)
        return datasource_url, state

    tab.select(set_active_tab, [datasource_url, state], [full_text, state])            


'''####################################################################
QA Chat UI component

NOTE: the 'full_text' component should be HIDDEN in the main UI and 
is used as a way to cache and keep the document available for prompt
context
####################################################################'''   
def qa_component(full_text_component: gr.components.textbox.Textbox,
                state: gr.State):
    with gr.Row():
        chatbot = gr.Chatbot(height=700)
        
    with gr.Row():
        msg = gr.Textbox()

    def respond(message, history, full_text, state):
        resp = ""
        active_tab = state["active_tab"]
        if (active_tab == "kb"):
            project_id = ProjectConfig.get_project_id()
            context = """You are a search engine answering questions for a user. 
            Return pertinent snippets from the source documents where you answer from."""
            resp, raw = search(project_id, full_text, context, message)
        else:
            resp = gemini_docqa_response(message, history, full_text)
            
        history.append((message, resp))

        return "", history

    msg.submit(respond, [msg, chatbot, full_text_component, state], [msg, chatbot])    

'''####################################################################
Main UI
 -- Add "/?__theme=light" for light mode; it default to dark 
####################################################################'''
def main():   
    with gr.Blocks() as demo:
        state = gr.State({
            "active_tab": "summary",
            "ocr_text": "none",
            "engine_id": "none"            
            })

        with gr.Row():
            gr.HTML("""
            <div>
                <img src="file/images/GoogleCloud_logo.png" />
            </div>
            """)
        with gr.Row():
            # using this as a way to cache the full text from the document to use
            # for context in the prompt for the QA chatbot
            # TODO: change this to use gr.State()
            full_text = gr.Textbox(lines=20, label="Full Text", visible=True)
        with gr.Row():
            with gr.Column():
                # the summary UI
                summary_component(full_text, handle_summary_upload, state)
                
                # the contract UI
                contract_component(full_text, handle_contract_upload, state)

                # the KB UI
                search_component(full_text, state)
            with gr.Column():
                # the QA chatbot
                qa_component(full_text, state)


        
        # Test code to verify that "set active tab" is working

        def handle(state: gr.State):
            return f"""
            active_tab: {state["active_tab"]}
            ocr_text: {state["ocr_text"]}
            engine_id: {state["engine_id"]}
            """
        msg = gr.Textbox()
        btn = gr.Button("Click me!")
        btn.click(handle, [state], [msg])
        

    demo.launch(share=False, debug=True, allowed_paths=["images"])

main()
