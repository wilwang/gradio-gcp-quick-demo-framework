import vertexai.preview.generative_models as generative_models
from vertexai.preview.generative_models import GenerativeModel, GenerationConfig
from .config import GeminiConfig

def gemini_docqa_response(message, history, ground_text):
    model = GeminiConfig.model()
    temp = GeminiConfig.temperature()
    p = GeminiConfig.top_p()
    k = GeminiConfig.top_k()

    gemini_pro_model = GenerativeModel(model)
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
    resp = gemini_pro_model.generate_content(context, generation_config=config)

    return resp.text
