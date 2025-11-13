# llm/openai_llm.py
from .base import BaseLLM
from google import genai
from google.genai import types

class GeminiLLM(BaseLLM):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = genai.Client(api_key=self.api_key)


    def generate(self, q: str, relevant_document: str) -> str:
        prompt = f"""
        DOCUMENT:
        {relevant_document}

        QUESTION:
        {q}

        INSTRUCTIONS:
        You are a helpful assistant that will give inforamtion about the services, the relevant
        documents about the services referenced in the users QUESTION have been provided to you, use them to answer the user's QUESTIOSN.
        Answer the users QUESTION using the DOCUMENT text above.
        Keep your answer ground in the facts of the DOCUMENT.
        If the DOCUMENT doesn’t contain the facts to answer the QUESTION state clearly why you can't answer the prompt
        """
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt],
            config=types.GenerateContentConfig(
                system_instruction="You are a helpful asssistant whose task is to give factual information about services to the user. Make sure to clearly mention the institution they should visit, requirements(documents they should bring etc), fees and other information about the services the user asked for",
                thinking_config=types.ThinkingConfig(thinking_budget=0) # Disables thinking
            ),
        )
        return response.text        
