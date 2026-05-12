import google.generativeai as genai
import json
import logging
from flask import current_app

def parse_natural_language_transaction(text: str) -> dict:
    """
    Parses a natural language transaction description into a structured dictionary.
    Returns a dict with keys: amount, category, description, date (YYYY-MM-DD), type (income/expense).
    """
    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured.")

    genai.configure(api_key=api_key)
    
    # Use an available model based on the API key
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    Extract transaction details from the following text and output ONLY a valid JSON object.
    If the text implies money received (e.g., salary, sold item, refund), set "type" to "income".
    If the text implies money spent (e.g., paid, bought, spent), set "type" to "expense".
    For "amount", provide a positive float number.
    For "date", provide a string in YYYY-MM-DD format (use current date if 'today', 'yesterday' = current date - 1). Assume today is {{today_date}}. If no date is mentioned, use today's date.
    For "category", infer a short, common category (e.g., Food, Transport, Salary, Entertainment, Utilities, Other).
    For "description", provide a brief summary of the transaction based on the text.
    
    Text: "{text}"
    
    Expected JSON Format:
    {{
      "amount": 0.0,
      "category": "string",
      "description": "string",
      "date": "YYYY-MM-DD",
      "type": "income|expense"
    }}
    
    JSON:
    """
    
    # We inject the actual today's date into the prompt so the model knows what "today" means.
    from datetime import datetime
    today_date = datetime.now().strftime('%Y-%m-%d')
    prompt = prompt.replace("{today_date}", today_date)

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean up any markdown formatting if present (e.g., ```json ... ```)
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
            
        parsed_json = json.loads(response_text.strip())
        return parsed_json
    except Exception as e:
        logging.error(f"Error parsing transaction with Gemini: {{e}}")
        raise
