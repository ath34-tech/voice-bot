import logging
import asyncio
import json
from groq import AsyncGroq
from config import settings
from schemas import LLMResponse

logger = logging.getLogger(__name__)

class GroqClient:
    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set in environment variables.")
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        # using a model that's good at JSON
        self.interviewer_model = "llama-3.1-8b-instant" 

    async def get_structured_decision(self, prompt: str) -> LLMResponse:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                chat_completion = await self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a JSON-only AI. Always output valid JSON matching the schema requested." },
                        {"role": "user", "content": prompt}
                    ],
                    model=self.interviewer_model,
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                
                content = chat_completion.choices[0].message.content
                logger.info(f"LLM Raw JSON: {content}")
                
                data = json.loads(content)
                return LLMResponse(**data)
                
            except Exception as e:
                logger.error(f"LLM attempt {attempt+1} failed: {e}")
                await asyncio.sleep(1)
        
        # Fallback if everything fails
        return LLMResponse(
            action="ERROR",
            answer_status="unknown",
            answer=None,
            response="I'm sorry, I'm having a technical issue right now."
        )

    async def stream_opening_message(self):
        # We can just yield a simple string for the opening
        opening = "Hi there! I'm your AI interviewer. I'd like to ask you a few questions about how you study. Are you ready?"
        yield opening
