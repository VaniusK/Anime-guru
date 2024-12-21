from imports import *
GEMINI_API_KEY = os.environ['GEMINI_API_KEY']

normal_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
}

mutli_tags_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
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

multi_anime_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
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
            "anime_title": content.Schema(
              type = content.Type.STRING,
            ),
            "compliance_factor": content.Schema(
              type = content.Type.NUMBER,
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
            model_name="gemini-2.0-flash-exp",
            generation_config=normal_config,
        )
        while True:
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                time.sleep(0.01)

    def generate_multi_tags(self, anime_list):
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config=mutli_tags_config,
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
                time.sleep(0.01)

    def rate_multi_anime_by_request(self, anime_list, request):
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config=multi_anime_config,
        )
        prompt = ""
        for anime in anime_list:
            prompt += str(anime) + '\n'
        prompt += f"User's request: \"{request}\""
        prompt += f"\n{config.RATE_ANIME_PROMPT}"
        while True:
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                print(e)
                time.sleep(0.01)