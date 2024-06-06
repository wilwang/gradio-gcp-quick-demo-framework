import os
import requests
from dotenv import load_dotenv

class ProjectConfig:
    load_dotenv()

    def get_project_id():
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
    load_dotenv()

    def upload_bucket():
        value = os.environ.get("SUMMARY_UPLOAD_BUCKET", "ww-genai-demo-upload-bucket")
        return value
        
    def output_bucket():
        value = os.environ.get("SUMMARY_OUTPUT_BUCKET", "ww-genai-demo-output-bucket")
        return value

    def location():
        value = os.environ.get("SUMMARY_LOCATION", "us")
        return value

    def processor_id():
        value = os.environ.get("SUMMARY_PROCESSOR_ID", "283ec8851725fcbe")
        return value
    
    def mime_type():
        value = os.environ.get("SUMMARY_MIME_TYPE", "application/pdf")
        return value
    
    def field_mask():
        value = os.environ.get("SUMMARY_FIELD_MASK", "text,entities,pages.pageNumber")
        return value

class ContractParserConfig:
    load_dotenv()

    def upload_bucket():
        value = os.environ.get("CONTRACT_UPLOAD_BUCKET", "ww-genai-demo-upload-bucket")
        return value
        
    def output_bucket():
        value = os.environ.get("CONTRACT_OUTPUT_BUCKET", "ww-genai-demo-output-bucket")
        return value

    def location():
        value = os.environ.get("CONTRACT_LOCATION", "us")
        return value

    def processor_id():
        value = os.environ.get("CONTRACT_PROCESSOR_ID", "283ec8851725fcbe")
        return value
    
    def mime_type():
        value = os.environ.get("CONTRACT_MIME_TYPE", "application/pdf")
        return value
    
    def field_mask():
        value = os.environ.get("CONTRACT_FIELD_MASK", "text,entities,pages.pageNumber")
        return value

    
class GeminiConfig:
    load_dotenv()

    def model():
        value = os.environ.get("model", "gemini-1.5-pro-preview-0409")
        return value
    
    def temperature():
        value = os.environ.get("temperature", 1)
        return value
    
    def top_k():
        value = os.environ.get("top_k", 5)
        return value
    
    def top_p():
        value = os.environ.get("top_p", 1)
        return value    
