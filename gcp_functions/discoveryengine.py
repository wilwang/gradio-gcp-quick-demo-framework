from typing import List
from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1 as discoveryengine
from .config import DiscoveryEngineConfig
from urllib.parse import quote

def search(project_id: str, 
            engine_id: str, 
            model_context_prompt: str, 
            search_query: str):
    '''
    Search function against Vertex Search / Discovery Engine API

    Args:
        project_id: id for the project that hosts the search engine
        engine_id: id of the vertex agent app
        model_context_prompt: customize preamble prompt for the model
        search_query: prompt/question for the search engine

    Returns:
        summary: summary output that combines the summary text and search results
        response: raw response of the search engine
    '''
    location = DiscoveryEngineConfig.location()

    client_options = (
        ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
        if location != "global"
        else None
    )

    # Create a client
    client = discoveryengine.SearchServiceClient(client_options=client_options)

    # The full resource name of the search app serving config
    serving_config = f"projects/{project_id}/locations/{location}/collections/default_collection/engines/{engine_id}/servingConfigs/default_config"

    # Optional: Configuration options for search
    # Refer to the `ContentSearchSpec` reference for all supported fields:
    # https://cloud.google.com/python/docs/reference/discoveryengine/latest/google.cloud.discoveryengine_v1.types.SearchRequest.ContentSearchSpec
    content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(
        # For information about snippets, refer to:
        # https://cloud.google.com/generative-ai-app-builder/docs/snippets
        snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
            return_snippet=True
        ),
        # For information about search summaries, refer to:
        # https://cloud.google.com/generative-ai-app-builder/docs/get-search-summaries
        summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
            summary_result_count=5,
            include_citations=True,
            ignore_adversarial_query=True,
            ignore_non_summary_seeking_query=True,
            #model_prompt_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelPromptSpec(
            #    preamble=model_context_prompt
            #),
            model_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelSpec(
                version="stable",
            ),
            use_semantic_chunks=False
        ),
        extractive_content_spec=discoveryengine.SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
            max_extractive_answer_count=1
        )
    )

    # Refer to the `SearchRequest` reference for all supported fields:
    # https://cloud.google.com/python/docs/reference/discoveryengine/latest/google.cloud.discoveryengine_v1.types.SearchRequest
    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=search_query,
        page_size=10,
        content_search_spec=content_search_spec,
        query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
            condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
        ),
        spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
            mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
        ),
    )

    response = client.search(request)
    summary = response.summary.summary_text

    # only returning 2 search results for purposes of demo
    max_results = 2
    count = 0
    for result in response.results:
        if count >= max_results:
            continue
        else:
            title = result.document.derived_struct_data["title"]
            gslink = result.document.derived_struct_data["link"]
            file_uri = gslink.replace("gs://", "")
            link = f'https://storage.cloud.google.com/{quote(file_uri)}'
            ans = result.document.derived_struct_data["extractive_answers"][0]
            pageNum = ans["pageNumber"]
            content = ans["content"]

            summary = f'{summary}\n\n[{title}]({link})\nPage: {pageNum}\n{content}'        
            count = count + 1
    #print (response)

    return summary, response
