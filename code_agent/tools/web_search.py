import os
import logging
from tavily import TavilyClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logger setup
logger = logging.getLogger(__name__)

def web_search(query: str) -> str:
    """
    Performs a web search using the Tavily API and returns a summary of the results.
    Useful for finding documentation, solutions to errors, or general information.
    
    Args:
        query: The search query string.
        
    Returns:
        A string containing the search results or an error message.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "Error: TAVILY_API_KEY not found in environment variables. Please ask the user to provide it."

    try:
        client = TavilyClient(api_key=api_key)
        # using search_depth="advanced" for better results usually, but "basic" is faster.
        # "answer" type returns a direct answer which is nice for agents.
        response = client.search(query=query, search_depth="advanced", include_answer=True)
        
        output = []
        if response.get("answer"):
            output.append(f"**Answer:** {response['answer']}\n")
        
        output.append("**Results:**")
        for result in response.get("results", [])[:5]: # Top 5 results
            title = result.get("title", "No Title")
            url = result.get("url", "#")
            content = result.get("content", "")[:300] # Truncate content
            output.append(f"- [{title}]({url}): {content}...")
            
        return "\n".join(output)
        
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return f"Error performing web search: {str(e)}"

def read_url(url: str) -> str:
    """
    Reads the content of a specific URL. 
    (Note: Tavily extract or just pure request can be used. Tavily extract is powerful).
    
    Args:
        url: The URL to read.
        
    Returns:
        Content of the page.
    """
    # Simply reusing search for now or could use specialized extract if needed.
    # For V1 of this tool, let's try to use Tavily's extract capability if available or just basic search context.
    # Tavily has an 'extract' feature but it might be separate. 
    # Let's use search with the URL as query context or just rely on the agent to search.
    
    # Actually, let's implement a simple requests based reader or use Tavily's robust 'get_search_context'
    # But for now, let's keep it simple with just 'web_search' as the primary tool.
    # We can add a specialized reader later if 'web_search' isn't enough.
    return web_search(f"site:{url} content summary")
