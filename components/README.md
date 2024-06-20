# "GCP" Components
These components are just layouts of Gradio components that were created to demo specific GCP services.

* [Summarizer](#summarizer)
* [Contract Parser](#contract-parser)
* [Search](#search)
* [QA Chatbot](#qa-chatbot)

## Summarizer
This component contains a simple [`Gradio.Textbox`](https://www.gradio.app/docs/gradio/textbox) to display the Cloud Storage URI of the file to be uploaded for summarization; a [`Gradio.UploadButton`](https://www.gradio.app/docs/gradio/uploadbutton) to handle file uploads; and a larger `Gradio.Textbox` to display the summary of the uploaded file. 

The component is encapsulated in a [`Gradio.Tab`](https://www.gradio.app/docs/gradio/tab) to allow for easy navigation between other "tabbed" components. 

To use the component, pass in a handler function that will handle the [Upload event](https://www.gradio.app/docs/gradio/tab) of the [`Gradio.UploadButton`](https://www.gradio.app/docs/gradio/uploadbutton).

### Summarizer Handler Func
The handler function you write will need to follow a strict convention. 
- 2 input parameters
  - Local url of the uploaded file
  - Gradio.State object
- list output parameter with 3 outputs
  - Google Cloud Storage URI of the file (to be displayed in textbox)
  - Summary output of the DocAI Summarizer Parser result
  - Gradio.State object

Example:
```python
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
    state.ocr_text = text
    
    # returns the result location, the summary portion, and the session state
    return gcs_input_uri, summary, state
```

## Contract Parser
This component contains a simple [`Gradio.Textbox`](https://www.gradio.app/docs/gradio/textbox) to display the Cloud Storage URI of the file to be uploaded for parsing; a [`Gradio.UploadButton`](https://www.gradio.app/docs/gradio/uploadbutton) to handle file uploads; and a [`Gradio.DataFrame`](https://www.gradio.app/docs/gradio/dataframe) to display a table of extracted entities from the uploaded file. 

The component is encapsulated in a [`Gradio.Tab`](https://www.gradio.app/docs/gradio/tab) to allow for easy navigation between other "tabbed" components. 

To use the component, pass in a handler function that will handle the [Upload event](https://www.gradio.app/docs/gradio/tab) of the [`Gradio.UploadButton`](https://www.gradio.app/docs/gradio/uploadbutton).

### Contract Parser Handler Func
The handler function you write will need to follow a strict convention. 
- 2 input parameters
  - Local url of the uploaded file
  - Gradio.State object
- list output parameter with 3 outputs
  - Google Cloud Storage URI of the file (to be displayed in textbox)
  - Dataframe containing [type, mentionText] of Contract Parser result
  - Gradio.State object

Example:
```python
def handle_contract_upload(file_url: str, state: gr.State):
    upload_bucket = ContractParserConfig.upload_bucket()
    
    # upload the file from the local dir to the cloud bucket
    f, gcs = StorageHelper.file_upload(file_url, upload_bucket)
    
    project_id = ProjectConfig.get_project_id()
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
        gcs_output_uri=gcs_output_uri
    )
    
    # assumes result json is from a DocAI Contract parser
    output_gcs_destination = metadata.individual_process_statuses[0].output_gcs_destination
    json_uri, entities, text = StorageHelper.extract_from_contract_output(output_gcs_destination)
    
    # convert to dataframe
    df_entities = pandas.DataFrame(entities)

    # store the full ocr text from the document in session state
    state.ocr_text = text
    
    # returns the result location, the extracted entities, and updated session state
    return gcs_input_uri, df_entities, state     
```

## Search
This component contains a simple [`Gradio.Textbox`](https://www.gradio.app/docs/gradio/textbox) to display and set the Engine Id for [Vertex AI Search](https://cloud.google.com/enterprise-search). You can change the Engine Id by just editing it in the textbox. 

The component is encapsulated in a [`Gradio.Tab`](https://www.gradio.app/docs/gradio/tab) to allow for easy navigation between other "tabbed" components. 

This component works in conjunction with the QA Component that supplies the interaction capability with the search engine.

## QA Chatbot
This component contains a [`Gradio.Chatbot`](https://www.gradio.app/docs/gradio/chatbot) and a `Gradio.Textbox` for inputs.

### QA Chatbot Handler Func
The handler function you write will need to follow a strict convention. 
- 3 input parameters
  - Message to submit 
  - History of the entire chat
  - Gradio.State object
- list output parameter with 2 outputs
  - Blank text to reset the input textbox
  - Chat history to display conversation in the chatbot

Example:
```python
def handle_qa_submit(message, history, state):
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
```

