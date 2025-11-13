from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests 

class ActionRagFallback(Action):
    def name(self) -> Text:
        return "action_rag_fallback"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        user_message = tracker.latest_message.get("text")
        
        rag_api_url = f"http://localhost:8000/rag?q={user_message}"
        
        try:
            response = requests.get(
                rag_api_url,
                timeout=10
            )
            response.raise_for_status()  
            
            rag_result = response.json()
            
            rag_answer = rag_result.get("message", "Sorry, I couldn't find an answer in the knowledge base.")

            dispatcher.utter_message(text=rag_answer)

        except requests.exceptions.RequestException as e:
            print(f"RAG API call failed: {e}")
            dispatcher.utter_message(template="utter_rag_failure") 
        
        return []
