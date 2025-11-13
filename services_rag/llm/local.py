# llm/openai_llm.py

from .base import BaseLLM

from openai import OpenAI


class LocalLLM(BaseLLM):

    def __init__(self, api_key: str):

        self.api_key = api_key

        self.client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")



    def generate(self, q: str, relevant_document: str) -> str:
        Instruction = """

        You are a helpful assistant that will give inforamtion about the services, the relevant documents about the services referenced in the users QUESTION have been provided to you, use them to answer the user's QUESTIONS. Answer the users QUESTION using the DOCUMENT text above. Keep your answer ground in the facts of the DOCUMENT.Please note that Service Name has been separated with ( \ ) to include parent service data, so a service whose name is 'A \ B \ C' be sub-sub service 'C' which is a sub-service of 'B' which is a sub-service of the service 'A'. this in mind when you encounter service names with that special character and present the name as Sub-service: name under service: name rather than the ' \ ' notation . You are answer should be well organized listing out requirements and the rest relevant data in a well formatted way. Be sure to indicate to the user other similar services/choices should there be any they have to consider. Take a natural tone when structuring your prompt. If the DOCUMENT doesn’t contain the facts to answer the QUESTION state clearly why you can't answer the prompt.
        VERY VERY IMPORTANT DO NOT SAY STUFF LIKE 'BASED ON THE PROVIDED INFORMATION' and the like that breaks the illusion of you being a rag-based assistant, you should act as if u r an assistant answering the users query make no mention of the system prompt or the data provided to u.
        """

        prompt = f"""

        DOCUMENT:

        {relevant_document}


        QUESTION:

        {q}


        INSTRUCTIONS:

        {Instruction}
        """
        

        response = self.client.chat.completions.create(

            model="local-model",  # Required parameter

            messages=[  

                {"role": "system", "content": Instruction},

                {"role": "user", "content": f"Context: {relevant_document}\n\nQuestion: {q}"}

            ],

            max_tokens=1000,

            temperature=0.7

        )

        return response.choices[0].message.content        

