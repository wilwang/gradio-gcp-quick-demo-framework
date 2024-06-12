import os
import json
from urllib.parse import urlparse
from google.cloud import storage
from typing import Optional
from google.oauth2.service_account import Credentials

def file_upload(file_url: str, 
                upload_bucket: str,
                credentials: Optional[Credentials] = None):
    """
    Helper function to upload a local file from gr.File() 
    to a designated Cloud Storage bucket

    Args:
        file_url: the local file path of he file to upload
        upload_bucket: bucket name to upload file to
        credentials: Optional. set to run as a specific user

    Returns:
        file_url: local file path of the file to upload
        gcs_upload_uri: the cloud storage URI of the file 
    """
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

def extract_from_summary_output(gcs_url: str, 
                                credentials: Optional[Credentials] = None):
    """
    Extract the blob uri, summary, and full extracted text of the 
    summarized result from docAI workbench summarizer

    Args: 
        gcs_url: the url of the output json of a document parser
        credentials: Optional. user to run as to get file from storage

    Returns:
        json_uri: URI of cloud storage directory of output
        summary: concatenated summary of the processor results
        full_text: the full OCR text from the parser
    """
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
    
    # output could be multiple json files; loop through them and concat results
    for blob in blobs:
        if path in blob.name:
            content = blob.download_as_string()

            blob_obj = json.loads(content)
            #print(json.dumps(blob_obj, indent=4, sort_keys=True))
            
            json_uri = f'{json_uri}gs://{bucket}/{blob.name}\n'
            summary = f'{summary}{blob_obj["entities"][0]["normalizedValue"]["text"]}\n'
            full_text = f'{full_text}{blob_obj["text"]}\n'
        
    return json_uri, summary, full_text

def extract_from_contract_output(gcs_url: str, 
                                credentials: Optional[Credentials] = None):
    """
    Extract the blob uri, list of entities, and full extracted text of the 
    contract parser result from docAI workbench contract parser

    Args: 
        gcs_url: the url of the output json of a document parser
        credentials: Optional. user to run as to get file from storage

    Returns:
        json_uri: URI of cloud storage directory of output
        entities: list of key value pair of extracted entities
        full_text: the full OCR text from the parser
    """
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
    
    # output could be multiple json files; loop through them and concat results
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

def copy_from_to(from_gcs_bucket: str, 
                 from_gcs_path: str, 
                 to_gcs_bucket: str, 
                 to_gcs_path: str,
                 credentials: Optional[Credentials] = None):
    """
    Copy from one GCS bucket to another

    Args: 
        from_gcs_bucket: cloud storage bucket of the "from" file
        from_gcs_path: path to the "from" file
        to_gcs_bucket: cloud storage bucket of the destination
        to_gcs_path: path of destination
        credentials: Optional. user to run as to get file from storage

    Returns:
        None
    """    
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
