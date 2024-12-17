import google.generativeai as genai
class LLM:
    def __init__(self, API_TOKEN):
        self.API_TOKEN = API_TOKEN
        genai.configure(api_key=self.API_TOKEN)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def generate(self, prompt):
        response = self.model.generate_content(prompt)
        return response.text
