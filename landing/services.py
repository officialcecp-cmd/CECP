import os
import re
import logging

logger = logging.getLogger(__name__)

def categorize_project_level(spec_text: str) -> str:
    """
    Analyzes the project specification text and automatically categorizes it
    into one of three levels: Beginner, Intermediate, or Pro.
    
    In a fully productionized setup, this function sends the spec_text to an 
    LLM API (like OpenAI or Gemini). For now, it uses a robust fallback 
    heuristic based on keywords, allowing the frontend UI to work immediately.
    """
    if not spec_text:
        return 'Beginner'

    # Try to simulate an AI API Call if an API key is provided
    # (Placeholder for future OpenAI / Gemini integration)
    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key:
        try:
            # Placeholder: Make request to LLM here
            # response = openai.ChatCompletion.create(...)
            # return response.choices[0].message.content.strip()
            logger.info("AI API Key detected. (Integration pending)")
            pass 
        except Exception as e:
            logger.error(f"AI API call failed: {e}. Falling back to heuristic.")

    # --- Fallback Heuristic Categorization ---
    text = spec_text.lower()
    
    pro_keywords = [
        'tensorrt', 'kubernetes', 'microservices', 'kernel', 'fpga', 
        'custom pcb', 'deep learning', 'transformer', 'distributed',
        'yolo', 'autonomous', 'defense', 'aerospace', 'rtos'
    ]
    
    intermediate_keywords = [
        'opencv', 'api', 'react', 'django', 'database', 'sql',
        'raspberry pi', 'esp32', 'machine learning', 'pid control',
        'socket', 'wireless'
    ]
    
    # Calculate score based on keyword frequency
    pro_score = sum(1 for kw in pro_keywords if kw in text)
    int_score = sum(1 for kw in intermediate_keywords if kw in text)
    
    if pro_score >= 1 or int_score >= 3:
        return 'Pro'
    elif int_score >= 1:
        return 'Intermediate'
    else:
        return 'Beginner'
