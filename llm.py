import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
import os
import time
import config
GEMINI_API_KEY = os.environ['GEMINI_API_KEY']

normal_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
}

json_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_schema": content.Schema(
    type = content.Type.OBJECT,
    properties = {
      "response": content.Schema(
        type = content.Type.ARRAY,
        items = content.Schema(
          type = content.Type.OBJECT,
          properties = {
            "anime_id": content.Schema(
              type = content.Type.INTEGER,
            ),
            "tags": content.Schema(
              type = content.Type.ARRAY,
              items = content.Schema(
                type = content.Type.STRING,
              ),
            ),
          },
        ),
      ),
    },
  ),
  "response_mime_type": "application/json",
}
class LLM:
    def __init__(self):
        self.API_TOKEN = GEMINI_API_KEY
        genai.configure(api_key=self.API_TOKEN)


    async def generate(self, prompt):
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=normal_config,
        )
        while True:
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                print(e)
                time.sleep(0.01)

    def generate_multi_tags(self, anime_list):
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=json_config,
        )
        prompt = ""
        for anime in anime_list:
            prompt += f"title: {anime[1]}\n"
            prompt += f"anime_id: {anime[0]}\n"
            prompt += f"synopsis: {anime[2]}\n"
        prompt += config.GENERATE_TAGS_PROMPT
        while True:
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                print(e)
                time.sleep(0.01)
