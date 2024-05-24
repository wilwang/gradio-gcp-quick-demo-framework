import os
import json
from urllib.parse import urlparse
from google.cloud import storage
from typing import Optional
from google.oauth2.service_account import Credentials

######################################################################
# Upload a local file from gr.File() to a designated Cloud Storage bucket
######################################################################
def file_upload(file_url: str, 
                upload_bucket: str,
                credentials: Optional[Credentials] = None):
    
    print(f'Uploading {file_url} to {upload_bucket}')

    if (credentials != None):
        client = storage.Client(credentials=credentials)
    else:
        client = storage.Client()
        
    filename = os.path.basename(file_url)
    bucket = client.get_bucket(upload_bucket)
    blob = bucket.blob(filename)
    blob.upload_from_filename(file_url)

    gcs_upload_uri = f"gs://{upload_bucket}/{filename}"

    print(f"Uploaded to {gcs_upload_uri}")    
    
    return file_url, gcs_upload_uri

######################################################################
# Extract the blob uri, summary, and full extracted text of the 
# summarized result from docAI workbench summarizer
######################################################################
def extract_from_summary_output(gcs_url: str, 
                                credentials: Optional[Credentials] = None):

    print(f'Extract docai summary parser output from {gcs_url}')
    
    if (credentials != None):
        client = storage.Client(credentials=credentials)
    else:
        client = storage.Client()
    
    uri = urlparse(gcs_url)
    bucket = uri.netloc
    path = uri.path[1:]    
    blobs = client.list_blobs(bucket)
    json_uri = ""
    summary = ""
    full_text = ""
    
    for blob in blobs:
        if path in blob.name:
            content = blob.download_as_string()

            blob_obj = json.loads(content)
            #print(json.dumps(blob_obj, indent=4, sort_keys=True))
            
            json_uri = f'{json_uri}gs://{bucket}/{blob.name}\n'
            summary = f'{summary}{blob_obj["entities"][0]["normalizedValue"]["text"]}\n'
            full_text = f'{full_text}{blob_obj["text"]}\n'
        
    return json_uri, summary, full_text

######################################################################
# Extract the blob uri, list of entities, and full extracted text of the 
# contract parser result from docAI workbench contract parser
######################################################################
def extract_from_contract_output(gcs_url: str, 
                                credentials: Optional[Credentials] = None):

    print(f'Extract docai summary parser output from {gcs_url}')
    
    if (credentials != None):
        client = storage.Client(credentials=credentials)
    else:
        client = storage.Client()
    
    uri = urlparse(gcs_url)
    bucket = uri.netloc
    path = uri.path[1:]    
    blobs = client.list_blobs(bucket)
    json_uri = ""
    entities = []
    full_text = ""
    
    for blob in blobs:
        if path in blob.name:
            content = blob.download_as_string()

            blob_obj = json.loads(content)
            #print(json.dumps(blob_obj, indent=4, sort_keys=True))
            
            json_uri = f'{json_uri}gs://{bucket}/{blob.name}\n'
            for entity in blob_obj['entities']:
                entities.append({'type':entity['type'], 
                                 'mentionText':entity['mentionText']})
                
            full_text = f'{full_text}{blob_obj["text"]}\n'
        
    return json_uri, entities, full_text

######################################################################
# Copy from one bucket to another
######################################################################
def copy_from_to(from_gcs_bucket: str, 
                 from_gcs_path: str, 
                 to_gcs_bucket: str, 
                 to_gcs_path: str,
                 credentials: Optional[Credentials] = None):
    
    print(f'Copy from {from_gcs_bucket}/{from_gcs_path} to {to_gcs_bucket}/{to_gcs_path}')
    
    if (credentials != None):
        client = storage.Client(credentials=credentials)
    else:
        client = storage.Client()
            
    src_bucket = client.bucket(from_gcs_bucket)
    dest_bucket = client.bucket(to_gcs_bucket)
    blobs = src_bucket.list_blobs(prefix=from_gcs_path)
        
    for blob in blobs:
        dest_blob_name = blob.name.replace(from_gcs_path, to_gcs_path, 1)
        blob_copy = dest_bucket.blob(dest_blob_name)
        blob_copy.rewrite(blob)
