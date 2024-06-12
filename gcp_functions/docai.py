from typing import Optional
from google.api_core.client_options import ClientOptions
from google.cloud import documentai as docai
from google.api_core.exceptions import InternalServerError
from google.api_core.exceptions import RetryError
from google.oauth2.service_account import Credentials
import io
import json

def process_document(
    project_id: str,
    location: str,
    processor_id: str,
    mime_type: str,
    gcs_input_uri: str,
    gcs_output_uri: str,
    field_mask: Optional[str] = None,
    processor_version_id: Optional[str] = None,
    credentials: Optional[Credentials] = None
):
    """
    Send a batch process request to the document AI processor

    Args:
        project_id: project id where processor is created
        location: location of the processor (us, global, etc)
        processor_id: id of the parser
        mime_type: file type that is being processed
        gcs_input_uri: the cloud storage URI of the file to be processed
        gcs_output_uri: the cloud storage URI of the folder where output gets sent
        field_mask: Optional. list of fields that a request should return
        processor_version_id: Optional. set to specify particular version of a model
        credentials: Optional. credentials to run as

    Returns:
       BatchProcessMetadata 
    """
    # You must set the `api_endpoint` if you use a location other than "us".
    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")

    # if no credentials, will use the default application credentials
    if credentials != None:
        client = docai.DocumentProcessorServiceClient(client_options=opts, credentials=credentials)
    else:
        client = docai.DocumentProcessorServiceClient(client_options=opts)

    gcs_document = docai.GcsDocument(gcs_uri=gcs_input_uri, mime_type=mime_type)
    gcs_documents = docai.GcsDocuments(documents=[gcs_document])
    input_config = docai.BatchDocumentsInputConfig(gcs_documents=gcs_documents)
    gcs_output_config = docai.DocumentOutputConfig.GcsOutputConfig(gcs_uri=gcs_output_uri,
                                                                   field_mask=field_mask)
    output_config = docai.DocumentOutputConfig(gcs_output_config=gcs_output_config)

    if processor_version_id:
        # The full resource name of the processor version, e.g.:
        # `projects/{project_id}/locations/{location}/processors/{processor_id}/processorVersions/{processor_version_id}`
        name = client.processor_version_path(project_id, 
                                             location, 
                                             processor_id, 
                                             processor_version_id)
    else:
        # The full resource name of the processor, e.g.:
        # `projects/{project_id}/locations/{location}/processors/{processor_id}`
        name = client.processor_path(project_id, location, processor_id)
        
    # Configure the batch process request
    request = docai.BatchProcessRequest(name=name, 
                                        input_documents=input_config,
                                        document_output_config=output_config)

    # Make the batch process request
    operation = client.batch_process_documents(request)

    try:
        print("Waiting for operation to complete...")
        response = operation.result()
    except (RetryError, InternalServerError) as e:
        print(e.message)

    # Once the operation is complete,
    # get output document information from operation metadata
    metadata = docai.BatchProcessMetadata(operation.metadata)
    
    if metadata.state != docai.BatchProcessMetadata.State.SUCCEEDED:
        raise ValueError(f"Batch Process Failed: {metadata.state_message}")

    print("process document complete")
    
    return metadata