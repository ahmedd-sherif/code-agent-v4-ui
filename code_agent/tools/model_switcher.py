"""
Model Switcher Tool - Allows switching between LLM providers.
"""

import os

# Available Models Configuration
AVAILABLE_MODELS = {
    # Gemini Models (Google AI Studio)
    "gemini-2.0-flash": {
        "provider": "google",
        "model_id": "gemini-2.0-flash",
        "description": "Google Gemini 2.0 Flash - Fast and capable"
    },
    "gemini-1.5-flash": {
        "provider": "google", 
        "model_id": "gemini-1.5-flash",
        "description": "Google Gemini 1.5 Flash - Stable"
    },
    "gemini-1.5-pro": {
        "provider": "google",
        "model_id": "gemini-1.5-pro", 
        "description": "Google Gemini 1.5 Pro - Most capable"
    },
    # Groq Models (via LiteLLM)
    "groq-llama3-70b": {
        "provider": "groq",
        "model_id": "groq/llama-3.3-70b-versatile",
        "description": "Llama 3.3 70B on Groq - Very fast"
    },
    "groq-llama3-8b": {
        "provider": "groq",
        "model_id": "groq/llama-3.1-8b-instant",
        "description": "Llama 3.1 8B on Groq - Ultra fast"
    },
    "groq-mixtral": {
        "provider": "groq",
        "model_id": "groq/mixtral-8x7b-32768",
        "description": "Mixtral 8x7B on Groq - Balanced"
    },
}


def list_models() -> dict:
    """
    List all available AI models that can be used.
    
    Returns:
        dict: List of available models with their descriptions
    """
    models_list = []
    for key, config in AVAILABLE_MODELS.items():
        models_list.append({
            "key": key,
            "provider": config["provider"],
            "description": config["description"]
        })
    
    return {
        "status": "success",
        "available_models": models_list,
        "note": "To switch models, you need to restart the agent with a different DEFAULT_MODEL in agent.py"
    }


def get_current_model() -> dict:
    """
    Get the currently active model.
    
    Returns:
        dict: Current model information
    """
    # Read from environment or default
    current = os.getenv("CURRENT_MODEL", "groq-llama3-70b")
    
    if current in AVAILABLE_MODELS:
        config = AVAILABLE_MODELS[current]
        return {
            "status": "success",
            "current_model": current,
            "provider": config["provider"],
            "description": config["description"]
        }
    
    return {
        "status": "success",
        "current_model": current,
        "note": "Model info not found in configuration"
    }
