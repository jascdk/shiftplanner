import google.generativeai as genai
import json
import os

def extract_shifts_with_ai(pdf_text_content):
    """
    Sends raw PDF text to Gemini and asks for a JSON response.
    Returns a tuple: (list_of_shifts, error_message)
    """
    # Ensure API key is set in environment
    if not os.environ.get("GOOGLE_API_KEY"):
        return None, "GOOGLE_API_KEY is not set in the environment."

    prompt = f"""
    You are a data extraction assistant. 
    Below is the text from a work shift PDF. 
    Extract all work shifts. 
    
    Return ONLY a valid JSON array of objects with these exact keys: 
    "date" (YYYY-MM-DD), 
    "start_time" (HH:MM in 24h format), 
    "end_time" (HH:MM in 24h format), 
    "title" (e.g., "Work Shift").
    
    If you cannot find any shifts in the text, return an empty JSON array: [].
    If a shift goes past midnight, split it or handle it logically, but ensure the date is correct.
    Do not include markdown formatting like ```json. Just the raw JSON string.

    PDF CONTENT:
    {pdf_text_content}
    """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        
        # Clean up response to ensure it's pure JSON
        cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
        shifts = json.loads(cleaned_text)
        return shifts, None
    except json.JSONDecodeError as e:
        error_message = f"AI returned invalid JSON. Error: {e}. AI Response: '{response.text[:200]}...'"
        print(error_message)
        return None, error_message
    except Exception as e:
        error_message = f"An unexpected error occurred with the AI service: {e}"
        print(error_message)
        return None, error_message