import google.generativeai as genai # type: ignore
import os

# Configure Gemini with your API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# AI task suggestion
def get_ai_task_suggestion():
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = "Give me a short, fun, and motivating study or wellness task for a student."
    response = model.generate_content(prompt)
    return response.text.strip()

# AI check-in based on mood
def get_ai_checkin_response(mood):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"My current mood is {mood}. Suggest one quick mindfulness tip or uplifting quote."
    response = model.generate_content(prompt)
    return response.text.strip()
