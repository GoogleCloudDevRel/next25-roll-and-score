from google import genai
from google.genai import types


class GeminiCoach:
    def __init__(self, project_id: str, location: str,
                 model_id: str, system_instruction: str, prompt_template: str):
        self.client = genai.Client(
            vertexai=True,
            project=project_id,
            location=location,
        )
        self.model_id = model_id
        self.system_instruction = system_instruction
        self.prompt_template = prompt_template

    def _prepare_contents(self, gcs_video_uri: str, mime_type: str = "video/mp4"):
        prompts = self.prompt_template.split("{lane_view_video}")
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompts[0]),
                    types.Part.from_uri(
                        file_uri=gcs_video_uri,
                        mime_type=mime_type,
                    ),
                    types.Part.from_text(text=prompts[1])
                ]
            )
        ]
        return contents

    def _prepare_generate_content_config(self):
        generate_content_config = types.GenerateContentConfig(
            temperature=1,
            top_p=0.95,
            max_output_tokens=1024,
            response_modalities=["TEXT"],
            safety_settings=[types.SafetySetting(
                category="HARM_CATEGORY_HATE_SPEECH",
                threshold="BLOCK_ONLY_HIGH"
            ), types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="BLOCK_ONLY_HIGH"
            ), types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                threshold="BLOCK_ONLY_HIGH"
            ), types.SafetySetting(
                category="HARM_CATEGORY_HARASSMENT",
                threshold="BLOCK_ONLY_HIGH"
            )],
            system_instruction=[types.Part.from_text(text=self.system_instruction)],
        )
        return generate_content_config

    def generate_feedback(self, gcs_video_uri: str):
        contents = self._prepare_contents(gcs_video_uri)
        generate_content_config = self._prepare_generate_content_config()
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=contents,
            config=generate_content_config,
        )
        return response.text.strip()
