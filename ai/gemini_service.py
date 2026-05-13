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
    For "date", provide a string in YYYY-MM-DDTHH:MM format. Assume today is {{today_date}} and current time is {{current_time}}. If no date or time is mentioned, use the current date and time.
    For "category", infer a short, common category from this list: Food & Dining, Groceries, Transport, Housing, Utilities, Healthcare, Entertainment, Shopping, Education, Salary, Freelance, Investment, Other.
    For "description", provide a brief summary of the transaction based on the text.
    
    Text: "{text}"
    
    Expected JSON Format:
    {{
      "amount": 0.0,
      "category": "string",
      "description": "string",
      "date": "YYYY-MM-DDTHH:MM",
      "type": "income|expense"
    }}
    
    JSON:
    """
    
    # We inject the actual today's date and time into the prompt
    from datetime import datetime
    now = datetime.now()
    today_date = now.strftime('%Y-%m-%d')
    current_time = now.strftime('%H:%M')
    prompt = prompt.replace("{today_date}", today_date)
    prompt = prompt.replace("{current_time}", current_time)

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
        logging.error(f"Error parsing transaction with Gemini: {e}")
        raise

def generate_financial_insights(summary_data: dict, user_question: str = None) -> dict:
    """
    Generates personalized financial insights using Gemini based on summarized transaction data.
    """
    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    system_prompt = f"""
    You are an expert AI financial advisor. Analyze the following summarized financial data for the user.
    Provide a short, conversational health summary, identify any unusual spending patterns, and give 3 actionable savings recommendations.
    Keep the tone encouraging, concise, and professional.
    
    Summarized Data:
    {json.dumps(summary_data, indent=2)}
    """
    
    if user_question:
        system_prompt += f"\n\nThe user also asked a specific question: '{user_question}'\nPlease answer this question directly in the 'answer' field."
    else:
        system_prompt += "\n\nThe user did not ask a specific question. Leave the 'answer' field null."
        
    system_prompt += """
    
    Output exactly in this JSON format:
    {
      "health_summary": "A conversational paragraph about their financial state.",
      "anomalies": ["Unusual pattern 1", "Unusual pattern 2"],
      "recommendations": ["Tip 1", "Tip 2", "Tip 3"],
      "answer": "Answer to user question, or null"
    }
    """
    
    try:
        response = model.generate_content(system_prompt)
        response_text = response.text.strip()
        
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
            
        return json.loads(response_text.strip())
    except Exception as e:
        logging.error(f"Error generating insights with Gemini: {e}")
        raise
