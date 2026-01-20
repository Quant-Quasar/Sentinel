import os
import time
import random
import json
from typing import Type, TypeVar, Any
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

T = TypeVar("T", bound=BaseModel)

class LLMClient:
    # You can change this to "gemini-1.5-pro-002" if you want reasoning
    def __init__(self, model="gemini-3-flash-preview"):
        self.model_name = model
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError("❌ CRITICAL: GEMINI_API_KEY not found in .env file.")
            
        self.client = genai.Client(api_key=api_key)

    def _sanitize_schema(self, schema: Any) -> Any:
        if isinstance(schema, dict):
            for key in ["additionalProperties", "title"]:
                if key in schema:
                    del schema[key]
            for key, value in schema.items():
                self._sanitize_schema(value)
        elif isinstance(schema, list):
            for item in schema:
                self._sanitize_schema(item)
        return schema

    def get_structured_completion(self, system_prompt: str, user_prompt: str, response_model: Type[T]) -> T:
        """
        Robust Client with Aggressive Backoff for Pro Models.
        """
        max_retries = 5 # Increased retries
        
        # If using Pro, start with a high delay
        if "pro" in self.model_name.lower():
            base_delay = 35 # 35 seconds minimum for Pro tier
        else:
            base_delay = 5  # 5 seconds for Flash tier
        
        for attempt in range(max_retries):
            try:
                raw_schema = response_model.model_json_schema()
                clean_schema = self._sanitize_schema(raw_schema)

                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        response_mime_type="application/json",
                        response_schema=clean_schema,
                        temperature=0.1
                    )
                )
                
                if hasattr(response, "parsed") and response.parsed:
                    try:
                        return response_model(**response.parsed)
                    except:
                        import json
                        return response_model(**json.loads(response.text))
                
                import json
                data = json.loads(response.text)
                return response_model(**data)
                
            except Exception as e:
                error_str = str(e)
                # Catch 429 (Rate Limit) AND 503 (Service Overload)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "503" in error_str:
                    if attempt < max_retries - 1:
                        # Exponential Backoff: 35s -> 70s -> 140s
                        wait_time = (base_delay * (2 ** attempt)) + random.uniform(1, 5)
                        print(f"   ⏳ Rate Limit/Overload ({self.model_name}). Sleeping for {wait_time:.1f}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"   🔥 Max Retries Exceeded.")
                        raise e
                else:
                    print(f"   🔥 GEMINI ERROR: {error_str}")
                    raise e