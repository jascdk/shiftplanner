from openai import OpenAI
import json
import os
import traceback

def extract_shifts_with_ai(pdf_text_content):
    """
    Sends raw PDF text to Gemini and asks for a JSON response.
    Returns a tuple: (list_of_shifts, error_message)
    """
    # Get the API key from the environment
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None, "OPENAI_API_KEY is not set in the environment."

    prompt = f"""
    You are a data extraction assistant. 
    Below is the text from a work shift PDF. 
    Extract all work shifts. 
    
    Return ONLY a valid JSON array of objects with these exact keys: 
    "date" (YYYY-MM-DD), 
    "start_time" (HH:MM in 24h format), 
    "end_time" (HH:MM in 24h format), 
    "title" (e.g., "Work Shift").
    
    Return the result as a JSON object with a single key "shifts" containing the array.
    Example: {{ "shifts": [ ... ] }}
    
    If a shift goes past midnight, split it or handle it logically, but ensure the date is correct.

    PDF CONTENT:
    {pdf_text_content}
    """

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Clean up response to ensure it's pure JSON
        cleaned_text = response.choices[0].message.content
        shifts = json.loads(cleaned_text)
        
        # Handle the wrapper key
        if isinstance(shifts, dict) and "shifts" in shifts:
            shifts = shifts["shifts"]
            
        return shifts, None
    except json.JSONDecodeError as e:
        error_message = f"AI returned invalid JSON. Error: {e}."
        print(f"JSONDecodeError: {error_message}")
        return None, error_message
    except Exception as e:
        error_message = f"An unexpected error occurred with the AI service. See container logs for full traceback."
        # Log the full exception, including traceback.
        print("--- Full Exception Traceback ---")
        traceback.print_exc()
        print("--------------------------------")
        return None, error_message