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
def handle_summary_upload(file_url: str, state: gr.State):
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

    # set the current full ocr text in session state; we use this for 
    # QnA prompting to provide context for the prompts
    state["ocr_text"] = text
    
    # returns the result location, the summary portion, and the session state
    return gcs_input_uri, summary, state
    
'''####################################################################
Document Summarizer UI component

####################################################################'''
def summary_component(handle_func: Callable, state: gr.State):
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
            [upload_btn, state],
            [file, summary, state])


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
def handle_contract_upload(file_url: str, state: gr.State):
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

    state["ocr_text"] = text
    
    # returns the result location, the extracted entities, and the OCR text
    return gcs_input_uri, df_entities, state

'''####################################################################
Document Contract Parser UI component

####################################################################'''
def contract_component(handle_func: Callable, state: gr.State):
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
            [upload_btn, state],
            [file, entities, state])


    def set_active_tab(state: gr.State):
        state["active_tab"] = "contract"
        return state

    tab.select(set_active_tab, [state], [state])

'''####################################################################
Enterprise Search UI component

####################################################################'''
def search_component(state: gr.State):
    engine_id = DiscoveryEngineConfig.engine_id()

    with gr.Tab("Enterprise KB") as tab:
        with gr.Row():
            search_engine = gr.Textbox(lines=1,
                                        label="Search Engine Id", 
                                        value=engine_id)

        def handle_search_engine_change(engine_id: str, state: gr.State):
            print (engine_id)
            state["engine_id"] = engine_id
            return state

        search_engine.change(handle_search_engine_change, [search_engine, state], [state])

    def set_active_tab(engine_id: str, state: gr.State):
        state["active_tab"] = "kb"
        state["engine_id"] = engine_id
        print(engine_id)
        return state

    tab.select(set_active_tab, [search_engine, state], [state])            


'''####################################################################
QA Chat UI component

NOTE: the 'full_text' component should be HIDDEN in the main UI and 
is used as a way to cache and keep the document available for prompt
context
####################################################################'''   
def qa_component(state: gr.State):
    with gr.Row():
        chatbot = gr.Chatbot(height=700)
        
    with gr.Row():
        msg = gr.Textbox()

    def respond(message, history, state):
        resp = ""
        active_tab = state["active_tab"]
        
        if (active_tab == "kb"):
            project_id = ProjectConfig.get_project_id()
            engine_id = state["engine_id"]
            context = """You are a search engine answering questions for a user. 
            Return pertinent snippets from the source documents where you answer from."""
            resp, raw = search(project_id, engine_id, context, message)
        else:
            ocr_text = state["ocr_text"]
            resp = gemini_docqa_response(message, history, ocr_text)
            
        history.append((message, resp))

        return "", history

    msg.submit(respond, [msg, chatbot, state], [msg, chatbot])    

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
            with gr.Column():
                # the summary UI
                summary_component(handle_summary_upload, state)
                
                # the contract UI
                contract_component(handle_contract_upload, state)

                # the KB UI
                search_component(state)
            with gr.Column():
                # the QA chatbot
                qa_component(state)


        
        # NOTE: Uncomment if you need to keep an eye on the session state
        '''
        def handle(state: gr.State):
            return f"""
            active_tab: {state["active_tab"]}
            ocr_text: {state["ocr_text"]}
            engine_id: {state["engine_id"]}
            """
        msg = gr.Textbox()
        btn = gr.Button("Click me!")
        btn.click(handle, [state], [msg])
        '''

    demo.launch(share=False, debug=True, allowed_paths=["images"])

main()
