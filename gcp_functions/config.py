import os
import requests

def get_project_id():
    metadata_url = "http://metadata.google.internal/computeMetadata/v1/project/project-id"
    headers = {"Metadata-Flavor": "Google"}
    response = requests.get(metadata_url, headers=headers)

    if response.status_code != 200:
        print("Failed to get project ID:", response.status_code)
        raise ValueError(f"Failed to get project id from metadata server: {response.status_code}")
    
    project_id = response.text
    print("Current project ID:", project_id)

    return project_id

class SummaryParserConfig:
    def upload_bucket():
        value = os.environ.get("UPLOAD_BUCKET", "ww-genai-demo-upload-bucket")
        return value
        
    def output_bucket():
        value = os.environ.get("OUTPUT_BUCKET", "ww-genai-demo-output-bucket")
        return value

    def location():
        value = os.environ.get("LOCATION", "us")
        return value

    def processor_id():
        value = os.environ.get("PROCESSOR_ID", "283ec8851725fcbe")
        return value
    
    def mime_type():
        value = os.environ.get("MIME_TYPE", "application/pdf")
        return value
    
    def field_mask():
        value = os.environ.get("FIELD_MASK", "text,entities,pages.pageNumber")
        return value

class ContractParserConfig:
    def upload_bucket():
        value = os.environ.get("UPLOAD_BUCKET", "ww-genai-demo-upload-bucket")
        return value
        
    def output_bucket():
        value = os.environ.get("OUTPUT_BUCKET", "ww-genai-demo-output-bucket")
        return value

    def location():
        value = os.environ.get("LOCATION", "us")
        return value

    def processor_id():
        value = os.environ.get("PROCESSOR_ID", "283ec8851725fcbe")
        return value
    
    def mime_type():
        value = os.environ.get("MIME_TYPE", "application/pdf")
        return value
    
    def field_mask():
        value = os.environ.get("FIELD_MASK", "text,entities,pages.pageNumber")
        return value

    
class GeminiConfig:
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
