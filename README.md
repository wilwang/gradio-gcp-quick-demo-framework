# Gradio GCP Quick Demo Framework
The purpose of this respository is to make creating GenAI focused demos on GCP quicker and easier. 
Common components can be found under the **components** directory. 
Re-usable helper functions are available in the **gcp_functions** directory.
The framework provides an opinionated way of using these common components and helper functions to quickly create your own demos.

## How to use the framework
### Configuration
For local development, create a `.env` file to store your environment variables to be used.

Example:
```
PROJECT_ID="ww-genai-demo"
SUMMARY_UPLOAD_BUCKET="my-upload-bucket"
SUMMARY_OUTPUT_BUCKET="my-output-bucket"
SUMMARY_LOCATION="us"
SUMMARY_PROCESSOR_ID="summary_processor_id"
SUMMARY_MIME_TYPE="application/pdf"
SUMMARY_FIELD_MASK="text,entities,pages.pageNumber"
CONTRACT_UPLOAD_BUCKET="my-contract-upload-bucket"
CONTRACT_OUTPUT_BUCKET="my-contract-output-bucket"
CONTRACT_LOCATION="us"
CONTRACT_PROCESSOR_ID="contract_processor_id"
CONTRACT_MIME_TYPE="application/pdf"
CONTRACT_FIELD_MASK="text,entities,pages.pageNumber"
model="gemini-1.5-pro-preview-0409"
temperature=1
top_k=5
top_p=1

DISCOVERY_ENGINE_ID="my-search-engine-id"
DISCOVERY_ENGINE_LOCATION="global"

DEMO_LOGO="demo-logo.png"
```

### "GCP" Components
The framework assumes some basic familiarity with Gradio. You should define your layout using [`Gradio.Blocks`](https://www.gradio.app/docs/gradio/blocks) and implement a [`Gradio.State`](https://www.gradio.app/guides/state-in-blocks) object to capture session state data. Most of the components will pass the state object as a way to pass data between components.

The components under **components** are just a layout of Gradio standard components. You just need to supply event handler code for the "GCP" component.

For more info on "GCP" components, go [here](./components/README.md).

Example:
```python
import gcp_functions.stateBag as sb

def handle_summary_upload(file_url: str, state: Gradio.State):
    print(file_url)

    return file_url, "", state

def main():
    # UI Layout
    with gr.Blocks() as demo:
        bag = sb.StateBag()

        # create the session state to be used within this Block()
        state = gr.State(bag)

        summary_component(handle_summary_upload, state)
        
    demo.launch(share=False, debug=True)
```
### Common Functions
There are also re-usable helper functions that can be found under the **gcp_functions** directory. These functions encapsulate logic for commmon GCP tasks on Cloud Storage Buckets, Document AI parsing, and DiscoveryEngine API calls; it also contains some common objects like Configuration classes and the StateBag object.

## Before you begin
### [Recommended] use Python virtual env
Create the virtual env to isolate dependencies and modules
```
> python -m venv venv
```

Activate the virtual env when developing
```
> source venv/bin/activate
```

Deactivate the virutal env when done
```
> deactivate
```

### Install dependencies
```
> pip install -r requirements.txt
```

### Main function (UI)
The main function is where you define the layout of the your app. To use a specific logo, save the image in the 'images' directory and update your `DEMO_LOGO` environment variable to the name of the image.

To use light theme, add `?__theme=light` to the end of the url.

Example:
```python
def main():
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
        
    demo.launch(share=False, debug=True, allowed_paths=["images"])
```