import vertexai.generative_models as generative_models
from vertexai.generative_models import GenerativeModel, GenerationConfig, Part
from .config import GeminiConfig

def gemini_docqa_response(message, history, ground_text):
    """
    Function to handle the document Q&A interaction

    Args:
        message: the question to send to the LLM
        history: full context of chat history (Not currently used)
        ground_text: text to use as context for the prompt
    """
    model_name = GeminiConfig.model()
    temp = GeminiConfig.temperature()
    p = GeminiConfig.top_p()
    k = GeminiConfig.top_k()

    model = GenerativeModel(model_name)
    config = GenerationConfig(
        # Only one candidate for now.
        candidate_count=1,
        temperature=temp,
        top_p=p,
        top_k=k)

    context = f"""
    Answer any questions using only data from the context below:\n

    {ground_text}
    
    Do not answer any questions where you do not have context for.
    
    Question: {message}
    """
    resp = model.generate_content(context, generation_config=config)

    return resp.text



def gemini_audio_response(audio_uri, prompt):
    """
    Function to handle the response from a Gradio Audio component that returns
    type of "filepath"

    Args: 
        audio_uri: the gcs uri of the audio file
        prompt: the prompt to pass to the generative model
    """
    model_name = GeminiConfig.model()
    temp = GeminiConfig.temperature()
    p = GeminiConfig.top_p()
    k = GeminiConfig.top_k()

    model = GenerativeModel(model_name)
    config = GenerationConfig(
        # Only one candidate for now.
        candidate_count=1,
        temperature=temp,
        top_p=p,
        top_k=k)

    audio_file = Part.from_uri(audio_uri, mime_type="audio/wav")
    contents = [audio_file, prompt]

    response = model.generate_content(contents)

    return response.text

