import gradio as gr
import pandas

import gcp_functions.storage as StorageHelper
import gcp_functions.stateBag as sb
from gcp_functions.docai import process_document
from gcp_functions.config import SummaryParserConfig, ContractParserConfig, ProjectConfig, DiscoveryEngineConfig
from gcp_functions.gemini import gemini_docqa_response
from gcp_functions.discoveryengine import search

from components.contract_parser import contract_component
from components.qa_chatbot import qa_component
from components.search import search_component
from components.summarizer import summary_component

from google.oauth2.service_account import Credentials
import json
from urllib.parse import urlparse

# only needed for edge case: contract parser in another GCP project
from dotenv import load_dotenv
import os

def handle_summary_upload(file_url: str, state: gr.State):
    """
    Handler function for uploading a file for doc summarization

    Will take a local file and upload to a Cloud Storage bucket and then
    use DocAI processor to make a batch request (to handle larger files)
    and then parse out the Summary and OCR Text from the json results

    Args:
        file_url (str): local file location to be uploaded
        state (gradio.State): session state object of type gcp_functions.stateBag

    Returns: 
        gcs_uri (str): cloud storage bucket URI of the input file
        summary (str): summary from parser result
        state (gradio.State): updated session state
    """
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
    state.ocr_text = text
    
    # returns the result location, the summary portion, and the session state
    return gcs_input_uri, summary, state
    

def handle_contract_upload(file_url: str, state: gr.State):
    """
    Handler function for uploading a file for doc contract parser

    Will take a local file and upload to a Cloud Storage bucket and then
    use DocAI processor to make a batch request (to handle larger files)
    and then parse out the Entities and OCR Text from the json results

    NOTE: this parser is in another GCP project so it uses service account
    to access the parser as well as to access GCS buckets

    Args:
        file_url (str): local file location to be uploaded
        state (gradio.State): session state object of type gcp_functions.stateBag

    Returns: 
        gcs_uri (str): cloud storage bucket URI of the input file
        df_entities (Dataframe): dataframe of the parsed out contract entities
        state (gradio.State): updated session state
    """
    # load environment vars; only necessary for cross project access
    load_dotenv()

    upload_bucket = ContractParserConfig.upload_bucket()

    # create credentials from service account because 
    # Contract Parser is in another project in another tenant
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
    
    # assumes result json is from a DocAI Contract parser
    output_gcs_destination = metadata.individual_process_statuses[0].output_gcs_destination
    json_uri, entities, text = StorageHelper.extract_from_contract_output(output_gcs_destination, credentials)
    
    # convert to dataframe
    df_entities = pandas.DataFrame(entities)

    # store the full ocr text from the document in session state
    state.ocr_text = text
    
    # returns the result location, the extracted entities, and updated session state
    return gcs_input_uri, df_entities, state     
    

def handle_qa_submit(message: str, history: str, state: gr.State):
    """
    Handler function for handling a response to a user input in the chatbot

    Args:
        message (str): the submitted message by the user
        history (str): retained history of the entire chat conversation. Not currently used
        state (gradio.State): session state object of type gcp_function.stateBag

    Returns: 
        message in user input box
        history of entire chat conversation
    
    """
    resp = ""
    
    # if active tab is on "Enterprise KB", use search function
    if (state.active_tab == "kb"):
        project_id = state.project_id
        engine_id = state.engine_id

        # set the preamble context for the search engine
        context = """You are a search engine answering questions for a user. 
        Return pertinent snippets from the source documents where you answer from."""

        resp, raw = search(project_id, engine_id, context, message)
    # otherwise use the gemini docqa response function
    else:
        ocr_text = state.ocr_text
        resp = gemini_docqa_response(message, history, ocr_text)
        
    # capture chat history
    history.append((message, resp))

    return "", history


def main():
    """
    Main UI layout. Set share=True to get a hosted version of the app

    Add "/?__theme=light" at the end of the query string for light mode; it defaults to dark 
    """
    # UI Layout
    with gr.Blocks() as demo:
        bag = sb.StateBag(active_tab="summary", 
                        ocr_text="none", 
                        engine_id=DiscoveryEngineConfig.engine_id(), 
                        project_id=ProjectConfig.get_project_id())

        # create the session state to be used within this Block()
        state = gr.State(bag)

        # logo on top of the page
        with gr.Row():
            logo = ProjectConfig.get_logo()
            gr.HTML(f"""<div><img src="file/images/{logo}" /></div>""")
        with gr.Row():
            with gr.Column():
                # the summary UI
                summary_component(handle_summary_upload, state)
                # the contract UI
                contract_component(handle_contract_upload, state)
                # the KB UI
                search_component(bag.engine_id, state)
            with gr.Column():
                # the QA chatbot
                qa_component(handle_qa_submit, state)
        
        # NOTE: Uncomment if you need to keep an eye on the session state
        '''
        def handle(state: gr.State):
            return f"""
            active_tab: {state.active_tab}
            ocr_text: {state.ocr_text}
            engine_id: {state.engine_id}
            """
        msg = gr.Textbox()
        btn = gr.Button("Click me!")
        btn.click(handle, [state], [msg])
        '''

    demo.launch(share=False, debug=True, allowed_paths=["images"])



# run the main routine
main()
