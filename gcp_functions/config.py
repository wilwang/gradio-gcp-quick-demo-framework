import os
import requests
from dotenv import load_dotenv

class ProjectConfig:
    """
    Config class for project settings
    """
    # attempt to load any local .env
    load_dotenv()

    def get_logo():
        """
        To use a custom logo, set the DEMO_LOGO env variable and 
        save the file in the images directory
        """
        value = os.environ.get("DEMO_LOGO", "GoogleCloud_logo.png")
        return value

    def get_project_id():
        """
        If the PROJECT_ID is not set, will try to use the metadata
        server to get the current PROJECT_ID
        """
        value = os.environ.get("PROJECT_ID")

        if value is None:
            metadata_url = "http://metadata.google.internal/computeMetadata/v1/project/project-id"
            headers = {"Metadata-Flavor": "Google"}
            response = requests.get(metadata_url, headers=headers)

            if response.status_code != 200:
                print("Failed to get project ID:", response.status_code)
                raise ValueError(f"Failed to get project id from metadata server: {response.status_code}")
            
            project_id = response.text
            print("Current project ID:", project_id)

            value = project_id
        
        return value

class SummaryParserConfig:
    """
    Config class for the Summary Parser settings
    """
    # attempt to load any local .env
    load_dotenv()

    # gcs bucket where to upload the file to be summarized
    def upload_bucket():
        value = os.environ.get("SUMMARY_UPLOAD_BUCKET", "ww-genai-demo-upload-bucket")
        return value
    
    # gcs bucket for where the parser output will go
    def output_bucket():
        value = os.environ.get("SUMMARY_OUTPUT_BUCKET", "ww-genai-demo-output-bucket")
        return value

    # location of the processor (us, global, etc)
    def location():
        value = os.environ.get("SUMMARY_LOCATION", "us")
        return value

    # processor id of the parser
    def processor_id():
        value = os.environ.get("SUMMARY_PROCESSOR_ID", "283ec8851725fcbe")
        return value
    
    # mime type of input file (https://cloud.google.com/document-ai/docs/file-types)
    def mime_type():
        value = os.environ.get("SUMMARY_MIME_TYPE", "application/pdf")
        return value
    
    # field mask to define list of fields that a request shoudl return
    # https://developers.google.com/docs/api/how-tos/field-masks
    # https://cloud.google.com/ruby/docs/reference/google-cloud-document_ai-v1/latest/Google-Protobuf-FieldMask
    def field_mask():
        value = os.environ.get("SUMMARY_FIELD_MASK", "text,entities,pages.pageNumber")
        return value

class ContractParserConfig:
    """
    Config class for the Contract Parser settings
    """
    # attempt to load local .env
    load_dotenv()

    # gcs bucket where to upload the file to be summarized
    def upload_bucket():
        value = os.environ.get("CONTRACT_UPLOAD_BUCKET", "ww-genai-demo-upload-bucket")
        return value
        
    # gcs bucket for where the parser output will go
    def output_bucket():
        value = os.environ.get("CONTRACT_OUTPUT_BUCKET", "ww-genai-demo-output-bucket")
        return value

    # location of the processor (us, global, etc)
    def location():
        value = os.environ.get("CONTRACT_LOCATION", "us")
        return value

    # processor id of the parser
    def processor_id():
        value = os.environ.get("CONTRACT_PROCESSOR_ID", "283ec8851725fcbe")
        return value
    
    # mime type of input file (https://cloud.google.com/document-ai/docs/file-types)
    def mime_type():
        value = os.environ.get("CONTRACT_MIME_TYPE", "application/pdf")
        return value
    
    # field mask to define list of fields that a request shoudl return
    # https://developers.google.com/docs/api/how-tos/field-masks
    # https://cloud.google.com/ruby/docs/reference/google-cloud-document_ai-v1/latest/Google-Protobuf-FieldMask
    def field_mask():
        value = os.environ.get("CONTRACT_FIELD_MASK", "text,entities,pages.pageNumber")
        return value

class GeminiConfig:
    """
    Config class for Gemini model
    """
    # attempt to load local .env
    load_dotenv()

    # set the model to use for the LLM (gemini-1.5-flash-001, gemini-1.5-pro-001, etc)
    def model():
        value = os.environ.get("model", "gemini-1.5-flash-001") 
        return value
    
    # temperature of the model (0-1 or 0-2 depending on model)
    def temperature():
        value = float(os.environ.get("temperature", "1"))
        return value
    
    # define top K for the model
    def top_k():
        value = int(os.environ.get("top_k", "5"))
        return value
    
    # defint top P for the model
    def top_p():
        value = float(os.environ.get("top_p", "1"))
        return value    

class DiscoveryEngineConfig:
    """
    Config class for the Discovery Engine API
    """
    # attempt to load local .env
    load_dotenv()

    # engine id of the search engine
    def engine_id():
        value = os.environ.get("DISCOVERY_ENGINE_ID", "")
        return value

    # location of the search engine (us, global, etc)
    def location():
        value = os.environ.get("DISCOVERY_ENGINE_LOCATION", "")
        return value


class AudioConfig:
    load_dotenv()

    def upload_bucket():
        value = os.environ.get("AUDIO_UPLOAD_BUCKET", "")
        return value
